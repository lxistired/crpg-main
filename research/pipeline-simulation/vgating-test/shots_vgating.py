"""VGAI (Visibility-Gated Attribute Injection) test: 22 shots."""

ANIME_PREAMBLE = """Modern Japanese manga / seinen anime illustration, digital painterly style with cel-shaded highlights. Mood: noir-romantic Chinese urban thriller. Saturated teal shadows and crimson accents, rim lighting, slight grain. Cinematic composition."""

# Minimal character sheet — ONLY region-independent attributes (hair, skin, eye color, face structure)
SU_WAN_MIN = "Su Wan: 28, Chinese, long straight black hair parted to one side falling to collarbone, fair skin, dark brown expressive eyes, soft jawline."

# Attribute fragments (each tied to a specific body region — NOT in the base sheet)
ATTRS = {
    "lips": "She wears bold red lipstick.",
    "nails": "Her fingernails have glossy red polish.",
    "earring": "She wears small jade teardrop earrings on both ears.",
    "pantyhose": "Her legs are covered in sheer black full-length pantyhose (seamless waist-to-toe tights).",
    "toes": "Her feet are bare with glossy red toenail polish matching her fingernails.",
    # Special test: eye detail attribute
    "eye_detail": "Her iris is a deep warm brown with faint golden flecks, long eyelashes casting shadow.",
}

# Framings — describe camera+scene only, no attributes
FRAMES = {
    "eye_ecu": "EXTREME CLOSE-UP, her right eye fills most of the frame. Detailed iris, pupil, lashes visible. Soft indirect light. Macro lens look.",
    "hand_ecu": "EXTREME CLOSE-UP of her right hand resting on a dark wooden table surface. Fingers relaxed. Shallow depth of field. No face in frame.",
    "ear_cu": "3/4 PROFILE CLOSE-UP. Her left ear, cheek, jawline visible. Hair pulled back exposing the ear. Neutral side lighting.",
    "feet_ecu": "EXTREME CLOSE-UP of her two feet on a grey tile floor, toes angled toward camera. Only feet and lower ankles in frame.",
    "leg_ecu": "EXTREME CLOSE-UP of her legs from mid-thigh to mid-calf, standing. Only legs in frame, no face, no feet.",
    "cu_face": "CLOSE-UP of her face and neck, shoulders just entering frame, head tilted slightly. Neutral studio lighting.",
    "ms_waist": "MEDIUM SHOT, waist-up, seated at a small wooden table with hands folded in her lap. Window behind showing out-of-focus city light.",
    "full_body": "FULL-LENGTH standing shot, head to toe fully in frame. She wears a form-fitting black dress with short sleeves, and strappy black heels. Standing in a plain grey concrete room.",
    "full_body_barefoot": "FULL-LENGTH standing shot, head to toe fully in frame. She wears a form-fitting black dress with short sleeves. Her feet are bare (no shoes). Standing in a plain grey concrete room.",
}

# Shot specs: (id, frame_key, attrs_list)
SHOTS = [
    # === Group M: single attribute × framing (matrix) ===
    ("m01_eye_in_eye_ecu",        "eye_ecu",            ["eye_detail"]),
    ("m02_eye_in_feet_ecu",       "feet_ecu",           ["eye_detail"]),   # should NOT render
    ("m03_nails_in_hand_ecu",     "hand_ecu",           ["nails"]),
    ("m04_nails_in_eye_ecu",      "eye_ecu",            ["nails"]),        # should NOT render
    ("m05_earring_in_ear_cu",     "ear_cu",             ["earring"]),
    ("m06_earring_in_feet_ecu",   "feet_ecu",           ["earring"]),      # should NOT render
    ("m07_pantyhose_in_leg_ecu",  "leg_ecu",            ["pantyhose"]),
    ("m08_pantyhose_in_cu_face",  "cu_face",            ["pantyhose"]),    # KEY: artifact test
    ("m09_pantyhose_in_full_body","full_body",          ["pantyhose"]),
    ("m10_toes_in_feet_ecu",      "feet_ecu",           ["toes"]),
    ("m11_toes_in_cu_face",       "cu_face",            ["toes"]),         # should NOT render
    ("m12_toes_in_fb_barefoot",   "full_body_barefoot", ["toes"]),

    # === Group K: kitchen sink (all 5 visible attrs in every framing) ===
    ("k01_allattrs_eye_ecu",      "eye_ecu",            ["lips","nails","earring","pantyhose","toes"]),
    ("k02_allattrs_cu_face",      "cu_face",            ["lips","nails","earring","pantyhose","toes"]),
    ("k03_allattrs_ms_waist",     "ms_waist",           ["lips","nails","earring","pantyhose","toes"]),
    ("k04_allattrs_full_body",    "full_body",          ["lips","nails","earring","pantyhose","toes"]),

    # === Group Z: zero attrs baseline ===
    ("z01_noattrs_full_body",     "full_body",          []),

    # === Group G: correctly visibility-gated injection ===
    ("g01_gated_eye_ecu",         "eye_ecu",            []),  # no attr applies
    ("g02_gated_cu_face",         "cu_face",            ["lips","earring"]),
    ("g03_gated_ms_waist",        "ms_waist",           ["lips","earring","nails"]),
    ("g04_gated_full_body",       "full_body",          ["lips","earring","nails","pantyhose"]),
    ("g05_gated_fb_barefoot",     "full_body_barefoot", ["lips","earring","nails","toes"]),
]


def build_prompt(frame_key, attr_keys):
    frame = FRAMES[frame_key]
    attr_lines = "\n".join(ATTRS[k] for k in attr_keys)
    parts = [ANIME_PREAMBLE, SU_WAN_MIN]
    if attr_lines:
        parts.append(attr_lines)
    parts.append(frame)
    return "\n\n".join(parts)
