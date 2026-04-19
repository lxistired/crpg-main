# Orchestrator Model Shortlist — Final (2026-04-19)

> **Audit methodology:** Live OpenRouter speed ranking screenshot (2026-04-19) cross-referenced against:
> - OpenRouter API `/api/v1/models` (live JSON, ~140+ models, fetched 2026-04-19)
> - Groq `/docs/rate-limits` (live model list, fetched 2026-04-19)
> - Groq blog / pricing pages
> - Provider TOS/AUP pages where reachable
> - Per-model OpenRouter detail pages

---

## TL;DR — Top 5 to Actually Test (Ranked)

| # | Model | OpenRouter slug | Direct endpoint | $/1M (in/out) | tok/s | Tool-call reliable? | Adult OK? |
|---|-------|----------------|----------------|--------------|-------|--------------------|-----------| 
| 1 | **Kimi K2.5** | `moonshotai/kimi-k2.5` | none yet (BaseTen via OR) | $0.38/$1.72 | 131 | YES — agentic-swarm design, K2 lineage field-proven in codebase | YES — Moonshot permissive for fiction |
| 2 | **GLM 4.7** | `z-ai/glm-4.7` | `api.z.ai/api/paas/v4` | $0.39/$1.75 (OR) | 428 (Cerebras) | YES — agent-loop optimised, ~0.67% error rate lineage | LIKELY (Z.ai less strict than Alibaba) |
| 3 | **GLM 4.7 Flash** | `z-ai/glm-4.7-flash` | `api.z.ai/api/paas/v4` | $0.06/$0.40 (OR) | ~200+ est. | YES — same Z.ai agentic lineage | LIKELY |
| 4 | **Grok 4 Fast** | `x-ai/grok-4-fast` | `api.x.ai/v1` (model: `grok-4-1-fast`) | $0.20/$0.50 | 172 | YES — xAI 4.20 confirms agentic tool calling | LIKELY YES (xAI/Grok known most permissive) |
| 5 | **Mercury 2** | `inception/mercury-2` | api.inceptionlabs.ai | $0.25/$0.75 | 133 | CLAIMS native tool use — diffusion arch needs empirical verification | UNKNOWN but no explicit prohibition found |

**Confidence note on #4 & #5:** xAI content policy not reachable via public URL (403/404 on their legal pages); Mercury 2 is a diffusion LLM (novel architecture) — OpenAI-format tool_calls response shape needs empirical confirmation. Both are "run spike test first" candidates.

**Strong fallback (not top-5, but proven):** `meta-llama/llama-3.3-70b-instruct` via Groq — most documented tool-call reliability of any Groq-hosted model, 173 tok/s, 131K context, $0.12/$0.38.

---

## Per-Rank Analysis — Top 20 Candidates → Keep/Drop Verdict

### Rank 1 — gpt-oss-20b (`openai/gpt-oss-20b`) | 855 tok/s | $0.07/M | Groq

**Speed:** Fastest on list. Groq rate-limits page confirms live: `openai/gpt-oss-20b` with 30 RPM / 200K TPD.

**Context:** 131,072 tokens. Meets 32K requirement.

**Tool calling:** "Function calling, tool use, structured outputs" confirmed on OpenRouter page. 21B MoE (3.6B active), Apache 2.0 open-weight.

**Adult content — CRITICAL ISSUE:** gpt-oss-20b is open-weight (Apache 2.0) so OpenAI's own API usage policy does NOT apply at Groq. However, the model's RLHF/safety training is baked into the weights and was done by OpenAI — it will refuse or sanitize adult-genre content in prompts. Groq's Terms of Use (website) also prohibit "obscene" material, with the binding Groq Services Agreement governing API usage. The combination of (a) OpenAI safety-aligned weights + (b) Groq "obscene content" prohibition creates **high refusal risk** when the orchestrator ingests skill/prose snippets referencing adult noir themes across 50+ turns.

**Note:** gpt-oss-20b is NOT in the OpenRouter live `/api/v1/models` JSON as of 2026-04-19 despite the OR detail page being accessible. Verify OpenRouter routing before assuming it's available there.

**Verdict: DROP. Adult content refusal risk is the blocker — OpenAI RLHF weights + Groq AUP = double barrier.**

---

### Rank 2 — gpt-oss-safeguard-20b (`openai/gpt-oss-safeguard-20b`) | 727 tok/s | $0.07/M | Groq

**What it is:** A **safety/content moderation classifier**, not a generative model. Built upon gpt-oss-20b for "content classification, LLM filtering, and trust & safety labeling."

**Verdict: DROP immediately. This is a moderation model, not an orchestrator.**

---

### Rank 3 — gpt-oss-120b (`openai/gpt-oss-120b`) | 676 tok/s | $0.35/M | Cerebras

