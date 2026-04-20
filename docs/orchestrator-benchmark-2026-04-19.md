# crpg Orchestrator Benchmark — 2026-04-19

Complete record of model + architecture benchmarks. Reference-only; do
not push to GitHub without sanitising if you paste actual key values.

---

## Current best-known — tentatively usable, still too slow

**Status (2026-04-20)**: This is the best full-completeness configuration
we found among the 6 rounds, but **10:54 on the short demo brief is
still too slow for production**. Treat it as "tentatively usable while
we keep searching for a faster orchestrator," not a final decision.

**Configuration**: m2.5-nitro main + grok-4-1-fast-non-reasoning worker,
minimal-combo architecture (4 tools).

| Field | Value |
|-------|-------|
| Profile name (PROFILES key in `main_agent.py`) | `m25-nitro` |
| Main model id | `minimax/minimax-m2.5:nitro` |
| Main endpoint | `https://openrouter.ai/api/v1` |
| Main API key env var | `OPENROUTER_API_KEY` |
| Worker model id | `grok-4-1-fast-non-reasoning` |
| Worker endpoint | `https://api.x.ai/v1` |
| Worker API key env var | `XAI_API_KEY` |
| Image generation model | `grok-imagine-image-pro` (xAI Grok Imagine) |
| Image endpoint | `https://api.x.ai/v1/images/generations` |
| Image API key env var | `XAI_API_KEY` |
| Architecture flag | `--minimal-combo` in harness |
| Tool count | 4 (`freeform_script_worker` + `save_shot_prompt` + `render_anchor` + `render_image`) |
| Wall time on short demo brief | ~10:54 |
| Prose hit rate | 8/8 beats; 7/8 in strict ±10% window, 8/8 in loose 60-130% |
| Shot Style Preamble consistency | 17/17 shots byte-identical (735-char canonical) |

Runner-up for **speed at acceptable quality**: m2.5-nitro **solo
freeform** (1 tool = `render_image`), ~5:12, 5/5 beats A-grade prose +
15 shots byte-identical Preamble, but one fewer beat branch completion.

---

## All models tested (profile table)

All profile dicts live in `src/crpg/agent/main_agent.py::PROFILES`.

| Profile | model_id | base_url | api_key_env | Notes |
|---------|----------|----------|-------------|-------|
| `minimax-baseline` | `MiniMax-M2.7-HighSpeed` | `https://api.minimaxi.com/v1` | `MINIMAX_API_KEY` | Original thinking baseline. Full pipeline succeeds, but SSE stream can crash on long prompts. |
| `m25-nitro` | `minimax/minimax-m2.5:nitro` | `https://openrouter.ai/api/v1` | `OPENROUTER_API_KEY` | **Current winner.** Reasoning model via OpenRouter's fastest provider. |
| `grok-xai` | `grok-4-1-fast-non-reasoning` | `https://api.x.ai/v1` | `XAI_API_KEY` | Fast non-thinking; used as default worker. |
| `grok-xai-reasoning` | `grok-4-1-fast-reasoning` | `https://api.x.ai/v1` | `XAI_API_KEY` | Reasoning variant of 4.1-fast. |
| `grok-xai-4.2-reasoning` | `grok-4.20-0309-reasoning` | `https://api.x.ai/v1` | `XAI_API_KEY` | 4.2 reasoning — consistently terminates early. |
| `grok-combo` | `grok-4-1-fast-reasoning` (main) + default worker | `https://api.x.ai/v1` | `XAI_API_KEY` | Reasoning main in combo mode. |
| `grok-combo-4.2` | `grok-4.20-0309-reasoning` (main) + default worker | `https://api.x.ai/v1` | `XAI_API_KEY` | 4.2 combo. |
| `gpt-oss-120b-nitro` | `openai/gpt-oss-120b:nitro` | `https://openrouter.ai/api/v1` | `OPENROUTER_API_KEY` | Fails on long Chinese prose (~18% of target). |
| `qwen3-32b-groq` | `qwen/qwen3-32b` with `provider={"only":["groq"]}` | `https://openrouter.ai/api/v1` | `OPENROUTER_API_KEY` | **Broken:** Groq's qwen3-32b on OpenRouter has no tool_use endpoint. |
| `kimi-k2.5-baseten` | `moonshotai/kimi-k2.5` with `provider={"only":["BaseTen"]}` | `https://openrouter.ai/api/v1` | `OPENROUTER_API_KEY` | **Broken:** BaseTen returns HTTP 502 on every call. |

### Worker model override

The script worker (used by `invoke_script_worker` and
`freeform_script_worker`) is configured via env vars (see
`src/crpg/agent/tools.py`):

```
CRPG_WORKER_MODEL       # default: grok-4-1-fast-non-reasoning
CRPG_WORKER_BASE_URL    # default: https://api.x.ai/v1
CRPG_WORKER_API_KEY_ENV # default: XAI_API_KEY (then value read from env)
```

