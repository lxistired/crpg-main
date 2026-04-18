"""Pass 1: brief → Story + Characters."""
from crpg.llm.openrouter import OpenRouterClient
from crpg.llm.prompts import SKELETON_SYSTEM
from crpg.types import Story, Character
from crpg.validation.schema import parse_skeleton_output

async def run_skeleton(
    client: OpenRouterClient,
    *,
    brief: str,
    model: str = "moonshotai/kimi-k2-0905",
    provider: str = "Groq",
    temperature: float = 0.7,
    max_tokens: int = 8000,
) -> tuple[Story, dict[str, Character]]:
    """Call the Skeleton pass on the given brief. Returns (story, {name: character})."""
    res = await client.chat(
        model=model,
        system=SKELETON_SYSTEM,
        user=brief,
        provider_pin=provider,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return parse_skeleton_output(res.content)
