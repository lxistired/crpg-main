import pathlib, json
import pytest
from crpg.passes.skeleton import run_skeleton
from crpg.llm.openrouter import OpenRouterClient

@pytest.mark.asyncio
async def test_skeleton_calls_groq(httpx_mock, fixture_path):
    canonical = (fixture_path / "canonical_skeleton.json").read_text(encoding="utf-8")
    httpx_mock.add_response(
        url="https://openrouter.ai/api/v1/chat/completions",
        json={"choices":[{"message":{"content":canonical},"finish_reason":"stop"}],
              "usage":{"cost":0.003},"provider":"Groq"},
    )
    client = OpenRouterClient(api_key="sk-or-test", concurrency=2)
    story, chars = await run_skeleton(client, brief="my brief")
    assert story.meta.title == "Rainy Noir"
    assert "Su Wan" in chars
    assert len(story.beats) == 4
    req = httpx_mock.get_requests()[0]
    body = json.loads(req.read())
    assert body["provider"]["order"] == ["Groq"]
    assert body["model"] == "moonshotai/kimi-k2-0905"

@pytest.mark.asyncio
async def test_skeleton_parse_error_raises(httpx_mock):
    httpx_mock.add_response(json={"choices":[{"message":{"content":"not json"},"finish_reason":"stop"}], "usage":{}})
    client = OpenRouterClient(api_key="sk-or-test", concurrency=2)
    with pytest.raises(Exception):
        await run_skeleton(client, brief="bad")
