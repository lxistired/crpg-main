---
name: skeleton
description: Use when a user brief (keywords / a sentence / a paragraph) must be turned into a complete story skeleton — beats, edges, characters (base + persistent_grooming + wardrobe_states + mutex + covers), controlling idea, and value shifts. Produces story.json + characters.json for downstream Script and Director passes.
---

# Skeleton Skill

Turn a raw creator brief (anything from a 3-keyword prompt to a full paragraph) into a structured, McKee-compliant story skeleton that downstream agents can narrate and shoot.

## Core principle

**Structure before prose.** You write titles, value tags, dependencies, and character sheets. You never write narrative paragraphs — that's the Script skill's job. If you catch yourself writing sensory detail, stop.

## Inputs

The user passes you free-form text. Treat it as intent, not literal plot. Fill defaults for anything missing:

| Field | Default when missing |
|-------|----------------------|
| `contentLength` | `short` |
| `detailRichness` | `detailed` |
| `structure` | `bifurcating` |
| `poeticMode` | `true` (keywords become atmospheric metaphors, not literal plot elements) |

## The nine hard constraints

These apply to every skeleton you produce. Six are from McKee via daisy V6; three are crpg additions (see `references/mckee-principles.md` for full rationale).

1. **Value Shift** — every beat turns at least one value. State `valueBefore` → `valueAfter` as 2-5 word tags.
2. **Progressive Complication** — each successive beat raises stakes or narrows options. Never plateau.
3. **Dilemma** — choice nodes present irreconcilable dilemmas. No obvious "good" answer.
4. **The Gap** — outcomes differ from the protagonist's expectation (better or worse).
5. **Controlling Idea** — one theme sentence, stated as `{finalValue, cause}`, consistent across all acts.
6. **Three Levels of Conflict** — weave inner (psych) / personal (relationships) / extra-personal (world) throughout.
7. **Genre** (crpg addition) — infer a genre from keywords; apply its conventions + obligatory scenes + visual style signals.
8. **Antagonism** (crpg addition) — the opposing force (person, system, or inner demon) must be ≥ protagonist on at least one dimension (physical / social / personal / intellectual / moral).
9. **Climax** (crpg addition) — there MUST be exactly one `climax` beat (a distinct node type), placed before any `ending`. The climax carries the biggest value flip in the story.

## Workflow (per brief)

```
1. Parse brief → infer: keywords, implied genre, implied protagonist, implied antagonist
2. Decide 3 axes (use defaults for any missing):
     contentLength → total beat count (short=3, medium=15-18, long=50-60)
     detailRichness → per-beat target word count (concise=1500, standard=2200,
                      detailed=2500, extreme=3500)
     structure → edge topology (linear / bifurcating / funnel / web)
3. Draft the controlling idea: {finalValue, cause}
4. Draft the antagonism profile: who/what, at which dimension stronger than protagonist
5. Place the climax beat (second-to-last slice of the arc, before any ending)
6. Generate beats with proper depends_on (DAG) and wardrobe_state tags
7. Generate character sheet(s):
   - base (age/ethnicity/hair/skin/eyes/jaw)
   - persistent_grooming (body marks that travel)
   - wardrobe_states (named narrative contexts, pick exactly one per beat)
   - mutex_groups (physically impossible pairs — see references/mutex-coverage.md)
   - covers field on every wardrobe item (sub_anchors fully occluded)
8. Validate: every beat has value shift, no plateau, exactly one climax, DAG is valid
9. Emit JSON via write_story_json + write_characters_json tools
```

Read `references/mckee-principles.md` before step 3, `references/structure-presets.md` before step 6, `references/mutex-coverage.md` before step 7, `references/node-types.md` any time beat types confuse you.

## Output schema

Return two JSON objects (via separate tool calls: `write_story_json` + `write_characters_json`).

`story.json` minimum shape:

