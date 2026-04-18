import pytest, json
from crpg.passes.script import run_script_short, run_script_detailed
from crpg.llm.openrouter import OpenRouterClient

@pytest.mark.asyncio
async def test_script_short_single_call(httpx_mock, fixture_path):
    text = (fixture_path / "canonical_script_short.md").read_text(encoding="utf-8")
    httpx_mock.add_response(
        json={"choices":[{"message":{"content":text},"finish_reason":"stop"}],
              "usage":{"cost":0.005},"provider":"Groq"},
    )
    client = OpenRouterClient(api_key="sk-or-test", concurrency=2)
    out = await run_script_short(client, beat_user_prompt="write this short bifurcation")
    assert "雨丝" in out

@pytest.mark.asyncio
async def test_script_detailed_three_calls(httpx_mock):
    # main call
    httpx_mock.add_response(
        json={"choices":[{"message":{"content":"主段文本..."},"finish_reason":"stop"}], "usage":{}},
    )
    # A branch
    httpx_mock.add_response(
        json={"choices":[{"message":{"content":"A 支线文本..."},"finish_reason":"stop"}], "usage":{}},
    )
    # B branch
    httpx_mock.add_response(
        json={"choices":[{"message":{"content":"B 支线文本..."},"finish_reason":"stop"}], "usage":{}},
    )
    client = OpenRouterClient(api_key="sk-or-test", concurrency=5)
    main, a, b = await run_script_detailed(client, scene_brief="scene setup...")
    assert main == "主段文本..."
    assert a == "A 支线文本..."
    assert b == "B 支线文本..."
    assert len(httpx_mock.get_requests()) == 3
