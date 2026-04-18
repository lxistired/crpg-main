import pytest
from crpg.validation.vgai import validate_shot, validate_shot_list, VgaiViolation
from crpg.types import Shot, Character, Base, Grooming, WardrobeItem, WardrobeState

@pytest.fixture
def char():
    return Character(
        base=Base(age=28, ethnicity="Chinese", hair="long black", skin="fair",
                  eyes="brown", jaw="soft"),
        persistent_grooming=[
            Grooming(name="red_fingernails", anchor="hand"),
            Grooming(name="red_toenails", anchor="foot"),
            Grooming(name="red_lipstick", anchor="face"),
        ],
        wardrobe_states={"public_formal": WardrobeState(items=[
            WardrobeItem(name="black_pencil_skirt", anchor="torso"),
            WardrobeItem(name="sheer_black_tights", anchor="leg"),
            WardrobeItem(name="black_ankle_boots", anchor="foot"),
        ])},
        mutex_groups=[["sheer_black_tights", "black_ankle_boots"]],
    )

def test_valid_hand_ecu(char):
    s = Shot(shot_id="s1", camera_framing="hand_ecu", pose="close-up hand",
             wardrobe_state_used="public_formal",
             vgai_injected_attrs=["red_fingernails"],
             vgai_dropped_attrs_with_reason=["red_toenails: foot not in visible"],
             final_prompt="hand with red fingernails")
    violations = validate_shot(s, char)
    assert violations == []

def test_vgai_violation_leg_in_ms_waist_up(char):
    s = Shot(shot_id="s2", camera_framing="ms_waist_up", pose="standing",
             wardrobe_state_used="public_formal",
             vgai_injected_attrs=["sheer_black_tights"],
             vgai_dropped_attrs_with_reason=[],
             final_prompt="...")
    violations = validate_shot(s, char)
    assert len(violations) == 1
    assert violations[0].attr == "sheer_black_tights"
    assert "leg" in violations[0].reason

def test_mutex_violation(char):
    s = Shot(shot_id="s3", camera_framing="full_body_standing", pose="stand",
             wardrobe_state_used="public_formal",
             vgai_injected_attrs=["sheer_black_tights", "black_ankle_boots"],
             vgai_dropped_attrs_with_reason=[],
             final_prompt="...")
    violations = validate_shot(s, char)
    assert any(v.kind == "mutex" for v in violations)

def test_back_reveal_skirt_allowed(char):
    # torso_back visibility should let torso-anchored items pass
    s = Shot(shot_id="s4", camera_framing="back_reveal_walking", pose="walking away",
             wardrobe_state_used="public_formal",
             vgai_injected_attrs=["black_pencil_skirt"],
             vgai_dropped_attrs_with_reason=[],
             final_prompt="...")
    violations = validate_shot(s, char)
    assert violations == []

def test_ws_establishing_empty_only(char):
    s = Shot(shot_id="s5", camera_framing="ws_establishing", pose="distant",
             wardrobe_state_used="public_formal",
             vgai_injected_attrs=["red_fingernails"],
             vgai_dropped_attrs_with_reason=[],
             final_prompt="...")
    violations = validate_shot(s, char)
    assert any("ws_establishing" in str(v.reason) for v in violations)
