from crpg.llm.suffixes import (
    STRONG_SUFFIX, FEW_SHOT_SUFFIX, LENGTH_SUFFIX_SHORT,
    is_character_agnostic,
)

def test_suffixes_nonempty():
    assert len(STRONG_SUFFIX) > 500
    assert len(FEW_SHOT_SUFFIX) > 1500
    assert len(LENGTH_SUFFIX_SHORT) > 200

def test_suffixes_character_agnostic():
    # CRITICAL: suffixes must not reference Su Wan or her specific attrs
    forbidden = [
        "Su Wan", "sheer_black_tights", "black_ankle_boots",
        "stocking_toes", "red_toenails", "red_fingernails",
        "red_lipstick", "black_pencil_skirt", "public_formal",
    ]
    for s_name, s in [
        ("STRONG", STRONG_SUFFIX),
        ("FEW_SHOT", FEW_SHOT_SUFFIX),
        ("LENGTH_SHORT", LENGTH_SUFFIX_SHORT),
    ]:
        leaked = is_character_agnostic(s, forbidden)
        assert leaked == [], f"{s_name} leaked: {leaked}"

def test_strong_suffix_contains_framing_table():
    assert "ms_waist_up" in STRONG_SUFFIX
    assert "visible_regions" in STRONG_SUFFIX
    assert "MUST NOT" in STRONG_SUFFIX

def test_length_suffix_has_word_count():
    assert "2200" in LENGTH_SUFFIX_SHORT
    assert "2800" in LENGTH_SUFFIX_SHORT
