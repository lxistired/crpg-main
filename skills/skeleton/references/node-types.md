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
- **Edge `condition`**: the option text — this is what the UI shows
- **Director**: typically 1-2 shots (the decision moment itself)

### Structural contract — choice beats end UNDECIDED

A `choice` beat's prose MUST end at the **decision threshold**: the protagonist has accepted the dilemma, collected the information, and arrived at the action point — but has NOT yet executed any option. The motor/verbal act of choosing belongs to the OPENING of the branch beat that the edge points to.

Why this is a structural contract rather than a stylistic suggestion: if the prose of the choice beat contains the protagonist's executed decision, the reader enters the next beat as a passive witness to a decision already made. The bifurcation is then fait accompli at the story level — no player agency, no real dilemma.

Skeleton's job on a choice beat:

- `valueBefore → valueAfter` should capture the internal shift that brings the protagonist TO the decision point, not across it.
- Any `synopsis` wording must describe the decision as **still open** at beat end. Avoid language like "chooses X" / "decides Y" / "accepts Z"; prefer "stands at the threshold of", "is confronted with", "must decide between".
- Quoted decision words (if any) belong in the synopsis of the branch beat, not the choice beat.

Downstream (Script): the prose ends with a poised-but-unexecuted action — the protagonist physically at the crux, all options still open. The branch beat's synopsis then re-opens with the decision being executed.

Downstream (Director): shots for the choice beat frame the poised moment (hesitation, threshold, crux) rather than any post-decision action.

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
