# Grok as Main Orchestrator in OpenAI Agents SDK — Investigation

**Researched:** 2026-04-20
**Scope:** Why Grok models stall at the Director phase under `openai-agents-python`, and how to make Grok finish the full Skeleton → Script → Director pipeline while keeping its 2–3× speed advantage over m25.
**Confidence:** HIGH on the root cause (verified in SDK source); MEDIUM on the ranked remediation paths (based on public docs + SDK source, not yet empirically re-benchmarked).

---

## 1. TL;DR

1. **The Director never fires on Grok because `openai-agents-python` has a terminal condition that says "if the latest turn has text output but no `tool_calls`, the run is finished."** `minimal_combo` mode *requires* the agent to emit markdown prose sections (`# Story`, `# Characters`) as pure text in the same turn it is otherwise expected to keep calling `save_shot_prompt` / `render_image`. The moment Grok satisfies the "output markdown" instruction without *also* attaching a tool call to that same assistant message, `turn_resolution.py` classifies the message as final output and exits. m25 happens to always pair text+tool_calls; Grok 4.1 Fast in non-reasoning mode leans toward emitting "I'm done with structure, here's the summary" and stopping.
2. **Concrete next step (cheapest, most likely to work):** kill the dual-channel design in `minimal_combo`. Convert the four existing tools into five so that `# Story` and `# Characters` also become tool calls (`save_story_markdown`, `save_characters_markdown`) — both accept a single `markdown: str`, persist it, and return `OK`. This removes every opportunity for Grok to end a turn on pure text. Re-run the bench; expected wall ≈ 3:00–4:00, expected shots ≥ 15.
3. **If step 2 still leaves Director weak**, switch to a 2-agent handoff (`grok-skeleton-agent` → `grok-director-agent`) using the SDK's `handoffs=` parameter with an explicit `transfer_to_director` tool. Handoff preserves history, and the second agent has a *smaller tool set focused on Director work*, which sharply reduces the "the model thinks it's done" failure mode. Each sub-agent can still run on a Grok variant (non-reasoning for Skeleton/Script speed, reasoning for Director planning).
4. **Do not** switch off `openai-agents-python`. The SDK is a minor configuration problem, not an architectural mismatch. LangGraph migration would cost days and solve nothing here.

---

## 2. Core Diagnosis — why Grok stalls at Director

### 2.1 The SDK's terminal rule (verified)

File: `.venv/lib/python3.12/site-packages/agents/run_internal/turn_resolution.py`, lines 670–716.

```python
message_items = [item for item in new_step_items if isinstance(item, MessageOutputItem)]
potential_final_output_text = (
    ItemHelpers.extract_text(message_items[-1].raw_item) if message_items else None
)

if not processed_response.has_tools_or_approvals_to_run():
    has_tool_activity_without_message = not message_items and bool(
        processed_response.tools_used
    )
    if not has_tool_activity_without_message:
        ...
        if not output_schema or output_schema.is_plain_text():
            return await execute_final_output_call(
                ...,
                final_output=potential_final_output_text or "",
                ...
            )

return SingleStepResult(..., next_step=NextStepRunAgain(), ...)
```

Rule: **if the model's latest turn produced any assistant text AND no new tool calls, the SDK exits with `NextStepFinalOutput`** (unless `tools_used` is non-empty *and* no text was emitted — an edge case). The docs confirm this in plain language: *"The rule for whether the LLM output is considered as a 'final output' is that it produces text output with the desired type, and there are no tool calls."* ([openai.github.io/openai-agents-python/running_agents](https://openai.github.io/openai-agents-python/running_agents/))

### 2.2 How this interacts with `minimal_combo`

`MINIMAL_COMBO_INSTRUCTIONS` explicitly asks the agent to output `# Story` and `# Characters` as markdown text in the *assistant response body*, not via a tool. The workflow depends on a delicate contract: every turn must *also* include at least one tool call (`freeform_script_worker`, then later `save_shot_prompt` / `render_image`) so the loop continues. On m25, empirically this contract is held. On Grok, it breaks in one of two places:

- **Mode A (observed in `grok-4-1-fast-non-reasoning + minimal-combo`, 2:47, 0 shots):** Grok completes Skeleton + Script phase (emits markdown Story/Characters, calls `freeform_script_worker` one or more times), then opens a turn that contains *only* a summary paragraph ("I've finished the prose. Now I'll design the shots...") with no tool call attached. SDK sees text + no tool_calls → exits. Director never happens.
- **Mode B (observed in reasoning variants, 1 shot):** Grok does call `save_shot_prompt` once, then emits "I'll continue with the remaining shots" as plain text without attaching the next tool call to that turn. SDK exits.