---

## Architectures compared

Selected via mutually-exclusive flags in `build_main_agent()` and the
harness `text_only_harness.py`. All use a ~105 KB skill corpus
pre-injected into the system prompt by `_load_skill_corpus()`.

| Arch | Harness flag | Tools in play | Notes |
|------|--------------|---------------|-------|
| Default (round-1 reference) | _(none — needs re-enabling old `read_skill` tools)_ | 13 (incl. `read_brief`, `read_skill*`) | Pre-refactor baseline; m25-nitro 7:59 with 3/3 strict prose. |
| Text-only | `--skip-director` | 9 | Skeleton + Script; stops before Director. |
| Combo (validated) | `--combo` | 9 (incl. `invoke_script_worker`) | Strict validation on worker output; worker regresses under retry pressure. |
| Freeform solo | `--freeform` | 1 (`render_image`) | No structural tools; everything in markdown. m25 shines (44 KB + 15 shots). |
| Freeform combo | `--freeform-combo` | 2 (`render_image` + `freeform_script_worker`) | Fast (~2:36) but Director stubs to one-liners. |
| Hybrid solo | `--hybrid` | 4 (`render_image`, `render_anchor`, `write_beat_shots`, `validate_vgai`) | **Empty bundles** on all grok variants. |
| Hybrid combo | `--hybrid-combo` | 5 (freeform_script_worker + hybrid Director tools) | Prose OK but Director paralyses. |
| **Minimal combo** | `--minimal-combo` | **4** (`freeform_script_worker`, `save_shot_prompt`, `render_anchor`, `render_image`) | **Winner for completeness.** Lenient Style Preamble prefix check; no Direction Layer / occlusion validation in tool. |

### Why minimal-combo won

- 4 tools = enough multi-turn cadence to drive the agent beat-by-beat.
- `save_shot_prompt` enforces Style Preamble prefix only (no full VGAI),
  which avoids the retry-regression trap where validation compresses
  worker output.
- Worker is called once per beat with the beat synopsis + target chars,
  and the prose is saved without re-prompt pressure.

---

## Full results matrix (demo short brief)

Each row is one profile × one architecture. `Wall` in seconds, `Prose`
= `N/M in strict ±10% window / loose 60-130% window`, `Shots` = number
of `save_shot_prompt` / `write_beat_shots` calls that succeeded.

| Profile | Arch | Wall | Outcome | Prose (strict / loose) | Shots | Verdict |
|---------|------|------|---------|-------------------------|-------|---------|
| minimax-baseline | default 13-tool | 29:32 | DONE ✓ | 4/7 / 7/7 | 10 | Complete but slow. |
| minimax-baseline | 9-tool preload | 17:58 | DONE ✓ | 3/8 / 7/8 | 10 | 40% faster than round-1. |
| m25-nitro | default 13-tool | **7:59** | DONE ✓ | 3/3 / 3/3 | 4 | Prior winner (round 1). |
| m25-nitro | 9-tool preload | 16:31 | DONE ✓ | 0/6 (over ceiling) | 0 (abandoned) | Big system prompt hurt shots phase. |
| m25-nitro | freeform solo (`--freeform`) | 5:12 | partial | 5/5 (by CJK only) | 15 | A-grade content. |
| m25-nitro | **minimal-combo** | **10:54** | partial | **7/8 / 8/8** | **17** | **Full-breadth winner; all 17 Preamble byte-identical.** |
| grok-xai | freeform-combo | 5:14 | partial | 0/6 in strict | 0 | Worker regresses under retry pressure. |
| grok-xai | minimal-combo | 2:47 | partial | 5/8 / 7/8 | 0 | Best grok prose but Director never fired. |
| grok-xai-reasoning | freeform solo | 53s | failed | 0 beats | 0 | Model stopped after skeleton. |
| grok-xai-reasoning | freeform-combo | 2:36 | partial | 2/6 / 6/6 | 0 (stubs) | Prior speed champion, Director stubbed. |
| grok-xai-reasoning | minimal-combo | 2:12 | partial | 2/7 / 6/7 | 1 | Prose good; shots start but barely. |
| grok-xai-4.2-reasoning | freeform solo (B) | 56s | partial | - / 2 Preamble in md | 1 | Agent self-stubs "[Preamble]". |
| grok-xai-4.2-reasoning | freeform-combo (B) | 2:03 | partial | 1/4 / 1/4 (46-60%) | 0 | Character / tone drift. |
| grok-xai-4.2-reasoning | minimal-combo | 2:36 | partial | 0/5 / 1/5 | 0 | Worst prose hit rate. |
| grok-combo (4.1 reason) | minimal-combo | 2:13 | partial | 2/7 / 6/7 | 1 | Brief hallucinated in b1 (陆谨言). |

(The `gpt-oss-120b`, `qwen3-32b-groq`, `kimi-k2.5-baseten` profiles all
failed before producing output and are omitted.)

