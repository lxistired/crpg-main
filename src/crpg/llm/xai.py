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
        model: str = "grok-imagine-image-pro",
        aspect_ratio: str = "16:9",
        resolution: str = "2k",
        n: int = 1,
        image_url: str | None = None,
        client: httpx.AsyncClient | None = None,
        retries: int = 3,
        backoff_base_s: float = 2.0,
    ) -> bytes:
        """Generate one image. Returns PNG bytes.

        Retries on 429 and 5xx with exponential backoff:
          wait = backoff_base_s * 2**attempt (e.g. 2s, 4s, 8s for default retries=3)
        Non-retriable 4xx (other than 429) raises immediately.
        """
        payload: dict = {
            "model": model,
            "prompt": prompt,
            "n": n,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
            "response_format": "b64_json",
        }
        # image_url enables Grok Imagine's image-to-image / editing mode —
        # the model applies the prompt as a natural-language edit on top of
        # the reference image. Used for character identity anchor lock.
        if image_url is not None:
            payload["image_url"] = image_url
        last_status: int | None = None
        last_body: str = ""
        for attempt in range(retries + 1):
            async with self._sem:
                owns = client is None
                c = client or httpx.AsyncClient(timeout=self._timeout)
                try:
                    r = await c.post(self._endpoint, json=payload, headers=self._headers)
                finally:
                    if owns:
                        await c.aclose()
            if r.status_code == 200:
                body = r.json()
                return base64.b64decode(body["data"][0]["b64_json"])
            last_status, last_body = r.status_code, r.text[:400]
            # Non-retriable: 4xx except 429
            if r.status_code != 429 and not (500 <= r.status_code < 600):
                raise RuntimeError(f"xAI {r.status_code}: {last_body}")
            # Retriable: wait then loop (unless this was final attempt)
            if attempt < retries:
                await asyncio.sleep(backoff_base_s * (2 ** attempt))
        raise RuntimeError(f"xAI {last_status} after {retries + 1} attempts: {last_body}")
