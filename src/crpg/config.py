"""Configuration loading from environment variables."""
import os
from pydantic import BaseModel
from dotenv import load_dotenv


class ProjectConfig(BaseModel):
    openrouter_key: str
    xai_key: str
    text_model: str
    text_provider: str
    concurrency: int
    openrouter_endpoint: str = "https://openrouter.ai/api/v1/chat/completions"
    xai_endpoint: str = "https://api.x.ai/v1/images/generations"


def load_config() -> ProjectConfig:
    """Load config from .env + environment. Raises ValueError on missing keys."""
    load_dotenv()  # no-op if no .env file
    or_key = os.environ.get("OPENROUTER_API_KEY")
    if not or_key:
        raise ValueError("OPENROUTER_API_KEY is required")
    xai_key = os.environ.get("XAI_API_KEY")
    if not xai_key:
        raise ValueError("XAI_API_KEY is required")
    return ProjectConfig(
        openrouter_key=or_key,
        xai_key=xai_key,
        text_model=os.environ.get("CRPG_TEXT_MODEL", "moonshotai/kimi-k2-0905"),
        text_provider=os.environ.get("CRPG_TEXT_PROVIDER", "Groq"),
        concurrency=int(os.environ.get("CRPG_CONCURRENCY", "50")),
    )
