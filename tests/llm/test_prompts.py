from crpg.llm.prompts import (
    SKELETON_SYSTEM, DIRECTOR_SYSTEM,
    SCRIPT_SHORT_SYSTEM, SCRIPT_MAIN_SYSTEM,
    SCRIPT_BRANCH_A_SYSTEM, SCRIPT_BRANCH_B_SYSTEM,
)

def test_skeleton_mentions_schema():
    assert "story" in SKELETON_SYSTEM
    assert "characters" in SKELETON_SYSTEM
    assert "beats" in SKELETON_SYSTEM
    assert "snake_case" in SKELETON_SYSTEM  # optimization #1 from spec §10

def test_director_asks_for_json_array():
    assert "JSON" in DIRECTOR_SYSTEM
    assert "vgai_injected_attrs" in DIRECTOR_SYSTEM

def test_script_prompts_nonempty():
    for p in [SCRIPT_SHORT_SYSTEM, SCRIPT_MAIN_SYSTEM,
              SCRIPT_BRANCH_A_SYSTEM, SCRIPT_BRANCH_B_SYSTEM]:
        assert "双支线" in p or "主段" in p or "分支" in p or "支线" in p
