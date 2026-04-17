# VGAI — Visibility-Gated Attribute Injection

> **Rule**: A character attribute should be written into the image prompt **only** if the attribute's anchor body region is visible within the shot's framing.

## Why the rule exists

On Grok Imagine Pro (likely most diffusion t2i), writing an attribute that is anatomically outside the current framing triggers a failure mode. The model does NOT hallucinate the attribute on the wrong body part. It does something more systematic:

## The 9 failure modes

| # | Name | Behavior | Trigger example |
|---|------|----------|-----------------|
| 1 | **Framing Expansion** | Model widens the shot to include the attribute's anchor | `CU face + pantyhose` → becomes 3/4 body |
| 2 | **Attribute Drop** | Model silently ignores the attr | `feet ECU + eye_detail` |
| 3 | **Composite Cheating** | Model jams disparate body parts in one frame | `feet ECU + earring` → foot + face-with-earring split frame |
| 4 | **Proxy Substitution** | Attribute color/texture migrates to a visible region | `CU face + red toenails` → red appears on fingernails |
| 5 | **Anatomical Relocation** | Figurative attrs (tattoos) move to visible region | `CU face + ankle tattoo` → tattoo appears on shoulder |
| 6 | **Wardrobe Modification** | "(covered by shirt)" / "(hidden)" parentheticals are stripped | `tattoo covered by shirt` → shirt opens |
| 7 | **Pose Rewrite** | Model changes the pose to expose the attribute | `hands in pockets + red nails` → hands come out |
| 8 | **Lighting Rewrite** | Silhouette / backlight overridden to light the attr | `silhouette + all attrs` → fully lit figure |
| 9 | **Mutex Split** | Conflicting mutex attrs render one per body side | `pantyhose + bare toes` → left leg pantyhose, right leg bare |

## The universal takeaway

> **Writing an attribute is a commitment to render it.**
>
> The model WILL render it — by reshaping framing, pose, lighting, wardrobe, or anatomy if needed.
>
> Therefore: **do not rely on any of the following as suppressors**:
> - Pose ("hands in pockets")
> - Covering ("under her coat")
> - Framing ("CU face only")
> - Lighting ("in silhouette")
> - Parentheticals ("(not shown)", "(off-screen)")
>
> **If you don't want it visible, don't write it.**

## Application in the Director workflow

For each shot:

1. Pick `wardrobe_state` from the character sheet.
2. Expand into full `attrs` list.
3. Look up `visible_regions = FRAMING_REGION_MAP[framing]` (see framing-region-map.yaml).
4. Filter: keep only attrs whose `anchor ∈ visible_regions`.
5. Inject filtered attrs into the prompt.
6. Drop everything else (do not mention them, even in negation).

## Mutex rule (derived from Mode 9)

If a wardrobe_state or shot design has two attrs in a **mutex group** (e.g., pantyhose vs. barefoot-toenails), **pick ONE** before applying VGAI. Never inject both.

## Empirical validation

VGAI was validated across 5 rounds / 113 shots / $7.98 on Grok Imagine Pro:
- v1 (22 shots): established the rule on 5 attributes × 9 framings
- v2 (21 shots): generalized to 5 novel attributes + multi-character + pose-dependent
- v3 (28 shots): scene variety stress — env/lighting/framing × scene
- v4 (18 shots): narrative moments + specialty ECUs
- v5 (6 shots): leg-boundary confirmation

All 9 failure modes reproduced with controlled experiments. Research artifacts at `research/pipeline-simulation/vgating-*/`.
