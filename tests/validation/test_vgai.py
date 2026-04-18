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


@pytest.fixture
def char_with_occlusion():
    """Character whose closed stilettos occlude toes (where toenails live)."""
    return Character(
        base=Base(age=28, ethnicity="Chinese", hair="long black", skin="fair",
                  eyes="brown", jaw="soft"),
        persistent_grooming=[
            Grooming(name="red_toenails", anchor="foot", sub_anchor="toes"),
            Grooming(name="red_fingernails", anchor="hand", sub_anchor="fingernails"),
        ],
        wardrobe_states={"closed_heels": WardrobeState(items=[
            WardrobeItem(name="black_closed_stilettos", anchor="foot",
                         covers=["toes", "foot_top_inner"]),
        ])},
    )


def test_occlusion_gate_drops_covered_grooming(char_with_occlusion):
    """red_toenails.sub_anchor=toes is fully covered by closed stilettos.covers.

    Even though anchor=foot is in full_body_standing's visible_regions, the
    toenails themselves are occluded by the shoe and must not be injected.
    """
    s = Shot(
        shot_id="s_occluded", camera_framing="full_body_standing", pose="stand",
        wardrobe_state_used="closed_heels",
        vgai_injected_attrs=["red_toenails", "black_closed_stilettos"],
        vgai_dropped_attrs_with_reason=[],
        final_prompt="...",
    )
    violations = validate_shot(s, char_with_occlusion)
    # Should flag red_toenails as occlusion violation
    occl = [v for v in violations if v.kind == "occlusion"]
    assert len(occl) == 1
    assert occl[0].attr == "red_toenails"
    assert "black_closed_stilettos" in occl[0].reason
    assert "toes" in occl[0].reason


def test_occlusion_gate_allows_non_occluded_grooming(char_with_occlusion):
    """red_fingernails.sub_anchor=fingernails is NOT covered by anything."""
    s = Shot(
        shot_id="s_ok", camera_framing="full_body_standing", pose="stand",
        wardrobe_state_used="closed_heels",
        vgai_injected_attrs=["red_fingernails", "black_closed_stilettos"],
        vgai_dropped_attrs_with_reason=[],
        final_prompt="...",
    )
    violations = validate_shot(s, char_with_occlusion)
    assert all(v.kind != "occlusion" for v in violations)


def test_occlusion_gate_grooming_without_sub_anchor_not_flagged(char_with_occlusion):
    """If a grooming has sub_anchor=None, occlusion check is skipped."""
    char = char_with_occlusion.model_copy(update={
        "persistent_grooming": [
            Grooming(name="generic_foot_mark", anchor="foot"),  # no sub_anchor
        ]
    })
    s = Shot(
        shot_id="s_nosub", camera_framing="full_body_standing", pose="stand",
        wardrobe_state_used="closed_heels",
        vgai_injected_attrs=["generic_foot_mark", "black_closed_stilettos"],
        vgai_dropped_attrs_with_reason=[],
        final_prompt="...",
    )
    violations = validate_shot(s, char)
    assert all(v.kind != "occlusion" for v in violations)


def test_occlusion_gate_bare_covers_item_no_false_positive(char_with_occlusion):
    """An item with covers=[] (e.g. sheer tights) must never occlude anything."""
    char = char_with_occlusion.model_copy(update={
        "wardrobe_states": {
            "sheer_hose": WardrobeState(items=[
                WardrobeItem(name="sheer_black_tights", anchor="leg", covers=[]),
            ])
        }
    })
    s = Shot(
        shot_id="s_sheer", camera_framing="full_body_standing", pose="stand",
        wardrobe_state_used="sheer_hose",
        vgai_injected_attrs=["red_toenails", "sheer_black_tights"],
        vgai_dropped_attrs_with_reason=[],
        final_prompt="...",
    )
    violations = validate_shot(s, char)
    assert all(v.kind != "occlusion" for v in violations)