Both failure modes stem from the same SDK rule. Neither is visible in isolation; they look like "Grok stopped early" which is why the team's initial framing was "Director doesn't point-fire" — but it's not a Grok-generative problem, it's a **handshake** problem between Grok's turn-granularity habits and the SDK's turn-termination rule.

### 2.3 Why Grok's turn-granularity differs from m25

From xAI's own docs ([docs.x.ai/developers/release-notes](https://docs.x.ai/developers/model-capabilities/text/reasoning)) and the [Grok 4.1 Fast announcement](https://x.ai/news/grok-4-1-fast): "Grok decides when and how to use tools, often invoking multiple tools in parallel across several turns, until it has everything it needs to deliver a final answer." The key word is *"until it has everything it needs"* — the model autonomously chooses to stop issuing tool calls when it judges the task complete. For Grok's internal RL reward surface (trained on customer support and deep research use cases), "task complete" often means "I've issued the obvious calls and now I should summarise."

The 105KB system prompt amplifies this. Even though Grok's 2M context handles the size, the skill corpus repeatedly describes the Director phase using the old tool names (`write_beat_shots`, `validate_vgai`). The `SKILL DISAMBIGUATION` preamble explicitly tells Grok to substitute `save_shot_prompt`, but the skill text itself still *reads as if Director has optional tooling* — Grok's parser weights the skill body more than the short override block and concludes "Director ran successfully when I summarised the plan."

**Root cause (one sentence):** the `minimal_combo` instruction asks Grok to emit any pure-text turn, and the SDK terminates on the first pure-text turn — so Grok stops Director before it starts, without any problem in Grok's tool-calling capability itself.

### 2.4 Side-effects mistaken for root causes

- **"Tool-call-mode bias U-curve"** (1 → 4 → 13 tools) is real but is not why Grok stalls. It's why `minimal_combo` (4 tools) is better than default (13 tools): at 13 tools Grok's arg-ceremony overhead compresses output. But even with the right tool count, the pure-text termination still triggers.
- **"Style Preamble byte-lock drift"** is a separate Director-quality problem (manifests when Grok *does* reach Director), not a fire-start problem. Fixing P0 termination exposes this, not creates it.
- **"REJECT retry shrinkage"** is a property of Grok's validation-pressure response curve and is neutralised by `freeform_script_worker` (no CJK validator). It applies to Script, not Director.

---

## 3. P0 — Grok + OpenAI Agents SDK compatibility

### 3.1 `tool_choice` semantics and what to set

