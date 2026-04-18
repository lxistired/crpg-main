# Script Mode Profiles

Per-tier word count, sentence style, dialogue density. Script reads these when it receives `detailRichness` from story meta.

## detailRichness = concise

| | |
|---|---|
| Target | ~1500 words total (or whatever `beat.targetWordCount` says) |
| Per-stanza | 2-3 short sentences |
| Dialogue | Minimal — 1 exchange or none |
| Description budget | 1 sentence before action |
| Sensory detail | 1 per scene, max |

**Style directive**: tight prose, action and value shifts only, no decorative detail. If you can cut a sentence without losing story movement, cut it.

## detailRichness = standard

| | |
|---|---|
| Target | ~2200 words |
| Per-stanza | 4-5 sentences |
| Dialogue | 1-2 short exchanges |
| Description budget | 2 sentences before action |
| Sensory detail | 1-2 per scene |

**Style directive**: balanced prose, brief dialogue, key sensory details. Short action sentences.

## detailRichness = detailed (default)

| | |
|---|---|
| Target | ~2500 words |
| Per-stanza | 6-8 sentences |
| Dialogue | 2-3 exchanges |
| Description budget | 2-3 sentences before action |
| Sensory detail | 2-3 per scene, concrete, actionable |

**Style directive** (from daisy V6, verbatim):
> Game-quality prose: short action sentences, punchy dialogue (2-3 exchanges), concrete details the player can interact with. Show character through what they DO and SAY. Max 6-8 sentences per node. Do NOT exceed the word limit.

This is the mode most adult-content briefs want. Rich enough to carry sensory texture, disciplined enough to stay game-like.

## detailRichness = extreme

| | |
|---|---|
| Target per beat | 40-80 words |
| Per-stanza | ONE beat = one tightly-bounded moment |
| Dialogue | Optional — at most 1 line per beat |
| Description budget | 1 concrete action or reaction |
| Sensory detail | 1 per beat max |

**Style directive** (from daisy V6):
> BEAT-LEVEL GRANULARITY: Each beat is ONE action-reaction exchange. Something happens, value shifts. 40-80 words. Sharp and punchy. Active voice. Concrete actions. The player DOES things. Choice and check beats are also beat-level: they represent the moment of decision/test, not a full scene.

**Within a sequence** (groups of 2-5 beats from Skeleton's `sequences` array):
- Beats alternate polarity (+/-/+/-)
- Each beat raises stakes or subverts expectations
- Final beat of sequence is its micro-climax

## How to read `beat.targetWordCount` from Skeleton

Skeleton already computed and emitted `targetWordCount` on every beat. Use that number. Don't recompute.

- If `targetWordCount = 2500` and you're writing in detailed mode → aim for 2400-2600 words.
- If `targetWordCount = 60` (extreme mode beat) → aim for 40-80.

If your draft is more than 10% off target, revise (expand or trim) before emitting.

## Sentence rhythm rules (all modes)

- Start a paragraph with a short action sentence, not a long description.
- Alternate short and medium sentences. Avoid long compound sentences stacking.
- Never open a scene with weather or ambient description — open with the protagonist doing something.

## Dialogue structure

- Max 2-3 exchanges between the same pair before someone DOES something or the scene turns.
- Each line should carry one of: info, dilemma, tension, characterization. Never filler pleasantries.
- Chinese bracket quotes only: `「」` for outer, `『』` for nested inner. Never ASCII `""`.
