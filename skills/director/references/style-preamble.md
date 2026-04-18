# Style Preamble — Visual DNA Layer 1 (byte-for-byte locked)

> **Rule**: Every shot's `final_prompt` — and every anchor render — MUST begin with the Style Preamble below, copied verbatim. Zero paraphrasing. Zero reordering. Zero omissions.

This is the technical + aesthetic base that makes every image feel like a frame from the same film. Without a byte-identical preamble across shots, Grok Imagine's random-seed latent initialization drifts — different color grades, different grain levels, different lens characters per shot.

## The preamble (copy this exact string)

```
Modern Japanese seinen manga / anime illustration, digital painterly style with
cel-shaded highlights and confident expressive line work. Cinematic noir
color grade: saturated teal shadows, crimson accents, rich deep blacks, subtle
amber practical lights. Slight organic film grain. Anamorphic 2.39 lens
philosophy with gentle horizontal flare on bright points. Shallow depth of
field separating subject from wet urban atmosphere. Single warm key light with
cool ambient fill. Volumetric haze where street-level neon catches rain.
Composition: cinematic — rule of thirds bias, off-center subject, negative
space lets the setting breathe. Frame reads as a still from a mid-2020s
Chinese urban noir film rather than a stock illustration.
```

## How to use

1. Begin the `final_prompt` of every shot with this block verbatim (no rewording, even minor).
2. Follow with the Character Sheet section (base identity + wardrobe visual_description strings copied verbatim from characters.json).
3. Follow with the Direction Layer action moment (see `direction-layer.md`).
4. Follow with the scene-specific setting description (the ONLY free-text section).
5. End with the framing directive (`camera_framing` + any composition notes).

Prompt skeleton:

```
{STYLE_PREAMBLE verbatim}

Character: {base identity + wardrobe visual_description verbatim}

Direction: {mid-action tell vocabulary per Direction Layer}

Scene: {setting, props, weather, time of day — the varying section}

Framing: {camera_framing + any composition notes}
```

## Why fixed string matters

Round 1 testing (2026-04-17) showed that when each shot's preamble was re-phrased by the Director LLM, Grok's style drifted wildly — some shots came out photorealistic, some came out anime, some came out illustration. Round 2 locked the preamble verbatim across 5 shots and style consistency jumped to ~90%. **This is the single highest-ROI intervention for visual continuity.**

## Anchor preamble variant

For `render_anchor` calls specifically, use the same preamble but append:

```
Anchor shot for cross-scene character consistency. Neutral pose, minimal
background (muted gradient or plain studio wall), subject centered, full
face clearly readable, outfit details crisply visible, even lighting
preserving color accuracy.
```

This keeps the anchor's visual noise low so its latent representation transfers cleanly into subsequent scene shots.