**Context:** 131K. **Tool calling:** "Native tool use, function calling, browsing, structured outputs" confirmed. Groq rate-limits page also lists it as live (routes to both Groq and Cerebras).

**Adult content:** Same analysis as Rank 1, compounded — a larger, more thoroughly safety-aligned OpenAI model. Even higher refusal probability.

**Verdict: DROP. Same adult content risk as Rank 1.**

---

### Rank 4 — GLM 4.7 (`z-ai/glm-4.7`) | 428 tok/s | $2.25/M (via OR/Cerebras) | Cerebras

**Speed:** 428 tok/s on Cerebras via OpenRouter. The $2.25/M shown in the screenshot is the blended OR-routed Cerebras price. Direct Z.ai API: $0.39/$1.75.

**Context:** 202,752 tokens.

**Tool calling:** Z.ai describes "enhanced programming capabilities and more stable multi-step reasoning/execution" and "tool collaboration." Same agent-loop lineage as GLM-5-Turbo from prior research (which had ~0.67% tool-call error rate in third-party tests). OpenRouter live JSON confirms `z-ai/glm-4.7` is available.

**GLM 4.7 vs GLM-5-Turbo:** Both are available on OpenRouter simultaneously. GLM-5-Turbo ($1.20/$4.00) was the prior research's PRIMARY pick for agent orchestration. GLM 4.7 (released Dec 22, 2025) is newer, cheaper, and has identical architectural strengths. GLM 4.7 Flash is even cheaper ($0.06/$0.40) — a sub-variant optimised for agentic coding workloads at 202K context.

**Adult content:** Z.ai (Zhipu AI) — Chinese company. API-level restrictions are governed by their Services Agreement, not the website ToU. GLM series has extensive open-source adult fiction use (uncensored GGUF variants widely distributed). The orchestrator use case (ingesting skill text, not generating adult prose) is lowest-risk. Cerebras's own ToS prohibits "obscene, pornographic" material, but this applies when routing via Cerebras direct — via OpenRouter, it's Z.ai's API policy that governs. **Rated: LIKELY OK, validate with spike.**

**Verdict: KEEP — Rank 2 in final shortlist.**

---

### Rank 5 — Qwen3 32B (`qwen/qwen3-32b`) | 310 tok/s | $0.29/M | Groq

**Context:** 32K native / 131K via YaRN. YaRN-extended coherence degrades at context edges — risky for 50+ turn loops near the 131K limit.

**Tool calling:** OpenRouter says "strong agent tool use" but the Qwen family has documented multi-turn tool-calling reliability issues (model outputs raw text instead of tool invocations after initial turns).

**Adult content:** Alibaba Cloud AUP explicitly prohibits adult content regardless of hosting provider. **Hard blocker.**

**Verdict: DROP. Alibaba AUP + Qwen multi-turn reliability risk.**

---

### Rank 6 — Llama 3.1 8B Instruct (`meta-llama/llama-3.1-8b-instruct`) | 232 tok/s | $0.05/M | Groq

**Context:** 16,384 tokens only. **FAILS 32K minimum requirement.**

**Verdict: DROP. Context window too small.**

---

### Rank 7 — Kimi K2 0905 (`moonshotai/kimi-k2-0905`) | 201 tok/s (STALE) | $1.00/M | "Groq" (STALE)

**Status: SEE DEDICATED KIMI SECTION BELOW.** Short verdict: NOT LIVE on Groq as of 2026-04-19. The screenshot data is stale. Superseded by Kimi K2.5.

**Verdict: SUPERSEDED BY KIMI K2.5.**

---

### Rank 8 — Llama 4 Scout (`meta-llama/llama-4-scout`) | 177 tok/s | $0.11/M | Groq

**Context:** 327,680 tokens via OpenRouter. Groq rate-limits page confirms `meta-llama/llama-4-scout-17b-16e-instruct` is live.

**Tool calling:** Not confirmed in research. 17B MoE model (Scout architecture).

**Adult content:** Open-weight; Meta's policy doesn't apply on Groq. Groq AUP applies. Llama 4 Scout's safety training is less restrictive than Llama 3.3 per Meta's own statements.

**Verdict: CONDITIONAL FALLBACK. Faster than Kimi K2.5 on Groq and cheaper ($0.11/M). Add to spike harness if budget is the primary driver after top-5 are tested. Tool-call reliability on 5-8 param schemas is the unknown.**

---

### Rank 9 — Llama 3.3 70B Instruct (`meta-llama/llama-3.3-70b-instruct`) | 173 tok/s | $0.59/M | Groq

**Context:** 131,072 tokens.

**Tool calling:** Gold standard among Groq-hosted open-weight models for function calling reliability. Widely benchmarked and used in production agent loops. Best documented tool-call reliability of any model in this list after Kimi K2 family.

**Adult content:** Open-weight on Groq. Groq AUP applies. Community reports indicate Llama 3.3 on Groq does pass adult-genre creative context without automatic refusal in most cases.

