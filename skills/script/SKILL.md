---
name: script
description: Use when generating Chinese prose for one beat — given the beat's metadata (synopsis, valueBefore, valueAfter, wardrobe_state, targetWordCount), the story controlling idea, character sheets, and adjacent-beat context. Emits game-ready narrative prose that respects McKee's soft constraints + daisy's Game Writing Rules + Anti-Melodrama. Not for structure generation (that's Skeleton) or shot design (that's Director).
---

# Script Skill

Write narrative prose for a single beat. Game-ready (the reader is a player, not a novel reader). Chinese by default, unless brief explicitly asks otherwise.

## Core principle

**Show through action and dialogue, not through description.** If you can't see the character DOING something or SAYING something, you're writing a paragraph instead of a scene. Stop. Rewrite.

## Inputs (what the agent passes you)

- **beat metadata** from `story.json`: `id`, `type`, `synopsis`, `valueBefore`, `valueAfter`, `wardrobe_state`, `targetWordCount`, `depends_on`
- **story meta**: `controllingIdea`, `contentLength`, `detailRichness`, `structure`, `poeticMode`
- **character sheets** — names + base + persistent_grooming + the wardrobe_state this beat uses
- **prior-beat summaries** — one-liners of beats in the path so far (for continuity; never reproduce verbatim)

## The 4 soft McKee constraints (apply to every beat)

These are softer than Skeleton's hard constraints because by the time Script runs, Skeleton already decided structure. Script's job is to **realize** the decided value shift in prose:

1. **Value Shift** — the prose MUST turn valueBefore → valueAfter. If the scene ends without that turn, you haven't written the beat.
2. **Progressive Complication** — within the beat, stakes tighten; within the story arc, this beat raises tension vs the previous beat in the same path.
3. **The Gap** — outcomes differ from the protagonist's expectation. "She tried X and it worked as planned" is a failed beat.
4. **Three Levels of Conflict** — at least two of {inner / personal / extra-personal} active in the scene.

## The 7 Game Writing Rules (daisy V6, non-negotiable)

Read `references/game-writing-rules.md` for full examples. Summary:

1. **Player as agent** — protagonist DOES things in active voice.
2. **Show the world through interaction** — no 4-sentence atmospheric paragraphs before something happens.
3. **Keep it punchy** — max 2-3 sentences of description before dialogue / discovery / decision.
4. **Concrete game information** — every detail is either actionable or foreshadows something actionable.
5. **Dialogue is gameplay** — NPC dialogue reveals info / presents dilemmas / creates tension, never exposition.
6. **Tension through stakes, not prose** — "氧气还剩三小时" beats any purple prose.
7. **Setup nodes are active too** — even world-building scenes show the PC doing something.

## Anti-Melodrama rules (daisy V6, non-negotiable)

Read `references/anti-melodrama.md` for examples. Summary:

- **Don't name emotions directly.** Show through action.
  - Bad: "她感到恐惧。"
  - Good: "她的指节在门把上发白。"
- **Max ONE physical sensation per beat.** Pick the strongest. Don't stack heartbeat + trembling + shortness-of-breath.
- **No overwrought metaphors.** Plain, precise language. "像电影镜头" is a crime.
- **Not every scene is a crisis** — include humor, awkwardness, mundane texture. Constant peak intensity = no peaks.

## Mode dispatch (read `references/three-modes-script.md` before writing)

Three orthogonal axes control the output shape:

- **`detailRichness`**: concise / standard / detailed / extreme → per-beat word count + sentence style
- **`contentLength`**: short / medium / long → affects nothing directly at Script stage (Skeleton already used it for beat count; ignore here)
- **`poeticMode`**: true / false → keyword interpretation + temperature tier

Pick the right style profile for `detailRichness`:

| tier | word count | sentences | dialogue |
|------|-----------:|----------:|---------:|
| concise | ~1500 | 2-3 per ~100-word stanza | minimal |
| standard | ~2200 | 4-5 per stanza | 1-2 exchanges |
| detailed | ~2500 | 6-8 per stanza | 2-3 exchanges |
| extreme | 40-80 per beat | short, punchy | optional |

Exact word budgets in `references/three-modes-script.md`. Never exceed `beat.targetWordCount` from the skeleton; use it verbatim.

## Workflow per beat

```
1. Read beat metadata + story meta from agent input
2. Read controllingIdea + prior-beat summaries; understand where in the arc you are
3. Look up the per-tier style profile in references/three-modes-script.md
4. Draft the prose:
   - Open with an action (not a description)
   - Keep description ≤ 2-3 sentences before something happens
   - Use dialogue to carry information / dilemma / tension
   - Stage the value shift as a concrete turning point
   - Close on a beat that hands the value cleanly to the next scene
5. Self-check against the checklist (below)
6. If it fails any check, rewrite before emitting
7. Emit via write_beat_prose tool — one call per beat
```

## Self-check before emit

- Does the prose turn valueBefore → valueAfter explicitly (not just conceptually)?
- Is the protagonist DOING something, not passively observing?
- Is every dialogue line doing narrative work (info / dilemma / tension)?
- Zero banned phrases? (see `references/banned-phrases.md` — "仿佛电影镜头", "她的签名款", "如往常般", etc.)
- Max ONE physical sensation per beat?
- Zero emotion names verbatim (恐惧 / 愤怒 / 悲伤 used as bare nouns)?
- Chinese bracket quotes 「」 for all dialogue (never ASCII `""`)?
- Prose length within ±5% of beat.targetWordCount?
- If `poeticMode=true`: metaphors are present but underlying action still advances stakes
- If `poeticMode=false`: keywords appear as concrete story elements (objects, characters, locations), not as metaphors

If any answer is no, rewrite.

## Chinese dialogue convention

All quoted speech uses Chinese bracket quotes: 「」 for outer, 『』 for nested inner. ASCII double quotes `""` anywhere inside the prose will break downstream tooling if the agent ever serializes the text as JSON.

- Correct: `「你也感觉到了吗？」她压低声音。`
- Wrong: `"你也感觉到了吗？"她压低声音。`

## Reference files

- `references/game-writing-rules.md` — 7 rules with good/bad examples
- `references/anti-melodrama.md` — 4 rules with good/bad examples + restraint heuristics
- `references/three-modes-script.md` — per-tier word counts, style rules, dialogue density
- `references/poetic-interpretation.md` — how to treat keywords in poetic vs literal mode
- `references/banned-phrases.md` — exhaustive list of forbidden 文青腔 / 出戏腔 / 煽情腔 phrases
