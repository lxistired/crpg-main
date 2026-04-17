# Visual Aesthetic Axes — Taxonomy & Analysis

**Companion document to** `visual-aesthetics.yaml`
**Version:** 2026-04-17
**Scope:** Aesthetic-language classification for crpg's adult narrative generator.
**Not in scope:** Explicit-content taxonomies, checkpoint catalogues, production tutorials.

---

## 1. Why 6 categories (not 5, not 8)

A visual aesthetic is a *dialect* — a bundle of palette, lighting, composition, texture, and cultural reference that together signal "this is the kind of image this is." Adult-content industries have produced many dialects, but they cluster around a small number of **structural axes**:

| Axis | Structural divide |
|------|-------------------|
| Medium | Photography vs. illustration |
| Cultural lineage | Japanese vs. Western |
| Publication era | Contemporary digital vs. pre-digital (vintage) |
| Institutional context | Commercial/popular vs. fine-art gallery |
| Representational mode | Realist vs. stylized/experimental |

Six categories fall out naturally from these axes:

1. **Japanese Photorealistic** — contemporary JP photo dialect (JAV, gravure, shi-shashin)
2. **Western Photorealistic** — contemporary Western photo dialect (Playboy/Penthouse/editorial lineage)
3. **Anime / Manga Illustration** — contemporary illustrated dialect from Japan
4. **Vintage Erotica** — pre-1980s print-medium dialects (Playboy-era, pin-up, ukiyo-e, Art Nouveau, Beardsley)
5. **Fine Art Erotica** — named-artist / gallery-context dialects (Schiele, Klimt, Amano, Yamamoto, Sorayama)
6. **Stylized / Experimental** — digital-native indie formats (pixel, cyberpunk, vaporwave, 3DCG, riso)

**Why not 5?** Collapsing Fine Art into Vintage loses the distinction between gallery-voice (single-artist signature) and publication-house aesthetic (Playboy etc. as institutional style). These are read differently by audiences.

**Why not 8?** Additional candidates (furry/anthro, 3D photoreal CGI, AR/VR UI aesthetics, game-engine cinematic) are either subcategories of existing axes or so nascent they fragment more than they clarify. Keep them as future expansion points, not top-level.

A **cross-category "Contemporary vs Vintage"** axis is also useful as a secondary filter: the same narrative beat can be rendered in 2025-JP-realism or 1970-Penthouse and signify completely different things.

---

## 2. The six categories: essence, origin, boundaries

### 2.1 Japanese Photorealistic (JP-R)

**Essence.** Photographic image-making rooted in Japanese visual conventions: muted palette, restrained framing, subtext-loaded, shadow-conscious. Tanizaki's *In Praise of Shadows* is the cultural thesis; JAV and gravure are the industrial expressions.

**Origin.** 1970s-80s: weekly gravure magazine culture (FRIDAY, FLASH) normalizes a specific photographic look — natural skin, available light, subtext over exhibition. The 1981 legalization of adult video creates JAV as industry; its studio conventions (flat soft-box key, set-dressed interiors) develop as a parallel photographic dialect. The 1990s-2000s shi-shashin ("I-photography") movement (Araki lineage) provides the fine-art-inflected extreme. AI generation crystallized this lineage through the **BRA → JSR → ChilloutMix → Majicmix** checkpoint family, which has become the de facto industry standard for "Japanese realistic" output.

**Inner divisions (6 sub-dialects).** These are defined by the *setting as meaning-bearer*: office (`jpr_urban_ol`), school uniform (`jpr_school_jk`), domestic (`jpr_housewife`), AV studio (`jpr_jav_studio`), diary (`jpr_private_diary`), traditional onsen (`jpr_onsen_traditional`). The visual grammar differs significantly — `jpr_jav_studio` uses flat shadowless lighting, `jpr_private_diary` uses on-camera flash and snapshot framing, `jpr_urban_ol` uses shallow-DoF cinema look. They are not interchangeable.

**Boundary.** The genre breaks when (a) colors saturate toward Western commercial, (b) retouching removes skin texture, (c) composition becomes symmetric-commercial. That is where JP-R ends and `wr_*` begins.

### 2.2 Western Photorealistic (W-R)

