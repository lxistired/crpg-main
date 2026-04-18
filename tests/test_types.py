from crpg.types import Base, Grooming, WardrobeItem, WardrobeState, Character, Beat, Story, Shot, ShotList, Edge

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

def test_shot_dropped_accepts_list_and_dict():
    """Different LLMs emit dropped_attrs in different shapes; both must parse."""
    # List-of-strings form (glm-5.1, nemotron, qwen3-max-thinking)
    s1 = Shot(shot_id="s1", camera_framing="hand_ecu", pose="p",
              wardrobe_state_used="public_formal",
              vgai_injected_attrs=["red_fingernails"],
              vgai_dropped_attrs_with_reason=["red_lipstick: face not in visible_regions"],
              final_prompt="x")
    assert isinstance(s1.vgai_dropped_attrs_with_reason, list)
    # Dict form (some kimi variants)
    s2 = Shot(shot_id="s2", camera_framing="hand_ecu", pose="p",
              wardrobe_state_used="public_formal",
              vgai_injected_attrs=["red_fingernails"],
              vgai_dropped_attrs_with_reason={"red_lipstick": "face not in visible_regions"},
              final_prompt="x")
    assert isinstance(s2.vgai_dropped_attrs_with_reason, dict)
    # Round-trip both
    assert Shot.model_validate_json(s1.model_dump_json()) == s1
    assert Shot.model_validate_json(s2.model_dump_json()) == s2

def test_edge_from_alias_round_trip():
    """Edge.from_ aliases the Python reserved word `from`; both directions must work."""
    # snake_case construction via populate_by_name
    e1 = Edge(from_="a", to="b")
    assert e1.from_ == "a"
    # JSON input with aliased key
    e2 = Edge.model_validate({"from": "a", "to": "b"})
    assert e2.from_ == "a"
    # Serialization with by_alias=True must emit "from" not "from_"
    dumped = e2.model_dump(by_alias=True)
    assert dumped["from"] == "a"
    assert "from_" not in dumped