**Verdict: STRONG FALLBACK. Include in spike harness. Not in top-5 only because Kimi K2.5 is faster at similar quality and GLM 4.7 is faster via Cerebras.**

---

### Rank 10 — Grok 4 Fast (`x-ai/grok-4-fast`) | 172 tok/s | $0.20/M | xAI

**Context:** 2,000,000 tokens — massively exceeds requirement.

**Tool calling:** xAI's grok-4.20 page explicitly confirms "industry-leading speed and agentic tool calling capabilities." Grok 4 Fast (`grok-4-1-fast` in xAI direct API) is the non-reasoning tier of the same model family.

**Adult content:** xAI/Grok is the most permissive of major Western AI providers for adult-themed content. The Grok chat app has explicit adult content modes. The API's usage policy page returned 403/404 from our fetch attempts but xAI's public reputation and the project's existing `XAI_API_KEY` for image generation both suggest permissive treatment of adult creative fiction.

**Single-vendor risk:** The project already uses xAI for image generation. Using xAI for orchestration too means a single xAI outage takes down both text orchestration AND image rendering. This is worth noting but not a disqualifier.

**OpenAI SDK compat:** Yes — `api.x.ai/v1` is OpenAI-compatible.

**Verdict: KEEP — Rank 4 in final shortlist.**

---

### Rank 11 — Nemotron 3 Nano 30B A3B (`nvidia/nemotron-3-nano-30b-a3b`) | 170 tok/s | ~no listed price on screenshot | Nvidia

**Context:** 262,144 tokens. **Pricing (OpenRouter):** $0.05/$0.20 per 1M — cheapest on the list.

**Tool calling:** Not confirmed. Nvidia Nemotron models are RLHF-refined Llama derivatives optimized for enterprise tasks.

**Adult content:** Nvidia's inference API has standard enterprise AUP that prohibits adult content. Likely blocked.

**Verdict: DROP. Nvidia AUP likely blocks adult content; tool-call reliability unverified.**

---

### Rank 12 — Gemini 2.5 Flash Lite (`google/gemini-2.5-flash-lite`) | 167 tok/s | $0.10/M | Google

**Context:** 1,048,576 tokens.

**Tool calling:** Gemini has excellent, well-documented native function calling.

**Adult content:** Google's API **HARD BLOCKS** adult content. Google API usage policy explicitly prohibits adult content generation and passing adult-themed content through. This is a firm, non-negotiable blocker for this project.

**Verdict: DROP. Google AUP — hard blocker, full stop.**

---

### Rank 13 — "Nano Banana" (Gemini 2.5 variant) | 165 tok/s | $0.30/M | Google

Same Google AUP hard blocker as Rank 12.

**Verdict: DROP.**

---

### Rank 14 — Devstral Small 1.1 (`mistralai/devstral-small-1.1`) | 137 tok/s | $0.10/M | Mistral

**Availability:** The slug `mistralai/devstral-small-1.1` returns "not available" on OpenRouter's model page as of 2026-04-19. The live OpenRouter model JSON shows `mistralai/devstral-2512` (Devstral December 2025 build) as the available Devstral variant.

**Purpose:** Devstral is Mistral's **code agent** model — optimized for software engineering tasks. Not designed for creative fiction orchestration with story beat / prose / shot schemas.

**Verdict: DROP. Wrong model class; slug may not be available.**

---

### Rank 15 — Qwen3.5-35B-A3B (`qwen/qwen3.5-35b-a3b`) | 134 tok/s | $0.23/M | AkashML

**Context:** 262,144 tokens.

**Tool calling:** Not confirmed. Qwen family multi-turn tool-call reliability issues apply.

**Adult content:** Qwen / Alibaba AUP prohibits adult content regardless of hosting provider. AkashML is a decentralized compute marketplace; their TOS focuses on illegal conduct, not adult content specifically — but Alibaba's license on the model weights applies.

**Verdict: DROP. Alibaba AUP + Qwen tool-call reliability risk.**

---

### Rank 16 — MiniMax M2.5 (`minimax/minimax-m2.5`) | 134 tok/s | $0.30/M | Mara

**Context:** 196,608 tokens.

**Reasoning model:** YES — OpenRouter confirms the `reasoning` parameter is supported and `reasoning_details` is available in responses. This is a **thinking model** — same root cause as MiniMax M2.7 HighSpeed causing 26-minute runs. M2.5 is the predecessor to M2.7 with the same architecture. There is no non-thinking mode.

**Tool calling:** Not confirmed. Mara content policy not retrievable (page returned empty content).

**Verdict: DROP. Reasoning/thinking model — same latency pathology as the original problem.**

---

### Rank 17 — Mercury 2 (`inception/mercury-2`) | 133 tok/s | $0.25/M | Inception

**Context:** 128,000 tokens. Passes 32K minimum.

