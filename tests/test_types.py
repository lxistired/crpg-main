from crpg.types import Base, Grooming, WardrobeItem, WardrobeState, Character, Beat, Story, Shot, ShotList

def test_character_roundtrip():
    c = Character(
        base=Base(age=28, ethnicity="汉族", hair="黑长发过肩中分",
                  skin="白皙", eyes="棕", jaw="柔软下颌线"),
        persistent_grooming=[Grooming(name="red_fingernails", anchor="hand")],
        wardrobe_states={
            "public_formal": WardrobeState(items=[
                WardrobeItem(name="black_pencil_skirt", anchor="torso"),
                WardrobeItem(name="sheer_black_tights", anchor="leg"),
            ])
        },
        mutex_groups=[["sheer_black_tights", "black_ankle_boots"]],
    )
    blob = c.model_dump_json()
    c2 = Character.model_validate_json(blob)
    assert c2 == c
    assert c2.base.age == 28

def test_beat_defaults():
    b = Beat(
        id="intro", type="narrative", synopsis="opening scene",
        value_before="calm", value_after="alert",
        target_word_count=2500, target_shot_count=5,
    )
    assert b.depends_on == []
    assert b.wardrobe_state is None

def test_invalid_anchor_rejected():
    import pytest
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        Grooming(name="x", anchor="invalid_region")
