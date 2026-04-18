# McKee Principles — the 9 hard constraints

Daisy's V6 narrative core distilled 6 of Robert McKee's *Story* principles into hard rules every skeleton must satisfy. crpg adds 3 more that daisy left out because they are especially load-bearing for branching fiction + image generation.

## The 6 from daisy V6

### 1. Value Shift (Scene Turning Point)
*"Every scene must turn. If it doesn't turn, it's not a scene, it's exposition." — McKee*

Every beat must turn at least one value. Tag with `valueBefore` and `valueAfter` as 2-5 word labels. The polarity should alternate between consecutive beats where possible (+/-/+/- rhythm).

Value axes: hope/despair, trust/betrayal, safety/danger, love/hate, truth/lie, freedom/servitude, control/loss, intimacy/distance, etc. Pick whichever axis the beat actually turns.

### 2. Progressive Complication
Each successive beat raises stakes or narrows options. Never plateau. If two consecutive beats have the same stakes, one of them is filler — delete it or combine them.

### 3. Dilemma
Choice nodes present irreconcilable dilemmas. Every option costs something meaningful. No choices where one option is obviously better — that's exposition dressed as agency.

Types of dilemma:
- **Good vs Good** — two positive values that can't coexist (love vs duty)
- **Bad vs Bad** — two losses that can't both be avoided (die or betray)

### 4. The Gap
Between a character's action and the world's reaction there must be a gap. The result is always different (better or worse) than the protagonist expected. This gap is the engine of dramatic energy.

Don't write: "She tried X, and X worked as planned." Write: "She tried X, but the world responded with Y." Y can be worse (complication) or surprisingly better (unearned success with later cost).

### 5. Controlling Idea
One theme sentence, shape: `{finalValue, cause}`.

Good: `{finalValue: "Justice prevails", cause: "when honest people outwit the corrupt"}`
Good: `{finalValue: "Love destroys", cause: "when lovers lie to protect each other"}`
Bad: `{theme: "love is complicated"}` — not a controlling idea, just a topic.

The controlling idea constrains every beat. If a beat doesn't serve it, either rewrite the beat or rewrite the idea.

### 6. Three Levels of Conflict
Weave all three throughout:
- **Inner conflict** — psychology / emotion / desire (what the character wants vs needs)
- **Personal conflict** — relationships (family / lovers / allies / enemies at the personal scale)
- **Extra-personal conflict** — society / institutions / environment / physical world

A scene with only one layer feels thin. Aim for at least two layers active in most beats, all three in climax.

---

## The 3 crpg additions

### 7. Genre
McKee: *"The writer who doesn't know his genre is a writer without a community."*

Infer a genre from the brief keywords (e.g. 雨夜 + 律师 + 酒吧 → 都市 noir). Every genre carries:
- **Conventions** — elements the audience expects (noir: moral ambiguity, night/rain, cigarette smoke)
- **Obligatory scenes** — moments the audience will feel cheated without (love story: the Meet, the Kiss, the Separation, the Reunion; horror: False Ending, Final Girl; crime: Investigation, Confrontation)
- **Visual style** — genre also signals image aesthetics (noir = wet streets, high-contrast lighting)

Emit `meta.genre` with a concrete label (e.g. `都市 noir`, `赛博朋克`, `民国谍战`). Downstream Director skill uses this.

Common adult-content-compatible genres: 都市 noir / 民国谍战 / 赛博朋克 / 维多利亚哥特 / 现代惊悚 / 古装权谋.

### 8. Antagonism
McKee: *"A protagonist can only be as compelling as the forces of antagonism make them."*

The opposing force must be ≥ the protagonist on at least one dimension:
- **Physical** — stronger, faster, armed, has more bodies
- **Social** — higher status, more power, bigger network
- **Personal** — emotional leverage, knows the protagonist intimately
- **Intellectual** — smarter, more information, better planner
- **Moral** — operates with fewer scruples (or paradoxically, more righteously)

Emit an `antagonism` block with `{force, dominant_dimension, justification}`. AI has a strong bias toward "weak antagonist / quick protagonist victory" — this constraint counter-weights it.

The antagonist does not have to be a person. It can be a system (bureaucracy, caste, genre convention), a place (a hostile environment), or an inner demon (addiction, guilt) — whichever is dominant in the genre.

### 9. Climax
McKee: Climax = the story's maximum value flip. All prior beats lead here.

Emit exactly one beat with `type: climax`. It must sit after all complications and before any `ending`. In bifurcating structures, each branch gets its own climax (so multiple branches × one climax per branch).

`climax` is a distinct node type from `ending` because:
- climax = the *decision/action* at peak stakes
- ending = the aftermath / resolution / epilogue

A story without a climax beat feels anticlimactic even when the ending is technically sad/happy — because the peak value-flip was never staged as a dramatic beat.

---

## Quick self-check before emit

- Does the skeleton have one controlling idea of the shape {finalValue, cause}?
- Does every beat have valueBefore → valueAfter?
- Is there at least one antagonism axis stronger than the protagonist?
- Is there exactly one climax beat per branch, placed before ending?
- Do choice beats have real dilemmas (no obviously right option)?
- Do successive beats escalate (no plateau)?
- Do the genre conventions and at least one obligatory scene appear?

If any answer is no, revise before emitting.
