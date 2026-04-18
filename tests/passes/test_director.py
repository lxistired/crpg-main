import pytest, json
from crpg.passes.director import run_director
from crpg.llm.openrouter import OpenRouterClient
from crpg.types import Character, Base, Grooming, WardrobeItem, WardrobeState

@pytest.fixture
def su_wan():
    return Character(
        base=Base(age=28, ethnicity="Chinese", hair="long black", skin="fair",
                  eyes="brown", jaw="soft"),
        persistent_grooming=[
            Grooming(name="red_fingernails", anchor="hand"),
            Grooming(name="red_lipstick", anchor="face"),
        ],
        wardrobe_states={"public_formal": WardrobeState(items=[
            WardrobeItem(name="black_pencil_skirt", anchor="torso"),
            WardrobeItem(name="sheer_black_tights", anchor="leg"),
            WardrobeItem(name="black_ankle_boots", anchor="foot"),
        ])},
        mutex_groups=[["sheer_black_tights", "black_ankle_boots"]],
    )

@pytest.mark.asyncio
async def test_director_returns_shots(httpx_mock, fixture_path, su_wan):
    canonical = (fixture_path / "canonical_shots.json").read_text(encoding="utf-8")
    httpx_mock.add_response(
        json={"choices":[{"message":{"content":canonical},"finish_reason":"stop"}],
              "usage":{"cost":0.004},"provider":"Groq"},
    )
    client = OpenRouterClient(api_key="sk-or-test", concurrency=2)
    shots = await run_director(
        client,
        beat_id="intro",
        beat_prose="主段文本",
        character_name="Su Wan", character=su_wan,
        wardrobe_state="public_formal",
        target_shot_count=2,
    )
    assert len(shots) == 2
    assert shots[0].camera_framing == "ms_waist_up"
    assert shots[0].vgai_injected_attrs == ["red_lipstick","red_fingernails","black_pencil_skirt"]

@pytest.mark.asyncio
async def test_director_user_message_includes_character(httpx_mock, fixture_path, su_wan):
    canonical = (fixture_path / "canonical_shots.json").read_text(encoding="utf-8")
    httpx_mock.add_response(
        json={"choices":[{"message":{"content":canonical},"finish_reason":"stop"}], "usage":{}},
    )
    client = OpenRouterClient(api_key="sk-or-test", concurrency=2)
    await run_director(
        client, beat_id="intro", beat_prose="p", character_name="Su Wan",
        character=su_wan, wardrobe_state="public_formal", target_shot_count=2,
    )
    req = httpx_mock.get_requests()[0]
    body = json.loads(req.read())
    # User message must carry character info for the model to reference names
    user_text = body["messages"][1]["content"]
    assert "Su Wan" in user_text
    assert "red_fingernails" in user_text