**Essence.** High-saturation, direct-engagement, commercially-retouched photographic dialect. The inheritance chain is: 1953 *Playboy* launch (Hefner's "tasteful glamour" position) → 1970s *Penthouse* (Guccione's soft-focus painterly counter-position) → 1970s-80s fashion editorial (Newton, Bourdin bring erotics into *Vogue*) → contemporary digital commercial.

**Origin.** The six sub-dialects here are not about *subject* (office/school/etc.) but about **lighting philosophy and era**:
- `wr_hardcore_contemporary` — beauty-dish flat, crisp, commercial
- `wr_glamour_playboy` — warm golden, aspirational-lifestyle
- `wr_penthouse_softfocus` — diffused, painterly, 1970s-romantic
- `wr_girl_next_door` — available-light amateur, 2010s-onward
- `wr_fashion_editorial` — hard-shadow staged cinematic (Newton/Bourdin)
- `wr_bw_fineart` — monochrome formal (Mapplethorpe lineage)

**Boundary.** Glamour/Playboy blurs into Girl-Next-Door as retouching drops. Editorial blurs into B&W Fine Art as color drops and pose formalizes. These are endpoints on continua; choose based on **which edge you want to be near**, not a hard taxonomic assignment.

### 2.3 Anime / Manga Illustration (ANI)

**Essence.** Line-based 2D illustration with Japanese visual-narrative heritage. Line is structural, not decorative. Color is flat-ish (cel-derivation) or painterly (Pixiv-evolved). Anatomy is stylized.

**Origin.** TV animation (cel-shading as economic necessity → aesthetic) → doujinshi culture from the late 1970s → Comiket (first held 1975) institutionalizing amateur manga → 2000s Pixiv platform → 2022 onward AI ecosystem (NovelAI, Pony Diffusion, Illustrious, NoobAI — all Danbooru-tag-indexed).

**Inner divisions (5 sub-dialects).** By *rendering mode*, not subject:
- `ani_cel_shaded_tv` — hard-shadow flat cel (TV animation inheritance)
- `ani_painterly_pixiv` — rendered soft brushwork (Pixiv 2010s-onward)
- `ani_soft_watercolor` — watercolor-inflected (iyashikei tonal mode)
- `ani_hmanga_linework` — B&W ink+screentone (doujin manga inheritance)
- `ani_retro_80s_90s` — OVA-era cel with nostalgic palette

**Boundary.** The five modes are *render techniques*; any subject can be done in any mode. The AI generation models for this category are the most mature ecosystem — Pony/Illustrious/NoobAI all use the Danbooru tag vocabulary, making artist-style pinning precise and consistent.

### 2.4 Vintage Erotica (VIN)

**Essence.** Pre-digital, medium-constrained dialects from distinct historical traditions. Category unifier: "the print medium shaped the image."

**Origin — five entirely distinct traditions with no shared root:**
- `vin_playboy_70s` — mid-century American magazine
- `vin_pinup_elvgren` — mid-century American commercial illustration
- `vin_shunga_ukiyoe` — Edo-period Japanese woodblock (17th-19th century)
- `vin_victorian_beardsley` — 1890s British Aestheticism / Decadence
- `vin_artnouveau_mucha` — 1895-1914 European decorative poster

**Boundary.** These do not merge with each other. Shunga and Beardsley share *only* flat-ink convention (and Beardsley explicitly copied shunga — see the V&A account). Mucha and Playboy share *only* the "decorative female figure" subject. They are a cluster by date-of-origin, not by shared visual grammar.

**Important finding.** Beardsley's erotic work was directly influenced by Edo shunga (V&A), which means the West-Japan boundary has been porous for 130+ years at the high-art level. This justifies treating ukiyoe-shunga and Beardsley in the same category (both pre-modern-print dialects) rather than splitting geographic-ally.

### 2.5 Fine Art Erotica (ART)

**Essence.** Named-artist, gallery-context, individual-voice aesthetics. Distinguished from Vintage by **signature as the primary reference** — the style is "the specific hand of Artist X," not "the publication-house of Magazine Y."

**Origin.** Six centuries of the Western/Eastern fine-art canon engaging with the erotic, compressed here to five entries that have strong AI-generation support through artist-tag pinning:
- `art_schiele_expressionist` — Viennese Expressionism (1910s)
- `art_klimt_decorative` — Vienna Secession (1900s-1910s)
- `art_amano_fantasy` — contemporary Japanese fantasy illustration
- `art_yamamoto_heisei` — contemporary Heisei Estheticism
- `art_sorayama_chrome` — contemporary superrealist airbrush

