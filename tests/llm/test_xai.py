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
    # 400 is non-retriable, raises immediately
    httpx_mock.add_response(status_code=400, json={"error":{"message":"bad request"}})
    client = XaiImageClient(api_key="xai-test", concurrency=3)
    with pytest.raises(RuntimeError, match="400"):
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

@pytest.mark.asyncio
async def test_xai_retries_on_503(httpx_mock):
    # Two 503s then 200
    httpx_mock.add_response(status_code=503, json={"error":"temporarily unavailable"})
    httpx_mock.add_response(status_code=503, json={"error":"temporarily unavailable"})
    httpx_mock.add_response(json={"data":[{"b64_json": FAKE_PNG_B64}]})
    client = XaiImageClient(api_key="xai-test", concurrency=3)
    png = await client.generate(prompt="p", backoff_base_s=0.01)  # speed up test
    assert png.startswith(b"\x89PNG")
    assert len(httpx_mock.get_requests()) == 3

@pytest.mark.asyncio
async def test_xai_retries_exhausted(httpx_mock):
    # 4 x 503 = all attempts fail (default retries=3 = 4 total tries)
    for _ in range(4):
        httpx_mock.add_response(status_code=503, json={"error":"outage"})
    client = XaiImageClient(api_key="xai-test", concurrency=3)
    with pytest.raises(RuntimeError, match="after 4 attempts"):
        await client.generate(prompt="p", backoff_base_s=0.01)
