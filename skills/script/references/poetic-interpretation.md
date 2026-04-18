# Poetic vs Literal Keyword Interpretation

Script inherits `poeticMode` from story meta (Skeleton decides; Script respects). This controls how the brief's keywords get woven into prose.

## poeticMode = true (default for crpg)

**Treat keywords as atmospheric metaphors, not literal plot elements.**

A keyword like `玻璃` might become:
- a fragile relationship ("他们之间那层透明的东西越来越薄")
- a mirror of the self ("她看见自己在酒杯上的倒影")
- a barrier between worlds ("她的指尖隔着玻璃碰到他的")

A keyword like `雨` might become:
- grief ("雨下了三天")
- liminality ("她走出那扇门，雨把她和刚才的房间隔开")
- renewal / cleansing

**Temperature equivalence** (daisy scale → crpg models):
- Daisy Claude: 0.9
- crpg M1 cap: **0.8** (per memory `feedback_crpg_poetic_temperature.md` — higher temperatures started breaking structure on multi-model tests)

### Rule in poetic mode

Metaphors are ALLOWED but must still **earn their place**. The anti-melodrama rules still apply:
- Don't name emotions via metaphor either (`心如刀绞` is disguised emotion-naming, still banned)
- Max ONE metaphorical device per paragraph
- The metaphor must reveal something concrete (visual, tactile, relational) that literal description couldn't

## poeticMode = false

**Treat keywords as concrete plot elements. Each keyword appears directly.**

- `玻璃` → there's an actual glass object in the story (a glass window, a broken glass, a glass eye)
- `雨` → actual rain plays a visible role (a rainstorm, wet streets, a character drenched)

**Temperature**: 0.7.

### Rule in literal mode

- Write "like a game script, not poetry" (daisy V6 verbatim directive)
- Concrete actions, specific objects, real dialogue
- Metaphors strongly discouraged — only for dialogue where a character speaking a metaphor reveals something about that character

## How the agent should detect the mode

Story meta from Skeleton contains `poeticMode: true|false`. Read it before writing prose.

If the story meta lacks `poeticMode` (shouldn't happen but robustness), default to `true` — crpg's audience skews adult-noir where atmospheric writing dominates.

## Boundary cases

### Keyword is already concrete in brief

Brief says "黑丝 + 红色指甲". Even in poetic mode, these are clothing/grooming specifics attached to a named character — they stay concrete (appear in character's wardrobe_states + persistent_grooming via Skeleton). Poetic mode applies to abstract keywords (`雨`, `玻璃`, `深夜`), not to character attribute specifications.

### Keyword is a place / person

"上海静安区" or "Kai" (a named character) — always concrete regardless of mode. Poetic interpretation doesn't dissolve named entities into metaphor.

### Keyword is an emotion word

Brief says "失控". In poetic mode, this becomes an undercurrent — Script writes scenes where characters lose control through action, never by narrating "她感到失控". In literal mode, same thing — "失控" is a value axis Skeleton already encoded as valueAfter, Script doesn't label it.

## Self-check

- If poetic: did I weave the keywords as atmospheric threads? Did I also keep them grounded per anti-melodrama rules?
- If literal: did every keyword appear as a concrete story element (object, character, location, event)?
- Either way: is the protagonist still DOING things (Rule 1)?
