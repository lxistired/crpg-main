import pytest, base64
from crpg.llm.xai import XaiImageClient

FAKE_PNG_B64 = base64.b64encode(b"\x89PNG\r\n\x1a\n" + b"\x00" * 64).decode()

@pytest.mark.asyncio
async def test_generate_image(httpx_mock):
    httpx_mock.add_response(
        url="https://api.x.ai/v1/images/generations",
        json={"data":[{"b64_json": FAKE_PNG_B64}]},
    )
    client = XaiImageClient(api_key="xai-test", concurrency=3)
    png_bytes = await client.generate(prompt="test prompt")
    assert png_bytes.startswith(b"\x89PNG")

@pytest.mark.asyncio
async def test_xai_error(httpx_mock):
    httpx_mock.add_response(status_code=500, json={"error":{"message":"oops"}})
    client = XaiImageClient(api_key="xai-test", concurrency=3)
    with pytest.raises(RuntimeError, match="500"):
        await client.generate(prompt="p")

@pytest.mark.asyncio
async def test_generate_sends_aspect_ratio_and_resolution(httpx_mock):
    httpx_mock.add_response(json={"data":[{"b64_json": FAKE_PNG_B64}]})
    client = XaiImageClient(api_key="xai-test", concurrency=3)
    await client.generate(prompt="p", aspect_ratio="1:1", resolution="2k")
    req = httpx_mock.get_requests()[0]
    import json as j
    body = j.loads(req.read())
    assert body["aspect_ratio"] == "1:1"
    assert body["resolution"] == "2k"
    assert body["model"] == "grok-imagine-image-pro"
    assert "size" not in body  # MUST NOT send size