**Architecture:** First reasoning **diffusion LLM** — generates and refines tokens in parallel. Inception claims >1,000 tok/s on standard GPUs; 133 tok/s in screenshot reflects OpenRouter overhead. Promising raw speed.

**Tool calling:** OpenRouter page confirms "native tool use" and "schema-aligned JSON output." However, since Mercury 2 is a diffusion model (not autoregressive), the implementation of function calling may differ at the API level. The critical question: does the response contain a standard `choices[0].message.tool_calls` array as the OpenAI SDK expects, or does Inception use a custom format? OpenRouter says "OpenAI API compatible" which should normalize this — but must verify empirically before trusting for 50+ turn loops.

**Adult content:** Inception Labs TOS page returned 404. No documented content policy found. Small startup — historically lower enforcement risk than enterprise Chinese or Google providers.

**Verdict: KEEP as Rank 5. Interesting speed/cost profile, native tool use claimed. Diffusion architecture is the one empirical unknown.**

---

### Rank 18 — Kimi K2.5 (`moonshotai/kimi-k2.5`) | 131 tok/s | $0.38/$1.72/M | BaseTen

**Context:** 262,144 tokens.

**Tool calling:** Moonshot positions K2.5 for "agentic tool-calling" and "self-directed agent swarm paradigm." K2 0905 was field-proven in this codebase at 3/3 clean JSON with 3.5s latency (per prior research). K2.5 is the direct successor with documented improvements. Strongest prior-evidence basis of any candidate.

**Adult content:** Moonshot AI has no documented adult content block at API level for fiction. Same analysis as prior K2 0905 research.

**OpenRouter slug confirmed:** `moonshotai/kimi-k2.5` (internal slug `moonshotai/kimi-k2.5-0127`). Live in OpenRouter `/api/v1/models` JSON as of 2026-04-19.

**Providers:** BaseTen at 131 tok/s per screenshot. Groq is NOT hosting K2.5 yet (not in Groq rate-limits list).

**Verdict: KEEP — Rank 1 in final shortlist. Best combination: proven tool-call lineage, permissive adult content, 262K context, available now.**

---

### Rank 19 — Nemotron Nano 12B 2 VL (`deepinfra/nemotron-nano-12b-2-vl`) | 129 tok/s | $0.20/M | DeepInfra

**Context:** Not confirmed. 12B with VL (vision-language) suffix.

**Tool calling:** Not confirmed. 12B models are generally insufficient for complex 5-8 param schemas in long loops.

**Adult content:** DeepInfra's ToS (successfully retrieved) does NOT explicitly prohibit adult creative fiction. Their prohibited conduct focuses on security breaches, malware, fraud, illegal activities — notably absent is adult content prohibition. One of the more permissive enterprise providers.

**OpenRouter availability:** Slug `deepinfra/nemotron-nano-12b-2-vl` returns "not available" on OpenRouter as of 2026-04-19.

**Verdict: DROP. 12B too small for complex schemas; not available on OpenRouter; VL capability not needed for text orchestration.**

---

### Rank 20 — Mistral Small 3.2 24B (`mistralai/mistral-small-3.2-24b-instruct`) | 122 tok/s | $0.10/M | Mistral

**Context:** 128,000 tokens.

**Tool calling:** OpenRouter confirms "improved function calling" — Mistral Small 3.2 was specifically trained for better tool use.

**Adult content:** Mistral's AUP pages were not fully retrievable (404s on multiple attempts). The `mistralai/mistral-small-creative` model (now discontinued April 30, 2026) was explicitly designed for "creative writing, narrative generation, roleplay and character-driven dialogue" — indicating Mistral's stance is permissive for creative use. Community reports consistent with this.

**Availability note:** The live OpenRouter model JSON does NOT list `mistralai/mistral-small-3.2-24b-instruct`. Instead it shows `mistralai/mistral-small-2603` — this is **Mistral Small 4** (March 2026), which has 262K context at $0.15/$0.60. Mistral Small 3.2 has been superseded.

**Updated recommendation:** Use `mistralai/mistral-small-2603` (Mistral Small 4) as the budget fallback if needed — 262K context, better than 3.2's 128K, confirmed in live model catalog.

**Verdict: CONDITIONAL FALLBACK (use mistral-small-2603 slug instead). After top-5 are tested, this is the cheapest western-provider option with likely adult-permissive policy.**

---

## Kimi K2 0905 on Groq — Live Status (2026-04-19)

**Question posed:** The OpenRouter speed ranking screenshot (captured 2026-04-19) shows "Kimi K2 0905 fastest on Groq at 201 tok/s." The prior research claimed Groq deprecated kimi-k2-0905 ~April 15, 2026. Which is correct?

### Evidence gathered (all fetched 2026-04-19)

