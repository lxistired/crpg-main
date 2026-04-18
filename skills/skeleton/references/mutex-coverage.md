# Mutex Groups & Wardrobe Coverage

These rules govern the character sheet fields `wardrobe_states[*].items[*].covers` and `mutex_groups`. They are physical / geometric rules — the body occupies 3D space, some items occlude others — NOT story-specific tastes.

The Director skill's VGAI validator enforces these at shot level. If Skeleton emits wrong coverage or wrong mutex, the Director agent will throw and everything downstream breaks.

## Anchor / sub_anchor taxonomy

Anchors are body regions. Sub_anchors are named parts within an anchor. Use exactly this vocabulary — **do NOT invent variants** (e.g. use `toes`, not `toenails`; use `lips`, not `lipstick_zone`).

| anchor | sub_anchors |
|--------|-------------|
| face | eyes, lips, lashes, brows, cheeks |
| ear | earlobe |
| neck | throat, collarbone |
| hand | fingernails, palm, wrist, back_of_hand |
| torso | front, cleavage, back (alias: torso_back), waist_front, waist_back, shoulders |
| leg_upper | thigh_front, thigh_back, knee |
| leg | shin, calf, ankle |
| foot | toes, foot_top_inner, foot_top_outer, heel, sole |

When in doubt, use the anchor only (omit sub_anchor). Don't invent vocabulary.

## Grooming → sub_anchor mapping (standard library)

When emitting `persistent_grooming` entries, pick sub_anchor from this table. These are the physical regions grooming lives in — NOT the grooming name itself.

| grooming kind | anchor | sub_anchor |
|---------------|--------|------------|
| nail polish on fingers (`red_fingernails`, `french_manicure`, etc.) | hand | `fingernails` |
| nail polish on toes (`red_toenails`, `black_toenails`, etc.) | foot | `toes` |
| lipstick / lip gloss / lip tint | face | `lips` |
| eye makeup / eyeliner / mascara accents | face | `eyes` |
| lash extensions | face | `lashes` |
| eyebrow tint / shaped brows | face | `brows` |
| blush / cheek contour | face | `cheeks` |
| ear piercing / stud | ear | `earlobe` |
| neck tattoo / necklace-resting-on-collarbone / chains | neck | `throat` or `collarbone` |
| wrist tattoo / bracelet | hand | `wrist` |
| back-of-hand tattoo | hand | `back_of_hand` |
| décolletage tattoo / chest scar | torso | `cleavage` or `front` |
| shoulder tattoo | torso | `shoulders` |
| back tattoo | torso | `torso_back` |
| thigh tattoo (front) | leg_upper | `thigh_front` |
| thigh tattoo (back) | leg_upper | `thigh_back` |
| knee scar / knee tattoo | leg_upper | `knee` |
| calf tattoo | leg | `calf` |
| shin scar | leg | `shin` |
| ankle tattoo / anklet | leg | `ankle` |
| foot-top tattoo (inner side) | foot | `foot_top_inner` |
| foot-top tattoo (outer side) | foot | `foot_top_outer` |

**Important**: the sub_anchor is the *region*, not the *grooming object*. `red_toenails` is a grooming name (what it IS); `toes` is the sub_anchor (where it LIVES). The validator matches sub_anchor against wardrobe `covers` for occlusion — so using `toenails` as a sub_anchor breaks occlusion detection because no shoe's `covers` list contains `toenails` (they contain `toes`).

## The `covers` field on wardrobe items

Every wardrobe item declares which sub_anchors it **fully occludes** (grooming attrs anchored there become invisible). If an item occludes only partially, **do NOT list** that sub_anchor in `covers` (Director will inject the attr with a "visible on non-occluded part" phrasing). If an item occludes nothing, emit `covers: []`.

## Footwear coverage table (reference — emit these for typical items)

| wardrobe item | anchor | covers |
|---------------|--------|--------|
| `closed_pumps` / `closed_stilettos` / `oxfords` | foot | `[toes, foot_top_inner]` |
| `peep_toe_pumps` | foot | `[foot_top_inner]` (toes visible through opening) |
| `sandals` / `strappy_heels` | foot | `[]` |
| `ballet_flats` | foot | `[foot_top_inner]` |
| `ankle_boots` | foot | `[toes, foot_top_inner, foot_top_outer, ankle]` |
| `thigh_high_boots` | foot (+ leg implicit) | `[toes, foot_top_inner, foot_top_outer, ankle, shin, calf]` |
| `combat_boots` | foot | `[toes, foot_top_inner, foot_top_outer, ankle]` |

## Hosiery coverage table

| wardrobe item | anchor | covers |
|---------------|--------|--------|
| `sheer_black_tights` / `sheer_pantyhose` | leg | `[]` (see rule below) |
| `opaque_black_tights` / `opaque_pantyhose` | leg | `[thigh_front, thigh_back, knee, shin, calf]` |
| `fishnet_stockings` | leg | `[]` |
| `thigh_high_stockings` | leg | `[shin, calf]` only |
| `socks_ankle` | foot | `[foot_top_inner, foot_top_outer]` |

**Sheer-tights rule**: `sheer_*_tights` items have `covers: []` because the underlying grooming (e.g. skin color, leg tattoo, toenail polish) is still rendered visible through transparent fabric. Grok Imagine handles this correctly when the Director describes the underlying attr WITHOUT a "through the fabric" rationalization.

## Garment coverage table

| wardrobe item | anchor | covers |
|---------------|--------|--------|
| `pencil_skirt` / `mini_skirt` | torso | `[waist_front, waist_back]` (hip region) |
| `maxi_dress` / `long_gown` | torso | `[waist_front, waist_back]` and conceptually the legs (but legs are not in torso anchor's sub_anchors, so list only torso's) |
| `strapless_top` | torso | `[front]` only (leaves cleavage, shoulders) |
| `off_shoulder_top` | torso | `[front]` only (leaves shoulders, cleavage) |
| `bra` | torso | `[cleavage]` |
| `leather_gloves` | hand | `[fingernails, back_of_hand, palm]` |
| `fingerless_gloves` | hand | `[back_of_hand, palm]` (fingernails still visible) |

## `mutex_groups` — pairs that physically cannot both render

Only list pairs where both items would occupy the same visual slot such that only one can be drawn at a time. This is RARE.

**Valid mutex examples:**
- `[bare_legs, opaque_tights]` — alternative states of the same anchor region
- `[bare_feet, ankle_boots]` — same
- `[short_hair_bob, long_ponytail]` — alternative hair states

**NOT valid mutex (these layer, don't conflict):**
- `[sheer_tights, ankle_boots]` — tights visible above boot top, boots visible below → layer
- `[long_gown, any_shoes]` — gown hides feet visually but shoes are a separate anchor → layer (Director handles visibility)
- `[fishnet_stockings, combat_boots]` — fishnet visible at thigh above boot top → layer
- `[red_fingernails, leather_gloves]` — covered case, not mutex. Use the `covers` field.

**Rule of thumb**: if one item *occludes* another, use `covers`. If two items *can't both exist on the body* (like bare vs clothed), use `mutex_groups`.

## Validity checks (Skeleton must self-check before emit)

- Every wardrobe item has a `covers` field (possibly empty, but present).
- Every `mutex_groups` pair has both members appearing verbatim as `name` in this character's own `persistent_grooming` or some `wardrobe_states[*].items[*]`.
- Never reference anchors as mutex members (`[face, leg]` is nonsense).
- Never reference items belonging to another character.
- `bare_X` entries (e.g. `bare_legs`, `bare_feet`) are valid mutex members ONLY when they also appear as a named wardrobe item in at least one state.
