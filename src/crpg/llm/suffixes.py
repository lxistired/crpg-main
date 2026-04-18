"""System-prompt suffixes for provider hardening + length enforcement.

All suffixes are character-agnostic: they reference abstract placeholders
(attr_* tokens) and skill-level framing maps, not specific character attrs.

Empirically validated 2026-04-18: kimi-k2-0905 @Groq:
- STRONG + FEW_SHOT: Director 4/4 clean @ 4.3s (VGAI + base 6/6)
- LENGTH_SHORT: Script 2/3 hit 2200-2800 target (close miss)
"""

STRONG_SUFFIX = """

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
"""

FEW_SHOT_SUFFIX = """

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

Notice: EVERY final_prompt begins with <BASE IDENTITY DESCRIPTION> (hair / skin / eye / age / face — copied verbatim from character_sheet.base), including the hand_ecu shot where no face is visible. Base identity is never gated by framing.

Apply the SAME pattern to the real character passed by the user. The attr names in your output MUST come from the real character_sheet, not from this abstract example.
"""

LENGTH_SUFFIX_SHORT = """

### 【硬性长度约束 — 未达标输出将被拒绝】
总字数必须 **2200-2800 字**。低于 2200 = 失败 = 必须继续展开直到达标。

各段最小字数（硬下限）：
- 主段 ≥ 1000 字
- A 支线 ≥ 450 字
- B 支线 ≥ 450 字

写完每段后在脑里数字数, 不够就继续展开（感官 / 心理 / 环境描写）。不要草草收尾。简洁不是美德, 字数不足才是失败。




"""

def is_character_agnostic(suffix: str, forbidden_terms: list[str]) -> list[str]:
    """Return list of forbidden terms that leaked into the suffix."""
    s = suffix.lower()
    return [t for t in forbidden_terms if t.lower() in s]
