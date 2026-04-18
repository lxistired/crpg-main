import pytest
from crpg.llm.openrouter import OpenRouterClient, ChatResult

@pytest.mark.asyncio
async def test_chat_basic(httpx_mock):
    httpx_mock.add_response(
        url="https://openrouter.ai/api/v1/chat/completions",
        json={
            "choices": [{"message": {"content": "hello"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "cost": 0.001},
            "provider": "Groq",
        },
    )
    client = OpenRouterClient(api_key="sk-or-test", concurrency=2)
    res = await client.chat(
        model="moonshotai/kimi-k2-0905",
        system="you are helpful",
        user="say hello",
        provider_pin="Groq",
        temperature=0.7,
        max_tokens=100,
    )
    assert isinstance(res, ChatResult)
    assert res.content == "hello"
    assert res.provider == "Groq"
    assert res.cost == 0.001

@pytest.mark.asyncio
async def test_chat_sends_provider_pin(httpx_mock):
    httpx_mock.add_response(
        json={"choices":[{"message":{"content":"ok"}, "finish_reason":"stop"}], "usage":{}},
    )
    client = OpenRouterClient(api_key="sk-or-test", concurrency=2)
    await client.chat(model="x", system="s", user="u", provider_pin="Groq")
    req = httpx_mock.get_requests()[0]
    import json as j
    body = j.loads(req.read())
    assert body["provider"] == {"order": ["Groq"], "allow_fallbacks": True}

@pytest.mark.asyncio
async def test_chat_sends_response_format(httpx_mock):
    httpx_mock.add_response(json={"choices":[{"message":{"content":"ok"}, "finish_reason":"stop"}], "usage":{}})
    client = OpenRouterClient(api_key="sk-or-test", concurrency=2)
    await client.chat(model="x", system="s", user="u",
                      response_format={"type": "json_object"})
    req = httpx_mock.get_requests()[0]
    import json as j
    body = j.loads(req.read())
    assert body["response_format"] == {"type": "json_object"}

@pytest.mark.asyncio
async def test_chat_error(httpx_mock):
    httpx_mock.add_response(
        status_code=429,
        json={"error": {"message": "rate limit"}},
    )
    client = OpenRouterClient(api_key="sk-or-test", concurrency=2)
    with pytest.raises(RuntimeError, match="429"):
        await client.chat(model="x", system="s", user="u")
