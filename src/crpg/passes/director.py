"""Pass 3: Director — beat prose + character → shot list."""
import json
from crpg.llm.openrouter import OpenRouterClient
from crpg.llm.prompts import DIRECTOR_SYSTEM
from crpg.llm.suffixes import STRONG_SUFFIX, FEW_SHOT_SUFFIX
from crpg.types import Character, Shot
from crpg.validation.schema import parse_director_output

def _format_user_message(
    beat_id: str,
    beat_prose: str,
    character_name: str,
    character: Character,
    wardrobe_state: str,
    target_shot_count: int,
) -> str:
    char_json = json.dumps(
        {character_name: character.model_dump(mode="json")},
        ensure_ascii=False, indent=2,
    )
    return (
        f"### Character sheet (for VGAI gating + base identity in final_prompt)\n"
        f"```json\n{char_json}\n```\n\n"
        f"### Beat\n"
        f"- beat_id: {beat_id}\n"
        f"- wardrobe_state: {wardrobe_state}\n"
        f"- target shot count: {target_shot_count}\n\n"
        f"### Prose\n{beat_prose}\n\n"
        f"产出 {target_shot_count} 个 shot 的 JSON 数组。"
    )

async def run_director(
    client: OpenRouterClient,
    *,
    beat_id: str,
    beat_prose: str,
    character_name: str,
    character: Character,
    wardrobe_state: str,
    target_shot_count: int,
    model: str = "moonshotai/kimi-k2-0905",
    provider: str = "Groq",
    temperature: float = 0.7,
    max_tokens: int = 8000,
) -> list[Shot]:
    user = _format_user_message(
        beat_id, beat_prose, character_name, character,
        wardrobe_state, target_shot_count,
    )
    res = await client.chat(
        model=model,
        system=DIRECTOR_SYSTEM + STRONG_SUFFIX + FEW_SHOT_SUFFIX,
        user=user,
        provider_pin=provider,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    raw_shots = parse_director_output(res.content)
    return [Shot.model_validate(s) for s in raw_shots]