---

## Key findings

1. **Tool count is a U-shape, not monotonic.** Too few (`--freeform`,
   1 tool) means no multi-turn drive — grok stops after a skeleton,
   m25 takes 5:12 but ships. Too many (13-tool default) means tool-call
   bias pulls output short (prose retries storm) and long skill
   reference chains dilute attention. The 4-tool `--minimal-combo`
   lands in the sweet spot.
2. **Validation pressure can regress output.** When `invoke_script_worker`
   REJECTs at 85% and main agent prompts the worker to expand, grok
   worker writes *shorter* on retry (seen: 85% → 49% → 39%). Removing
   the validation gate in `freeform_script_worker` let worker deliver
   60-118% naturally.
3. **Style Preamble byte-lock is load-bearing for image consistency.**
   The only bundle with all shots byte-identical (17/17) is the m25
   minimal-combo. Lenient `save_shot_prompt` prefix-only check is
   enough for m25 to self-enforce; looser modes let grok paraphrase
   per shot.
4. **grok-4.2 underperforms 4.1 on this task.** 4.2 reasoning terminates
   before branch resolution, has brief-drift more often, and hits the
   prose window less reliably (0-52% vs 4.1's 2/8 in strict window).
5. **Hybrid A architecture is dead.** Every hybrid run produced an
   empty bundle (render_anchor errors, nothing else). Removed from the
   recommended set.
6. **grok-4.1-non-reason solo-combo (`grok-xai --minimal-combo`)
   matches m25 on prose window** (5/8 strict, 8/8 loose at 80-144%) at
   2:47, 4× faster than m25. If image generation is deferred (text-only
   draft), grok-4.1-non-reason in minimal-combo is a viable fast path.

---

## .env template

Local reference only — do NOT commit actual keys.

```
# Main agent (MiniMax direct — baseline)
MINIMAX_API_KEY=...
MINIMAX_ENDPOINT=https://api.minimaxi.com/v1
MINIMAX_MODEL=MiniMax-M2.7-HighSpeed

# OpenRouter (m25-nitro, qwen, kimi, gpt-oss, …)
OPENROUTER_API_KEY=...

# xAI (grok models + Grok Imagine)
XAI_API_KEY=...

# Script worker override (defaults shown)
# CRPG_WORKER_MODEL=grok-4-1-fast-non-reasoning
# CRPG_WORKER_BASE_URL=https://api.x.ai/v1
# CRPG_WORKER_API_KEY_ENV=XAI_API_KEY
```

---

## Reproducing the winner

```
# From project root:
rm -rf /tmp/crpg-bench-m25 /tmp/crpg-bench-m25.log
.venv/bin/python research/agent-streaming-debug/text_only_harness.py \
    tests/fixtures/demo_brief.md \
    /tmp/crpg-bench-m25 \
    --profile m25-nitro \
    --minimal-combo \
    > /tmp/crpg-bench-m25.log 2>&1

# Then score:
.venv/bin/python research/agent-streaming-debug/check_bundle.py \
    /tmp/crpg-bench-m25 /tmp/crpg-bench-m25.log \
    --label "m25-minimal-combo"
```

---

## Next steps

**The speed bar is not yet met.** Keep searching for a faster
orchestrator before treating `m25-nitro + --minimal-combo` as the
final choice. Candidate directions:

- Try newer/faster reasoning models as they ship (Sonnet 4.6 +,
  GPT-5 class, Gemini 2.5 Pro variants, Grok 5) on `--minimal-combo`.
- Try `grok-xai --minimal-combo` (2:47 on short brief, 5/8 strict
  prose) paired with a secondary shots-only pass, to see if decoupling
  prose and shots beats the single-agent approach on wall time.
- Investigate whether the 13-tool default's speed-win (m25-nitro 7:59)
  can be reconstructed without its prose-window regression.

**Non-blocking follow-ups on the current best-known config:**

1. Implement `b5a` (回家分支结尾) retry logic — main agent should
   re-call worker when a beat is missing at finish time.
2. Upgrade `save_shot_prompt` to additionally check for a
   `Direction:` line (lenient — presence, not content).
3. Add a second pass that turns freeform_output markdown into
   `story.json` / `characters.json` so downstream image pipeline can
   consume it (one-off conversion, not a tool call).

**Scaling test brief — do NOT use the民国谍战 fixture.**
`tests/fixtures/medium_detailed_brief.md` and
`tests/fixtures/skeleton_briefs/shanghai_1930s.md` are 1930s-Shanghai
political-thriller period pieces and do not match crpg's project
positioning (modern-urban adult-oriented anime visuals). They remain
in the repo as historical skeleton-generalization artifacts only.
Before running a long-brief scaling test, author a new fixture that
sits inside the product style: contemporary setting, adult-oriented
(Literotica/AO3-adjacent, not explicit political history), compatible
with the locked anime Style Preamble.