**Source 1 — Groq rate-limits page (live):**
Lists 16 models with explicit rate limits. `moonshotai/kimi-k2-instruct-0905` (or any kimi variant) is **absent**. Models confirmed live on Groq include: `openai/gpt-oss-20b`, `openai/gpt-oss-120b`, `qwen/qwen3-32b`, `meta-llama/llama-4-scout-17b-16e-instruct`, `llama-3.1-8b-instant`, `llama-3.3-70b-versatile`.

**Source 2 — Groq pricing page (live):**
kimi-k2-instruct-0905 appears only in the **prompt caching section** (as a legacy pricing reference row), NOT in the main LLM pricing table. This is the documentation pattern Groq uses for deprecated models — pricing entry remains as reference but the model is no longer actively served.

**Source 3 — OpenRouter live `/api/v1/models` JSON (~140+ models):**
`kimi-k2-0905` is **absent**. The only Kimi model in the current catalog is `moonshotai/kimi-k2.5`. There is no `moonshotai/kimi-k2-0905` or `moonshotai/kimi-k2-instruct-0905` in the live response.

**Source 4 — OpenRouter model page for kimi-k2-0905:**
The page `openrouter.ai/moonshotai/kimi-k2-0905` **exists** and shows $0.40/$2.00 pricing and 256K context — but the providers section (dynamic/interactive) does not list Groq in the fetched content. Other providers at lower speed may still route to it.

**Source 5 — Groq blog:**
Has an intro post for kimi-k2-0905 from September 2025, no deprecation announcement visible in the April 2026 blog listing. However, Groq does not always blog deprecations — they just remove models from the rate-limits page.

### Conclusion

**kimi-k2-0905 is NOT currently served on Groq as of 2026-04-19.** The prior research's deprecation claim (~April 15, 2026) is **confirmed as essentially correct.**

The OpenRouter speed ranking screenshot's "fastest on Groq at 201 tok/s" label is **stale speed data** — OpenRouter's speed ranking caches measurements from when models were last benchmarked and does not always update immediately when a provider drops a model. The live model catalog and Groq's rate-limits page are authoritative; both confirm K2 0905 is gone from Groq.

**What exists instead:**
- `moonshotai/kimi-k2.5` is the live Kimi successor on OpenRouter (BaseTen provider, 131 tok/s, 262K context, $0.38/$1.72)
- Groq has NOT added kimi-k2.5 yet (not in rate-limits list as of 2026-04-19)
- If kimi-k2-0905 is still accessible via OpenRouter it routes to non-Groq providers at ~16-20 tok/s (much slower)

---

## Concrete Test Harness

Python snippet that tests all 5 candidates against a realistic crpg-style tool schema with 6 parameters (including a nested dict), across a multi-beat orchestration sequence.

