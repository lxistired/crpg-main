"""Pass 1: brief → Story + Characters."""
from crpg.llm.openrouter import OpenRouterClient
from crpg.llm.prompts import SKELETON_SYSTEM
from crpg.types import Story, Character
from crpg.validation.schema import parse_skeleton_output, SchemaError

async def run_skeleton(
    client: OpenRouterClient,
    *,
    brief: str,
    model: str = "moonshotai/kimi-k2-0905",
    provider: str = "Groq",
    temperature: float = 0.7,
    max_tokens: int = 8000,
    retries: int = 1,
) -> tuple[Story, dict[str, Character]]:
    """Call the Skeleton pass on the given brief. Returns (story, {name: character}).

    On JSON parse failure, retries up to `retries` times (default 1, so 2 total attempts).
    Uses response_format=json_object to force the model to emit valid JSON.
    """
    last_err: Exception | None = None
    for attempt in range(retries + 1):
        res = await client.chat(
            model=model,
            system=SKELETON_SYSTEM,
            user=brief,
            provider_pin=provider,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
        try:
            return parse_skeleton_output(res.content)
        except SchemaError as e:
            last_err = e
            continue
    raise last_err  # type: ignore[misc]
