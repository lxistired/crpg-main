"""Final full-story render: 'The Informant' — 18-shot narrative arc.

Applies VGAI v5 methodology: attributes gated per framing; no over-injection;
no reliance on pose/covering/lighting as suppressors; mutex respected.
"""

ANIME_PREAMBLE = """Modern Japanese manga / seinen anime illustration, digital painterly style with cel-shaded highlights and expressive line work. Noir-romantic Chinese urban thriller. Saturated teal shadows and crimson accents, dramatic rim lighting, slight atmospheric grain. Cinematic composition with confident framing."""

# Minimal character bases — only region-independent identifiers
SU_WAN = "Su Wan: 28, Chinese, long straight black hair parted to one side falling to collarbone, fair skin, dark brown expressive eyes, soft jawline."
LIN_ZE = "Lin Ze: mid-30s, Chinese, short black hair, stern dark eyes, angular jaw with light stubble, tired handsome face."
MEIJIE = "Meijie: 50s Chinese woman, hair in tight silver-streaked chignon, sharp high cheekbones, commanding presence."

# Attribute fragments
A = {
    "su_lips":       "Su Wan wears bold red lipstick.",
    "su_nails":      "Su Wan's fingernails have glossy red polish.",
    "su_earring":    "Su Wan wears a small jade teardrop earring on her exposed ear.",
    "su_pantyhose":  "Su Wan's legs are in sheer black full-length pantyhose (seamless waist-to-toe).",
    "su_toes":       "Su Wan's bare feet show glossy red toenail polish.",
    "me_lips":       "Meijie wears deep plum lipstick.",
    "me_earring":    "Meijie wears jade drop earrings.",
    "me_cigarette":  "Meijie holds a lit cigarette between her closed painted lips, smoke curling up.",
    "me_cheongsam":  "Meijie wears an emerald-green silk cheongsam.",
    "lz_watch":      "Lin Ze wears a steel wristwatch on his left wrist.",
    "lz_tie":        "Lin Ze wears a rumpled off-white dress shirt with a loosened charcoal tie.",
}

