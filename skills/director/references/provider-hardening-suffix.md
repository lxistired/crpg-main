# Provider Hardening Suffix

**Load when**: running Director against a backend whose default VGAI compliance is unreliable (e.g. OpenRouter `moonshotai/kimi-k2-0905` via Groq routing).

Some provider deployments optimize for throughput at the expense of instruction-following fidelity. Under default prompt language ("you should…"), these models tend to emit wardrobe descriptions from common-sense priors and ignore the `visible_regions` gating rule.

This file provides two drop-in system-prompt suffixes that empirically restore VGAI compliance. Zero character-specific hardcoding — suffixes reference the `framing-region-map` (skill-level config) and use abstract `attr_*` placeholders.

## Empirical validation

Tested on `moonshotai/kimi-k2-0905 @Groq` (the hardest case):

| config | latency | VGAI violations | base consistency |
|--------|---------|-----------------|------------------|
| default DIRECTOR_SYSTEM alone | ~4s | 7–11 per 6-shot list | 6/6 |
| + STRONG_SUFFIX | ~4.3s | 0 | 6/6 |
| + FEW_SHOT_SUFFIX | ~4.3s | 0 | 6/6 |
| + both (recommended) | ~4.3s | **0 × 4 iter** | **6/6 × 4 iter** |

4.3s is 14× faster than the Alibaba Qwen baseline (~61s) while matching compliance.

## How to use

Concatenate either suffix (or both) to the Director system prompt before the user message. Both are character-agnostic — no per-story edits needed.

```python
system = DIRECTOR_SYSTEM + STRONG_SUFFIX + FEW_SHOT_SUFFIX
```

Do not add either suffix when running against backends that already comply (e.g. `qwen/qwen3-max @Alibaba`, `moonshotai/kimi-k2.5 @Together`). They cost ~400 prompt tokens and provide no lift there.

## STRONG_SUFFIX (≈1,280 chars)

```text

### CRITICAL RULE (output will be rejected if violated)

For every shot, before writing vgai_injected_attrs, verify each attribute's anchor region is in the framing's visible_regions set. Use this reference table:

| framing | visible_regions |
|---------|-----------------|
| ws_establishing | {} (empty — subject too small) |
| cu_face | {face, ear, neck} |
| ms_waist_up | {face, ear, neck, torso, hand} |
| three_quarter_knee_up | {face, ear, neck, torso, hand, leg_upper} |
| full_body_standing | {face, ear, neck, torso, hand, leg, foot} |
| hand_ecu | {hand} |
| feet_ecu | {foot} |
| back_reveal_walking | {torso_back, hand, leg, foot} |

Procedure for each shot:
1. Look up visible_regions for the chosen camera_framing.
2. For each attr from character_sheet.persistent_grooming ∪ wardrobe_state.items:
   - If attr.anchor ∈ visible_regions → may inject.
   - If attr.anchor ∉ visible_regions → MUST NOT inject; add to dropped list with reason.
3. ws_establishing means vgai_injected_attrs MUST be an empty list [] (subject too small for any detail).
4. Mutex check: for each pair in character_sheet.mutex_groups, if both would survive step 2, pick the visually dominant one for the pose; the other goes to dropped.

Violating step 1-4 makes the entire output invalid.
```

## FEW_SHOT_SUFFIX (≈2,725 chars)

```text

### Canonical output pattern (abstract example — NOT copy these attr names)

Important: base identity (hair, skin, eye color, age, face shape) is ALWAYS in final_prompt regardless of framing. It is NEVER listed in vgai_injected_attrs or vgai_dropped (it's not a gated attribute).

Only GROOMING and WARDROBE items go through VGAI gating.

Suppose an abstract character with these GATED attrs:
- attr_LIP  (anchor: face)
- attr_NAIL (anchor: hand)
- attr_RING (anchor: hand)
- attr_SKIRT (anchor: torso)
- attr_HOSE  (anchor: leg)
- attr_TOENAIL (anchor: foot)
- attr_SHOE (anchor: foot)

And mutex_groups = [{attr_HOSE, attr_SHOE}, {attr_TOENAIL, attr_SHOE}].

Then the correct outputs look like:

```json
[
  {
    "shot_id": "example_ws",
    "camera_framing": "ws_establishing",
    "pose": "subject walks down street from a distance",
    "wardrobe_state_used": "some_state",
    "vgai_injected_attrs": [],
    "vgai_dropped_attrs_with_reason": ["all attrs dropped: ws_establishing visible_regions is empty"],
    "final_prompt": "<BASE IDENTITY DESCRIPTION>, walking down street, ws_establishing framing"
  },
  {
    "shot_id": "example_ms",
    "camera_framing": "ms_waist_up",
    "pose": "facing camera from waist up",
    "wardrobe_state_used": "some_state",
    "vgai_injected_attrs": ["attr_LIP", "attr_NAIL", "attr_RING", "attr_SKIRT"],
    "vgai_dropped_attrs_with_reason": [
      "attr_HOSE: leg not in visible_regions {face,ear,neck,torso,hand}",
      "attr_TOENAIL: foot not in visible_regions",
      "attr_SHOE: foot not in visible_regions"
    ],
    "final_prompt": "<BASE IDENTITY DESCRIPTION>, wearing attr_SKIRT, attr_LIP, attr_NAIL, attr_RING, ms_waist_up framing"
  },
  {
    "shot_id": "example_hand",
    "camera_framing": "hand_ecu",
    "pose": "extreme close-up on hand",
    "wardrobe_state_used": "some_state",
    "vgai_injected_attrs": ["attr_NAIL", "attr_RING"],
    "vgai_dropped_attrs_with_reason": [
      "attr_LIP: face not in visible_regions {hand}",
      "attr_SKIRT: torso not in visible_regions",
      "attr_HOSE: leg not in visible_regions",
      "attr_TOENAIL: foot not in visible_regions",
      "attr_SHOE: foot not in visible_regions"
    ],
    "final_prompt": "<BASE IDENTITY DESCRIPTION>, hand with attr_NAIL and attr_RING, hand_ecu framing"
  }
]
```

Notice: EVERY final_prompt begins with `<BASE IDENTITY DESCRIPTION>` (hair / skin / eye / age / face — copied verbatim from character_sheet.base), including the hand_ecu shot where no face is visible. Base identity is never gated by framing.

Apply the SAME pattern to the real character passed by the user. The attr names in your output MUST come from the real character_sheet, not from this abstract example.
```

## When to drop this reference

If a future model upgrade (e.g. kimi-k3 on Groq) achieves default VGAI compliance without suffix, delete this file and the one-line bullet in SKILL.md. This is a provider-specific remediation, not core methodology.
