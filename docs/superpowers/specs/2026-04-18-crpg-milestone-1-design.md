# crpg — Milestone 1 Design Spec

**Date**: 2026-04-18
**Scope**: Creator-facing CLI pipeline that turns a prose brief into a story bundle (JSON + real images).
**Status**: Design approved, pending implementation plan.

---

## 1. Goal

Produce a standalone CLI tool (`crpg generate`) that takes a creator's brief and emits a bundle a reader client can consume later. End-to-end includes real image generation.

```
$ crpg generate --brief brief.md --out bundle/
  → bundle/story.json
  → bundle/characters.json
  → bundle/shots/<beat_id>/shot-NNN.png
  → bundle/meta.json
```

This milestone delivers **only the creator pipeline**. No reader frontend, no auth, no payment, no publishing flow. Those come in later milestones.

## 2. Pipeline

Four LLM passes plus one pure function. Each pass operates on a **beat** (节拍, ~2000 字 + 4-6 shots) as the atomic unit of work. Everything scales linearly in beats.

```
Brief + config  ──►  Pass 1: Skeleton
                     (骨架 JSON + character sheet)
                        │
                        ▼
                     Pass 2: Script (per beat)
                     (散文正文, 2200-2800 字 / 2500+ for detailed)
                        │
                        ▼
                     Pass 3: Director (per beat)
                     (shot list JSON, VGAI-gated)
                        │
                        ▼
                     Pass 4: Prompt Assembler (pure function)
                     (ANIME_PREAMBLE + base + pose + gated_attrs → Grok prompt string)
                        │
                        ▼
                     Pass 5: Image Batch
                     (Grok Imagine Pro, 批量生图)
```

## 3. Models (empirically validated 2026-04-18)

All text passes share **one model + provider**: `moonshotai/kimi-k2-0905 @Groq`. Different system-prompt suffixes per pass.

| Pass | Primary | Fallback | Per-call latency | Notes |
|------|---------|----------|:----------------:|-------|
| Skeleton | kimi-k2-0905 @Groq | — | 3.5s | 3/3 clean JSON, 6 beats + mutex + character sheet |
| Script short | kimi-k2-0905 @Groq + `LENGTH_SUFFIX` | xiaomi/mimo-v2-pro | 9s | 2/3 hit target 2200-2800; close miss |
| Script detailed | kimi-k2-0905 @Groq (segmented main→A‖B) | xiaomi/mimo-v2-pro single-call | 19s (3 calls concurrent) | 3/3 hit 5500-7000, $0.018/scene |
| Director | kimi-k2-0905 @Groq + `STRONG_SUFFIX` + `FEW_SHOT_SUFFIX` | qwen/qwen3-max @Alibaba | 4.3s | 4/4 VGAI clean, base 6/6 |
| Image | Grok Imagine Pro (xAI direct) | — | TBD per shot | User validated earlier in project |

**Why kimi-k2-0905 @Groq for everything**: 14× faster than Alibaba-hosted alternatives (qwen3-max ~61s), empirically clean after hardening suffixes, single API surface simplifies infra.

**Why Groq needs suffixes**: Groq's throughput-optimized deployment has weaker default instruction-following. Hardening via "output rejected if violated" language + abstract few-shot restores compliance. See `skills/director/references/provider-hardening-suffix.md`.

### Model alternatives kept on the bench

- **z-ai/glm-5.1** — top literary density on Script (155-163s @ SiliconFlow). Reserve as "premium edit mode" later milestone.
- **xiaomi/mimo-v2-pro** — 52s, quality comparable to glm-5.1. Primary Script backup.
- **qwen/qwen3-max-thinking** — 61s, clean Director with traceable thinking. Fallback if Groq outage.

Rejected: minimax m2.5/m2.7 (VGAI violations), mistral-large (VGAI violations), mistral-small-creative (JSON truncation), ds-v3.2-speciale (JSON failure), xiaomi/mimo-v2-flash (schema/prompt semantic mismatch), nex-agi/deepseek-v3.1-nex-n1 (mutex violation).

## 4. Orthogonal configuration axes

```
detailRichness: concise | standard | detailed | extreme
    → per-beat word count: 1500 / 2200 / 2500 / 3500
    → per-beat shot count: 1-2 / 2-3 / 4-6 / 6-10

contentLength:  short | medium | long
    → total beat count: 3 / 15-18 / 50-60

structure:      linear | bifurcating | funnel | web
    → determines edge topology in story.json
```

