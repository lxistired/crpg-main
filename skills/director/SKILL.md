---
name: director
description: Use when translating prose narrative (novel excerpt, story.md, scene description) into shot prompts for text-to-image generation, especially when continuity, character identity, and framing-appropriate detail matter.
---

# Director Skill

Translate narrative prose into shot prompts for text-to-image generation. Principles below apply to any story, character, or genre. Examples in `examples/`; load only when needed.

## 10 Principles

1. **Base identity is region-gated too** — split into two tiers:
   - **Region-agnostic** (ALWAYS in every final_prompt): age, ethnicity, skin tone, body frame
   - **Region-specific** (VGAI-gate): hair (anchor=face/neck), eyes (anchor=face), jaw (anchor=face)
   Tight-crop framings (hand_ecu / feet_ecu / back_reveal_walking) omit face-specific base tokens so Grok doesn't render an unwanted face in the frame. See `references/provider-hardening-suffix.md` for canonical examples.

2. **Grooming travels** — persistent body marks (nail polish, tattoos, scars) always considered; states can suppress explicitly.

3. **Wardrobe is situational** — pick exactly ONE named `wardrobe_state` per shot. No default / "signature look".

4. **VGAI gate** — inject attr IFF its `anchor` region is in the framing's visible regions. See `references/framing-region-map.yaml`.

5. **Default KEEP on uncertainty** — ambiguous pose visibility → keep the attr. Grok handles partial visibility. Drop only on clear evidence (pure sole / pure back / fully occluded).

6. **Fact over instruction** — attribute values are positive factual statements. See `references/rationalization-counters.md` for banned phrasings.

7. **Pose doesn't suppress** — pose can expand visibility, not shrink it. If you don't want it visible, don't write it. See `references/vgai.md` for the 9 failure modes.

8. **Mutex picks one** — physically impossible pairs resolved at assembly time, not at render time.

9. **Grok hard limits** — no Dutch angle, ≤2 characters for gaze narrative, mirror physics unreliable, aspect ratios restricted. See `references/grok-constraints.md`.

10. **Shot grammar for rhythm** — WS establishes, MS exposes, CU emotes, ECU reveals. Emotional beats get reverse reaction. See `references/narrative-heuristics.md`.

## Workflow (per shot)

```
1. Read beat → classify (establishing/exposition/emotional/revelation/confrontation/transition)
2. Pick framing + pose + wardrobe_state (from character sheet)
3. Assemble candidate attrs:
   grooming ∪ state.items − state.removes
4. Gate by framing visible_regions (VGAI)
5. Gate by pose visibility (Principle 5: DEFAULT KEEP)
   ⚠ Phrases like "pose-dependent", "may not be primary focus",
      "not guaranteed", "depends on framing" are NOT sufficient reasons to drop.
      Drop ONLY when the pose unambiguously hides the anchor (pure sole view,
      hair fully covers ear, character fully behind opaque object).
      If ambiguous → KEEP.
6. Mutex resolve (MANDATORY pre-assembly check):
   For each pair in character_sheet.mutex_groups, if BOTH members are in the
   surviving attr set, pick ONE based on which is visually dominant in the
   pose context (e.g., shoes on feet → keep shoes, drop stocking_toes).
   Never emit two mutex-conflicting attrs in vgai_injected_attrs.
7. Assemble prompt: ANIME_PREAMBLE + base + pose + scene + framing_directive + gated_attrs
   Note: base identity (hair/skin/eye/face/age) goes in the base segment,
   NOT in vgai_injected_attrs — base is always injected as part of the
   character preamble, it is not a gated attribute.
8. Sanity check against rationalization-counters.md red flags
```

## Red flags — if any appear, STOP and fix

- Prompt contains "NOT X" / "never Y" / "not exposed" in attr text
- Prompt contains "visible through" / "hint of red at tips" / "every toe outlined" (prescriptive layering)
- Wardrobe says "her signature look" / "usual outfit" (no named state)
- Dutch angle word anywhere
- >2 characters with explicit gaze interaction
- Aspect ratio not in Grok's allowed list
- Attribute injected whose anchor isn't in framing

## Output format

```json
{
  "shot_id", "scene_ref", "beat_type", "camera_framing", "aspect_ratio",
  "pose", "wardrobe_state_used",
  "vgai_injected_attrs", "vgai_dropped_attrs",
  "final_prompt"
}
```

Emit JSON array. That's the deliverable.

## Reference files (load when applying the principle)

- `references/vgai.md` — VGAI rule + 9 failure modes
- `references/framing-region-map.yaml` — framing→visible regions lookup
- `references/shot-grammar.yaml` — shot vocabulary + reliability tags
- `references/grok-constraints.md` — hard limits + allowed aspect ratios
- `references/character-sheet-schema.yaml` — schema for input character sheets
- `references/narrative-heuristics.md` — prose→shot decomposition
- `references/rationalization-counters.md` — known rationalizations + counters
- `references/provider-hardening-suffix.md` — optional system-prompt suffix for throughput-optimized backends (e.g. Groq-hosted) whose default VGAI compliance is weak
- `examples/worked-example.md` — one minimal worked example
- `examples/character-sheet-example.yaml` — one minimal populated sheet

No default character sheet is bundled. Pass one as input.
