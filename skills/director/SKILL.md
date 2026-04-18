---
name: director
description: Use when translating prose narrative (novel excerpt, story.md, scene description) into shot prompts for text-to-image generation, especially when continuity, character identity, and framing-appropriate detail matter.
---

# Director Skill

Translate narrative prose into shot prompts for text-to-image generation. Principles below apply to any story, character, or genre. Examples in `examples/`; load only when needed.

## 12 Principles

**0. Style Preamble is byte-for-byte locked** — the first section of EVERY `final_prompt` is the Visual DNA Style Preamble copied verbatim from `references/style-preamble.md`. No paraphrasing. Same preamble → same film feel across shots. This is the single highest-ROI lever for visual continuity.

**0b. Direction Layer is mandatory** — every `final_prompt` includes a Direction section that frames the shot as a candid mid-action moment (present-continuous verbs, specific muscle-level tells, photographic reference by name). See `references/direction-layer.md`. Without it, Grok defaults to stock-photo staged portraits.

**0c. Anchors before shots** — for every named character, two anchors (`body` + `face`) are rendered BEFORE any scene shot. Every scene shot's `Shot.anchor_ref` points at one of these anchors so Grok's `image_url` mode anchors the face/outfit across scenes. Pick anchor by framing:
  - `cu_face`, `ms_waist_up`, or any portrait crop → `<char>:face`
  - `three_quarter_knee_up`, `full_body_standing`, `back_reveal_walking` → `<char>:body`
  - `ws_establishing` → no anchor (subject too small)
  - Multi-character frame → use the POV character's anchor

**0d. Wardrobe visual_description is verbatim** — every wardrobe_state item in characters.json has a `visual_description` field. Copy it byte-for-byte into the Character section of `final_prompt`. NEVER paraphrase, shorten, or creatively restate. Outfit drift is ~50% caused by paraphrasing; lock the string.

1. **Base identity is region-gated too** — split into two tiers:
   - **Region-agnostic** (ALWAYS in every final_prompt): age, ethnicity, skin tone, body frame
   - **Region-specific** (VGAI-gate): hair (anchor=face/neck), eyes (anchor=face), jaw (anchor=face)
   Tight-crop framings (hand_ecu / feet_ecu / back_reveal_walking) omit face-specific base tokens so Grok doesn't render an unwanted face in the frame. See `references/provider-hardening-suffix.md` for canonical examples.

2. **Grooming travels** — persistent body marks (nail polish, tattoos, scars) always considered; states can suppress explicitly.

3. **Wardrobe is situational** — pick exactly ONE named `wardrobe_state` per shot. No default / "signature look".

4. **VGAI gate** — inject attr IFF its `anchor` region is in the framing's visible regions. See `references/framing-region-map.yaml`.

4b. **Occlusion gate** — even if an attr's anchor is visible, if another wardrobe item (that you are ALSO injecting) declares the attr's `sub_anchor` in its `covers` list, DROP the attr and record the reason `"occluded by <item>"`. Never paper over with "visible through" or "showing beneath" — that instructs the image model to open the occluding item (peep-toe where a closed pump should be, sheer where opaque should be). See `references/occlusion.md`.

5. **Default KEEP on uncertainty** — ambiguous pose visibility → keep the attr. Grok handles partial visibility. Drop only on clear evidence (pure sole / pure back / fully occluded).

6. **Fact over instruction** — attribute values are positive factual statements. See `references/rationalization-counters.md` for banned phrasings.

7. **Pose doesn't suppress** — pose can expand visibility, not shrink it. If you don't want it visible, don't write it. See `references/vgai.md` for the 9 failure modes.

8. **Mutex picks one** — physically impossible pairs resolved at assembly time, not at render time.

9. **Grok hard limits** — no Dutch angle, ≤2 characters for gaze narrative, mirror physics unreliable, aspect ratios restricted. See `references/grok-constraints.md`.

10. **Shot grammar for rhythm** — WS establishes, MS exposes, CU emotes, ECU reveals. Emotional beats get reverse reaction. See `references/narrative-heuristics.md`.

## Workflow (per shot)

```
0. BEFORE any shots: render anchors (once per run)
   - For EACH named character in characters.json:
     - render_anchor(char, "body", anchor_body_prompt)
     - render_anchor(char, "face", anchor_face_prompt)
   - Anchor prompts = STYLE_PREAMBLE verbatim + anchor-preamble variant
     + base identity + wardrobe.visual_description verbatim. Zero scene cues.

PER SHOT:

1. Read beat → classify (establishing/exposition/emotional/revelation/confrontation/transition)
2. Pick framing + pose + wardrobe_state (from character sheet)
3. Assemble candidate attrs:
   grooming ∪ state.items − state.removes
4. Gate by framing visible_regions (VGAI)
4b. Occlusion drop: for each candidate grooming G with sub_anchor S, if any
    injected wardrobe item i has S ∈ i.covers → DROP G with reason
    "occluded by i". NEVER write 'visible through' / 'showing beneath'.
5. Gate by pose visibility (Principle 5: DEFAULT KEEP)
   ⚠ Phrases like "pose-dependent", "may not be primary focus",
      "not guaranteed", "depends on framing" are NOT sufficient reasons to drop.
      Drop ONLY when the pose unambiguously hides the anchor.
6. Mutex resolve (MANDATORY pre-assembly check)
7. Pick anchor_ref for this shot (Principle 0c)
8. Assemble final_prompt — in this exact order:
   - Style Preamble (verbatim from references/style-preamble.md)
   - Character: region-agnostic base + wardrobe.visual_description verbatim
     (one block per character in frame); append disambiguation_layers for
     any high-prior garment in frame (see references/occlusion.md §garment)
   - Direction: mid-action verbs + tells + gaze + photographic reference
     (per references/direction-layer.md)
   - Scene: the ONLY free-form section — setting, props, weather, time
   - Framing: camera_framing + composition notes
9. Sanity check against rationalization-counters.md red flags + Principle 0/0b/0c/0d
10. Emit the Shot object with shot_id / camera_framing / pose / wardrobe_state_used
    / vgai_injected_attrs / vgai_dropped_attrs_with_reason / final_prompt
    / aspect_ratio / anchor_ref / characters_in_frame
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

- `references/style-preamble.md` — **Principle 0**; byte-for-byte locked style string
- `references/direction-layer.md` — **Principle 0b**; mid-action tells + photographic references
- `references/occlusion.md` — **Principle 4b**; full / partial / no occlusion branches
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