**Combined cost/latency estimates** (paid OpenRouter key, 50-concurrency limit assumed):

| Combo | Beats | Script+Director calls | End-to-end time | Est cost |
|-------|:-----:|:---------------------:|:---------------:|:--------:|
| short + concise | 3 | 6 | ~16s | $0.03 |
| **short + detailed** | **3** | **6** | **~26s ✓ tested** | **$0.04** |
| medium + standard | 15 | 30 | ~80s | $0.20 |
| medium + detailed | 18 | 36 | ~2 min | $0.30 |
| long + concise | 60 | 120 | ~3-4 min | $0.60 |
| long + detailed | 120 | 240 | ~8 min | $1.50 |

Excludes image generation time (Grok Imagine Pro, ~5-15s per shot).

UI (future milestone) must warn on impractical combos (e.g., long + extreme exceeds 400K chars / $5 per story).

## 5. Concurrency model

```python
# Beat-level atomic, semaphore-limited, DAG-scheduled
sem = asyncio.Semaphore(50)   # paid OpenRouter concurrency limit

for beat_batch in dag.topological_layers(plan.beats):
    # All beats in one layer have no pending deps → run concurrent
    results = await asyncio.gather(*[process_beat(b) for b in beat_batch])
```

- **Within a scene**: main → (A ‖ B) pattern
- **Between scenes**: DAG scheduling, scenes without inter-deps run concurrent
- **Architect provides `depends_on`** per beat (validated: Skeleton pass outputs this field)
- **Groq rate limit discovery**: TBD on paid tier, defaults to 50-concurrent semaphore

## 6. Framework

**OpenAI Agents SDK** (Python 0.14.1, Apache/MIT license).

Not Claude Agent SDK — that one binds to Anthropic Commercial TOS whose AUP prohibits adult content generation, which conflicts with product scope.

OpenAI Agents SDK is a pure Python library; endpoint is configurable, so we point it at OpenRouter / xAI.

## 7. Bundle data contract

```
story-bundle/
├── story.json           # beats + edges + meta (content/length/richness/structure)
├── characters.json      # per-character base + persistent_grooming + wardrobe_states + mutex_groups
├── shots/
│   └── <beat_id>/
│       ├── shot-001.png
│       ├── shot-002.png
│       └── ...
└── meta.json            # generation timestamp, LLM versions, suffix versions, git sha
```

**story.json schema** (validated by Skeleton test):

```json
{
  "meta": {"title": "...", "genre": "...", "contentLength": "short", "detailRichness": "detailed", "structure": "bifurcating"},
  "beats": [
    {
      "id": "intro",
      "type": "narrative|choice|check|merge|act_break|ending",
      "synopsis": "...",
      "valueBefore": "职业警觉",
      "valueAfter": "模糊失控",
      "wardrobe_state": "office_exit",
      "targetWordCount": 2500,
      "targetShotCount": 5,
      "depends_on": ["prev_beat_id", ...]
    }
  ],
  "edges": [{"from": "beat_a", "to": "beat_b", "condition": "..."}]
}
```

**characters.json schema** (from Director skill `references/character-sheet-schema.yaml`):

```json
{
  "<character_name>": {
    "base": {"age": 28, "ethnicity": "...", "hair": "...", "skin": "...", "eyes": "...", "jaw": "..."},
    "persistent_grooming": [{"name": "red_fingernails", "anchor": "hand"}, ...],
    "wardrobe_states": {"<state>": {"items": [...], "removes": [...]}},
    "mutex_groups": [["stocking_toes", "black_ankle_boots"], ...]
  }
}
```

**Naming convention**: all grooming/wardrobe item names MUST be snake_case English (not Chinese) so they match the Director skill's anchor map and audit logic across teams/languages. (See §10 optimization #1.)

## 8. Success criteria

| Metric | Target |
|--------|:------:|
| End-to-end short+detailed pipeline | ≤30s (text) + image time |
| End-to-end medium+standard | ≤2 min (text) |
| VGAI compliance per shot list | 0 real violations (pass auditor) |
| Character base identity injection | 6/6 consistent per shot list |
| CLI smoke test | `crpg generate --brief fixtures/demo.md` produces valid bundle |
| Auditor smoke test | bundle passes VGAI + mutex + base-consistency checks |

## 9. Explicit out-of-scope (deferred milestones)

