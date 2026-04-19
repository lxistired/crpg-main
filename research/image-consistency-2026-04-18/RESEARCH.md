# Image Consistency Research — 2026-04-18

> Scope: character identity drift + wardrobe drift across 15–40 Grok Imagine API calls in the crpg MiniMax M2.7 agent pipeline. Adult content required. API-only. Anime/noir style. $2–5 per story budget.

---

## TL;DR

- **Primary recommendation**: Keep Grok Imagine as primary renderer but implement the two-anchor strategy — one style anchor + per-character portrait anchor — using `image_url` on every shot call. Pair with verbatim wardrobe-canonical-string injection (already partially in Visual DNA Layer 10). Expected uplift: ~40–60% reduction in face/wardrobe drift based on community benchmarks; not 100%.
- **Fallback**: Wan 2.7 Image Pro via Alibaba Cloud Model Studio API — 9 reference images per call, `seed` parameter, `enable_sequential` mode for batch consistency, $0.037/image. Adult content permissiveness unclear but Alibaba's commercial API historically passes more than consumer-facing Western platforms.
- **Rough cost/effort**: Grok anchor strategy = 2–4 hours integration, $0–0.04 extra per story (1–2 extra anchor renders). Wan 2.7 fallback = 1 day integration, ~$0.60–$1.50 extra per story (15–40 images at $0.037 vs $0.02). Full LoRA-per-character path = 2–3 days setup + $8–16 per character training run; too expensive for per-story use, viable only for recurring protagonist.

---

## Q1 — Grok Imagine current state (as of 2026-04-18)

### Endpoint

```
POST https://api.x.ai/v1/images/generations
```

Confirmed live (January 28, 2026 public launch). Same OpenAI-compatible endpoint shape.

### Models (April 2026)

| Model name | Price | RPM | Notes |
|---|---|---|---|
| `grok-imagine-image` | $0.02/image | 300 | Standard quality |
| `grok-imagine-image-pro` | $0.07/image | 30 | Higher fidelity; "Pro mode" teased for late April 2026 at 1080p |