```json
{
  "meta": {
    "title": "...",
    "genre": "...",
    "contentLength": "short|medium|long",
    "detailRichness": "concise|standard|detailed|extreme",
    "structure": "linear|bifurcating|funnel|web",
    "poeticMode": true
  },
  "controllingIdea": {"finalValue": "...", "cause": "..."},
  "antagonism": {"force": "...", "dominant_dimension": "physical|social|personal|intellectual|moral", "justification": "..."},
  "beats": [
    {
      "id": "b1",
      "type": "narrative|choice|check|merge|act_break|climax|ending",
      "synopsis": "one-line what-happens",
      "valueBefore": "2-5 words",
      "valueAfter": "2-5 words",
      "wardrobe_state": "state_name",
      "targetWordCount": 2500,
      "targetShotCount": 5,
      "depends_on": ["prev_beat_id", ...]
    }
  ],
  "edges": [
    {"from": "b1", "to": "b2", "condition": "...|null"}
  ]
}
```

`characters.json` minimum shape (see `references/mutex-coverage.md` for the full covers / mutex rules):

```json
{
  "<character_snake_case_name>": {
    "base": {"age": 28, "ethnicity": "...", "hair": "...", "skin": "...", "eyes": "...", "jaw": "..."},
    "persistent_grooming": [
      {"name": "red_fingernails", "anchor": "hand", "sub_anchor": "fingernails"}
    ],
    "wardrobe_states": {
      "<state_name>": {
        "items": [
          {
            "name": "black_stilettos",
            "anchor": "foot",
            "covers": ["toes", "foot_top_inner"],
            "visual_description": "glossy black patent-leather stiletto pumps, pointed toe, closed back, 10cm spike heel, no ankle strap, matte underside",
            "disambiguation_layers": []
          }
        ],
        "removes": []
      }
    },
    "mutex_groups": []
  }
}
```

### `visual_description` — verbatim canonical outfit string (REQUIRED)

Every wardrobe item MUST populate `visual_description` with a complete, vivid, byte-for-byte canonical description the Director will copy literally into every shot prompt. This is the single biggest lever for wardrobe consistency across shots.

Guidance:
- 30-80 English words per item
- Material + cut + color + closure + silhouette + any signature detail
- Avoid ambiguous terms ("tights" → "sheer 15-denier black nylon pantyhose with no visible waistband")
- Avoid aesthetic words ("sexy", "elegant") — use geometric/material facts
- For high-prior garments (see `references/mutex-coverage.md` High-Prior list), ALSO populate `disambiguation_layers`: 3+ independent visual cues that prevent Grok from snapping the item to the nearest training-distribution peak (e.g. "upper boundary: meets pencil skirt hem at mid-thigh — NOT pantyhose, no waist band visible")

## Naming convention (hard rule)

All `persistent_grooming[].name`, `wardrobe_states.*.items[].name`, and `mutex_groups` entries MUST be **snake_case English**. These names round-trip through the Director skill's anchor map and VGAI validator. Chinese descriptive labels go in a separate `display_name` field only if needed.

Good: `red_fingernails`, `black_pencil_skirt`, `sheer_black_tights`, `closed_pumps`.
Bad: `红色指甲`, `black heels with red sole`, `RedNails`, `sheer-tights`.

## JSON safety

Any dialogue you quote in any string field must use Chinese bracket quotes 「」 — ASCII double quotes inside JSON strings break the JSON. But Skeleton rarely needs dialogue; titles and value tags don't include quoted speech.

## Anti-patterns (if you catch yourself doing any of these, stop and fix)

- Writing narrative paragraphs in any field (belongs to Script skill)
- Nodes with no `valueBefore`/`valueAfter` (every beat must turn)
- A choice that has an "obviously right" option
- An antagonist weaker than the protagonist in every dimension
- Skipping the `climax` node and hoping `ending` covers it
- Chinese names in `persistent_grooming` / `wardrobe_states.items` / `mutex_groups`
- Wardrobe items without a `covers` field (even if empty — emit `covers: []`)
- Convergence inside the same scene (branches must develop 3-5+ beats before any merge; in `bifurcating`, branches never merge at all)

## Reference files

- `references/mckee-principles.md` — the 6 hard constraints + 3 crpg additions, with examples
- `references/structure-presets.md` — linear / bifurcating / funnel / web: topology, beat targets, edge patterns
- `references/mutex-coverage.md` — when two wardrobe items are mutex; the `covers` sub-anchor taxonomy
- `references/node-types.md` — narrative / choice / check / merge / act_break / climax / ending semantics
- `references/three-modes.md` — concise / standard / detailed / extreme / poetic modes (word counts, temperature caps)
