from crpg.passes.assembler import assemble_image_prompt, ANIME_PREAMBLE
from crpg.types import Shot

def test_anime_preamble_prepended():
    shot = Shot(shot_id="s1", camera_framing="cu_face", pose="face",
                wardrobe_state_used="public_formal",
                vgai_injected_attrs=["red_lipstick"],
                vgai_dropped_attrs_with_reason=[],
                final_prompt="28 y.o. woman face close-up")
    prompt = assemble_image_prompt(shot)
    assert prompt.startswith(ANIME_PREAMBLE)
    assert "28 y.o. woman face close-up" in prompt

def test_assembler_is_pure():
    shot = Shot(shot_id="s1", camera_framing="cu_face", pose="p",
                wardrobe_state_used="public_formal",
                vgai_injected_attrs=[], vgai_dropped_attrs_with_reason=[],
                final_prompt="x")
    p1 = assemble_image_prompt(shot)
    p2 = assemble_image_prompt(shot)
    assert p1 == p2  # deterministic, no state
