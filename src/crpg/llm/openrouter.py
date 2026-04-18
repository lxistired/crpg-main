"""Async OpenRouter client wrapping OpenAI-compatible /chat/completions."""
import asyncio
from dataclasses import dataclass
import httpx

@dataclass(slots=True)
class ChatResult:
    content: str
    prompt_tokens: int
    completion_tokens: int
    cost: float
    provider: str
    finish_reason: str
    elapsed_s: float

class OpenRouterClient:
    def __init__(
        self,
        api_key: str,
        *,
        endpoint: str = "https://openrouter.ai/api/v1/chat/completions",
        concurrency: int = 50,
        referer: str = "https://crpg.local",
        title: str = "crpg",
        timeout_s: float = 240.0,
    ) -> None:
        self._api_key = api_key
        self._endpoint = endpoint
        self._sem = asyncio.Semaphore(concurrency)
        self._timeout = timeout_s
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": referer,
            "X-Title": title,
        }

    async def chat(
        self,
        *,
        model: str,
        system: str,
        user: str,
        provider_pin: str | None = None,
        allow_fallbacks: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 8000,
        client: httpx.AsyncClient | None = None,
    ) -> ChatResult:
        payload: dict = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if provider_pin is not None:
            payload["provider"] = {"order": [provider_pin], "allow_fallbacks": allow_fallbacks}
        import time
        async with self._sem:
            owns_client = client is None
            c = client or httpx.AsyncClient(timeout=self._timeout)
            try:
                t0 = time.time()
                r = await c.post(self._endpoint, json=payload, headers=self._headers)
                elapsed = time.time() - t0
                if r.status_code != 200:
                    raise RuntimeError(f"OpenRouter {r.status_code}: {r.text[:400]}")
                body = r.json()
            finally:
                if owns_client:
                    await c.aclose()
        msg = body["choices"][0].get("message", {})
        content = msg.get("content") or msg.get("reasoning") or ""
        usage = body.get("usage") or {}
        return ChatResult(
            content=content,
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            cost=usage.get("cost", 0.0) or 0.0,
            provider=body.get("provider", "?"),
            finish_reason=body["choices"][0].get("finish_reason", "?"),
            elapsed_s=elapsed,
        )