Source: [xAI Models & Pricing page](https://docs.x.ai/developers/models), confirmed April 2026.

### Confirmed parameters

| Parameter | Type | Notes |
|---|---|---|
| `prompt` | string (required) | |
| `model` | string | `grok-imagine-image` or `grok-imagine-image-pro` |
| `image_url` | string | Base64 data URI (`data:image/png;base64,...`) OR public URL. **This is the image-to-image anchor mechanism.** Up to 5 source images supported for editing mode. |
| `aspect_ratio` | enum | 1:1, 16:9, 9:16, 4:3, 3:4, 3:2, 2:3, 2:1, 1:2, 19.5:9, 9:19.5, 20:9, 9:20, auto |
| `resolution` | enum | `"1k"` or `"2k"` |
| `n` | int | 1–10 images per request |
| `response_format` | enum | `"url"` or `"b64_json"` |

**Confirmed NOT present** (as of April 2026):
- `seed` — not exposed via API
- `negative_prompt` — not exposed
- `strength` / `cfg_scale` / `denoising_strength` — not exposed
- Style presets — not exposed

Source: [xAI Image Generation docs](https://docs.x.ai/docs/guides/image-generations), [fal.ai Grok Imagine listing](https://fal.ai/models/xai/grok-imagine-image/api), [aimlapi docs for grok-imagine-image-pro](https://docs.aimlapi.com/api-references/image-models/xai/grok-imagine-image-pro).

### image_url behavior — what it actually does

- Passing `image_url` switches the call to an **image editing / style-transfer mode**, not pure text-to-image.
- The model applies the prompt as a **natural-language edit instruction** on top of the source image.
- Edit cost via fal.ai: $0.022/image ($0.02 output + $0.002 input), consistent with direct API pricing.
- Multi-image editing: community reports suggest 2–3 reference images can be combined via the editing mode, but the official parameter schema shows a single `image_url` slot. WaveSpeedAI's wrapper supports 2–3 images in their higher-level API via multi-image blending internally.
- **Critical limitation**: Because there is no `strength` knob, there is no way to dial between "loose style reference" and "strong identity copy." The model decides how much to follow the anchor. Community testing (April 2026) reports anchor adherence varies significantly based on how "editable" the prompt reads — a prompt that reads as a large change gets less anchor weight than a prompt that reads as a small tweak.

Source: [Grok Imagine API launch post](https://x.ai/news/grok-imagine-api), [WaveSpeedAI image edit intro](https://wavespeed.ai/blog/posts/introducing-x-ai-grok-imagine-image-edit-on-wavespeedai/).

### Rate limits for image generation

xAI's rate-limit tier documentation explicitly states: **"Rate limit tiers only apply to text models. For Imagine API rate limit increases, email sales@x.ai."** The RPM figures (300 for standard, 30 for Pro) are from the models page and are baseline; no public tiering table for images.

Source: [xAI Consumption and Rate Limits](https://docs.x.ai/docs/key-information/consumption-and-rate-limits).

### Adult content (API tier)

The xAI API applies the same moderation as the consumer product. As of March 2026, the consumer product's "Spicy Mode" (partial nudity, adult themes for fictional characters) requires SuperGrok or X Premium+ subscription + age verification. Whether the API tier inherits Spicy Mode unlocking is **not officially documented**. Community reports (April 2026) indicate the API does enforce filters and is not unrestricted. Explicit content (beyond partial nudity, non-penetrative) is blocked even with Premium+ in practice — moderation is described as "extremely heavy" and inconsistent.

**Practical implication**: Grok Imagine's adult content ceiling is "R-rated / tasteful partial nudity of fictional characters." The crpg use case (noir fiction, seductive but not explicit) likely falls within the allowed range, but edge cases will hit moderation. This is a **risk factor** for the primary stack.

Source: [Grok NSFW policy analysis](https://blog.laozhang.ai/en/posts/how-to-enable-nsfw-grok), [Yahoo Finance Grok Imagine launch](https://finance.yahoo.com/news/grok-imagine-xai-ai-image-150418597.html).

### Anime style in Grok Imagine

Multiple reviewers note that Grok Imagine's underlying base (Flux 1 lineage) handles photorealistic/cinematic styles well but **struggles with pure anime style** — "when you ask for anime styles, the model often delivers a 3D interpretation instead." For crpg's "anime seinen with cinematic noir" aesthetic, the hybrid framing (anime + cinematographic language) has been working (Visual DNA Layer 1 achieves this), but pure anime line art is unreliable.

Source: [MindStudio Grok image models comparison](https://www.mindstudio.ai/blog/grok-2-vs-grok-imagine-xai-image-models-comparison), [apiyi.com quality mode guide](https://help.apiyi.com/en/grok-imagine-quality-speed-mode-guide-en.html).

---

## Q2 — Industry methods

### Summary table

| Method | Access | Adult content | Cost/img | Character consistency | Wardrobe consistency | Fit for crpg |
|---|---|---|---|---|---|---|
| Grok Imagine `image_url` anchor | API (xAI direct) | R-rated, inconsistent enforcement | $0.022 | Moderate (no strength knob) | Moderate (verbatim string + anchor) | PRIMARY — already in stack |
| MidJourney `--cref` | UI + restricted API | Unclear/filtered | ~$0.05 | High (85–95% face match) | Moderate | NO — no reliable API; UI-only |
| DALL-E 3 / GPT-Image-1 | API (OpenAI) | Blocked | — | — | — | RULED OUT (AUP) |
| Seedream 4.5/5.0 | API (ByteDance/WaveSpeedAI) | Unclear | $0.035–$0.04 | High (up to 14 ref images) | High (subject tracking) | CANDIDATE — verify adult policy |
| Flux Kontext pro | API (fal.ai, Replicate) | Filtered (NSFW flag returned, content blocks adult) | $0.04 | High (multi-turn consistency, no fine-tune needed) | Moderate | FALLBACK — not adult-permissive via hosted API |
| IP-Adapter / InstantID | API (fal.ai, Replicate) | fal.ai: safety checker enabled by default | $0.014–0.05 | 70–85% (IP-Adapter) / 85–95% (InstantID) | Poor (face only) | PARTIAL — face only, not wardrobe |
| LoRA-per-character (Flux 2 dev) | API training (fal.ai) | NSFW LoRAs exist; training platform may not | $8–16/train run, $0.003–0.008/inference step | Highest (99%+) | High if outfit in training images | TOO EXPENSIVE per story; viable for permanent protagonists only |
| Wan 2.7 Image Pro | API (Alibaba Cloud, Segmind) | Chinese commercial platform; NSFW unclear | $0.037 | High (9 ref images, seed, sequential mode) | High (multi-subject tracking) | FALLBACK — investigate adult policy |
| Qwen Image | Open source / self-host only | Open weights = permissive | — | Moderate | Moderate | NO — requires self-host GPU |
| CogView 3 | Open source / self-host | Open weights | — | Unknown | Unknown | NO — requires self-host GPU |

### Per-method notes

#### 1. Reference-image + img2img (Grok `image_url`)

The "pass one anchor portrait and style-transfer the rest" pattern. This is already planned in Visual DNA Layer 7. The mechanism: generate 1 style+character anchor image in Stage 1, then pass it as `image_url` in all subsequent shot calls. Works because the diffusion model uses the anchor's latent representation as a prior.

**Limitation in Grok's implementation**: No `strength` knob means no control over how strongly the anchor is followed. Observed behavior: if the scene prompt is very different from the anchor (e.g., anchor is "Su Wan seated in interrogation room" and next shot is "exterior rooftop"), the anchor's influence diminishes. Mitigation: use a **neutral** anchor (plain background, clear face/outfit, no strong setting cues) to maximize transferability.

**Multi-anchor strategy** (not yet in Visual DNA): use 2 anchors — one pure-character (face closeup, white/neutral background) and one style-only (abstract noir composition, no character). Pass character anchor for identity-critical shots and style anchor for setting-heavy shots.

#### 2. MidJourney `--cref` (character reference)

`--cref` feeds a reference image into MJ's character embedding space and applies it to new generations. Character weight `--cw 0–100` controls how strictly the face is locked vs how much creative freedom the model takes. As of 2026 v8, `--cref` is replaced by "Omni Reference" in v8; for strict character-only lock, MJ docs recommend `--v 6.0` rollback.

**API access**: Enterprise dashboard only; requires application. No self-serve API in 2026. ImaginePro offers a third-party wrapper, but it is UI-automation-based, not a stable function call. **Ruled out for our agent tool pattern.**

Source: [MidJourney Character Reference docs](https://docs.midjourney.com/hc/en-us/articles/32162917505293-Character-Reference), [ImaginePro blog](https://www.imaginepro.ai/blog/2025/11/midjourney-cref-character-reference-guide).

#### 3. DALL-E 3 / GPT-Image-1

Ruled out (Anthropic AUP compliance — Claude cannot call DALL-E 3 for adult-adjacent content; OpenAI AUP blocks adult content). Technique for reference: GPT-Image-1 supports multi-image conditioning (up to 10 reference images in prompt as base64) and handles outfit/character reference well. Not applicable here.

#### 4. Seedream 4.5 / 5.0 Lite (ByteDance)

**Seedream 4.5** (mid-2025): up to ~90% character consistency across edits, multi-reference image support.
**Seedream 5.0 Lite** (February 2026): chain-of-thought visual reasoning, up to 14 reference images per request, native image editing, 4K resolution.

**API availability**: BytePlus (ByteDance international commercial API) and WaveSpeedAI offer access. Pricing: $0.035–$0.04/image.

**Adult content policy**: Not documented in BytePlus or WaveSpeedAI API docs. ByteDance's Chinese origin means the API for international markets may be more permissive than US-headquartered providers on the fictional adult content spectrum, but this is unconfirmed. **Requires a test API call with crpg-style prompts before committing.**

**Anime style**: Seedream is trained heavily on Asian aesthetics; the model performs well on anime/manga illustrations. This is a genuine advantage over Grok Imagine for the crpg style.

**Character consistency mechanism**: Multi-reference image tracking preserves "facial structure, proportions, and overall identity" including clothing details. The `edit-sequential` mode processes multiple source images with a uniform prompt, applying edits while tracking the same subject — directly useful for the "18 shots of the same character" problem.

Source: [Seedream 4.5 page](https://seed.bytedance.com/en/seedream4_5), [WaveSpeedAI Seedream sequential](https://wavespeed.ai/models/bytedance/seedream-v4.5/edit-sequential), [MindStudio Seedream guide](https://www.mindstudio.ai/blog/what-is-bytedance-seedream-4-5).

#### 5. Flux Kontext / Flux Pro / Flux 2 LoRA

**FLUX.1 Kontext [pro]** (Black Forest Labs, April–May 2025, still active April 2026):
- API via fal.ai ($0.04/image), Replicate, TogetherAI.
- Takes a single `image_url` + text instruction; preserves character identity across edits without fine-tuning.
- `seed` parameter available.
- Multi-turn: each output can become the next input, maintaining identity through successive edits.
- Character consistency via "in-context image generation" — the model extracts and re-applies visual concepts from the reference image.

**Adult content**: Flux's pre-training data was filtered for NSFW. Hosted APIs (fal.ai, Replicate) return `has_nsfw_concepts` flags and apply safety filters. NSFW-uncensored versions exist on CivitAI and HuggingFace for local use but not via the hosted APIs. **Not adult-permissive via API — ruled out for crpg's adult content requirement** unless the content is below the filter threshold.

**FLUX.2 [dev] LoRA (fal.ai)**: Train a character-specific LoRA via API. Cost: $2–$8 per training run (1,000–4,000 steps at $0.002/step via fal.ai fast trainer). Inference: $0.003–0.008 per step. Requires 10–30 reference images of the character. Once trained, inference is cheap and consistency is near-perfect. **Integration effort: 2–3 days.** This is the gold standard for recurring protagonists, but not cost-effective for one-off story characters.

Source: [Flux Kontext announcement](https://bfl.ai/announcements/flux-1-kontext), [fal.ai Flux Kontext pro](https://fal.ai/models/fal-ai/flux-pro/kontext), [fal.ai LoRA training](https://fal.ai/models/fal-ai/flux-lora-fast-training).

#### 6. IP-Adapter / InstantID / PhotoMaker

**IP-Adapter Face ID** (fal.ai):
- Inputs: text prompt + face image(s) (or ZIP of multiple faces averaged together).
- Parameters: `face_image_url`, `face_images_data_url` (ZIP for multi-face averaging), `guidance_scale`, `seed`, `num_inference_steps`.
- Zero-shot personalization: no training required.
- Face consistency: 70–85%.
- **Anime style limitation**: IP-Adapter uses CLIP embeddings that capture geometric face features, but anime characters differ enough from real-face training data that consistency drops. Works better when combined with an anime-specific base model (e.g., AnimagineXL) or character LoRA.
- Adult content: fal.ai runs a safety checker enabled by default; no separate adult-permissive tier advertised.

**InstantID** (fal.ai / Replicate):
- Better face fidelity than IP-Adapter for realistic styles; 85–95% face match.
- Single `image_url` input (no multi-reference).
- `enable_safety_checker` toggle in fal.ai's InstantCharacter variant — but default is enabled.
- **Not adult-permissive via hosted API.**
- For anime: IP-Adapter outperforms InstantID on drastic style shifts (realistic → anime); InstantID is better for same-style consistency.

**Verdict**: Both are face-only mechanisms. Wardrobe is not locked. For crpg's full-body character consistency requirement, IP-Adapter would need to be combined with a clothing-reference approach. Not a complete solution; also not adult-permissive.

Source: [fal.ai IP-Adapter Face ID](https://fal.ai/models/fal-ai/ip-adapter-face-id/api), [fal.ai Instant Character](https://fal.ai/models/fal-ai/instant-character/api), [nowadais.com consistency guide](https://www.nowadais.com/ai-character-consistency-guide-consistent-visual/).

#### 7. LoRA-per-character

Train one FLUX.2 or Pony-based LoRA per protagonist. The LoRA encodes the character's face, body proportions, and signature outfit into the model weights. Consistency at inference: 95%+.

**API training**: fal.ai FLUX LoRA Fast Training: $2 flat per training run (scales with steps; base is ~$0.002/step). FLUX.2 [dev] Trainer: $0.008/step (higher quality). For 500 steps (fast pass): ~$1–4. Requires 10–30 curated reference images.

**Inference**: FLUX.2 LoRA on fal.ai: billed per inference step ($0.003–0.008); a typical 20–30 step generation = $0.06–0.24/image — much more expensive than Grok Imagine's $0.02 baseline.

**Adult content via LoRA**: LoRA doesn't bypass the base model's safety filters on hosted platforms. For adult content, you'd need a NSFW-uncensored base on a permissive platform (not available via standard fal.ai/Replicate).

**Verdict**: Gold standard for consistency, but: (a) too expensive per-image for the $2–5 story budget, (b) requires pre-generating training images (chicken-and-egg problem for new characters), (c) adult content still blocked on hosted APIs. **Appropriate only for permanent recurring protagonists** (Su Wan) if we ever invest in it, with a permissive self-hosted or specialized platform.

Source: [fal.ai Flux LoRA fast training](https://fal.ai/models/fal-ai/flux-lora-fast-training), [apatero.com FLUX 2 LoRA guide](https://apatero.com/blog/flux-2-pro-lora-training-character-consistency-2026).

#### 8. GPT-Image-1 / Imagen 3 / Nano Banana multi-image conditioning

- **GPT-Image-1**: Multi-image conditioning (up to 10 images as base64 in prompt). Good character consistency. **Ruled out — OpenAI AUP.**
- **Imagen 3** (Google): No public adult content API. **Ruled out.**
- **Nano Banana**: Niche provider; limited documentation; not evaluated.

#### 9. Qwen Image / Wan 2.7 / CogView 3

**Wan 2.7 Image Pro** (Alibaba, released April 3, 2026):
- Endpoint: `https://api.segmind.com/v1/wan2.7-image-pro` (Segmind), also Alibaba Cloud Model Studio directly.
- Parameters (Alibaba Cloud): `prompt`, up to 9 reference images via content array, `seed` (0–2147483647), `enable_sequential` (boolean), `n` (1–12 for sequential), `bbox_list` for spatial editing control.
- Pricing: $0.037/image (Segmind), billing per successfully generated image only.
- Resolution: up to 4K (Pro), 2K (Standard).
- 9-Grid / 3x3 multi-reference: Pass 9 images showing character from front, 3/4, side, different expressions, different poses. Model builds comprehensive character understanding.
- `enable_sequential` mode: generates thematically linked image set — directly maps to "18 shots of the same story."
- Adult content policy: **Unspecified** in official docs. Chinese commercial API. Historically, Alibaba's commercial AI services include content filters, but the specific threshold for anime-style adult content is unverified. Community reports do not mention explicit blocking of suggestive-but-non-explicit anime content.

**Qwen Image** (Alibaba): Primarily open-source / self-hosted. HuggingFace discussions indicate the open-source version can generate adult content when guided. No production API with adult-permissive policy found.

**CogView 3** (Zhipu AI): Open-source. Self-hosted only. Not evaluated.

Source: [Alibaba Cloud Wan 2.7 API reference](https://www.alibabacloud.com/help/en/model-studio/wan-image-generation-and-editing-api-reference), [Segmind Wan 2.7 blog](https://blog.segmind.com/wan-2-7-image-pro-now-on-segmind/), [apiyi.com Wan 2.7 deep dive](https://help.apiyi.com/en/wan-2-7-image-pro-4k-text-to-image-thinking-mode-api-guide-en.html).

---

## Q3 — Wardrobe/outfit consistency specifically

### Root cause of wardrobe drift

Wardrobe drift is separate from face drift and requires a separate solution. As documented in Visual DNA Layer 10 (Layered Garment Visibility Rule, 2026-04-17), the root cause is **Default-Prior Override**: diffusion models have strong priors toward the most common training-distribution variant of a garment category. "Seamed thigh-high stocking" gets pulled toward the closest peak — which may be "tights" or "over-the-knee sock" depending on the composition context.

### Do the methods above handle wardrobe specifically?

- **Grok `image_url` anchor**: The anchor image preserves the *visual appearance* of the outfit in the anchor, but only weakly — as discussed above, there is no strength control. If the scene changes significantly, the anchor's outfit influence fades. **Partial help.**
- **Seedream 5.0 Lite sequential mode**: Multi-subject tracking preserves "clothing details" explicitly in their documentation. This is the strongest hosted-API solution for wardrobe. **High value.**
- **Flux Kontext**: "Unique characters, objects, or styles across scenes without fine-tuning." Style includes garment — but again, not adult-permissive on hosted API.
- **IP-Adapter**: Face-only. No garment transfer. **No help.**
- **LoRA-per-character**: If training images include the specific outfit, the LoRA encodes both face and outfit. Best wardrobe consistency. Expensive.

### State of the art: verbatim string + anchor image

The practical answer for 2026 API-only setups is: **verbatim canonical outfit string (locked byte-for-byte across all shots) + reference anchor image.** The canonical string approach is already partially in the Visual DNA (Layer 3 character sheets, Layer 10 garment visibility rules). What is missing is formalization of a "wardrobe canonical string" object that is injected with no paraphrasing.

**Key insight from Layer 10**: the canonical string is not just a description — it must include layered visual disambiguation (upper boundary → skin gap → band → body → seam) to prevent the model from snapping to the wrong distribution peak. This is not just a prompt-engineering nice-to-have; it is essential for hosiery, qipao, and other high-prior garment types.

### Outfit-LoRA approaches

Research found IP-Adapter-based garment transfer tools (MagicClothing, outfit2outfit ControlNet on CivitAI), but these are ComfyUI workflows — not hosted APIs with a simple function call interface. Mobile-VTON (CVPR 2026) uses IP-Adapter for garment transfer in a research context, not production API.

**Virtual try-on APIs** (Pixelcut, etc.) exist for photorealistic e-commerce use cases — they transfer a garment photo onto a person. But they are: (a) photorealistic style only, not anime, and (b) not adult-permissive.

### Production studio approaches

Wonder Studio and Runway Gen-3 handle wardrobe in video via continuous temporal coherence (the frame-to-frame latent is naturally coherent in video generation). For image generation pipelines, production studios (based on available community research) use:
1. **Character turnaround sheet as reference**: Generate a 360-degree character sheet showing front/back/side with the full outfit visible. Pass this as reference for all subsequent shots.
2. **Locked prompt with outfit micro-detail description**: Exact material, color code (not "burgundy" but "deep wine red #6B0000"), garment silhouette geometry.
3. **Post-generation wardrobe check**: Automated classifier or VLM check that detects outfit drift and regenerates the specific shot.

The third point (automated wardrobe consistency check) is the VGAI validator's `covers` assertion — already planned in pending task #48 (WardrobeItem schema with covers field) and #52 (wardrobe-coverage reference doc).

### Recommended wardrobe strategy for crpg

1. **Formalize the wardrobe canonical string** (task #75) as a structured object with:
   - `garment_id`: unique identifier
   - `canonical_prompt_fragment`: verbatim, never paraphrased, injected byte-for-byte
   - `disambiguation_layers`: the Layer 10 structure (upper boundary, skin gap, band, body, seam)
   - `hard_negatives`: the triple-redundant negations
2. **Generate a character turnaround anchor** in Stage 1: a 2-image or 4-panel image showing front and 3/4 view of each character in their signature outfit. This is richer than the current single-pose anchor and locks garment geometry across multiple viewpoints.
3. **VGAI validator wardrobe check**: VLM-based check for outfit key attributes (skirt silhouette = pencil, stocking visibility = yes, heel = present). Already partially designed.

---

## Q4 — Style / atmosphere consistency

### IP-Adapter-Style equivalent via hosted API

IP-Adapter-Plus (style variant) on fal.ai captures aesthetic style from a reference image (color palette, texture, rendering style) separate from subject identity. Available on fal.ai and Invoke. However:
- Adult content: fal.ai safety checker default on.
- Anime style transfer: works but anime style adapters need an anime base model to be effective.

**For crpg**: The Visual DNA Layer 1 (Style Preamble) already handles this via text — the preamble is the IP-Adapter equivalent for Grok Imagine. Because Grok has no style preset parameter, the preamble is the only knob. The anchor image (Layer 7) also carries style implicitly.

If Grok is replaced by Wan 2.7 in fallback mode, Wan's multi-reference allows passing one pure-style-reference image alongside character references. This is the cleanest dual-reference approach available without self-hosting.

### Combining character reference + style reference

The problem with passing both character anchor and style anchor to models that only accept one `image_url`:
- Grok Imagine: single `image_url` only. Solution: pre-composite a combined image (character portrait in a styled environment = the current Stage 1 anchor approach).
- Wan 2.7: up to 9 reference images. Can pass character anchor at position 0 and style reference at position 1 separately. The model's multi-reference handling merges them.
- Seedream 5.0 Lite: up to 14 reference images. Same opportunity.
- Flux Kontext: single `image_url` + text. Cannot separate style and character references.

**Recommendation**: the current Stage 1 anchor (character in styled environment, single composite image) is the right solution for Grok. For Wan 2.7 fallback, pass character portrait + style-only image as separate references.

---

## Q5 — Recommendation for crpg

### Primary recommendation: Grok Imagine enhanced anchor strategy

**Keep Grok Imagine as primary**. Reasons:
1. Already integrated in the pipeline.
2. $0.02/image keeps story budget well within $2–5 (18–40 images = $0.36–$0.80 at baseline; up to $1.60 adding pro mode).
3. Adult content: crpg's target content (seductive noir, partial nudity of fictional characters) falls within Grok's stated R-rated ceiling. The moderation inconsistency is a risk, not a blocker — failed shots get regenerated.
4. The `image_url` anchor mechanism is confirmed and live.

**Enhancements to implement** (estimated 2–4 hours):

1. **Two-stage anchor generation** (Layer 7, already designed):
   - Stage 1a: Generate 1 character portrait anchor per protagonist (neutral background, clear face + outfit, front view). Store as base64.
   - Stage 1b: Generate 1 style anchor (no character, just mood/setting/color grade). Store as base64.
   - Composite Stage 1a + 1b into a single combined anchor image (character standing in a styled environment). This is the anchor passed to all Stage 2 calls.

2. **Neutral anchor design principle** (not yet in Visual DNA):
   - Anchor should show the character in a neutral pose, plain or minimal-cue background, full body visible, outfit fully readable.
   - Avoid anchor images with heavy setting/environment cues — they compete with the scene-specific prompt in the editing call.

3. **Wardrobe canonical string** (task #75):
   - Lock the outfit description string exactly in the Visual DNA JSON. The Shot Director must inject this string verbatim, zero paraphrasing.
   - Append the disambiguation layers from Layer 10 whenever a High-Prior garment is in frame.

4. **Per-character anchor in visual DNA** (extend Layer 7):
   - Instead of one story-level anchor, one anchor per character (face closeup version + full-body version).
   - When a scene contains Character A but not Character B, only pass Character A's anchor as `image_url`.

**Expected quality uplift**: Anchor-based image_url anchoring, based on community benchmarks and the prior Visual DNA rounds, is estimated to reduce face drift by 40–60% and wardrobe drift by 30–50%. Not 100%. The remaining drift requires VGAI-level detection + regeneration.

**Budget impact**: 2 extra API calls per story for anchors ($0.04 at standard, $0.14 at pro). Negligible.

### Wardrobe primary recommendation: verbatim canonical string + Layer 10

No additional model or API needed. Pure prompt engineering. Implement task #75 (wardrobe canonical string object in Visual DNA) and enforce in Shot Director:
- `wardrobe_canonical_string`: locked, never paraphrased.
- `disambiguation_layers`: always injected for High-Prior garments.
- `hard_negatives`: triple-redundant.

This alone, based on the Round 5 results documented in `visual-dna-system.md`, is the single highest-ROI intervention for wardrobe drift.

### Fallback: Wan 2.7 Image Pro

If Grok Imagine's moderation blocks too many crpg shots (>15% shot failure rate), switch to **Wan 2.7 Image Pro** via Alibaba Cloud Model Studio or Segmind.

**Why Wan 2.7 as fallback**:
- 9 reference images per call: pass face-closeup + full-body outfit anchor + style anchor separately.
- `seed` parameter: use the same seed across all shots in a story for latent-space consistency.
- `enable_sequential` mode: batch up to 12 shots in one call, model maintains cross-shot consistency internally.
- Pricing: $0.037/image. For 18 shots: $0.67. For 40 shots: $1.48. Within budget.
- April 2026 release: actively maintained, Alibaba backing.
- Anime style: stronger than Grok Imagine based on Asian aesthetics training data.

**Adult content risk**: Unverified. Must run a test batch of crpg-style prompts before committing. If Alibaba Cloud API blocks them, next option is Segmind's hosted version (separate content policy) or BytePlus.

**Integration effort**: 1 day. Need to write a new `render_image` function tool that switches between Grok and Wan 2.7 based on a config flag. The OpenAI Agents SDK `function_tool` wrapper stays the same; only the inner HTTP call changes.

### Fallback #2: Seedream 5.0 Lite

If both Grok and Wan 2.7 fail on adult content, **Seedream 5.0 Lite** (ByteDance BytePlus) is the next candidate:
- 14 reference images per call.
- Strong anime style affinity.
- $0.035–$0.04/image.
- WaveSpeedAI hosts a stable API endpoint.
- Adult content policy: unverified but ByteDance's international API has historically been less restrictive on anime-style content than US-headquartered providers. Requires testing.

**Integration effort**: 0.5 days (same interface pattern as Wan 2.7 fallback).

### What is NOT recommended

- **LoRA-per-character via fal.ai**: Too expensive per story ($8–16 training + $0.06–0.24/image inference vs $0.02 for Grok). Consider only if Su Wan becomes a permanent protagonist across 100+ stories, making the amortized training cost acceptable.
- **MidJourney cref**: No stable programmatic API. UI-only. Incompatible with agent function_tool pattern.
- **IP-Adapter / InstantID on fal.ai**: Face-only, not wardrobe. Not adult-permissive on hosted API.
- **Flux Kontext on fal.ai**: Not adult-permissive on hosted API despite excellent character consistency.
- **Self-hosted models (Qwen Image, CogView, Wan 2.1 open weights)**: We do not run local GPUs.

### Integration effort and expected quality uplift summary

| Work item | Effort | Expected uplift |
|---|---|---|
| Two-anchor strategy (Grok `image_url` enhanced) | 2–4 hours | Face drift -40–60% |
| Wardrobe canonical string (task #75) + Layer 10 enforcement | 2–3 hours | Wardrobe drift -30–50% |
| VGAI wardrobe coverage check (tasks #48, #52, #75) | 3–5 hours | Catch remaining wardrobe drift for regeneration |
| Wan 2.7 fallback function_tool | 1 day | Full story rescue if Grok moderation fails |
| LoRA-per-protagonist (future, Su Wan only) | 2–3 days | Face + wardrobe drift ~-95% (but adult content still blocked on hosted) |

---

## Appendix: URLs referenced

- xAI Image Generation docs: https://docs.x.ai/docs/guides/image-generations
- xAI Models & Pricing: https://docs.x.ai/developers/models
- xAI Rate Limits: https://docs.x.ai/docs/key-information/consumption-and-rate-limits
- Grok Imagine API launch: https://x.ai/news/grok-imagine-api
- grok-imagine-image-pro on AIML API: https://docs.aimlapi.com/api-references/image-models/xai/grok-imagine-image-pro
- fal.ai Grok Imagine image edit: https://fal.ai/models/xai/grok-imagine-image/edit
- fal.ai Grok Imagine API: https://fal.ai/models/xai/grok-imagine-image/api
- WaveSpeedAI Grok Imagine image edit intro: https://wavespeed.ai/blog/posts/introducing-x-ai-grok-imagine-image-edit-on-wavespeedai/
- Grok NSFW policy (LaoZhang): https://blog.laozhang.ai/en/posts/how-to-enable-nsfw-grok
- Grok adult content guide (YingTu): https://yingtu.ai/en/blog/grok-imagine-adult-content-guide
- Grok quality/speed mode guide (apiyi): https://help.apiyi.com/en/grok-imagine-quality-speed-mode-guide-en.html
- MindStudio Grok models comparison: https://www.mindstudio.ai/blog/grok-2-vs-grok-imagine-xai-image-models-comparison
- Flux Kontext announcement: https://bfl.ai/announcements/flux-1-kontext
- fal.ai Flux Kontext pro: https://fal.ai/models/fal-ai/flux-pro/kontext
- fal.ai Flux LoRA fast training: https://fal.ai/models/fal-ai/flux-lora-fast-training
- fal.ai Flux 2 LoRA: https://fal.ai/models/fal-ai/flux-2/lora
- fal.ai IP-Adapter Face ID: https://fal.ai/models/fal-ai/ip-adapter-face-id/api
- fal.ai Instant Character: https://fal.ai/models/fal-ai/instant-character/api
- Seedream 4.5 page: https://seed.bytedance.com/en/seedream4_5
- WaveSpeedAI Seedream sequential: https://wavespeed.ai/models/bytedance/seedream-v4.5/edit-sequential
- WaveSpeedAI Seedream V5.0 Lite: https://wavespeed.ai/docs/docs-api/bytedance/bytedance-seedream-v5.0-lite-sequential
- Alibaba Cloud Wan 2.7 API reference: https://www.alibabacloud.com/help/en/model-studio/wan-image-generation-and-editing-api-reference
- Segmind Wan 2.7 blog: https://blog.segmind.com/wan-2-7-image-pro-now-on-segmind/
- apiyi.com Wan 2.7 deep dive: https://help.apiyi.com/en/wan-2-7-image-pro-4k-text-to-image-thinking-mode-api-guide-en.html
- MidJourney Character Reference docs: https://docs.midjourney.com/hc/en-us/articles/32162917505293-Character-Reference
- ImaginePro cref guide: https://www.imaginepro.ai/blog/2025/11/midjourney-cref-character-reference-guide
- nowadais.com consistency guide: https://www.nowadais.com/ai-character-consistency-guide-consistent-visual/
- apatero.com FLUX 2 LoRA guide: https://apatero.com/blog/flux-2-pro-lora-training-character-consistency-2026
- Yahoo Finance Grok Imagine launch: https://finance.yahoo.com/news/grok-imagine-xai-ai-image-150418597.html
- MindStudio Seedream guide: https://www.mindstudio.ai/blog/what-is-bytedance-seedream-4-5
