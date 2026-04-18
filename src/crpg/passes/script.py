"""Pass 2: Script generation (short single-call, detailed segmented)."""
import asyncio
from crpg.llm.openrouter import OpenRouterClient
from crpg.llm.prompts import (
    SCRIPT_SHORT_SYSTEM, SCRIPT_MAIN_SYSTEM,
    SCRIPT_BRANCH_A_SYSTEM, SCRIPT_BRANCH_B_SYSTEM,
)
from crpg.llm.suffixes import LENGTH_SUFFIX_SHORT


async def run_script_short(
    client: OpenRouterClient,
    *,
    beat_user_prompt: str,
    model: str = "moonshotai/kimi-k2-0905",
    provider: str = "Groq",
    temperature: float = 0.7,
    max_tokens: int = 8000,
) -> str:
    """Single-call bifurcating short: main + A + B in one output."""
    res = await client.chat(
        model=model,
        system=SCRIPT_SHORT_SYSTEM + LENGTH_SUFFIX_SHORT,
        user=beat_user_prompt,
        provider_pin=provider,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return res.content


async def run_script_detailed(
    client: OpenRouterClient,
    *,
    scene_brief: str,
    model: str = "moonshotai/kimi-k2-0905",
    provider: str = "Groq",
    temperature: float = 0.7,
    max_tokens: int = 8000,
) -> tuple[str, str, str]:
    """Segmented detailed: main first, then A and B concurrent with main as context.

    Returns (main, branch_a, branch_b) strings.
    """
    # Step 1: main
    main_res = await client.chat(
        model=model,
        system=SCRIPT_MAIN_SYSTEM,
        user=scene_brief,
        provider_pin=provider,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    main_text = main_res.content
    # Step 2+3: A and B concurrent, main as context
    branch_user = f"{scene_brief}\n\n【主段全文 (承接尾部)】\n{main_text}"
    a_task = client.chat(
        model=model, system=SCRIPT_BRANCH_A_SYSTEM, user=branch_user,
        provider_pin=provider, temperature=temperature, max_tokens=max_tokens,
    )
    b_task = client.chat(
        model=model, system=SCRIPT_BRANCH_B_SYSTEM, user=branch_user,
        provider_pin=provider, temperature=temperature, max_tokens=max_tokens,
    )
    a_res, b_res = await asyncio.gather(a_task, b_task)
    return main_text, a_res.content, b_res.content