**Boundary.** Schiele and Klimt are teacher-student but visually opposite (Klimt = ornate ecstatic; Schiele = raw psychological). Amano and Yamamoto are both contemporary Japanese but one is fantasy-ethereal, the other gothic-decadent. Each entry is a single-voice target; audiences read the voice, not the category.

**Rationale for inclusion.** These artist-tags are well-represented in Illustrious XL / NoobAI XL / Pony tag vocabularies because Danbooru captions include artist attribution. This makes "Fine Art Erotica" operationally distinct from general art history — it is the subset of named artists **that Danbooru-trained AI models can reliably replicate**.

### 2.6 Stylized / Experimental (EXP)

**Essence.** Digital-native or medium-native indie aesthetics. "Medium-as-message" — the format constrains (and thereby defines) the style.

**Origin.** Five live lineages:
- `exp_pixel_retro` — NEC PC-98 visual novel tradition (1990s Japan) + modern indie pixel
- `exp_cyberpunk_neon` — Blade Runner (1982) → Ghost in the Shell (1995) → now
- `exp_vaporwave_pastel` — early 2010s internet-native microgenre
- `exp_3dcg_honey` — Illusion Soft game engines + doujin 3DCG community
- `exp_risograph_zine` — 2010s-onward indie print-making revival

**Boundary.** These do not merge easily; each is its own visual world. The category unifier is "none of the other five categories fit."

---

## 3. Aesthetic × Narrative Genre affinity matrix

Rows: aesthetic sub-dialects (abbreviated to codes). Columns: McKee-style narrative genre codes used in crpg.
Cells: **H** = high affinity (this aesthetic natively signals this genre), **M** = medium (works but not first choice), **L** = low (mismatch or fights the genre), **-** = incompatible.

| | Power Dynamic | Forbidden Affair | Coming of Age | Noir Seduction | Romantic Fantasy | Domestic Disruption | Cyberpunk Romance | Gothic Decadence | Commercial Encounter | Slice of Life Intimate |
|---|---|---|---|---|---|---|---|---|---|---|
| `jpr_urban_ol` | **H** | **H** | M | M | L | M | L | L | M | M |
| `jpr_school_jk` | M | M | **H** | L | M | L | L | L | L | M |
| `jpr_housewife` | M | **H** | L | L | L | **H** | L | L | L | M |
| `jpr_jav_studio` | M | M | L | L | L | L | L | L | **H** | L |
| `jpr_private_diary` | M | M | M | M | L | M | L | M | L | **H** |
| `jpr_onsen_traditional` | M | **H** | L | L | M | L | L | L | L | M |
| `wr_hardcore_contemporary` | M | L | L | L | L | L | L | L | **H** | L |
| `wr_glamour_playboy` | M | M | L | M | **H** | L | L | L | **H** | L |
| `wr_penthouse_softfocus` | L | **H** | L | M | **H** | L | L | L | M | L |
| `wr_girl_next_door` | L | M | M | L | M | M | L | L | M | **H** |
| `wr_fashion_editorial` | **H** | M | L | **H** | L | L | M | M | M | L |
| `wr_bw_fineart` | M | L | L | **H** | M | L | L | M | L | M |
| `ani_cel_shaded_tv` | M | M | **H** | L | **H** | M | L | L | L | **H** |
| `ani_painterly_pixiv` | M | M | M | M | **H** | L | M | M | L | M |
| `ani_soft_watercolor` | L | M | **H** | L | **H** | M | L | L | L | **H** |
| `ani_hmanga_linework` | M | M | M | L | M | L | L | M | **H** | L |
| `ani_retro_80s_90s` | L | M | M | M | **H** | L | M | L | L | M |
| `vin_playboy_70s` | L | **H** | L | L | **H** | M | L | L | M | L |
| `vin_pinup_elvgren` | L | M | L | L | M | L | L | L | M | L |
| `vin_shunga_ukiyoe` | **H** | **H** | L | L | M | M | L | M | L | L |
| `vin_victorian_beardsley` | M | **H** | L | M | L | L | L | **H** | L | L |
| `vin_artnouveau_mucha` | L | M | L | L | **H** | L | L | M | L | L |
| `art_schiele_expressionist` | **H** | M | M | M | L | L | L | **H** | L | M |
| `art_klimt_decorative` | L | **H** | L | L | **H** | L | L | **H** | L | L |
| `art_amano_fantasy` | L | M | M | L | **H** | L | M | **H** | L | L |
| `art_yamamoto_heisei` | M | **H** | L | M | L | L | L | **H** | L | L |
| `art_sorayama_chrome` | M | L | L | **H** | L | L | **H** | L | M | L |
| `exp_pixel_retro` | L | M | M | L | M | L | L | L | M | **H** |
| `exp_cyberpunk_neon` | **H** | M | L | **H** | L | L | **H** | M | L | L |
| `exp_vaporwave_pastel` | L | M | L | L | M | L | M | L | L | M |
| `exp_3dcg_honey` | M | M | M | L | M | L | M | L | M | M |
| `exp_risograph_zine` | L | M | M | L | M | L | L | L | L | **H** |

