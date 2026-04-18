```json
[
    {
        "shot_id": "shot_1",
        "camera_framing": "ws_establishing",
        "pose": "wide shot of a hotel room at night, a bed with two figures intimately intertwined, silhouettes and shapes visible under rumpled bedsheets",
        "wardrobe_state_used": "intimate_undressed",
        "vgai_injected_attrs": [],
        "vgai_dropped_attrs_with_reason": [
            "bedsheet_draped: anchor 'torso' not in framing.visible_regions [] for 'ws_establishing'",
            "red_lipstick: anchor 'face' not in framing.visible_regions [] for 'ws_establishing'",
            "red_fingernails: anchor 'hand' not in framing.visible_regions [] for 'ws_establishing'",
            "red_toenails: anchor 'foot' not in framing.visible_regions [] for 'ws_establishing'"
        ],
        "final_prompt": "wide shot, hotel room at night, a bed with two figures intimately intertwined, silhouettes and shapes visible under rumpled bedsheets, dim lighting, intimate atmosphere"
    },
    {
        "shot_id": "shot_2",
        "camera_framing": "ms_waist_up",
        "pose": "medium shot, two-shot, Su Wan and Lin Ze intertwined, her leg hooked around his waist, his body over hers, their upper bodies pressed together, intimate moment",
        "wardrobe_state_used": "intimate_undressed",
        "vgai_injected_attrs": ["bedsheet_draped"],
        "vgai_dropped_attrs_with_reason": [
            "red_lipstick: removed by state 'intimate_undressed'",
            "red_fingernails: anchor 'hand' not in framing.visible_regions ['face', 'ear', 'neck', 'torso'] for 'ms_waist_up' (hand visibility depends on pose, but anchor region 'hand' is not guaranteed in this framing definition)",
            "red_toenails: anchor 'foot' not in framing.visible_regions ['face', 'ear', 'neck', 'torso'] for 'ms_waist_up'"
        ],
        "final_prompt": "medium shot, two-shot, a 28-year-old Chinese woman with long black center-parted hair past shoulders, fair skin, brown eyes, long eyelashes, soft jawline, and a man intimately intertwined, her leg hooked around his waist, his body over hers, their upper bodies pressed together, rumpled bedsheet draped partially covering her torso, intimate moment, sweat on skin, night, hotel room"
    },
    {
        "shot_id": "shot_3",
        "camera_framing": "cu_face",
        "pose": "close-up, Su Wan's face, head thrown back, lips slightly parted, eyes half-closed, expression of pleasure, sweat on skin",
        "wardrobe_state_used": "intimate_undressed",
        "vgai_injected_attrs": [],
        "vgai_dropped_attrs_with_reason": [
            "bedsheet_draped: anchor 'torso' not in framing.visible_regions ['face', 'ear', 'neck'] for 'cu_face'",
            "red_lipstick: removed by state 'intimate_undressed'",
            "red_fingernails: anchor 'hand' not in framing.visible_regions ['face', 'ear', 'neck'] for 'cu_face'",
            "red_toenails: anchor 'foot' not in framing.visible_regions ['face', 'ear', 'neck'] for 'cu_face'"
        ],
        "final_prompt": "close-up, a 28-year-old Chinese woman's face, long black center-parted hair past shoulders, fair skin, brown eyes, long eyelashes, soft jawline, head thrown back, lips slightly parted, eyes half-closed, expression of pleasure, sweat on skin, intimate moment, night"
    },
    {
        "shot_id": "shot_4",
        "camera_framing": "hand_ecu",
        "pose": "extreme close-up, Su Wan's hand gripping Lin Ze's muscular back, tension in her fingers, skin contact",
        "wardrobe_state_used": "intimate_undressed",
        "vgai_injected_attrs": ["red_fingernails"],
        "vgai_dropped_attrs_with_reason": [
            "bedsheet_draped: anchor 'torso' not in framing.visible_regions ['hand'] for 'hand_ecu'",
            "red_lipstick: anchor 'face' not in framing.visible_regions ['hand'] for 'hand_ecu'",
            "red_toenails: anchor 'foot' not in framing.visible_regions ['hand'] for 'hand_ecu'"
        ],
        "final_prompt": "extreme close-up, a woman's hand gripping a man's muscular back, tension in her fingers, skin contact, red fingernails, intimate moment"
    },
    {
        "shot_id": "shot_5",
        "camera_framing": "over_the_shoulder",
        "pose": "over-the-shoulder shot from behind Lin Ze, looking down at Su Wan beneath him, her face visible, intimate perspective",
        "wardrobe_state_used": "intimate_undressed",
        "vgai_injected_attrs": ["bedsheet_draped"],
        "vgai_dropped_attrs_with_reason": [
            "red_lipstick: removed by state 'intimate_undressed'",
            "red_fingernails: anchor 'hand' not in framing.visible_regions ['face', 'neck', 'torso'] for 'over_the_shoulder' (hand visibility depends on pose, but anchor region 'hand' is not guaranteed in this framing definition)",
            "red_toenails: anchor 'foot' not in framing.visible_regions ['face', 'neck', 'torso'] for 'over_the_shoulder'"
        ],
        "final_prompt": "over-the-shoulder shot from behind a man, looking down at a 28-year-old Chinese woman with long black center-parted hair past shoulders, fair skin, brown eyes, long eyelashes, soft jawline, beneath him, her face visible, rumpled bedsheet draped partially covering her torso, intimate perspective, night, hotel room"
    },
    {
        "shot_id": "shot_6",
        "camera_framing": "leg_ecu",
        "pose": "extreme close-up, rumpled bedsheet and entangled legs, skin and fabric, intimate detail",
        "wardrobe_state_used": "intimate_undressed",
        "vgai_injected_attrs": [],
        "vgai_dropped_attrs_with_reason": [
            "bedsheet_draped: anchor 'torso' not in framing.visible_regions ['leg'] for 'leg_ecu'",
            "red_lipstick: anchor 'face' not in framing.visible_regions ['leg'] for 'leg_ecu'",
            "red_fingernails: anchor 'hand' not in framing.visible_regions ['leg'] for 'leg_ecu'",
            "red_toenails: anchor 'foot' not in framing.visible_regions ['leg'] for 'leg_ecu'"
        ],
        "final_prompt": "extreme close-up, rumpled bedsheet and entangled legs, skin and fabric, intimate detail, night"
    }
]
```