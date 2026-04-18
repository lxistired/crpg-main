"""Parse + validate LLM JSON outputs against our schemas."""
import json
import re
from pydantic import ValidationError
from crpg.types import Story, Character

class SchemaError(Exception):
    pass

def _strip_fence(s: str) -> str:
    s = s.strip()
    if s.startswith("```"):
        s = re.sub(r"^```\w*\s*", "", s)
        s = re.sub(r"\s*```\s*$", "", s)
    return s.strip()

def parse_skeleton_output(raw: str) -> tuple[Story, dict[str, Character]]:
    """Parse Skeleton LLM output → (Story, {name: Character})."""
    text = _strip_fence(raw)
    try:
        blob = json.loads(text)
    except json.JSONDecodeError as e:
        raise SchemaError(f"Skeleton output is not valid JSON: {e}") from e
    if not isinstance(blob, dict):
        raise SchemaError("Skeleton output must be a JSON object")
    if "story" not in blob:
        raise SchemaError("Skeleton output missing 'story' key")
    if "characters" not in blob:
        raise SchemaError("Skeleton output missing 'characters' key")
    try:
        story = Story.model_validate(blob["story"])
    except ValidationError as e:
        raise SchemaError(f"story schema invalid: {e}") from e
    chars: dict[str, Character] = {}
    for name, payload in blob["characters"].items():
        try:
            chars[name] = Character.model_validate(payload)
        except ValidationError as e:
            raise SchemaError(f"character {name!r} schema invalid: {e}") from e
    return story, chars

def parse_director_output(raw: str) -> list[dict]:
    """Parse Director LLM output (shot JSON array). Returns raw dicts for Shot validation."""
    text = _strip_fence(raw)
    try:
        blob = json.loads(text)
    except json.JSONDecodeError as e:
        raise SchemaError(f"Director output is not valid JSON: {e}") from e
    if not isinstance(blob, list):
        raise SchemaError("Director output must be a JSON array of shots")
    return blob