```python
"""
research/orchestrator-model-2026-04-19/spike_tool_test.py

Orchestrator tool-call smoke test for crpg candidates.
Tests: multi-turn tool calling with 6-param schema, tool result handling, finish signal.

Usage:
  MODEL_SLUG=moonshotai/kimi-k2.5 \
  BASE_URL=https://openrouter.ai/api/v1 \
  API_KEY=$OPENROUTER_API_KEY \
    .venv/bin/python research/orchestrator-model-2026-04-19/spike_tool_test.py
"""
import asyncio, os, json, time
from openai import AsyncOpenAI

MODEL    = os.environ.get("MODEL_SLUG", "moonshotai/kimi-k2.5")
BASE_URL = os.environ.get("BASE_URL",   "https://openrouter.ai/api/v1")
API_KEY  = os.environ.get("API_KEY",    os.environ["OPENROUTER_API_KEY"])

# Realistic crpg schema: 6 params, one nested dict — matches actual tool complexity
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "write_beat_prose",
            "description": "Invoke a script worker to write prose for a beat",
            "parameters": {
                "type": "object",
                "properties": {
                    "beat_id":           {"type": "string", "description": "Beat identifier, e.g. 'b1'"},
                    "beat_type":         {"type": "string", "enum": ["action", "dialogue", "reflection", "climax"]},
                    "target_word_count": {"type": "integer", "description": "Target CJK character count"},
                    "poetic_mode":       {"type": "boolean", "description": "Enable poetic prose style"},
                    "synopsis":          {"type": "string", "description": "Beat synopsis and mandated quotes"},
                    "prior_context":     {"type": "string", "description": "Prose from previous beat for continuity"},
                },
                "required": ["beat_id", "beat_type", "target_word_count", "poetic_mode", "synopsis"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_beat_shots",
            "description": "Invoke a director worker to design shot list for a beat",
            "parameters": {
                "type": "object",
                "properties": {
                    "beat_id":           {"type": "string"},
                    "prose_summary":     {"type": "string"},
                    "character_anchors": {
                        "type": "object",
                        "description": "Map of character name to anchor image URL",
                        "additionalProperties": {"type": "string"}
                    },
                    "num_shots": {"type": "integer", "minimum": 3, "maximum": 8},
                },
                "required": ["beat_id", "prose_summary", "num_shots"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "finish_bundle",
            "description": "Mark bundle complete and return summary",
            "parameters": {
                "type": "object",
                "properties": {
                    "beats_completed": {"type": "array", "items": {"type": "string"}},
                    "notes":           {"type": "string"}
                },
                "required": ["beats_completed"]
            }
        }
    }
]

SYSTEM = (
    "You are a story bundle orchestrator. You ONLY call tools — never write prose directly. "
    "Your job: for each beat, first call write_beat_prose, then write_beat_shots. "
    "After all beats are done, call finish_bundle. Always use tool calls, never plain text."
)

MSGS = [
    {
        "role": "user",
        "content": (
            "Orchestrate a 2-beat bundle. "
            "Beat b1: action type, 2500 words, poetic_mode=true, synopsis='Su Wan finds the burner phone.' "
            "Beat b2: dialogue type, 1800 words, poetic_mode=false, synopsis='Kai arrives at the apartment.' "
            "Do b1 prose, b1 shots, b2 prose, b2 shots, then finish_bundle. Start now."
        )
    }
]

EXPECTED_SEQUENCE = [
    "write_beat_prose",   # b1
    "write_beat_shots",   # b1
    "write_beat_prose",   # b2
    "write_beat_shots",   # b2
    "finish_bundle",
]

async def main():
    client  = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
    seq_idx = 0
    errors  = []

    print(f"\n=== Smoke test: {MODEL} ===")
    print(f"Base URL: {BASE_URL}\n")

    for turn in range(12):
        t0   = time.time()
        resp = await client.chat.completions.create(
            model=MODEL,
            messages=MSGS,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.0,
        )
        elapsed = time.time() - t0
        msg = resp.choices[0].message
        MSGS.append(msg)

        if not msg.tool_calls:
            errors.append(f"turn {turn}: NO TOOL CALL — got prose: {(msg.content or '')[:120]!r}")
            print(f"  FAIL turn {turn} ({elapsed:.1f}s): no tool call")
            break

        for tc in msg.tool_calls:
            fname = tc.function.name
            try:
                args = json.loads(tc.function.arguments)
            except json.JSONDecodeError as e:
                errors.append(f"turn {turn}: INVALID JSON args for {fname}: {e}")
                args = {}

            expected = EXPECTED_SEQUENCE[seq_idx] if seq_idx < len(EXPECTED_SEQUENCE) else "?"
            status   = "OK" if fname == expected else f"UNEXPECTED (wanted {expected})"
            print(f"  turn {turn} ({elapsed:.1f}s): {fname}({list(args.keys())}) — {status}")

            if fname != expected:
                errors.append(f"turn {turn}: called {fname} but expected {expected}")

            seq_idx += 1

            # Simulate tool result
            if fname == "write_beat_prose":
                result = json.dumps({"status": "ok", "beat_id": args.get("beat_id", "?"),
                                     "word_count": args.get("target_word_count", 0),
                                     "prose_preview": "故事开始..."})
            elif fname == "write_beat_shots":
                result = json.dumps({"status": "ok", "beat_id": args.get("beat_id", "?"),
                                     "shots_written": args.get("num_shots", 4)})
            elif fname == "finish_bundle":
                result = json.dumps({"status": "complete",
                                     "beats": args.get("beats_completed", [])})
            else:
                result = json.dumps({"status": "unknown_tool"})

            MSGS.append({"role": "tool", "tool_call_id": tc.id, "content": result})

        if any(tc.function.name == "finish_bundle" for tc in msg.tool_calls):
            break

    print(f"\n--- Results: {MODEL} ---")
    if not errors:
        print(f"  PASS: all {seq_idx} tool calls in correct sequence")
    else:
        print(f"  FAIL: {len(errors)} error(s):")
        for e in errors:
            print(f"    - {e}")

asyncio.run(main())
```

### Run commands — all 5 candidates