Three xAI-accepted values, per [docs.x.ai/docs/guides/function-calling](https://docs.x.ai/docs/guides/function-calling):

| Value | Behavior on Grok 4.1 Fast | Verdict for crpg |
|-------|----------------------------|------------------|
| `"auto"` (default) | Model decides per turn. Compatible with multi-turn loops where some turns are reasoning-only. | **Default. Keep.** |
| `"required"` | Every response must contain at least one tool call. Empirically Grok will then emit a "no-op" tool call or degrade to one tool per turn. | **Do NOT use globally.** |
| `"none"` | No tool calls. | N/A. |

The SDK's `ModelSettings` already supports passing these. Note: `openai-agents-python` resets `tool_choice` back to `"auto"` automatically after every tool call to prevent infinite loops (`agent.reset_tool_choice=True` by default) — confirmed at [openai.github.io/openai-agents-python/agents](https://openai.github.io/openai-agents-python/agents/). So you cannot use `tool_choice="required"` as a persistent "force Director" lever; it degrades to `auto` the moment one tool fires.

**Trick we can exploit:** set `tool_choice="required"` *in combination with* `reset_tool_choice=False` for the Director sub-agent (in handoff mode — see §4.2). This guarantees every turn of the Director phase emits at least one tool call, blocking the pure-text early-exit path.

Caveat: a known edge case exists where `tool_choice` set to a specific *function name* (rather than `"auto"`/`"required"`/`"none"`) crashes with Pydantic validation errors when streaming through LiteLLM — reported in [openai-agents-python#980](https://github.com/openai/openai-agents-python/issues/980) and [#1846](https://github.com/openai/openai-agents-python/issues/1846). If you use `tool_choice`, keep it to the three literals only.

### 3.2 `parallel_tool_calls`

Default on xAI: enabled. Per [xAI function-calling docs](https://docs.x.ai/docs/guides/function-calling): *"By default, parallel function calling is enabled — the model can request multiple tool calls in a single response."* The SDK passes it through when tools are registered (see `openai_chatcompletions.py:355`). **Keep enabled.** For Director, parallel calls are exactly what we want — Grok can, in a single turn, plan 3 shots and emit `save_shot_prompt` ×3 side-by-side, halving wall-time.

One caveat: the 4.1 Fast model card confirms parallel tool calling, but does *not* guarantee that all three calls fit in one response if `max_tokens` is constrained. We currently don't set `max_tokens` so this is moot, but note: [public reports](https://www.datastudios.org/post/grok-context-window-token-limits-memory-policy-and-2025-rules) confirm "once total tokens exceed the cap, Grok may stop referencing earlier messages, fail to execute tools, or return partial completions." Our 105KB system prompt leaves enormous headroom; no concern here.

### 3.3 System prompt length

xAI has no official upper bound, but prompt engineering writeups converge on two pieces of advice relevant to us:

- **Segment with XML tags or Markdown headers** ([datastudios.org grok prompting guide](https://www.datastudios.org/post/grok-prompt-engineering-full-guide-on-practical-prompting-tool-use-control-structured-outputs-an)): *"XML-tagged context works like labeled folders... prevents the model from conflating examples with instructions."* Our skill corpus uses `===== SKILL: script =====` delimiters which is fine but not XML; Grok will likely parse it, but XML `<skill name="script">...</skill>` would be a free upgrade.
- **Stable prefix for prompt caching:** *"A stable system instruction and stable prefix reduce the amount of 'new' text the model must interpret."* Our skill corpus *is* stable across runs (same 3 SKILL.md + same references). xAI's caching infra will exploit this only if the prefix is byte-identical across requests. Our current code builds `full_instructions` by concatenation — deterministic — so caching should engage.

There's no public "100KB is too much" threshold for Grok 4.1 Fast. The 2M context is real, and the long-horizon RL training [per xAI](https://x.ai/news/grok-4-1-fast) specifically addresses consistency across the full span. **105KB is not the problem.**

### 3.4 Streaming + tool use

The SDK's `Runner.run` is non-streaming by default (our current code path). The streaming path `Runner.run_streamed` is known to have fiddly tool_choice handling ([#980](https://github.com/openai/openai-agents-python/issues/980), [#1846](https://github.com/openai/openai-agents-python/issues/1846)) and a latency-after-last-token bug ([#2343](https://github.com/openai/openai-agents-python/issues/2343)). **We're safe — don't switch to streaming without explicit reason.**

### 3.5 Reasoning-mode parameter

Critical correction to an assumption you might be making: `grok-4-1-fast-reasoning` and `grok-4-1-fast-non-reasoning` are **two separate model IDs** on xAI direct. There is no `reasoning_effort` or `reasoning_enabled` parameter accepted by either model — per [xAI reasoning docs](https://docs.x.ai/developers/model-capabilities/text/reasoning): *"Not supported. Specifying reasoning_effort on these models will return an error."* The model ID choice IS the reasoning switch. ([aimlapi grok-4-1-fast-reasoning docs](https://docs.aimlapi.com/api-references/text-models-llm/xai/grok-4-1-fast-reasoning) confirms this.)

Practical implication: when the `grok-combo` profile tries to do "reasoning main + non-reasoning worker," the main agent must be built with `grok-4-1-fast-reasoning`, the worker with `grok-4-1-fast-non-reasoning`. Looking at the current `PROFILES` dict this is what `grok-combo` does — good. But note: OpenRouter's `x-ai/grok-4.1-fast` exposes the reasoning switch as a `reasoning: {enabled: true|false}` body parameter ([OpenRouter page](https://openrouter.ai/x-ai/grok-4.1-fast)), so *if* you later route via OpenRouter instead of xAI direct, the parameterisation changes.

Reasoning vs tool use compatibility: both modes support tool use; xAI claims Grok 4.1 Fast is *"xAI's best agentic tool-calling model"* regardless of reasoning mode. There is no documented "reasoning + tools" conflict. Reasoning mode does burn more output tokens for thinking, which is why it's slower — not a correctness issue.

### 3.6 Structured outputs — the underused weapon

[docs.x.ai/developers/model-capabilities/text/structured-outputs](https://docs.x.ai/developers/model-capabilities/text/structured-outputs):

> "Structured outputs is supported by all language models... Structured outputs with tools is only available for supported Grok 4 family models... The model is guaranteed to match your input schema."

Grok 4.1 Fast is in the supported family. You can pass `response_format={"type": "json_schema", "json_schema": {...}}` *simultaneously* with a tool list.

**This is the lever that replaces per-shot `save_shot_prompt` calls.** Instead of making the agent emit 17 sequential tool calls for 17 shots, define a schema:

```json
{
  "type": "object",
  "properties": {
    "beat_shots": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "beat_id": {"type": "string"},
          "shot_id": {"type": "string"},
          "final_prompt": {"type": "string"},
          "aspect_ratio": {"type": "string"},
          "anchor_ref": {"type": "string"}
        },
        "required": ["beat_id", "shot_id", "final_prompt", "aspect_ratio"]
      }
    }
  },
  "required": ["beat_shots"]
}
```

Ask the agent to emit the *complete* shot list as one structured JSON response (which *is* a final-output turn — that's fine, the SDK terminates correctly here), parse it server-side, then *separately* iterate `render_image` calls yourself outside the agent loop.

Caveats from the xAI docs: no `allOf`, no `minItems`/`maxItems`, no `minLength`/`maxLength`. So validation of "Style Preamble byte-for-byte" can't live in the schema — that stays in your Python code. The schema gives you structural type safety, not string-content lock.

The SDK supports this via `Agent.output_type=SomeModel` (Pydantic model) — see [openai.github.io/openai-agents-python/ref/agent](https://openai.github.io/openai-agents-python/ref/agent/). It does produce an early terminal turn when the structured output is emitted. That termination is *expected and correct* for a "generate all shots at once" sub-agent.

### 3.7 Known openai-agents-python + Grok issues

- [#1056](https://github.com/openai/openai-agents-python/issues/1056) ("xAI Grok 4 Usage"): closed stale, no official integration docs. User ran into the "how do I wire LiteLLM" question. Our approach (direct `AsyncOpenAI` with `base_url="https://api.x.ai/v1"` + `OpenAIChatCompletionsModel`) sidesteps this entirely and is the SDK-recommended path per [openai.github.io/openai-agents-python/models](https://openai.github.io/openai-agents-python/models/).
- [#130](https://github.com/openai/openai-agents-python/issues/130): dummy-key validation errors against custom `base_url`. We're past this; we pass real keys.
- [#678](https://github.com/openai/openai-agents-python/issues/678): "Unable to use reasoning models with tool calls using LitellmModel." **This is LiteLLM-specific** — we don't use LiteLLM, we use `OpenAIChatCompletionsModel` directly. Not our bug.
- [#686](https://github.com/openai/openai-agents-python/issues/686): "Agent attempts to use non-existing tool." Generic, not Grok-specific.
- **Structured-output malformation warning** on the Models doc: *"your app will often break because of malformed JSON"* when the provider doesn't support structured outputs well. Grok 4 family explicitly supports `json_schema` with `strict: true`, so we're safe — but test before relying.

**No open critical blockers for `OpenAIChatCompletionsModel + xAI base_url`.** The SDK integration is solid; every Grok failure in the benchmark is explainable by the turn-termination rule, not by a bug in the adapter.

---

## 4. P1 — Architecture options

### 4.1 All-Grok variable tool-role split inside one agent

Already partially exists in `grok-combo` profile (reasoning main + non-reasoning worker via `invoke_script_worker`). The benchmark result (2:13, 2/7 prose, 1 shot) shows the combo is fast but still hits the terminal-text bug on Director.

Refinement worth testing **after P0 fix**: inside `minimal_combo` with `grok-4-1-fast-reasoning` as the main (instead of non-reasoning). Reasoning mode plans Director more carefully. Expected: 3:30–4:30 wall, 15+ shots. Cost: higher token spend.

Downside of staying single-agent: the main agent's context stays stuffed with Skeleton/Script work by the time Director phase starts. Switching to a handoff pushes Skeleton+Script context *out* of the Director agent's working memory and lets it focus. That's §4.2.

### 4.2 Two-agent handoff: grok-skeleton-script → grok-director

Per [openai-agents-python handoffs doc](https://openai.github.io/openai-agents-python/handoffs/):

- Handoff is LLM-initiated via a synthetic tool (e.g. `transfer_to_director_agent`) auto-generated by the SDK.
- Second agent sees the full conversation history *by default* (can be filtered with `input_filter`).
- Second agent can have a completely different tool set and model.
- Handoff is one-way per run — no ping-pong.

**Recommended shape for crpg:**

```python
director_agent = Agent(
    name="crpg-director[grok-reasoning]",
    instructions=DIRECTOR_ONLY_INSTRUCTIONS + skill_corpus_director_only,
    model=build_grok_model("grok-4-1-fast-reasoning"),
    model_settings=ModelSettings(tool_choice="required"),
    reset_tool_choice=False,   # keeps 'required' sticky — every turn must call a tool
    tools=[save_shot_prompt, render_anchor, render_image],
)

skeleton_script_agent = Agent(
    name="crpg-skeleton-script[grok-non-reasoning]",
    instructions=SKELETON_SCRIPT_INSTRUCTIONS + skill_corpus_no_director,
    model=build_grok_model("grok-4-1-fast-non-reasoning"),
    tools=[freeform_script_worker],
    handoffs=[director_agent],
)

# Runner.run(skeleton_script_agent, input=brief, ...)
```

**Why this fixes Grok's Director stall:**

- The first agent only needs to get to *one* tool call: `transfer_to_director_agent`. Its prose-section markdown is free text, it happens once, and as long as the last turn emits the handoff tool, the SDK hands off rather than terminating.
- The director agent's `tool_choice="required"` + `reset_tool_choice=False` makes the "pure-text early exit" impossible — every turn is forced to emit at least one tool call (which in Director's case is `save_shot_prompt` or `render_image`, both valid).
- Skill corpus in each agent is narrowed: the Director agent only carries `director/SKILL.md + director/references/*.md` (~35KB) instead of the full 105KB, so the "my task is complete, time to summarise" drift is suppressed because there's nothing for Director to summarise except its own next tool call.

**Expected:** wall 3:30–4:30 (handoff adds ~15s overhead for context replay), shots 15+, prose 6/6–7/8 window.

**Risk:** the handoff tool itself must be triggered by the first agent. Grok typically obeys `handoffs=[...]` because the SDK presents it as a regular tool. But if Grok decides to keep prose-working instead of handing off, you're back to §4.1.

**Mitigation:** add `transfer_to_director_agent` description that reads *"MANDATORY once all beat-prose `freeform_script_worker` calls have returned OK."* Plus: set `tool_use_behavior=StopAtTools(["transfer_to_director_agent"])` on the Skeleton/Script agent — not actually needed because the SDK already special-cases handoff, but it reinforces.

### 4.3 Mixed-provider handoff: grok-skeleton-script + m25-director

Structurally identical to §4.2 but the director agent runs `m25-nitro` via OpenRouter. Cost: one extra API key hop, one extra `AsyncOpenAI` client. Benefit: m25 empirically already completes Director perfectly (17/17 shots, byte-identical Style Preamble per your bench). The ~10:54 m25 wall-time was driven by *m25 also doing Skeleton and Script*. By confining m25 to Director only (where it takes ~4 minutes of that 10:54), total wall should be ≈ **6:30** (Grok Skeleton+Script ~2:30 + handoff overhead ~30s + m25 Director ~3:30).

**This is the least-risky path if P0 + §4.2 still leave Grok Director quality weak.** You keep the Grok speed for the 60% of work that Grok is good at, swap in m25 for the 40% that needs Style Preamble byte-lock discipline.

**Risk:** two billing surfaces (xAI + OpenRouter). Both already in `PROFILES` so plumbing is there.

### 4.4 "Emit the whole shot list at once via structured outputs"

Per §3.6. Implementation sketch:

1. Build a second Grok sub-agent `director_planner_agent` with `output_type=ShotList` (Pydantic model matching the schema).
2. Skeleton/Script agent hands off to `director_planner_agent`.
3. `director_planner_agent` has *no tools*. It replies with a single structured JSON blob → the SDK's `output_schema.validate_json` catches it → returns as `final_output`.
4. Your runner code receives the ShotList, iterates over it, calls `render_image` for each shot itself (no agent involved in this step, just Python).

**This is orthogonal to §4.2/§4.3.** You can combine: handoff to a structured-output planner, then have *your runner code* call `render_image` afterwards.

**Wall-time expectation:** planner 1:00 (one reasoning turn, generating 17 shots), renders 17 × 8s parallel = ~2:00 (you'd parallelise with `asyncio.gather`). Total ≈ 3:00–4:00.

**Risk:** loses the per-shot iterative feedback that `validate_vgai` gives you (in modes where it runs). If you're already skipping VGAI in `minimal_combo`, you're not losing anything. If Style Preamble byte-lock is a hard correctness requirement, enforce it in Python *after* parsing the JSON — truncate any shot whose `final_prompt` doesn't begin with the canonical 735-char preamble.

### 4.5 Intra-Grok role split without handoff (just different tools in same agent)

Already what `grok-combo` does for prose. You could extend: the "save_shot_prompt" tool could internally route to `grok-4-1-fast-reasoning` to generate the Direction Layer, then echo back to the main agent. This is what `invoke_script_worker` does for prose.

**Verdict:** strictly worse than handoff. Adds latency (sub-agent call per shot) with no gain over §4.2.

---

## 5. P2 — Community / industry experience

### 5.1 superagent-ai/grok-cli

Public GitHub project, TypeScript (Bun), ~1.5k stars. Long-horizon tool loop support via `--max-tool-rounds N` flag. Does *not* publish its loop internals on the README or AGENTS.md in readable form — would require source code dive. Key fact gleaned from [superagent.sh/open-source/grok-cli](https://www.superagent.sh/open-source/grok-cli): supports sub-agents by default; "step_start, text, tool_use, step_finish, error events" as semantic events. This suggests their loop is *not* terminating on text events, which is consistent with them having implemented their own terminal rule rather than relying on the OpenAI Agents SDK shape.

**Takeaway:** Grok *can* do long-horizon tool loops in production; the `openai-agents-python` terminal rule is the specific incompatibility, not Grok itself.

### 5.2 LangGraph + Grok

[Docs by LangChain](https://docs.langchain.com/oss/python/integrations/providers/xai) confirm Grok integration. LangGraph uses an explicit `StateGraph` with nodes, so there is no "terminal on text-only turn" default — you write the transition function yourself. This is architecturally *more permissive* than `openai-agents-python` for our use case.

**But:** migration cost is high. You'd rewrite `main_agent.py`, `runner.py`, all tool decorators (`@function_tool` → LangChain `@tool`), and the entire state-passing mechanism. Roughly 2–3 days of work. Do not pay this cost until you've run §4.2 and §4.3 first.

### 5.3 Vercel AI SDK + Grok

[ai-sdk.dev/docs/agents/loop-control](https://ai-sdk.dev/docs/agents/loop-control) shows a `stopWhen` parameter — the opposite of `openai-agents-python`'s implicit terminal rule. You define stop conditions explicitly. Same migration cost calculation as LangGraph.

### 5.4 Adult content viability

Per [TechCrunch 2025-08-04](https://techcrunch.com/2025/08/04/grok-imagine-xais-new-ai-image-and-video-generator-lets-you-make-nsfw-content/) and your existing research notes: xAI's AUP is the most permissive of the major providers. Grok 4.1 Fast for *text* orchestration (ingesting skill-text that references mature noir themes) has no documented content refusal pattern. The moderation you'll encounter is on the *image generation* side (Grok Imagine moderation-sweep pass) — that's already live in your pipeline and not the subject here.

### 5.5 System prompt length, community consensus

Aggregated view:

- [datastudios.org grok prompt engineering guide](https://www.datastudios.org/post/grok-prompt-engineering-full-guide-on-practical-prompting-tool-use-control-structured-outputs-an): XML-tag segmentation > Markdown-header segmentation > flat text. Stable prefix for caching.
- [xAI's own guide via promptlayer](https://blog.promptlayer.com/xais-prompt-engineering-guide-for-grok-code-fast-1/): Grok is an iterative-refinement model; "fire off a quick attempt and refine" philosophy. No stated upper bound on prompt length.
- Our 105KB skill corpus is well within norms for Grok 4.1 Fast at 2M context.

**One practical lever worth applying:** our current skill-corpus delimiter is `===== SKILL: <name> =====` (5 equals signs, no XML). Grok would marginally benefit from `<skill name="script">...</skill>` shape. This is a nice-to-have, not a root-cause fix.

---

## 6. P3 — Escape hatches

### 6.1 Official xAI Python SDK (`xai-sdk-python`)

[github.com/xai-org/xai-sdk-python](https://github.com/xai-org/xai-sdk-python): no built-in agent loop, just `chat.append()` + `chat.sample()`. Would mean we rewrite the entire agent orchestration. Cost: 3–5 days. Benefit over `openai-agents-python`: we'd control the terminal rule. But we already control the terminal rule via §4.2 with ~5% of the work. **Reject this path.**

### 6.2 Switch orchestration framework

- **LangGraph:** 2–3 days migration. Gain: explicit transition semantics. Loss: `@function_tool` ergonomics, streaming event model, existing state machine.
- **Mastra (TypeScript):** language switch. No.
- **pydantic-ai:** similar class to openai-agents-python; no clear win. [Issue #2799](https://github.com/pydantic/pydantic-ai/issues/2799) shows it has its own `tool_choice` gaps.
- **AG2 (AutoGen):** documented Grok support at [docs.ag2.ai](https://docs.ag2.ai/latest/docs/user-guide/models/grok-and-oai-compatible-models/). Multi-agent orchestration is first-class. Migration cost similar to LangGraph. Reject for same reason — our problem is a config issue, not a framework issue.

### 6.3 Stay on m25

The honest fallback: if all Grok paths fail after §4.2 + §4.3 attempts, run everything on m25. Accept 10:54 wall-time. This is where you are today.

---

## 7. Ranked candidate remediation paths

### Path A — "Close the text-exit holes in minimal_combo" (CHEAPEST, DO FIRST)

**What changes:**
- `src/crpg/agent/tools.py`: add two new tools `save_story_markdown(markdown: str)` and `save_characters_markdown(markdown: str)`. Each persists to the bundle directory (same file mechanism as `freeform_script_worker`) and returns `"OK"`.
- `src/crpg/agent/main_agent.py`: `MINIMAL_COMBO_INSTRUCTIONS` updated — every section that says "output `# Story` as markdown text" becomes "call `save_story_markdown(markdown=...)` with the full section". Add to `MINIMAL_COMBO_TOOLS` tuple.
- Keep `grok-xai` (non-reasoning) profile for speed parity with the 2:47 baseline.

**Expected:**
- wall: 3:00–4:00
- shots: 15–17 (Director fires because there's no pure-text turn available before Director work completes)
- risk: medium — Grok might still close the loop with a "summary" text turn after `save_shot_prompt` is done. Mitigation: require a `finish_bundle(summary)` tool call as the closing step (already exists in the codebase), and add `reset_tool_choice=False` + `tool_choice="required"` for Director turns via a custom `ToolsToFinalOutputFunction`.

**Cost:** 2–3 hours of code. No API cost.

### Path B — "Two-agent handoff, all-Grok" (HIGH VALUE)

**What changes:**
- `src/crpg/agent/main_agent.py`: factor current agent into two `Agent` instances: `skeleton_script_agent` and `director_agent`. Wire `handoffs=[director_agent]` on the first. The director agent gets `tool_choice="required"` + `reset_tool_choice=False` + a `ToolsToFinalOutputFunction` that only returns final when `finish_bundle` is called.
- Skill corpus loader: split `_load_skill_corpus` into `load_skeleton_script_skills()` and `load_director_skill()`. Each agent gets its narrower corpus (~70KB vs ~35KB).
- `src/crpg/agent/runner.py`: no change; `Runner.run(skeleton_script_agent, ...)` automatically flows through handoffs.

**Expected:**
- wall: 3:30–4:30
- shots: 16–17 with Style Preamble discipline matching m25's best runs
- risk: low-medium — Grok has to initiate the handoff; mitigation is explicit "MANDATORY" language in the handoff tool description plus `ToolsToFinalOutputFunction`.

**Cost:** 1–1.5 days. Test matrix: single Grok-reasoning vs Grok-non-reasoning for the Director role.

### Path C — "Mixed-provider handoff: Grok + m25" (SAFETY NET)

**What changes:**
- Same shape as Path B, but `director_agent.model = build_m25_model()` (m25-nitro via OpenRouter).
- Existing `PROFILES["m25-nitro"]` already has the wiring.

**Expected:**
- wall: 6:00–7:00
- shots: 17/17 (m25 already proved this)
- risk: lowest, because m25 Director already works empirically.

**Cost:** 0.5 day on top of Path B.

### Why in this order

Path A is the *cheapest experiment that could confirm the diagnosis*. If Path A takes the 2:47 "0 shots" run to "3:30, 15+ shots" you've confirmed the pure-text-exit was the sole blocker and Grok is correctness-viable. If Path A only partially helps, Path B's narrower agent scope is the next lever. Path C is the fallback that's guaranteed to work but gives up some speed.

Do NOT jump straight to Path C — it leaves Grok's speed-advantage capability unexploited.

---

## 8. Excluded options and why

| Option | Excluded because |
|--------|------------------|
| **LangGraph migration** | Solves no Grok-specific issue. `openai-agents-python` terminal rule is fixable in-place via Paths A/B. 2–3 day cost unjustified. |
| **Switch to `xai-sdk-python`** | No agent loop primitives. Would force us to write our own `Runner`. Strictly higher cost than Path A. |
| **Pure streaming mode** | SDK streaming has open bugs with custom providers + tool_choice ([#980](https://github.com/openai/openai-agents-python/issues/980), [#1846](https://github.com/openai/openai-agents-python/issues/1846)), and we don't need token-level streaming for a batch pipeline. |
| **Fine-tuning Grok on crpg tool schemas** | Not exposed by xAI today; also not the root cause. |
| **Using `tool_choice="required"` globally** | SDK auto-resets to `"auto"` after every tool call (`agent.reset_tool_choice=True` default). Must combine with `reset_tool_choice=False` AND use on a Director-scoped sub-agent only. |
| **Routing Grok via OpenRouter instead of xAI direct** | Adds a hop, changes reasoning parameterisation (`reasoning.enabled` body field), loses ~5% latency. Only worth it if xAI direct is rate-limited. Not the bottleneck. |
| **grok-4.20-multi-agent as the pipeline orchestrator** | [docs.x.ai multi-agent](https://docs.x.ai/developers/model-capabilities/text/multi-agent) explicitly states: *"client-side tools (function calling) and custom tools are not currently supported"* for this model. Cannot run our custom tool surface. Hard no. |
| **Replacing Grok with Claude/Gemini** | Ruled out by project content-policy constraints (adult). |
| **Removing the skill-corpus pre-injection** | 105KB isn't the problem per §3.3. Would harm skill adherence without solving the terminal-text exit. |

---

## 9. Appendix — SDK terminal rule reference for future incidents

If the same "Director doesn't fire" pattern appears with a future model, check this first:

1. Does the last assistant turn before the run exits contain **only text content, no `tool_calls`**? Look at `result.new_items[-N:]` for a `MessageOutputItem` not followed by any `ToolCallItem`.
2. If yes — the SDK's `turn_resolution.py:675-706` terminal rule fired. Fix by either:
   - Making every instruction-sanctioned text-emit also happen via a tool call (Path A).
   - Wrapping the subsequent phase in a separate agent via handoff, and using `ToolsToFinalOutputFunction` to only terminate on an explicit `finish_*` tool (Path B).
3. Do *not* look for "why is the model misbehaving." The model is doing what its training says. The SDK is doing what its terminal rule says. The mismatch is at the interface.

---

## Sources

### Primary (HIGH confidence — verified in source)
- `openai-agents-python` SDK source, `run_internal/turn_resolution.py:670-716` — the terminal rule.
- `openai-agents-python` SDK source, `models/chatcmpl_converter.py:180-198` — confirms the SDK accepts combined text+tool_calls responses.
- `openai-agents-python` SDK source, `models/openai_chatcompletions.py:355-413` — `parallel_tool_calls` pass-through.
- [openai.github.io/openai-agents-python/running_agents](https://openai.github.io/openai-agents-python/running_agents/) — *"final output: text output with the desired type, and there are no tool calls."*
- [openai.github.io/openai-agents-python/agents](https://openai.github.io/openai-agents-python/agents/) — `tool_use_behavior`, `reset_tool_choice` semantics.
- [openai.github.io/openai-agents-python/handoffs](https://openai.github.io/openai-agents-python/handoffs/) — handoff mechanics.
- [openai.github.io/openai-agents-python/models](https://openai.github.io/openai-agents-python/models/) — official non-OpenAI provider integration.
- [docs.x.ai/docs/guides/function-calling](https://docs.x.ai/docs/guides/function-calling) — tool_choice literals, parallel_tool_calls default.
- [docs.x.ai/developers/model-capabilities/text/structured-outputs](https://docs.x.ai/developers/model-capabilities/text/structured-outputs) — json_schema support with tools for Grok 4 family.
- [docs.x.ai/developers/model-capabilities/text/reasoning](https://docs.x.ai/developers/model-capabilities/text/reasoning) — reasoning_effort NOT supported on grok-4-1-fast; model-ID selection IS the reasoning switch.
- [docs.x.ai/developers/model-capabilities/text/multi-agent](https://docs.x.ai/developers/model-capabilities/text/multi-agent) — grok-4.20-multi-agent lacks client-side custom tool support.
- [x.ai/news/grok-4-1-fast](https://x.ai/news/grok-4-1-fast) — long-horizon RL, 2M context, agentic tool-calling claims.

### Secondary (MEDIUM confidence — cross-verified)
- [openai-agents-python#1056](https://github.com/openai/openai-agents-python/issues/1056) — Grok integration question, closed stale.
- [openai-agents-python#980](https://github.com/openai/openai-agents-python/issues/980) — streaming + tool_choice fn-name Pydantic error.
- [openai-agents-python#1846](https://github.com/openai/openai-agents-python/issues/1846) — LiteLLM + streaming + tool_choice failure.
- [openai-agents-python#1279](https://github.com/openai/openai-agents-python/issues/1279) — stop_on_first_tool behaviour when no tool called; closed not-planned.
- [openai-agents-python#2343](https://github.com/openai/openai-agents-python/issues/2343) — streaming latency-after-last-token bug.
- [anomalyco/opencode#20719](https://github.com/anomalyco/opencode/issues/20719) — analogous terminal-rule bug in a different SDK with LiteLLM + Ollama, confirming the class of problem.
- [docs.ag2.ai grok-and-oai-compatible-models](https://docs.ag2.ai/latest/docs/user-guide/models/grok-and-oai-compatible-models/) — AG2's Grok recommendations.
- [openrouter.ai/x-ai/grok-4.1-fast](https://openrouter.ai/x-ai/grok-4.1-fast) — OpenRouter Grok params, 2M context.
- [aimlapi grok-4-1-fast-reasoning](https://docs.aimlapi.com/api-references/text-models-llm/xai/grok-4-1-fast-reasoning) — reasoning vs non-reasoning as separate model IDs.
- [datastudios.org grok prompting guide](https://www.datastudios.org/post/grok-prompt-engineering-full-guide-on-practical-prompting-tool-use-control-structured-outputs-an) — XML tag segmentation, stable prefix cache.
- [datastudios.org grok context window](https://www.datastudios.org/post/grok-context-window-token-limits-memory-policy-and-2025-rules) — max_tokens / truncation behaviour.

### Tertiary (LOW confidence — community / blog)
- [superagent-ai/grok-cli](https://github.com/superagent-ai/grok-cli) — production Grok agent loop exists, loop internals not publicly documented.
- [blog.promptlayer.com xai prompt engineering for grok-code-fast-1](https://blog.promptlayer.com/xais-prompt-engineering-guide-for-grok-code-fast-1/) — general prompt principles for Grok.
- [TechCrunch 2025-08-04 Grok Imagine NSFW](https://techcrunch.com/2025/08/04/grok-imagine-xais-new-ai-image-and-video-generator-lets-you-make-nsfw-content/) — xAI content policy context.
