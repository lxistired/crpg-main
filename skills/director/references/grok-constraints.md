# Grok Imagine Pro — Hard Constraints

What Grok Imagine Pro CAN and CANNOT do. Follow strictly; do not waste generations violating these.

## API parameters

- Endpoint: `https://api.x.ai/v1/images/generations`
- Model: `grok-imagine-image-pro` ($0.07 / image)
- `n`: 1
- `response_format`: `b64_json` recommended (direct bytes) or `url`
- `resolution`: `2k` (only value accepted for anime-style output)
- `aspect_ratio`: see below

## Allowed aspect ratios

Grok accepts these and NOTHING else. If you want a weird ratio, pick the closest:

| Ratio | Use for |
|-------|---------|
| `1:1` | Portrait symmetry, square social-media format |
| `3:2` | Classic photo, narrative medium scenes |
| `4:3` | Old TV / retro, bounded compositions |
| `16:9` | Cinematic widescreen, default for dialogues/2-shots |
| `19.5:9` | Ultra-widescreen / anamorphic feel (use for `21:9` intent) |
| `9:16` | Vertical, mobile, full-body standing shots |
| `3:4` | Vertical portrait |

Attempts to use `4:5` or `5:4` or `2:1` → **API returns 422**. Fail fast.

## What Grok Imagine Pro DOES well

- Anime / seinen / Japanese manga aesthetic (anime preamble locks it)
- 2-person gaze interaction (mutual, asymmetric, OTS, profile)
- Shot grammar: WS / MS / CU / ECU / low angle / high angle / OTS / back reveal / POV
- Gaze-at-object (phone, mirror, document)
- Explicit NOT-X-YES-Y pattern for wardrobe (ankle socks NOT thigh-high)
- Crowd (5 characters in frame readable and distinct)
- Specific Chinese text in small display (phone screens)
- Anchor + image_url carries character face ~70% consistency
- POV / 4th-wall break (direct-camera stare)

## What Grok Imagine Pro CANNOT do

Use these terms/concepts at your peril:

### BLOCKED — do not use

- **Dutch angle** — frame never tilts. The word is ignored.
- **3-character gaze triangle** — always degrades. Even with explicit directives, Grok will silently unify the gaze to one direction. Use ≤ 2 characters for gaze-driven storytelling.
- **Physically accurate mirror** — mirror reflections are stylized anime, not left-right accurate. Expect reflection to show slightly different content than source.
- **Conflict / paradox attrs** — "frozen + in motion", "cold palette + warm mood" — Grok picks one side and drops the other.

### DEGRADED — use carefully

- **Hand close-ups** — anatomy may go wrong (extra fingers, warped digits). Avoid ECU hand unless needed; use partial hand with prop context.
- **Text in large signage** — Chinese/English characters legible but often slightly malformed for large signs. Phone/small screen text renders correctly.
- **Wide shot with small figures** — if character occupies <20% of frame, Grok may render as chibi / super-deformed. Keep WS people-less or make the figure a reasonable fraction.
- **Extreme angle variance within anchor-preserved scene** — anchors preserve face ~70% not 100%. Cross-shot identity drifts.

### RESPECTED — use confidently

- VGAI-gated attribute lists
- Mutex-respected attribute pairs
- NOT-X-YES-Y explicit negation (e.g., "ankle socks, NOT thigh-high")
- 2-person gaze configurations
- Shot grammar vocabulary (except Dutch angle)

## Anime preamble (prepend to every character prompt)

```
Modern Japanese manga / seinen anime illustration, digital painterly style with
cel-shaded highlights and expressive line work. Noir-romantic Chinese urban
thriller. Saturated teal shadows and crimson accents, dramatic rim lighting,
slight atmospheric grain. Cinematic composition with confident framing.
```

This is the locked aesthetic validated by user. Do not substitute.

## Cost planning

- $0.07 per image
- ~25-40 seconds per shot at concurrency 1
- With `asyncio.Semaphore(8)`, a 20-shot story runs in ~1-2 minutes

## Reliability by shot type (empirical, from ~113 test shots)

| Shot type | First-try success |
|-----------|-------------------|
| Gated MS/CU/WS, 2-person or less | ~95% |
| Gated ECU with one prop/body region | ~90% |
| Gated full-body with all attrs | ~90% |
| Mutex-clean compositions | ~95% |
| Over-injected / Dutch / 3-gaze | <20% |

With retries (max 3 attempts): success rate → ~99% on well-gated shots.
