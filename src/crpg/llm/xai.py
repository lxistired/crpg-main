"""Async xAI Grok Imagine Pro client."""
import asyncio
import base64
import httpx


class XaiImageClient:
    def __init__(
        self,
        api_key: str,
        *,
        endpoint: str = "https://api.x.ai/v1/images/generations",
        concurrency: int = 10,
        timeout_s: float = 120.0,
    ) -> None:
        self._api_key = api_key
        self._endpoint = endpoint
        self._sem = asyncio.Semaphore(concurrency)
        self._timeout = timeout_s
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    async def generate(
        self,
        *,
        prompt: str,
        model: str = "grok-imagine-pro",
        size: str = "1024x1024",
        n: int = 1,
        client: httpx.AsyncClient | None = None,
    ) -> bytes:
        """Generate one image. Returns PNG bytes."""
        payload = {"model": model, "prompt": prompt, "n": n, "size": size,
                   "response_format": "b64_json"}
        async with self._sem:
            owns = client is None
            c = client or httpx.AsyncClient(timeout=self._timeout)
            try:
                r = await c.post(self._endpoint, json=payload, headers=self._headers)
                if r.status_code != 200:
                    raise RuntimeError(f"xAI {r.status_code}: {r.text[:400]}")
                body = r.json()
            finally:
                if owns:
                    await c.aclose()
        b64_str = body["data"][0]["b64_json"]
        return base64.b64decode(b64_str)
