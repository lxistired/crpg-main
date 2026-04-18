```json
[
  {
    "shot_id": 1,
    "camera_framing": "ws_establishing",
    "pose": "Su Wan walking out of a modern office building in the evening, city street background",
    "wardrobe_state_used": "public_formal",
    "vgai_injected_attrs": [],
    "vgai_dropped_attrs_with_reason": [
      "red_fingernails (anchor: hand) - anchor not in visible_regions []",
      "red_toenails (anchor: foot) - anchor not in visible_regions []",
      "red_lipstick (anchor: face) - anchor not in visible_regions []",
      "black_pencil_skirt (anchor: torso) - anchor not in visible_regions []",
      "sheer_black_tights (anchor: leg) - anchor not in visible_regions []",
      "stocking_toes (anchor: foot) - anchor not in visible_regions []",
      "black_ankle_boots (anchor: foot) - anchor not in visible_regions []"
    ],
    "final_prompt": "wide shot, establishing, a Chinese woman with long black center-parted hair walking out of a modern glass office building at dusk, city street with evening light, cinematic"
  },
  {
    "shot_id": 2,
    "camera_framing": "ms_waist_up",
    "pose": "Su Wan standing at a subway exit flower stall, looking down at colorful flowers, holding her bag",
    "wardrobe_state_used": "public_formal",
    "vgai_injected_attrs": [
      "black_pencil_skirt",
      "red_lipstick"
    ],
    "vgai_dropped_attrs_with_reason": [
      "red_fingernails (anchor: hand) - anchor not in visible_regions [face, ear, neck, torso]; hands are holding bag and may be visible but pose-dependent, assume not primary focus for attribute injection in MS",
      "red_toenails (anchor: foot) - anchor not in visible_regions [face, ear, neck, torso]",
      "sheer_black_tights (anchor: leg) - anchor not in visible_regions [face, ear, neck, torso]",
      "stocking_toes (anchor: foot) - anchor not in visible_regions [face, ear, neck, torso]",
      "black_ankle_boots (anchor: foot) - anchor not in visible_regions [face, ear, neck, torso]"
    ],
    "final_prompt": "medium shot, waist-up, a 28-year-old Chinese woman with long black center-parted hair, fair skin, brown eyes with long eyelashes, soft jawline, wearing red lipstick and a black pencil skirt, standing at a flower stall near a subway exit, looking at colorful blooms, holding a handbag, evening, cinematic lighting"
  },
  {
    "shot_id": 3,
    "camera_framing": "hand_ecu",
    "pose": "a man's hand offering a business card, Su Wan's hand reaching to take it, fingers slightly trembling",
    "wardrobe_state_used": "public_formal",
    "vgai_injected_attrs": [
      "red_fingernails"
    ],
    "vgai_dropped_attrs_with_reason": [
      "red_toenails (anchor: foot) - anchor not in visible_regions [hand]",
      "red_lipstick (anchor: face) - anchor not in visible_regions [hand]",
      "black_pencil_skirt (anchor: torso) - anchor not in visible_regions [hand]",
      "sheer_black_tights (anchor: leg) - anchor not in visible_regions [hand]",
      "stocking_toes (anchor: foot) - anchor not in visible_regions [hand]",
      "black_ankle_boots (anchor: foot) - anchor not in visible_regions [hand]"
    ],
    "final_prompt": "extreme close-up shot, hands, a woman's hand with red fingernails trembling slightly as it reaches to take a business card from a man's hand, shallow depth of field, dramatic"
  },
  {
    "shot_id": 4,
    "camera_framing": "cu_face",
    "pose": "Su Wan's face, tense expression, eyes slightly wide, looking at the stranger offering the card",
    "wardrobe_state_used": "public_formal",
    "vgai_injected_attrs": [
      "red_lipstick"
    ],
    "vgai_dropped_attrs_with_reason": [
      "red_fingernails (anchor: hand) - anchor not in visible_regions [face, ear, neck]",
      "red_toenails (anchor: foot) - anchor not in visible_regions [face, ear, neck]",
      "black_pencil_skirt (anchor: torso) - anchor not in visible_regions [face, ear, neck]",
      "sheer_black_tights (anchor: leg) - anchor not in visible_regions [face, ear, neck]",
      "stocking_toes (anchor: foot) - anchor not in visible_regions [face, ear, neck]",
      "black_ankle_boots (anchor: foot) - anchor not in visible_regions [face, ear, neck]"
    ],
    "final_prompt": "close-up shot, face, a 28-year-old Chinese woman with long black center-parted hair, fair skin, brown eyes with long eyelashes, soft jawline, wearing red lipstick, tense expression, eyes slightly wide, looking at someone off-camera, shallow depth of field, cinematic"
  },
  {
    "shot_id": 5,
    "camera_framing": "hand_ecu",
    "pose": "Su Wan's hand holding the business card, looking down at it",
    "wardrobe_state_used": "public_formal",
    "vgai_injected_attrs": [
      "red_fingernails"
    ],
    "vgai_dropped_attrs_with_reason": [
      "red_toenails (anchor: foot) - anchor not in visible_regions [hand]",
      "red_lipstick (anchor: face) - anchor not in visible_regions [hand]",
      "black_pencil_skirt (anchor: torso) - anchor not in visible_regions [hand]",
      "sheer_black_tights (anchor: leg) - anchor not in visible_regions [hand]",
      "stocking_toes (anchor: foot) - anchor not in visible_regions [hand]",
      "black_ankle_boots (anchor: foot) - anchor not in visible_regions [hand]"
    ],
    "final_prompt": "extreme close-up shot, hand, a woman's hand with red fingernails holding a white business card, looking down at it, shallow depth of field"
  },
  {
    "shot_id": 6,
    "camera_framing": "back_reveal_walking",
    "pose": "Su Wan walking away, back to camera, turning her body slightly as she leaves the flower stall",
    "wardrobe_state_used": "public_formal",
    "vgai_injected_attrs": [
      "black_pencil_skirt",
      "sheer_black_tights",
      "stocking_toes",
      "black_ankle_boots"
    ],
    "vgai_dropped_attrs_with_reason": [
      "red_fingernails (anchor: hand) - anchor in visible_regions [torso_back, hand, leg, foot] but hands may be in motion/partial, attribute injection for hand region is allowed; however, for a back shot focusing on walking away, the red fingernails may not be a prominent detail. Considering the framing and primary focus, we drop it.",
      "red_toenails (anchor: foot) - anchor in visible_regions [torso_back, hand, leg, foot] but sub_anchor foot_top is covered by black_ankle_boots (mutex), so dropped",
      "red_lipstick (anchor: face) - anchor not in visible_regions [torso_back, hand, leg, foot]"
    ],
    "final_prompt": "medium long shot, back reveal, a Chinese woman with long black hair walking away, wearing a black pencil skirt, sheer black tights, and black ankle boots, turning her body slightly as she leaves a flower stall, evening street, cinematic"
  }
]
```