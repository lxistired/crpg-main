"""Configuration loading from environment variables."""
import os
from pydantic import BaseModel
from dotenv import load_dotenv


class ProjectConfig(BaseModel):
    # Main agent (MiniMax) — drives Skeleton + Script + Director
    minimax_key: str
    minimax_endpoint: str
    minimax_model: str
    # Script worker (kimi via OpenRouter) — called by agent as a tool
    openrouter_key: str
    openrouter_endpoint: str = "https://openrouter.ai/api/v1/chat/completions"
    text_model: str = "moonshotai/kimi-k2-0905"
    text_provider: str = "Groq"
    # Image worker (Grok Imagine Pro) — direct API
    xai_key: str
    xai_endpoint: str = "https://api.x.ai/v1/images/generations"
    concurrency: int = 50


def load_config() -> ProjectConfig:
    """Load config from .env + environment. Raises ValueError on missing keys."""
    load_dotenv()
    mm_key = os.environ.get("MINIMAX_API_KEY")
    if not mm_key:
        raise ValueError("MINIMAX_API_KEY is required (main agent)")
    or_key = os.environ.get("OPENROUTER_API_KEY")
    if not or_key:
        raise ValueError("OPENROUTER_API_KEY is required (Script worker)")
    xai_key = os.environ.get("XAI_API_KEY")
    if not xai_key:
        raise ValueError("XAI_API_KEY is required (image generation)")
    return ProjectConfig(
        minimax_key=mm_key,
        minimax_endpoint=os.environ.get("MINIMAX_ENDPOINT", "https://api.minimaxi.com/v1"),
        minimax_model=os.environ.get("MINIMAX_MODEL", "MiniMax-M2.7-HighSpeed"),
        openrouter_key=or_key,
        xai_key=xai_key,
        text_model=os.environ.get("CRPG_TEXT_MODEL", "moonshotai/kimi-k2-0905"),
        text_provider=os.environ.get("CRPG_TEXT_PROVIDER", "Groq"),
        concurrency=int(os.environ.get("CRPG_CONCURRENCY", "50")),
    )
