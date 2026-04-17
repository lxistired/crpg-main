# Worked Example — Story Paragraph to 4-Shot Decomposition

## Input narrative

> Lian stood at her kitchen window watching the rain. She hadn't moved in
> twenty minutes. The knife was in her hand. She hadn't realized she was
> still holding it.

## Input character sheet (abridged)

```yaml
id: lian
base: ["early 30s", "Chinese", "shoulder-length black hair", "pale skin"]
wardrobe_states:
  - id: home_morning_alone
    context: "In her own home, alone, casual"
    items:
      - attr: red_fingernails
        anchor: hand
        value: "glossy red fingernail polish"
      - attr: oversized_cashmere_sweater
        anchor: torso
        value: "cream-colored oversized cashmere sweater"
        neckline_hint: "soft cashmere collar at neck"
      - attr: bare_legs
        anchor: leg
        value: "bare legs"
      - attr: bare_feet
        anchor: foot
        value: "bare feet (no polish)"
```

## Director's decomposition

**Beat analysis**:
- Beat 1: **Exposition + atmosphere** — she stands at the window, watching rain (setup mood)
- Beat 2: **Revelation** — we see she has a knife
- Beat 3: **Emotional** — she realizes she's holding it

So 3 beats. 3 well-paced shots:

### Shot 1 — Atmosphere / Exposition

```json
{
  "shot_id": "01_kitchen_window_ms",
  "beat_type": "exposition",
  "camera_framing": "ms_waist_up",
  "aspect_ratio": "3:2",
  "pose": "Lian standing at the kitchen window, hands at her sides (not visible in frame below waist), in 3/4 profile looking out, face soft and absent",
  "wardrobe_state_used": "home_morning_alone",
  "vgai_injected_attrs": ["oversized_cashmere_sweater"],
  "vgai_dropped_attrs": ["red_fingernails", "bare_legs", "bare_feet"],
  "final_prompt": "[ANIME_PREAMBLE]\n\nLian, early 30s, Chinese, shoulder-length black hair, pale skin. She wears a cream-colored oversized cashmere sweater with soft cashmere collar at neck. MEDIUM SHOT, waist-up, 3:2 aspect. Lian stands at her kitchen window in a small Chinese apartment. She is in 3/4 profile, looking out at heavy rain on the glass. Her face is soft and absent, lost in thought. Warm indoor light vs cool grey rain-light from the window. Teal shadows and warm amber accents. Cinematic seinen anime style."
}
```

Why these choices:
- **MS waist-up** because hands are at her sides (below frame) — we don't want to show the knife yet (that's beat 2)
- **Dropped red_fingernails** because hands are below frame per VGAI
- **Dropped bare_legs / bare_feet** because MS waist-up doesn't include legs/feet
- **Kept sweater + neckline_hint** because torso is in frame and face CU adjacent needs a neck/collar cue

### Shot 2 — Revelation ECU insert

```json
{
  "shot_id": "02_knife_hand_ecu",
  "beat_type": "revelation",
  "camera_framing": "hand_ecu",
  "aspect_ratio": "4:3",
  "pose": "Her right hand is down at her side, loosely gripping a kitchen knife blade down. We see only hand, knife, and a sliver of her sweater cuff.",
  "wardrobe_state_used": "home_morning_alone",
  "vgai_injected_attrs": ["red_fingernails"],
  "vgai_dropped_attrs": ["oversized_cashmere_sweater", "bare_legs", "bare_feet"],
  "final_prompt": "[ANIME_PREAMBLE]\n\nEXTREME CLOSE-UP INSERT. A woman's right hand with glossy red fingernail polish, loosely gripping the handle of a kitchen paring knife, blade pointed down. Only the hand, knife, and a sliver of cream-colored cashmere sleeve at the edge of frame are visible. Shallow depth of field, knife edge sharp, background dissolving into soft blur. 4:3 aspect."
}
```

Why:
- **ECU hand** puts the knife front-and-center — revelation beat delivered as insert
- **Only red_fingernails** (VGAI gated)
- "Sliver of cashmere sleeve" at edge — visual continuity to shot 1

### Shot 3 — Emotional close

```json
{
  "shot_id": "03_lian_cu_face_realization",
  "beat_type": "emotional",
  "camera_framing": "cu_face",
  "aspect_ratio": "4:3",
  "pose": "Lian's head and shoulders, turning slightly down to look at her own hand (which is off-screen below). Eyes lowered, lips parted in a faint 'oh' of slow realization.",
  "wardrobe_state_used": "home_morning_alone",
  "vgai_injected_attrs": ["oversized_cashmere_sweater"],
  "vgai_dropped_attrs": ["red_fingernails", "bare_legs", "bare_feet"],
  "final_prompt": "[ANIME_PREAMBLE]\n\nLian, early 30s, Chinese, shoulder-length black hair, pale skin. She wears a cream-colored oversized cashmere sweater with soft cashmere collar at neck. CLOSE-UP face and upper shoulders. She is turned slightly downward, looking at her own hand (off-screen below frame). Her eyes are lowered, long lashes cast shadow on her cheek, lips parted in a faint soft 'oh' of slow dawning realization. Soft window side-light. 4:3 aspect. The moment she notices what's in her hand."
}
```

Why:
- **CU face** delivers the emotional beat
- **Pose**: her head tilt and eye direction lock the reader onto "she's seeing her hand" (off-screen), connecting to shot 2
- **sweater + neckline_hint** kept because torso is partially visible at frame bottom
- **Dropped red_fingernails** (hand off-screen)

## What this worked example shows

- 3 narrative beats → 3 shots (1:1 mapping when beats are compact)
- Shot size variation: MS → ECU → CU (moves the eye, punctuates)
- VGAI gating per shot (different attrs dropped each time)
- The ECU insert "carries" the knife reveal — efficient storytelling
- Eyeline match across shots 2→3 (hand off-screen below = her looking down at hand)

This is the Director's core skill: read prose, design shots, gate attributes, assemble prompts.
