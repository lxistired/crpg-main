import pytest
from crpg.config import ProjectConfig, load_config


def test_load_config_with_defaults(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test")
    monkeypatch.setenv("XAI_API_KEY", "xai-test")
    c = load_config()
    assert c.openrouter_key == "sk-or-test"
    assert c.xai_key == "xai-test"
    assert c.text_model == "moonshotai/kimi-k2-0905"
    assert c.text_provider == "Groq"
    assert c.concurrency == 50


def test_load_config_overrides(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test")
    monkeypatch.setenv("XAI_API_KEY", "xai-test")
    monkeypatch.setenv("CRPG_TEXT_MODEL", "qwen/qwen3-max-thinking")
    monkeypatch.setenv("CRPG_CONCURRENCY", "10")
    c = load_config()
    assert c.text_model == "qwen/qwen3-max-thinking"
    assert c.concurrency == 10


def test_missing_key_raises(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
        load_config()
