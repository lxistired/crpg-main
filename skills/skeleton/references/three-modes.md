# Modes: concise / standard / detailed / extreme / poetic

Four `detailRichness` tiers control word count per beat and Script writing style. One orthogonal `poeticMode` toggle controls keyword interpretation + temperature.

## detailRichness tiers

| tier | word count / beat | shot count / beat | beat granularity |
|------|------------------:|------------------:|------------------|
| concise | 1500 | 1-2 | scene-level, one value shift per beat |
| standard | 2200 | 2-3 | scene-level, one value shift per beat |
| detailed | 2500 | 4-6 | scene-level, one value shift per beat |
| extreme | 3500 total across beats; each individual beat 40-80 words | 6-10 across beats | **beat-level granularity** — each node is ONE action-reaction moment; scenes are split into 2-4 beat-nodes grouped into sequences |

### Key difference: extreme mode

In extreme mode, `beat` no longer means "scene" — it means "the smallest dramatic unit" (one action, one reaction, one value shift). Split each scene into 2-4 nodes. Add a `sequences` top-level array that groups related beats:

```json
"sequences": [
  {"id": "seq-1-1", "actIndex": 0, "name": "觉醒与探索", "valueBefore": "...", "valueAfter": "..."}
]
```

Each beat references `sequenceId` + `beatIndex`. Within a sequence, beats alternate polarity (+/-/+/-). The final beat is the sequence's micro-climax.

Only use extreme mode when the brief requests it explicitly (`detailRichness=extreme`) — default to `detailed` if unspecified.

## poeticMode toggle

- **`poeticMode: true`** (default for crpg) — keywords become atmospheric metaphors, not literal plot elements. "雨" might become grief, liminality, a boundary; "玻璃" might become a fragile relationship or a mirror of the self. Temperature: 0.8 (capped — higher starts hallucinating structure).
- **`poeticMode: false`** — keywords are concrete plot elements. "雨" means actual rain plays a visible role. "玻璃" means glass appears as an object / location. Temperature: 0.7.

For crpg adult-content use, **poeticMode on is usually right** — the brief is rarely literal, and poetic interpretation gives the Script agent more narrative latitude while still being constrained by McKee.

## Temperature equivalence across models

`poeticMode=true` means temperature ≤ 0.8 when expressed on the daisy scale (Claude Sonnet). For other models, use the equivalent-temperature table (stored in `.planning/intel/` of the original daisy project; crpg M1 caps at 0.8 across all text models for poetic mode).

## What Skeleton emits vs what Script/Director consume

- Skeleton emits `contentLength`, `detailRichness`, `structure`, `poeticMode` in `story.meta`
- Script reads `detailRichness` → applies per-tier word count + style
- Script reads `poeticMode` → applies temperature + keyword interpretation
- Director reads `detailRichness` → allocates `targetShotCount` per beat

Never hard-code temperature or word count in the Skeleton output — the tier name is the contract; per-tier values live in this reference and in Script's own reference file.