**Reading the matrix.** When the AI has a narrative-beat tag (e.g. "forbidden affair in corporate setting"), it can intersect with the aesthetic column to get candidate aesthetics. `jpr_urban_ol`, `jpr_housewife`, `wr_penthouse_softfocus`, and `vin_shunga_ukiyoe` all hit H for "Forbidden Affair" — but they disagree on **era and culture**, so the narrative's setting tags break the tie.

---

## 4. AI model mapping — summary table

For each aesthetic, the practical "pick one default" model as of 2026-Q2. More options in the YAML.

| Aesthetic | Default model | Alternative | Notes |
|---|---|---|---|
| `jpr_urban_ol` | BRA v7 (SD 1.5) | FLUX dev + JP LoRA | BRA lineage unmatched for JAV-adjacent realism |
| `jpr_school_jk` | Majicmix + JK LoRA | Illustrious XL realistic | **Hard adult-age gate required** |
| `jpr_housewife` | BRA v7 + mature LoRA | RealVisXL + interior LoRA | Mature-face LoRA is critical |
| `jpr_jav_studio` | BRA v7 + set LoRA | Realistic Vision + softbox LoRA | Highly convention-locked |
| `jpr_private_diary` | Analog Diffusion | FLUX dev + film LoRA stack | Film-emulation LoRAs are the axis |
| `jpr_onsen_traditional` | BRA v7 + onsen LoRA | RealVisXL + traditional LoRA | Steam volumetric LoRA helps |
| `wr_hardcore_contemporary` | Realistic Vision v6 / EpicRealism | FLUX dev | Most saturated Western-default |
| `wr_glamour_playboy` | Juggernaut XL | RealVisXL v5 + lifestyle | Warm interior LoRA mandatory |
| `wr_penthouse_softfocus` | Analog Diffusion + soft-focus | Realistic Vision + diffusion | Soft-focus must be strong |
| `wr_girl_next_door` | Realistic Vision (raw) | RealVisXL | Avoid retouch LoRAs |
| `wr_fashion_editorial` | Juggernaut XL + Newton LoRA | FLUX dev + editorial | Hard-flash LoRA helps |
| `wr_bw_fineart` | Realistic Vision + Mapplethorpe | RealVisXL + B&W fine-art | Silver-gelatin LoRA is key |
| `ani_cel_shaded_tv` | Animagine XL 3.1 | Illustrious XL | Artist tags reliable |
| `ani_painterly_pixiv` | **Pony Diffusion V6 XL** | Illustrious XL (artist tags) | Default choice for this lane |
| `ani_soft_watercolor` | Illustrious XL + watercolor LoRA | NoobAI XL + artist tag | Watercolor LoRA important |
| `ani_hmanga_linework` | NoobAI XL | Illustrious XL + mono LoRA | Monochrome manga LoRA |
| `ani_retro_80s_90s` | Mistoon + 80s LoRA | Animagine + OVA LoRA | VHS-color LoRA helps |
| `vin_playboy_70s` | Analog Diffusion + 70s LoRA | Realistic Vision + vintage | Kodachrome LoRA |
| `vin_pinup_elvgren` | SDXL + Elvgren LoRA | Illustrious + artist tag | Strong dedicated LoRAs exist |
| `vin_shunga_ukiyoe` | Illustrious XL + ukiyoe | SDXL + shunga LoRA | Artist tags for Utamaro/Hokusai |
| `vin_victorian_beardsley` | Illustrious XL + Beardsley | SDXL + decadent LoRA | Very line-dependent |
| `vin_artnouveau_mucha` | Illustrious XL + Mucha tag | SDXL + Art Nouveau | Well-supported artist tag |
| `art_schiele_expressionist` | Illustrious XL + Schiele tag | SDXL + expressionist | Strong tag support |
| `art_klimt_decorative` | Illustrious XL + Klimt tag | SDXL + ornament LoRA | Gold-ornament LoRA helps |
| `art_amano_fantasy` | Illustrious XL + Amano tag | SDXL + Amano LoRA | Well-known style |
| `art_yamamoto_heisei` | Illustrious XL + Yamamoto tag | SDXL + Heisei LoRA | Medium tag recognition |
| `art_sorayama_chrome` | Illustrious XL + Sorayama tag | SDXL + chrome LoRA | Strong airbrush LoRAs |
| `exp_pixel_retro` | SDXL + Pixel Art XL LoRA | FLUX dev + pixel LoRA | PC-98 palette LoRA for JP flavor |
| `exp_cyberpunk_neon` | Juggernaut XL + cyberpunk | FLUX dev + Blade Runner LoRA | Volumetric-haze LoRA |
| `exp_vaporwave_pastel` | SDXL + vaporwave LoRA | FLUX + synthwave | Retro-grid LoRA |
| `exp_3dcg_honey` | Nova 3DCG XL | RealCartoon3D | Dedicated ecosystem |
| `exp_risograph_zine` | SDXL + riso LoRA | FLUX + indie print LoRA | 2-color overprint LoRA |

