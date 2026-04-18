# Rationalization Counters

Empirically observed rationalizations from 7+ rounds of subagent testing (~180 shots on Grok Imagine Pro, 2026-04-17). Each produced a specific failure; each has an explicit counter.

## Banned phrasings in attribute values

These cascade across anchor regions and force the model to paint wrong things. **Rewrite as positive factual.**

| Banned | Why it fails | Use instead |
|--------|--------------|-------------|
| `NOT bare skin on feet` | Model paints red / dark on sole, heel — wherever "not bare" applies | `feet in continuous sheer black stocking material` (state the presence, not the absence) |
| `NOT exposed` / `hidden from view` | Triggers Mode 6 Wardrobe Modification — model opens clothing to expose | Drop the attribute entirely if framing doesn't show it |
| `never visible` / `must not appear` | Same cascade | Drop the attribute |
| `every toe outlined` / `on each toe` | Positional micromanagement → red spreads to sole + heel in sole-view shots | `red toenail polish on her toenails` (minimal fact) |
| `at the toe tips` | Forces red at specific location; when toes not in frame, cascades | Same — minimal fact |
| `hint of red through the sheer` | Prescriptive layering → double-injection conflict | Two independent facts: `red toenail polish` + `sheer black stocking`. Model layers naturally. |
| `visible as a hint of color through` | Same | Same |
| `covered by shirt` / `hidden under coat` | Mode 6: model opens the cover | Drop the attribute |

## Rule: cross-anchor continuity cues for layered garments

> When an attribute covers multiple body regions and VGAI-gates one out (e.g., `leg_pantyhose` at anchor:leg is dropped for a feet_ecu shot that keeps only `stocking_toes` at anchor:foot), the remaining attr must **state its continuity above the frame**, or the model interprets it as a localized garment (pantyhose → ankle sock).
>
> **Rationalization to avoid:** "The feet_ecu doesn't show legs so I only mention stocking on foot." → Model renders an ankle sock.
>
> **Fix:** In `stocking_toes.value`, include positive fact: `"feet in sheer black pantyhose hosiery that continues seamlessly up past the ankle onto the leg above the frame"`. States continuity factually without using "NOT ankle sock" negation.
>
> **Generalizable:** Whenever a wardrobe item spans ≥2 body regions and VGAI drops the connective region, the surviving region's value needs a "continues past the frame" cue. Applies to: pantyhose/tights, long gloves (hand vs arm), turtleneck (neck vs torso), etc.

## Rule: no absolute negations

> In attribute `value` fields, every word must be a positive factual statement about what IS, not what IS NOT.
>
> If you find yourself writing "NOT", "never", "without", "hidden", "covered by" — **rewrite or drop**.

## Rule: no prescriptive layering

> When two attrs survive VGAI at the same anchor (e.g., `red_toenails` grooming + `stocking_toes` wardrobe on `foot`), inject both as independent factual statements. Do NOT add connective phrasing like "visible through", "showing beneath", "hint of red at".
>
> The model's aesthetic prior handles natural layering. Explicit layering instructions create double-rendering conflicts.

## Rule: default KEEP on ambiguous pose visibility

> When a pose might or might not reveal an attribute's anchor (side profiles, 3/4 angles, partial occlusion), **keep the attribute**. The model will render it where anatomy allows and skip it where not.
>
> Drop only on unambiguous evidence (pure sole-of-foot view; hair explicitly covering entire ear; character fully behind an opaque object).
>
> **Rationalization to avoid:** "I'll drop it to be safe." This is false safety. Over-injection produces bounded failure modes (framing expansion ≈ bigger shot). False-drop silently loses signature character detail.

## Rule: no default wardrobe state

> Every shot's `wardrobe_state` is a conscious choice. "Signature look" is banned.
>
> **Rationalization to avoid:** "The character has a default outfit." No. Each scene's narrative context determines the state; the sheet has no default. If the story implies a specific outfit, it maps to ONE named state.

## Rule: no workaround suppressors

> Pose does not suppress. Covering does not suppress. Framing does not suppress. Lighting does not suppress.
>
> If you don't want an attribute visible: **drop it from injection**. Do not write it and hope pose/cover/frame/light will hide it — the model will override pose/cover/frame/light to make it visible (Modes 1, 6, 7, 8).

## Rule: character sheet never hard-coded in skill

> A character's persistent_grooming and wardrobe_states live in a project-level character sheet file, NOT in the Director skill itself.
>
> **Rationalization to avoid:** "This story uses these states, I'll add them to the skill's template." No. The skill's schema is generic. Put the populated sheet in `projects/<project>/character-sheets/<name>.yaml`.

## Rule: one anchor per attr

> If an attribute covers two body regions (e.g., a one-piece that covers torso AND legs; pantyhose stocking over both leg AND foot), **split into two attrs**, each with a single anchor. Otherwise VGAI can't gate it correctly when framing isolates one region.
>
> **Rationalization to avoid:** "I'll anchor it to the most important region." Then when the other region is the only one in frame, VGAI drops everything — bare region defaults in. Split instead.

## Red-flag detection self-check (before emitting any prompt)

Scan the final_prompt text for:
- Any word from the Banned phrasings table above → rewrite
- Strings `NOT `, `never`, `not exposed`, `hidden`, `covered by`, `despite the` → rewrite or drop
- `her signature`, `her default`, `her usual` → replace with a named wardrobe_state
- `Dutch angle`, `tilted camera`, `canted horizon` → remove (Grok ignores)
- `3 characters looking at each other`, `gaze triangle` → reduce to ≤2 or make group decorative
- Aspect ratio not in `{1:1, 3:2, 4:3, 16:9, 19.5:9, 9:16, 3:4}` → fix to nearest

## Pose phrase disambiguation

### "stepping out of X"

- **Correct interpretation**: leaving X as a place/situation (wardrobe UNCHANGED)
- **Wrong interpretation**: removing X as a garment (wardrobe changed)

Rationale: "stepping out of an office", "stepping out of a cab", "stepping out of high-heels onto pavement" — the English idiom means exiting the location context. It does NOT mean removing wardrobe items unless the surrounding prose explicitly describes undressing (e.g., "她踢掉高跟鞋", "slipping off her heels").

When the pose text uses "stepping out of", "walking out of", "leaving" — keep all wardrobe items in the injected set. Only drop a wardrobe item when the prose explicitly describes its removal.

### Similar phrases to watch for

- "slipping into" — entering a space, not putting on clothes
- "walking out of" — leaving a place
- "getting out of" — exiting (car/bed/elevator)

If you're uncertain whether a phrase implies undressing, default to keeping the wardrobe — prose must explicitly say "removed", "undid", "unzipped", "slipped off" before dropping an item.