```bash
cd /Users/lxxxxxx/个人项目/crpg

# 1. Kimi K2.5 — PRIMARY (proven K2 lineage, agentic design)
MODEL_SLUG=moonshotai/kimi-k2.5 \
BASE_URL=https://openrouter.ai/api/v1 \
API_KEY=$OPENROUTER_API_KEY \
  .venv/bin/python research/orchestrator-model-2026-04-19/spike_tool_test.py

# 2. GLM 4.7 — SECONDARY (Cerebras 428 tok/s, agent-loop lineage, cheap direct)
MODEL_SLUG=z-ai/glm-4.7 \
BASE_URL=https://openrouter.ai/api/v1 \
API_KEY=$OPENROUTER_API_KEY \
  .venv/bin/python research/orchestrator-model-2026-04-19/spike_tool_test.py

# 3. GLM 4.7 Flash — BUDGET VARIANT ($0.06/$0.40, same lineage)
MODEL_SLUG=z-ai/glm-4.7-flash \
BASE_URL=https://openrouter.ai/api/v1 \
API_KEY=$OPENROUTER_API_KEY \
  .venv/bin/python research/orchestrator-model-2026-04-19/spike_tool_test.py

# 4. Grok 4 Fast — PERMISSIVE (xAI, existing vendor, 2M context)
MODEL_SLUG=x-ai/grok-4-fast \
BASE_URL=https://openrouter.ai/api/v1 \
API_KEY=$OPENROUTER_API_KEY \
  .venv/bin/python research/orchestrator-model-2026-04-19/spike_tool_test.py
# OR via xAI direct (same key already in .env):
# MODEL_SLUG=grok-4-1-fast BASE_URL=https://api.x.ai/v1 API_KEY=$XAI_API_KEY ...

# 5. Mercury 2 — DARK HORSE (diffusion LLM, verify tool_calls format)
MODEL_SLUG=inception/mercury-2 \
BASE_URL=https://openrouter.ai/api/v1 \
API_KEY=$OPENROUTER_API_KEY \
  .venv/bin/python research/orchestrator-model-2026-04-19/spike_tool_test.py

# Fallback: Llama 3.3 70B (most proven tool-call reliability on Groq)
MODEL_SLUG=meta-llama/llama-3.3-70b-instruct \
BASE_URL=https://openrouter.ai/api/v1 \
API_KEY=$OPENROUTER_API_KEY \
  .venv/bin/python research/orchestrator-model-2026-04-19/spike_tool_test.py
```

### Integrate winner into main_agent.py

```python
# Before (MiniMax — 60-180s thinking overhead, architectural)
client = AsyncOpenAI(base_url="https://api.minimaxi.com/v1", api_key=MINIMAX_API_KEY)
model  = "MiniMax-M2.7-HighSpeed"

# After spike test — swap to winning model:

# Option A: Kimi K2.5 via OpenRouter
client = AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)
model  = "moonshotai/kimi-k2.5"

# Option B: GLM 4.7 via OpenRouter (428 tok/s on Cerebras)
client = AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)
model  = "z-ai/glm-4.7"

# Option B-cheap: GLM 4.7 Flash direct via Z.ai ($0.06/$0.40)
client = AsyncOpenAI(base_url="https://api.z.ai/api/paas/v4", api_key=ZAI_API_KEY)
model  = "glm-4.7-flash"   # confirm exact ID: GET api.z.ai/api/paas/v4/models

# Option C: Grok 4 Fast direct (single-vendor with image gen, but most permissive)
client = AsyncOpenAI(base_url="https://api.x.ai/v1", api_key=XAI_API_KEY)
model  = "grok-4-1-fast"
```

---

## Appendix: URLs, Dates, Evidence