**Platform reality.** For a production platform, the economical shape is:
- **2 self-hosted bases** (SDXL-Illustrious for anime/art, SDXL-realistic like Juggernaut or RealVis for photoreal)
- **1 premium API** (FLUX dev via fal.ai) for fallback on style misses
- **~30 LoRAs** (one or two per sub-dialect) — this is where the aesthetic specificity actually lives

Do not maintain 30 separate base checkpoints. The base-model × LoRA matrix is far more maintainable.

---

## 5. Implementation priority for crpg

A pragmatic "which aesthetics should we build first" ranking, based on **(narrative fit × audience demand × AI-model maturity × implementation cost)**.

### Tier 1 — Must-have for v1 (build these first)

**`jpr_urban_ol` (日系都市 OL 风)** — the most versatile JP-R dialect. Maps to forbidden-affair, power-dynamic, routine-with-twist genres, all of which are bread-and-butter for adult narrative platforms. AI model maturity is very high (BRA lineage). Low implementation risk.

**`ani_painterly_pixiv` (厚涂插画 Pixiv 风)** — covers the entire modern anime market via Pony Diffusion V6. One checkpoint gets you 80% of the anime use case. Audience demand is enormous (Pixiv ecosystem). No meaningful alternative.

**`wr_girl_next_door` (邻家女孩日常亲密风)** — the accessible, "real-person-feeling" Western photo dialect. Maps to mundane-intimacy, casual-hookup, dating-app-scenario narratives — which are the highest-volume narrative genres on amateur-adjacent adult platforms. AI model maturity is high (any realistic SDXL checkpoint).

### Tier 2 — Build in v1.1 to v1.3

**`jpr_housewife`** (`人妻`) — huge JP market, needs mature-face LoRA effort, but genre fit is sharp.

**`wr_penthouse_softfocus`** — distinctive "romantic-vintage" visual that differentiates from generic Western realistic output.

**`ani_cel_shaded_tv`** — TV anime feel, complements painterly-pixiv with different genre coverage (slice-of-life, coming-of-age).

**`ani_hmanga_linework`** — B&W manga mode; cheap to implement, high recognition value, connects to doujin aesthetic heritage.

**`art_schiele_expressionist`** — cheap (just an artist tag on Illustrious), extremely distinctive output; use for psychological-drama narrative mode.

**`exp_cyberpunk_neon`** — powerful for sci-fi/noir narratives; well-supported by multiple base checkpoints.

### Tier 3 — v2+ or aesthetic-module for power users

