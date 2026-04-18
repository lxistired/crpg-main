# Occlusion — full / partial / none

A wardrobe item between the camera and a grooming attr changes whether and how the attr renders. This page defines the three branches the Director must route through.

The Skeleton skill emits two fields that drive this: `wardrobe_item.covers: list[str]` (which sub_anchors it fully occludes) and `grooming.sub_anchor: str | None` (where the grooming lives). The VGAI validator enforces the full-occlusion rule and will flag violations.

## Branch 1 — FULL occlusion → DROP

If `grooming.sub_anchor ∈ wardrobe_item.covers` and the wardrobe_item is injected in this shot, the grooming is not visible. **Drop it** and record reason `"occluded by <item_name>"`.

**Examples:**

| Wardrobe | Grooming | Rule |
|----------|----------|------|
| `closed_pumps` with `covers=[toes, foot_top_inner]` | `red_toenails` with `sub_anchor=toes` | DROP |
| `leather_gloves` with `covers=[fingernails, back_of_hand, palm]` | `red_fingernails` with `sub_anchor=fingernails` | DROP |
| `opaque_tights` with `covers=[thigh_front, thigh_back, knee, shin, calf]` | `calf_tattoo` with `sub_anchor=calf` | DROP |

**Do NOT** write sentences like "visible through the fabric", "showing beneath the glove", "faintly outlined" — these instruct the image model to open, sheerify, or remove the occluding item. The image model is not subtle about layer rendering; if you write the attr under any see-through rationalization, it WILL make the garment see-through or remove it.

## Branch 2 — PARTIAL occlusion → describe on non-occluded part

If `grooming.sub_anchor ∉ wardrobe_item.covers` (the item partially covers the anchor region but leaves the sub_anchor visible), inject the attr normally with a concrete location phrase anchored to the visible part.

**Examples:**

| Wardrobe | Grooming | Rule |
|----------|----------|------|
| `peep_toe_pumps` with `covers=[foot_top_inner]` (toes exposed) | `red_toenails` with `sub_anchor=toes` | INJECT as "red toenail polish on exposed toes through peep-toe opening" |
| `fingerless_gloves` with `covers=[back_of_hand, palm]` (fingers exposed) | `red_fingernails` with `sub_anchor=fingernails` | INJECT as "red nail polish on exposed fingertips past the glove edge" |

Partial occlusion is rare in typical wardrobe — most items either fully enclose (closed pumps, opaque tights) or fully leave visible (sandals, bare hands). Default: if unsure, treat as Branch 1 (drop) OR Branch 3 (inject) based on whether sub_anchor is listed in covers.

## Branch 3 — NO occlusion → inject

If no injected wardrobe item's `covers` list contains this grooming's `sub_anchor`, inject the attr directly with its standard value.

**Examples:**

| Wardrobe | Grooming | Rule |
|----------|----------|------|
| `sheer_black_tights` with `covers=[]` (transparent, occludes nothing) | `red_toenails` with `sub_anchor=toes` | INJECT normally; tights are transparent, the model handles see-through naturally |
| `sandals` with `covers=[]` | `red_toenails` with `sub_anchor=toes` | INJECT normally |
| `bare_hand` (or no glove at all) | `red_fingernails` | INJECT normally |

**Sheer fabrics are Branch 3, not Branch 1.** Sheer tights have `covers=[]` because the underlying skin / toenails / tattoos are supposed to be visible through transparent material. Describe the underlying attr without any "through the fabric" language — the model handles transparency fine if you just describe what's there.

## What NOT to do (banned rationalizations)

| Rationalization | Why it breaks | Use instead |
|-----------------|---------------|-------------|
| "red toenails visible through the fabric" | implies fabric is supposed to be see-through → Grok renders sheer where opaque was intended | drop the attr |
| "hint of red at the tips of her fingers, under the gloves" | implies gloves are fingerless → Grok opens the fingertips | drop the attr |
| "ankle tattoo faintly visible beneath the stocking" | implies sheer / translucent stocking → Grok weakens opacity | drop the attr |
| "her red lipstick visible in the gap between her lips" | micromanagement forces model to render lips parted | just "red lipstick" — no micromanagement |

## Validator enforcement

`validate_vgai` emits an `occlusion` violation if you inject a grooming whose sub_anchor is in any injected item's `covers`. Re-audit and drop, then re-validate until CLEAN. Never call `render_image` with unresolved occlusion violations.

## Quick decision tree

```
grooming G, injected items set I, G has sub_anchor S
  ↓
any item i in I with S ∈ i.covers?
  ↓ yes → FULL occlusion → DROP G, reason "occluded by i"
  ↓ no → is G still anchor-visible via framing? (Principle 4 VGAI)
         ↓ yes → INJECT G normally (Branch 3)
         ↓ no → DROP G, reason "anchor not in visible_regions"
```

Partial occlusion is a controller choice when the physics of the item leaves the sub_anchor exposed. Default to Branch 1 (drop) unless the wardrobe item's design explicitly exposes that sub_anchor (peep-toe, fingerless).
