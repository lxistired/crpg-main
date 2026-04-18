```json
[
  {
    "shot_id": "establishing",
    "camera_framing": "full_body_standing",
    "pose": "walking out of modern office building, elegant posture",
    "wardrobe_state_used": "public_formal",
    "vgai_injected_attrs": ["black_pencil_skirt", "sheer_black_tights", "stocking_toes", "black_ankle_boots", "red_fingernails", "red_toenails", "red_lipstick"],
    "vgai_dropped_attrs_with_reason": [],
    "final_prompt": "28 year old Chinese woman Su Wan, shoulder length black hair center parted, fair skin, brown eyes with long eyelashes, soft jawline, wearing black pencil skirt, sheer black tights, black ankle boots, red fingernails, red lipstick, walking out of modern office building at dusk, elegant posture, cinematic establishing shot, natural evening light"
  },
  {
    "shot_id": "MS_flower_shop",
    "camera_framing": "ms_waist_up",
    "pose": "standing at flower stall, gently looking at flowers",
    "wardrobe_state_used": "public_formal",
    "vgai_injected_attrs": ["black_pencil_skirt", "sheer_black_tights", "red_fingernails", "red_lipstick"],
    "vgai_dropped_attrs_with_reason": [
      {"attr": "red_toenails", "reason": "foot not in ms_waist_up visible_regions"},
      {"attr": "black_ankle_boots", "reason": "foot not in ms_waist_up visible_regions"},
      {"attr": "stocking_toes", "reason": "foot not in ms_waist_up visible_regions"}
    ],
    "final_prompt": "28 year old Chinese woman Su Wan, shoulder length black hair center parted, fair skin, brown eyes with long eyelashes, soft jawline, wearing black pencil skirt, sheer black tights, red fingernails, red lipstick, standing at outdoor flower stall near subway exit, gently looking at colorful flowers, soft evening light, MS waist up shot"
  },
  {
    "shot_id": "hand_receiving_card_ECU",
    "camera_framing": "hand_ecu",
    "pose": "delicate hand reaching out to receive a business card, fingers slightly trembling",
    "wardrobe_state_used": "public_formal",
    "vgai_injected_attrs": ["red_fingernails"],
    "vgai_dropped_attrs_with_reason": [
      {"attr": "red_toenails", "reason": "foot not in hand_ecu visible_regions"},
      {"attr": "red_lipstick", "reason": "face not in hand_ecu visible_regions"},
      {"attr": "black_pencil_skirt", "reason": "torso not in hand_ecu visible_regions"},
      {"attr": "sheer_black_tights", "reason": "leg not in hand_ecu visible_regions"},
      {"attr": "black_ankle_boots", "reason": "foot not in hand_ecu visible_regions"},
      {"attr": "stocking_toes", "reason": "foot not in hand_ecu visible_regions"}
    ],
    "final_prompt": "extreme close up of elegant hand with long red fingernails, fingers slightly trembling as it receives a white business card from a male hand, soft natural light, highly detailed skin texture, cinematic ECU"
  },
  {
    "shot_id": "CU_facial_tension",
    "camera_framing": "cu_face",
    "pose": "tense expression with slightly widened eyes and pressed lips, looking away",
    "wardrobe_state_used": "public_formal",
    "vgai_injected_attrs": ["red_lipstick"],
    "vgai_dropped_attrs_with_reason": [
      {"attr": "red_fingernails", "reason": "hand not in cu_face visible_regions"},
      {"attr": "red_toenails", "reason": "foot not in cu_face visible_regions"},
      {"attr": "black_pencil_skirt", "reason": "torso not in cu_face visible_regions"},
      {"attr": "sheer_black_tights", "reason": "leg not in cu_face visible_regions"},
      {"attr": "black_ankle_boots", "reason": "foot not in cu_face visible_regions"},
      {"attr": "stocking_toes", "reason": "foot not in cu_face visible_regions"}
    ],
    "final_prompt": "close up of face of 28 year old Chinese woman Su Wan, shoulder length black hair center parted, fair skin, brown eyes with long eyelashes, soft jawline, red lipstick, tense expression with slightly widened eyes and pressed lips, looking away nervously, soft evening light, cinematic CU face shot"
  },
  {
    "shot_id": "hand_looking_at_card_ECU",
    "camera_framing": "hand_ecu",
    "pose": "hand holding and looking at a business card, fingers slightly trembling",
    "wardrobe_state_used": "public_formal",
    "vgai_injected_attrs": ["red_fingernails"],
    "vgai_dropped_attrs_with_reason": [
      {"attr": "red_toenails", "reason": "foot not in hand_ecu visible_regions"},
      {"attr": "red_lipstick", "reason": "face not in hand_ecu visible_regions"},
      {"attr": "black_pencil_skirt", "reason": "torso not in hand_ecu visible_regions"},
      {"attr": "sheer_black_tights", "reason": "leg not in hand_ecu visible_regions"},
      {"attr": "black_ankle_boots", "reason": "foot not in hand_ecu visible_regions"},
      {"attr": "stocking_toes", "reason": "foot not in hand_ecu visible_regions"}
    ],
    "final_prompt": "extreme close up of elegant hand with long red fingernails holding a white business card, fingers slightly trembling, soft natural light, highly detailed skin texture and card details, cinematic ECU"
  },
  {
    "shot_id": "leaving_back_view",
    "camera_framing": "back_reveal_walking",
    "pose": "walking away with elegant and slightly hurried posture",
    "wardrobe_state_used": "public_formal",
    "vgai_injected_attrs": ["black_pencil_skirt", "sheer_black_tights", "red_fingernails"],
    "vgai_dropped_attrs_with_reason": [
      {"attr": "red_toenails", "reason": "red_toenails anchor foot_top not clearly visible under black_ankle_boots"},
      {"attr": "red_lipstick", "reason": "face not in back_reveal_walking visible_regions"},
      {"attr": "stocking_toes", "reason": "foot_top covered by black_ankle_boots"}
    ],
    "final_prompt": "28 year old Chinese woman Su Wan seen from behind walking away, shoulder length black hair center parted, wearing black pencil skirt, sheer black tights, black ankle boots, elegant and slightly hurried posture, subway exit area in background, cinematic back reveal walking shot, natural evening light"
  }
]
```