Remaining 16 entries. These are valuable for discerning users but do not move the needle on first-pass product-market fit.

### Tier 4 — Skip / research-depth insufficient for MVP

**`exp_risograph_zine`** — niche indie-queer audience, hard to get right without dedicated LoRA effort, unlikely to be a differentiator for mass-market crpg.

**`exp_vaporwave_pastel`** — aesthetic is strong but narrative affinity is narrow; rarely what a user needs.

**`vin_pinup_elvgren`** — cheery Americana doesn't match the dramatic-narrative core of crpg's likely content; niche.

---

## 6. Appendix — two surprises from the research

**Surprise 1: The Beardsley–Shunga loop.**
Aubrey Beardsley's late-1890s decadent black-ink erotica (the *Lysistrata* portfolio, *Salome*) was directly inspired by Edo shunga woodblock prints via Whistler and the broader Japonisme movement. The V&A collection documents this explicitly. **This means a single category — "pre-modern flat-ink print erotica" — can legitimately unify `vin_shunga_ukiyoe` and `vin_victorian_beardsley`**, despite their 150-year and 9000-km separation. More practically: a narrative set in Edo Japan that uses Beardsley's compositional sensibility is not anachronistic pastiche — it is recovering a real historical cross-pollination.

**Surprise 2: JP-R is a checkpoint-shaped category.**
The six JP-R sub-dialects in our taxonomy map almost one-to-one onto the LoRA ecosystem around the BRA (Beautiful Realistic Asians) checkpoint family. This is not a coincidence — the Japanese AI-image community has been doing this exact sub-classification work informally since 2023, naming LoRAs after settings (`jk_uniform`, `office_lady`, `housewife`, `onsen`, `analog_film`). Our taxonomy is partially *reverse-engineered from the tool ecosystem*, which suggests the industry has converged on this division through years of actual generation practice. The corresponding Western ecosystem has NOT converged this way — W-R tooling is organized by *lighting philosophy* (beauty-dish, softbox, film-emulation) rather than *setting*. This is a genuine cultural difference in how the two photo traditions think about aesthetic specificity, and crpg's architecture should reflect it: JP-R dialects are **setting-indexed**, W-R dialects are **lighting-indexed**.

---

## 7. Open research gaps

- **JAV studio aesthetic (`jpr_jav_studio`) research depth is medium.** Cinematography-specific literature on Japanese adult video is sparse in English-language academic sources. Conventions identified here are cross-validated against adjacent gravure/TV-drama sources and AI-community LoRA naming, but would benefit from dedicated industry-ethnographic research.
- **`exp_3dcg_honey` ecosystem is active but lightly documented.** Illusion Soft 3DCG aesthetic has enormous doujin presence but little taxonomic writing; classification here is pragmatic rather than canonical.
- **`art_yamamoto_heisei` artist-tag support is medium-reliable.** Illustrious XL/NoobAI XL may recognize "takato yamamoto" but output quality varies; a dedicated LoRA would be higher-quality than raw artist-tag pinning.
- **Queer/alt aesthetic coverage is thin.** This taxonomy is inherited from mainstream industry classifications. A second-pass taxonomy focused on queer / alternative / non-binary aesthetic dialects (overlapping but distinct — e.g. tumblr-2015 aesthetic, contemporary queer zine aesthetic, radical-erotic fine art per the Dazed 2020s piece) is a natural future expansion.

---

## 8. Source pointers (for human review, not citations)

The research behind this taxonomy drew on Wikipedia articles (ukiyo-e, shunga, erotic photography, glamour photography, Penthouse, Helmut Newton, Mapplethorpe, Schiele, Beardsley, Mucha, Sorayama, doujinshi), artist-focused sources (theartstory.org, artsy.net, artnet.com, artincontext.org), industry/technical sources (Civitai article corpus on Pony/Illustrious/NoobAI/BRA lineage, stable-diffusion-art.com), and dedicated scholarship (Tate, V&A articles on Beardsley; art-museum catalogs on Klimt, Schiele, Yamamoto).

File paths:
- Structured data: `/Users/lxxxxxx/个人项目/crpg/assets/daisy-narrative-core/visual-aesthetics.yaml`
- This document: `/Users/lxxxxxx/个人项目/crpg/assets/daisy-narrative-core/visual-aesthetic-axes.md`
