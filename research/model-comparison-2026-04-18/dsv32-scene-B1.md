[
  {
    "shot_id": "shot_1",
    "camera_framing": "ws_establishing",
    "pose": "wide shot of a hotel bed at dawn, two figures lying on crumpled white sheets, dim room with a faint red neon glow from the distant window",
    "wardrobe_state_used": "intimate_undressed",
    "vgai_injected_attrs": [],
    "vgai_dropped_attrs_with_reason": [
      "bedsheet_draped: anchor 'torso' not in framing.visible_regions []",
      "red_lipstick: anchor 'face' not in framing.visible_regions []"
    ],
    "final_prompt": "Wide shot of a hotel bed at dawn, two figures lying on crumpled white sheets, dim room with a faint red neon glow from the distant window."
  },
  {
    "shot_id": "shot_2",
    "camera_framing": "ms_waist_up",
    "pose": "medium shot of two people lying in bed, Su Wan, a 28-year-old Chinese woman with pale skin and long black hair, lying on her side with her face resting on a pillow, eyes half-open, lips slightly parted, Lin Ze lying facing her, his hand resting gently on her bare shoulder, looking at her",
    "wardrobe_state_used": "intimate_undressed",
    "vgai_injected_attrs": ["bedsheet_draped"],
    "vgai_dropped_attrs_with_reason": [
      "red_lipstick: removed by intimate_moment state"
    ],
    "final_prompt": "Medium shot of two people lying in bed, Su Wan, a 28-year-old Chinese woman with pale skin and long black hair, lying on her side with her face resting on a pillow, eyes half-open, lips slightly parted, a white bedsheet draped over her torso, Lin Ze lying facing her, his hand resting gently on her bare shoulder, looking at her."
  },
  {
    "shot_id": "shot_3",
    "camera_framing": "cu_face",
    "pose": "close-up of Su Wan's face, a 28-year-old Chinese woman with pale skin, long black hair parted in the middle, brown eyes with long eyelashes, soft jawline, resting on a pillow, eyes half-open, lips slightly parted, expression serene",
    "wardrobe_state_used": "intimate_undressed",
    "vgai_injected_attrs": [],
    "vgai_dropped_attrs_with_reason": [
      "red_lipstick: removed by intimate_moment state",
      "bedsheet_draped: anchor 'torso' not in framing.visible_regions ['face', 'ear', 'neck']"
    ],
    "final_prompt": "Close-up of Su Wan's face, a 28-year-old Chinese woman with pale skin, long black hair parted in the middle, brown eyes with long eyelashes, soft jawline, resting on a pillow, eyes half-open, lips slightly parted, expression serene."
  },
  {
    "shot_id": "shot_4",
    "camera_framing": "hand_ecu",
    "pose": "extreme close-up of a man's hand resting gently on a woman's bare shoulder, soft skin, intimate touch",
    "wardrobe_state_used": "intimate_undressed",
    "vgai_injected_attrs": [],
    "vgai_dropped_attrs_with_reason": [
      "red_fingernails: anchor 'hand' is Lin Ze's hand, not Su Wan's",
      "bedsheet_draped: anchor 'torso' not in framing.visible_regions ['hand']",
      "red_lipstick: anchor 'face' not in framing.visible_regions ['hand']"
    ],
    "final_prompt": "Extreme close-up of a man's hand resting gently on a woman's bare shoulder, soft skin, intimate touch."
  },
  {
    "shot_id": "shot_5",
    "camera_framing": "cu_face",
    "pose": "close-up of Lin Ze's face looking at Su Wan, his gaze soft, intimate moment",
    "wardrobe_state_used": "intimate_undressed",
    "vgai_injected_attrs": [],
    "vgai_dropped_attrs_with_reason": [
      "red_lipstick: removed by intimate_moment state",
      "bedsheet_draped: anchor 'torso' not in framing.visible_regions ['face', 'ear', 'neck']"
    ],
    "final_prompt": "Close-up of Lin Ze's face looking at Su Wan, his gaze soft, intimate moment."
  },
  {
    "shot_id": "shot_6",
    "camera_framing": "hand_ecu",
    "pose": "extreme close-up of two hands intertwined on white bedsheets, intimate touch, fingers loosely holding each other",
    "wardrobe_state_used": "intimate_undressed",
    "vgai_injected_attrs": [],
    "vgai_dropped_attrs_with_reason": [
      "red_fingernails: anchor 'hand' not visible for injection (focus is on intertwined hands, not individual nails)",
      "bedsheet_draped: anchor 'torso' not in framing.visible_regions ['hand']",
      "red_lipstick: anchor 'face' not in framing.visible_regions ['hand']"
    ],
    "final_prompt": "Extreme close-up of two hands intertwined on white bedsheets, intimate touch, fingers loosely holding each other."
  }
]