SHOTS = [
    # === ACT 1: SETUP ===
    {
        "id": "01_establishing_ws_city",
        "aspect": "21:9",
        "body": "EXTREME WIDE SHOT, cinematic establishing. Shanghai at 2am, heavy rain, teal-slick streets reflecting red and magenta neon. A cluster of midrise buildings with Chinese signage '夜上海' in neon red on one tower. A single dim yellow window glows in a side alley building. Streetlamps smear through wet mist. No characters — pure atmosphere.",
    },
    {
        "id": "02_su_wan_arrival_entrance",
        "aspect": "9:16",
        "body": f"{SU_WAN}\n{A['su_lips']}\n{A['su_earring']}\n{A['su_nails']}\n{A['su_pantyhose']}\nFULL-LENGTH shot, 9:16 vertical. Su Wan walks in the rain toward the entrance of a Shanghai nightclub. She wears a form-fitting black cocktail dress with thin straps, sheer black pantyhose, and black stiletto heels. One red-nailed hand holds a small clutch; the other lifts slightly to shield her face from the rain. Neon red 'LOUNGE' sign glowing above the entrance door. Her face in 3/4 profile, determined expression.",
    },
    {
        "id": "03_su_wan_vanity_mirror_prep",
        "aspect": "3:2",
        "body": f"{SU_WAN}\n{A['su_lips']}\n{A['su_earring']}\n{A['su_nails']}\nMEDIUM shot. Su Wan seated at a vanity with a ring of amber bulbs, leaning forward toward her own reflection in the large oval mirror. Her red-nailed right hand holds a tube of red lipstick near her mouth; her left hand steadies on the vanity edge. Jade earring visible, concentrated expression in the mirror reflection. Faded rose floral wallpaper behind. One cigarette burning in an ashtray on the vanity.",
    },
    {
        "id": "04_meijie_door_enters",
        "aspect": "4:3",
        "body": f"{MEIJIE}\n{A['me_lips']}\n{A['me_earring']}\n{A['me_cigarette']}\n{A['me_cheongsam']}\nMEDIUM shot, low-key lighting. Meijie pushes open a beaded door curtain and steps into the backstage room. The beaded curtain sways behind her. Frame from slightly low angle making her look powerful. She wears an emerald-green silk cheongsam with gold embroidery. Hair in tight silver-streaked chignon. Her eyes are sharp, fixed on someone off-frame right. Smoke from her cigarette drifts up past her face.",
    },
    {
        "id": "05_backstage_2shot_tense",
        "aspect": "16:9",
        "body": f"{SU_WAN}\n{MEIJIE}\n{A['su_lips']}\n{A['su_earring']}\n{A['su_nails']}\n{A['me_lips']}\n{A['me_earring']}\n{A['me_cigarette']}\n{A['me_cheongsam']}\nMEDIUM two-shot. Backstage dressing room. Meijie seated at the vanity (left of frame) looking UP AND RIGHT at Su Wan. Su Wan stands to her right, LEANING DOWN, LOOKING DIRECTLY AT MEIJIE'S FACE. Tense mutual gaze between them. Amber vanity bulbs behind Meijie cast warm glow. Faded rose wallpaper. Magenta stage light bleeding through the doorway at far right.",
    },
    {
        "id": "06_ecu_envelope_pass",
        "aspect": "21:9",
        "body": f"{A['su_nails']}\nEXTREME CLOSE-UP insert shot. Two Chinese women's hands. LEFT: an older woman's manicured hand (plum polish, older skin) extending a thin manila envelope across a dark wood surface. RIGHT: a younger woman's hand (glossy red nails, slimmer fingers) accepting the envelope, two fingers curling around its edge. Warm amber vanity light. Shallow depth of field, envelope crystal sharp. No faces, no bodies.",
    },

    # === ACT 2: MIDPOINT ===
    {
        "id": "07_bathroom_cavity_ms",
        "aspect": "3:2",
        "body": f"{SU_WAN}\n{A['su_lips']}\n{A['su_nails']}\nMEDIUM shot, hip-up. Small old-city Chinese apartment bathroom, dim single-bulb lighting. Su Wan stands at a round hinged bathroom mirror, mirror SWUNG OPEN on its hinge revealing a wall cavity. Her red-nailed right hand reaches INTO the cavity holding a small black waterproof pouch, about to tuck it in. Her left hand steadies on the tile wall. She wears a loose white button-up shirt (sleeves rolled). 3/4 profile face with concentrated serious expression. Rain-streaked window behind showing distant neon.",
    },
    {
        "id": "08_ecu_pouch_into_cavity",
        "aspect": "4:3",
        "body": f"{A['su_nails']}\nEXTREME CLOSE-UP insert. A slim woman's hand with glossy red nail polish pushing a small black waterproof zipped pouch into a dark rectangular hole in a tiled bathroom wall. The round mirror edge visible at frame left. Only hand, pouch, cavity, tile — no face, no body. Single bulb overhead light.",
    },
    {
        "id": "09_interrogation_2shot_ms",
        "aspect": "16:9",
        "body": f"{SU_WAN}\n{LIN_ZE}\n{A['su_lips']}\n{A['su_earring']}\n{A['su_nails']}\n{A['lz_tie']}\nMEDIUM two-shot. A modern Chinese police interrogation room at night. Su Wan seated on the left side of a brushed steel table in her black dress. Lin Ze seated opposite on the right in rumpled off-white shirt with loosened tie. Both lean slightly toward each other, LOCKED EYES. Su Wan's red-nailed hand rests on a manila folder on the table; Lin Ze's hand on a paper cup. Red venetian-blind neon shadows cut diagonal bars across both. One-way observation mirror on back wall.",
    },
    {
        "id": "10_cu_lin_ze_grave",
        "aspect": "4:3",
        "body": f"{LIN_ZE}\nCLOSE-UP. Lin Ze's face and upper shoulders. Stern tired eyes, jaw set hard, faint stubble, a bead of sweat at his temple from the hot interrogation lamp. He looks VIEWER-LEFT toward off-screen Su Wan. Red neon bar of light crossing his face diagonally. Off-white shirt collar and loosened charcoal tie visible. Emotional weight — he knows what he's asking her.",
    },
    {
        "id": "11_cu_su_wan_tear_decision",
        "aspect": "4:3",
        "body": f"{SU_WAN}\n{A['su_lips']}\n{A['su_earring']}\nCLOSE-UP. Su Wan's face and neck, a single tear welling at the lower lid of her right eye, not yet falling. Her red-lipped mouth pressed tight, jaw rigid trying not to cry. Jade earring catching red neon. Her eyes looking VIEWER-RIGHT toward off-screen Lin Ze. The moment of deciding to turn informant. Neon-shadow bars crossing her cheek. Still fierce behind the vulnerability.",
    },
    {
        "id": "12_walk_out_back_reveal",
        "aspect": "9:16",
        "body": f"{SU_WAN}\n{A['su_lips']}\n{A['su_earring']}\n{A['su_nails']}\n{A['su_pantyhose']}\nFULL-LENGTH shot from behind, 9:16 vertical. Su Wan walks away from camera down a long dim hallway of the police station, her BACKLESS black dress exposing the line of her spine and shoulder blades. Sheer black pantyhose from mid-thigh down to her black stiletto heels. She turns her head LEFT over her shoulder, 3/4 profile face visible — red lips, jade earring, one tear trail on her cheek. Her red-nailed left hand rests on her hip. Dim sconces lining the hallway, single door at far end lit red.",
    },

    # === ACT 3: CLIMAX + RESOLUTION ===
    {
        "id": "13_alley_ws_distance",
        "aspect": "21:9",
        "body": "EXTREME WIDE SHOT. A narrow Shanghai alleyway at 2am, heavy rain. Red lanterns hanging along the alley walls, wet cobblestones reflecting neon. At the far end of the alley, TWO distant figures face each other — both in dark coats, both small in the frame (figures occupy ~15% of vertical height). Steam rising from a vent between them. Behind them: Chinese signage '夜市' glowing faintly. No character detail — pure atmospheric tension.",
    },
    {
        "id": "14_alley_confrontation_2shot",
        "aspect": "16:9",
        "body": f"{SU_WAN}\n{MEIJIE}\n{A['su_lips']}\n{A['su_earring']}\n{A['su_nails']}\n{A['me_lips']}\n{A['me_earring']}\n{A['me_cigarette']}\nMEDIUM two-shot. Rainy alley at 2am. Su Wan faces Meijie across 2 meters of wet cobblestones. Both wear dark trench coats buttoned to collar. Their faces tilted toward each other, expressions stern. Su Wan's right hand is INSIDE her coat pocket. Meijie's cigarette glows between her closed painted lips. Rain falls between them in visible streaks. Red lantern light bleeding across both their faces.",
    },
    {
        "id": "15_ecu_hand_knife_reveal",
        "aspect": "4:3",
        "body": f"{A['su_nails']}\nEXTREME CLOSE-UP insert. A woman's hand with glossy red nail polish, wet with rain, sliding INSIDE a dark trench coat pocket. At the edge of the pocket, the edge of a small folding knife's blade just barely catches the red neon light. Droplets on the coat fabric. Shallow depth of field, hand and blade crystal sharp, background alley blurred red-black. No face.",
    },
    {
        "id": "16_lin_ze_silhouette_arrival",
        "aspect": "16:9",
        "body": "WIDE SHOT. Rainy Shanghai alley at 2am, viewed from deep in the alley looking toward its entrance. At the entrance, silhouetted against bright street neon behind him, a MAN in a long coat stands with feet planted wide, right arm raised holding a pistol pointed forward into the alley. He is PURE SILHOUETTE — only his dark outline visible against the backlight, no facial details, no clothing details. Rain streaks between him and camera. Red neon signage blazing behind him.",
    },
    {
        "id": "17_rooftop_aftermath_full",
        "aspect": "9:16",
        "body": f"{SU_WAN}\n{A['su_lips']}\n{A['su_earring']}\n{A['su_nails']}\n{A['su_pantyhose']}\nFULL-LENGTH shot, 9:16 vertical. Sunrise is starting. Su Wan stands at the edge of a building rooftop, Shanghai skyline and distant neon fading behind her in pale blue-pink dawn light. Wind blows her hair sideways. Form-fitting black dress hem fluttering. Sheer black pantyhose visible, black stiletto heels planted shoulder-width. Her face lifted, looking out over the city. One red-nailed hand hanging loose at her side, the other touching the railing. Trench coat abandoned on the rooftop behind her. End of a long night.",
    },
    {
        "id": "18_bonus_sofa_dawn_final",
        "aspect": "3:2",
        "body": f"{SU_WAN}\n{A['su_nails']}\n{A['su_toes']}\nMEDIUM shot slightly from above. A small old-city Chinese apartment at dawn. Su Wan asleep on a worn dark leather sofa, wearing only an OPEN oversized white men's dress shirt (Lin Ze's). NO pantyhose — her BARE legs curled up in fetal position beneath her. Red-polished fingernails on her hand tucked under her cheek. Red toenail polish visible on her bare feet. Lips softly parted in sleep, eyelashes casting shadow. Rain-streaked window behind showing pale blue-pink dawn. Low wooden table: a single mug, creased newspaper, dead ashtray. Dust motes in a dawn beam. Peaceful aftermath.",
    },
]


def build_prompt(shot):
    return ANIME_PREAMBLE + "\n\n" + shot["body"]
