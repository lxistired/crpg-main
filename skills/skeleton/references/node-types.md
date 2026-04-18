# Beat / Node Types

`beat.type` takes one of these values. Downstream pipeline and Director skill treat them differently.

## narrative

A prose scene. Most common beat type. Has `valueBefore`, `valueAfter`, `wardrobe_state`, `targetWordCount`, `targetShotCount`. No branching.

- **Outgoing edges**: exactly one (to the next beat)
- **Edge `condition`**: null
- **Director**: produces shots for this beat's prose

## choice

The player is presented with 2-4 incompatible options. Must be a genuine dilemma (rule 3 in mckee-principles.md).

- **Outgoing edges**: one per option, 2-4 total
- **Edge `condition`**: the option text (e.g. `"拒绝玫瑰"`, `"跟他去酒吧"`) — this is what the UI shows
- **Director**: typically 1-2 shots (the decision moment itself)

## check

Skill / attribute check with pass/fail branches.

- **Outgoing edges**: exactly 2
- **Edge `condition`**: exactly `"success"` or `"fail"` (lowercase, no variants like "pass" / "failure")
- **Director**: 1 shot (the testing moment)

## merge

Two or more prior branches converge here. No content of its own; threads rejoin.

- **Outgoing edges**: exactly one
- **Edge `condition`**: null
- **NOT used in `bifurcating` structure** — branches never merge there

## act_break

Act boundary marker. Commonly placed at the inciting incident, midpoint, and end of penultimate act. Narrative-ish but distinguished so the UI / renderer can mark it.

- **Outgoing edges**: exactly one
- **Edge `condition`**: null

## climax (crpg addition)

The highest-stakes beat. Exactly one per branch. Must be placed before any `ending` of that branch. See `mckee-principles.md` rule 9.

- **Outgoing edges**: one or more — a climax can branch into distinct endings based on what the protagonist does at the peak
- **Edge `condition`**: mirrors `choice` semantics if the climax itself is a decision; otherwise null
- **Director**: gets the highest shot budget (2× a normal narrative beat)

## ending

Terminal resolution. No content generation beyond the beat's synopsis.

- **Outgoing edges**: NONE (hard rule — ending is a DAG sink)
- **Ending type annotation** (optional): `positive` / `negative` / `ironic` / `ambiguous` — Script and Director skills adjust tone accordingly.

## Quick lookup: edge `condition` values

| from-beat type | condition values |
|----------------|------------------|
| narrative, merge, act_break | `null` |
| choice | the option text |
| check | `"success"` or `"fail"` |
| climax | `null` (if auto-transition) or option text (if climax is itself a decision) |
| ending | N/A (no outgoing edges) |
