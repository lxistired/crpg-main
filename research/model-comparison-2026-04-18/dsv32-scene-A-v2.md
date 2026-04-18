[
  {
    "shot_id": "shot_1",
    "camera_framing": "ws_establishing",
    "pose": "Su Wan walks out of the office building onto the busy evening street.",
    "wardrobe_state_used": "public_formal",
    "vgai_injected_attrs": [],
    "vgai_dropped_attrs_with_reason": "All attributes dropped because framing is 'ws_establishing' (人物太小，不注入任何 attr).",
    "final_prompt": "wide establishing shot, evening, Su Wan, a 28-year-old Chinese woman with long black hair parted in the middle past her shoulders, fair skin, brown eyes with long eyelashes, soft jawline, walks out of a modern office building onto a busy city street, wearing a black pencil skirt, sheer black tights, and black ankle boots, public_formal attire."
  },
  {
    "shot_id": "shot_2",
    "camera_framing": "ms_waist_up",
    "pose": "Su Wan stops at a flower stall by a subway exit, looking at the blooms.",
    "wardrobe_state_used": "public_formal",
    "vgai_injected_attrs": ["black_pencil_skirt", "sheer_black_tights"],
    "vgai_dropped_attrs_with_reason": "red_fingernails (anchor: hand) - KEEP (pose-dependent but default KEEP). red_lipstick (anchor: face) - KEEP. stocking_toes and black_ankle_boots are in mutex_group; black_ankle_boots is visually dominant for 'ms_waist_up' framing where foot is not in visible_regions, so stocking_toes is dropped due to mutex conflict.",
    "final_prompt": "medium shot, waist-up, Su Wan, a 28-year-old Chinese woman with long black hair parted in the middle past her shoulders, fair skin, brown eyes with long eyelashes, soft jawline, stops at a vibrant flower stall by a subway exit, looking at colorful blooms, wearing a black pencil skirt and sheer black tights, red lipstick on her lips, red fingernails on her hands, public_formal attire, evening street scene."
  },
  {
    "shot_id": "shot_3",
    "camera_framing": "hand_ecu",
    "pose": "A man's hand offers a business card, Su Wan's hand reaches out to take it, her fingers trembling slightly.",
    "wardrobe_state_used": "public_formal",
    "vgai_injected_attrs": ["red_fingernails"],
    "vgai_dropped_attrs_with_reason": "black_pencil_skirt (anchor: torso), sheer_black_tights (anchor: leg), stocking_toes (anchor: foot), black_ankle_boots (anchor: foot) - dropped because anchor body regions not in framing.visible_regions for 'hand_ecu'. red_lipstick (anchor: face) - dropped because anchor body region not in framing.visible_regions for 'hand_ecu'.",
    "final_prompt": "extreme close-up shot, hands, a man's hand offering a white business card, Su Wan's hand reaching out to take it, her fingers trembling slightly, red fingernails on her fingers, shallow depth of field, focused on the hands and card."
  },
  {
    "shot_id": "shot_4",
    "camera_framing": "cu_face",
    "pose": "Close-up on Su Wan's face, showing tension and unease as she looks at the man.",
    "wardrobe_state_used": "public_formal",
    "vgai_injected_attrs": ["red_lipstick"],
    "vgai_dropped_attrs_with_reason": "red_fingernails (anchor: hand), black_pencil_skirt (anchor: torso), sheer_black_tights (anchor: leg), stocking_toes (anchor: foot), black_ankle_boots (anchor: foot) - dropped because anchor body regions not in framing.visible_regions for 'cu_face'.",
    "final_prompt": "close-up shot, face, Su Wan, a 28-year-old Chinese woman with long black hair parted in the middle past her shoulders, fair skin, brown eyes with long eyelashes, soft jawline, looking tense and uneasy, red lipstick on her lips, shallow depth of field, eye light, evening ambient light from street and flower stall."
  },
  {
    "shot_id": "shot_5",
    "camera_framing": "hand_ecu",
    "pose": "Extreme close-up of Su Wan's hand holding the business card, her gaze fixed on it.",
    "wardrobe_state_used": "public_formal",
    "vgai_injected_attrs": ["red_fingernails"],
    "vgai_dropped_attrs_with_reason": "black_pencil_skirt (anchor: torso), sheer_black_tights (anchor: leg), stocking_toes (anchor: foot), black_ankle_boots (anchor: foot) - dropped because anchor body regions not in framing.visible_regions for 'hand_ecu'. red_lipstick (anchor: face) - dropped because anchor body region not in framing.visible_regions for 'hand_ecu'.",
    "final_prompt": "extreme close-up shot, hand, Su Wan's hand holding a white business card, her gaze (implied) fixed on the card, red fingernails on her fingers, shallow depth of field, focused on the card and fingers, evening light."
  },
  {
    "shot_id": "shot_6",
    "camera_framing": "back_reveal_walking",
    "pose": "Su Wan turns and walks away from the flower stall, her back to the camera.",
    "wardrobe_state_used": "public_formal",
    "vgai_injected_attrs": ["black_pencil_skirt", "sheer_black_tights", "black_ankle_boots"],
    "vgai_dropped_attrs_with_reason": "red_fingernails (anchor: hand) - KEEP (hand in visible_regions). red_lipstick (anchor: face) - dropped because anchor body region not in framing.visible_regions for 'back_reveal_walking'. stocking_toes and black_ankle_boots are in mutex_group; black_ankle_boots is visually dominant (foot in visible_regions), so stocking_toes is dropped due to mutex conflict.",
    "final_prompt": "medium-long shot, back view, Su Wan, a 28-year-old Chinese woman with long black hair parted in the middle past her shoulders, fair skin, turns and walks away from a flower stall, her back to the camera, wearing a black pencil skirt, sheer black tights, and black ankle boots, red fingernails on her hands, evening street scene, motion blur on legs, shallow depth of field."
  }
]