- **Reader/player frontend** (纯享版) — separate milestone, consumes bundle as read-only
- **Authentication / user accounts**
- **Payment mechanisms** (both platform-subscription and BYOK flow)
- **Content moderation pipeline** (pre-filter, post-image classifier, human review)
- **Publishing flow** from creator bundle to public pool
- **Multi-style support** (non-anime aesthetics)
- **Story-level re-generation / interactive editing** (currently the CLI is one-shot; iterative refinement is later)
- **Shot-level partial regeneration** (re-doing one bad shot without full bundle rebuild)
- **Prose-level granular edits** post-generation
- **Async/progressive image filling** (bundle is sync — all shots rendered before CLI returns)

## 10. Known optimizations recorded for implementation

1. **Snake_case item naming in Skeleton output**. Current Skeleton test outputs Chinese names (`红色指甲油`, `透黑丝袜`). Add one line to Skeleton system prompt requiring snake_case English for `persistent_grooming.name` and `wardrobe_states.items[].name` and `mutex_groups`. Descriptive Chinese labels can live in a separate `display_name` field if needed.

2. **Skeleton LLM shared with Director** — reuse same endpoint / key / session to reduce connection overhead.

3. **Suffix assembly** — Director and Script each concatenate `DIRECTOR_SYSTEM + {mode-specific suffix}`. Cache the base DIRECTOR_SYSTEM string; only vary the suffix per pass.

4. **Fallback routing policy** — `allow_fallbacks=True` on all Groq calls. If Groq has downtime, OpenRouter auto-routes to AtlasCloud/Together (slower but clean). Log which provider actually served each call.

5. **Per-provider adapter layer** — future models (glm-5.1 @SiliconFlow, mimo-v2-pro, qwen3-max) plug in without restructuring the pipeline. Each is just a different system-prompt profile.

6. **ANIME_PREAMBLE placement** — to be added as a constant block in existing `skills/director/references/grok-constraints.md` during implementation (avoid creating a new reference file). Referenced by Director workflow step 7 where prompt assembly happens.

## 11. Open architectural questions deferred to later milestones

From `memory/project_crpg_architecture_pending.md`:

- **Q4-2** Image sync vs async filling — creator bundle is sync; reader-side progressive load is a player-UI concern (out of Milestone 1).
- **Q4-3** Multi-shot player UX (carousel / Ken Burns / cover-only) — reader frontend.
- **Q4-4** Bundle format — addressed in §7, may refine in Milestone 2 after reader implementation.
- **Q4-5** Cost allocation (platform subscription vs BYOK) — post-Milestone-1.
- **Q4-6** Content moderation layers — post-Milestone-1.
- **Q4-7** Publishing flow creator → pure-reader pool — post-Milestone-1.

## 12. Provider & cost assumptions

- **OpenRouter paid key** (`sk-or-v1-3d3e...b18`) — allows ~50 concurrent requests, sufficient for DAG scheduling.
- **xAI paid key** for Grok Imagine Pro — already set up from prior testing.
- **Fallback to alternate providers** built in (allow_fallbacks=True).

## 13. References

Empirical validation artifacts (committed to this repo):

- `research/model-comparison-2026-04-18/open-source-broad/` — 15+ models × Director+Script broad test
- `research/model-comparison-2026-04-18/open-source-broad/director_speed/groq_experiments/` — Groq hardening discovery (26 API calls)
- `research/model-comparison-2026-04-18/open-source-broad/director_speed/generic_suffix/` — zero-hardcoding suffix validation (4/4 clean)
- `research/model-comparison-2026-04-18/open-source-broad/detailed_mode/` — segmented detailed-mode Script test (3/3 hit)
- `research/model-comparison-2026-04-18/open-source-broad/k2_0905_groq_script/` — Script on Groq k2-0905 (9s avg)
- `research/model-comparison-2026-04-18/open-source-broad/director_detailed_test/` — single-call vs segmented Director on detailed Script (7 vs 22 violations)
- `research/model-comparison-2026-04-18/open-source-broad/skeleton_test/` — Skeleton on Groq k2-0905 (3/3 clean, 3.5s)
- `skills/director/SKILL.md` + `references/` — finalized Director skill including `provider-hardening-suffix.md`

Prior session context:

- `SESSION-HANDOFF-2026-04-17-EVENING.md`
- `SESSION-HANDOFF-2026-04-18-MIDDAY.md`
- `memory/project_crpg_architecture_pending.md` (Q4-2 through Q4-7)
- `memory/project_crpg_visual_system.md` (Visual DNA, Grok Imagine capabilities)
- `memory/project_crpg_model_strategy.md` (content positioning, routing constraints)