| Source | URL | Date | Key finding |
|--------|-----|------|-------------|
| Groq rate-limits (live) | https://console.groq.com/docs/rate-limits | 2026-04-19 | 16 models listed; kimi-k2-0905 ABSENT; gpt-oss-20b, gpt-oss-120b, qwen3-32b confirmed live |
| Groq pricing page | https://groq.com/pricing/ | 2026-04-19 | kimi-k2-instruct-0905 in caching section only (legacy reference), not main LLM table |
| Groq blog | https://groq.com/blog/ | 2026-04-19 | Kimi K2 0905 intro post (Sep 2025) exists; no deprecation post in Apr 2026 listings |
| OpenRouter /api/v1/models | https://openrouter.ai/api/v1/models | 2026-04-19 | ~140 models; kimi-k2-0905 ABSENT; kimi-k2.5 present; z-ai/glm-4.7, z-ai/glm-4.7-flash, z-ai/glm-5-turbo, z-ai/glm-5.1 all present; inception/mercury-2 present |
| OR: kimi-k2-0905 page | https://openrouter.ai/moonshotai/kimi-k2-0905 | 2026-04-19 | Page exists, $0.40/$2.00; Groq NOT listed as provider in fetched content |
| OR: kimi-k2.5 | https://openrouter.ai/moonshotai/kimi-k2.5 | 2026-04-19 | Live, 262K context, $0.38/$1.72, BaseTen at 131 tok/s |
| OR: GLM 4.7 | https://openrouter.ai/z-ai/glm-4.7 | 2026-04-19 | Live, 202K context, $0.39/$1.75 |
| OR: GLM 4.7 Flash | https://openrouter.ai/z-ai/glm-4.7-flash | 2026-04-19 | Live, 202K context, $0.06/$0.40, agentic coding optimised |
| OR: GLM 5 Turbo | https://openrouter.ai/z-ai/glm-5-turbo | 2026-04-19 | Live, 202K context, $1.20/$4.00, agent-loop "deeply optimized" |
| OR: gpt-oss-20b | https://openrouter.ai/openai/gpt-oss-20b | 2026-04-19 | Open-weight Apache 2.0, 21B MoE, 131K context, OpenAI safety RLHF baked in |
| OR: gpt-oss-safeguard-20b | https://openrouter.ai/openai/gpt-oss-safeguard-20b | 2026-04-19 | Safety classifier model, not generative — wrong model class |
| OR: gpt-oss-120b | https://openrouter.ai/openai/gpt-oss-120b | 2026-04-19 | 131K context, $0.039/$0.19, native tool use confirmed |
| OR: Grok 4 Fast | https://openrouter.ai/x-ai/grok-4-fast | 2026-04-19 | Live, 2M context, $0.20/$0.50 |
| xAI docs models | https://docs.x.ai/docs/models | 2026-04-19 | grok-4-1-fast (non-reasoning) confirmed at $0.20/$0.50, 2M context, function calling |
| OR: Grok 4.20 | https://openrouter.ai/x-ai/grok-4.20 | 2026-04-19 | "Agentic tool calling capabilities" confirmed; grok-4-fast is fast/non-reasoning tier |
| OR: Mercury 2 | https://openrouter.ai/inception/mercury-2 | 2026-04-19 | Live, 128K context, $0.25/$0.75, "native tool use," diffusion LLM |
| Inception Labs announcement | https://www.inceptionlabs.ai/introducing-mercury | 2026-04-19 | Diffusion LLM, "drop-in replacement for autoregressive LLM, supporting tool use and agentic workflows" |
| OR: MiniMax M2.5 | https://openrouter.ai/minimax/minimax-m2.5 | 2026-04-19 | Reasoning model (thinking param confirmed) — same latency pathology as M2.7 |
| DeepInfra ToS | https://deepinfra.com/terms | 2026-04-19 | Does NOT explicitly prohibit adult creative fiction — only illegal/malicious content |
| Cerebras ToS | https://cerebras.ai/terms-of-service/ | 2026-04-19 | Prohibits "obscene, pornographic" material — adult fiction likely blocked on Cerebras direct API |
| OR: Qwen3 32B | https://openrouter.ai/qwen/qwen3-32b | 2026-04-19 | 131K context, $0.08/$0.24; Alibaba AUP blocks adult content |
| OR: Mistral Small 3.2 24B | https://openrouter.ai/mistralai/mistral-small-3.2-24b-instruct | 2026-04-19 | 128K context; superseded by mistral-small-2603 (Mistral Small 4, 262K, $0.15/$0.60) |
| OR: Mistral Small Creative | https://openrouter.ai/mistralai/mistral-small-creative | 2026-04-19 | Designed for "roleplay and character-driven dialogue" — confirms Mistral permissive for creative; DISCONTINUED Apr 30, 2026; 32K context only |
| OR: Llama 3.3 70B | https://openrouter.ai/meta-llama/llama-3.3-70b-instruct | 2026-04-19 | 131K context, $0.12/$0.38; best-documented tool-call reliability among Groq-hosted open-weight models |
| OR: Nemotron 3 Nano 30B A3B | https://openrouter.ai/nvidia/nemotron-3-nano-30b-a3b | 2026-04-19 | 262K context, $0.05/$0.20; Nvidia AUP likely blocks adult content |
| Groq blog: Kimi intro | https://groq.com/blog/introducing-kimi-k2-0905-on-groqcloud/ | 2026-04-19 | Model ID `moonshotai/Kimi-K2-Instruct-0905`, 256K context, $1.00/$3.00; intro post only, no deprecation announcement |

### Corrections to prior research (RESEARCH.md v1)

| Prior claim | Status | Corrected finding |
|-------------|--------|------------------|
| kimi-k2-0905 deprecated on Groq ~April 15 — "WARNING" | **CONFIRMED CORRECT** | Absent from Groq rate-limits page and OpenRouter live model JSON as of 2026-04-19. The "fastest on Groq" label in the speed screenshot is stale. |
| Primary: `z-ai/glm-5-turbo` | **STILL VALID, but superseded** | glm-5-turbo is still available but glm-4.7 (newer, Dec 2025) and glm-4.7-flash ($0.06/$0.40) are better picks — same lineage, lower cost. |
| Fallback 2: `stepfun/step-3.5-flash` | **UNCONFIRMED** | stepfun/step-3.5-flash does not appear in the OpenRouter live model JSON as of 2026-04-19. Cannot confirm availability. Remove from shortlist until verified. |
| kimi-k2.5 listed as "WATCH — not on Groq" | **UPGRADED TO PRIMARY** | kimi-k2.5 IS the live Kimi model now, on OpenRouter/BaseTen at 131 tok/s. Groq has not yet added it. |
| OpenRouter screenshot rank 7 "Kimi K2 0905 fastest on Groq 201 tok/s" | **STALE DATA** | Groq no longer serves K2 0905. Speed measurement is from before deprecation. |
