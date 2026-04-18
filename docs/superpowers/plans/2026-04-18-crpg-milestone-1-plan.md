# crpg Milestone 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a Python CLI (`crpg generate`) that turns a creator brief into a complete story bundle (story.json + characters.json + real images) via a 4-pass LLM pipeline on kimi-k2-0905 @Groq + Grok Imagine Pro.

**Architecture:** Async Python 3.12 pipeline. Beat-level atomic unit; each beat = 1 Script call + 1 Director call. DAG-scheduled across beats (scenes parallel when independent, siblings A/B parallel within a scene). Semaphore-limited concurrent HTTP via httpx. Pure-function prompt assembler feeds Grok Imagine Pro for real images.

**Tech Stack:**
- Python 3.12
- `httpx` (async HTTP, OpenAI-compatible calls to OpenRouter + xAI)
- `pydantic` v2 (schemas, config)
- `click` (CLI)
- `pytest` + `pytest-asyncio` (testing, mocked LLM by default; one opt-in real-API E2E)
- `pytest-httpx` (HTTP mocking)
- No heavy framework — `openai-agents` SDK was considered but adds no value for a linear pipeline; we use plain httpx.

**Empirical baselines (from spec §3, already validated 2026-04-18):**
- Skeleton @ Groq: 3.5s, 3/3 schema clean
- Script short @ Groq + length suffix: ~9s, 2/3 hit target (use segmented fallback if miss)
- Script detailed @ Groq segmented: ~19s concurrent, 3/3 hit target
- Director @ Groq + STRONG + FEW_SHOT suffix: 4.3s, 4/4 VGAI clean
- Groq paid-tier concurrency: assume 50, validated by actual smoke test

---

## File Structure

```
crpg/                              # project root (already a git repo)
├── pyproject.toml                 # project metadata + deps (uv-managed)
├── .env.example                   # API key templates
├── .gitignore                     # extend with .venv/, bundles/, .env
├── README.md                      # CLI usage
│
├── src/crpg/                      # main package (src layout)
│   ├── __init__.py
│   ├── __main__.py                # enables `python -m crpg`
│   ├── cli.py                     # click entry point
│   ├── config.py                  # .env loading + ProjectConfig pydantic model
│   ├── types.py                   # core data models: Beat, Story, Character, Shot
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── openrouter.py          # async OpenRouter chat client (provider pinning)
│   │   ├── xai.py                 # async xAI Grok Imagine client
│   │   ├── suffixes.py            # STRONG / FEW_SHOT / LENGTH constants
│   │   └── prompts.py             # SKELETON_SYSTEM, SCRIPT_*, DIRECTOR_SYSTEM
│   │
│   ├── passes/
│   │   ├── __init__.py
│   │   ├── skeleton.py            # Pass 1: brief → Story + Characters
│   │   ├── script.py              # Pass 2: beat → prose (short + detailed modes)
│   │   ├── director.py            # Pass 3: beat prose + characters → shot list
│   │   ├── assembler.py           # Pass 4: pure fn, shot + base → Grok image prompt
│   │   └── image.py               # Pass 5: prompts → PNG files (Grok Imagine)
│   │
│   ├── validation/
│   │   ├── __init__.py
│   │   ├── vgai.py                # VGAI gating + mutex audit
│   │   └── schema.py              # story.json / characters.json validators
│   │
│   ├── orchestration/
│   │   ├── __init__.py
│   │   ├── dag.py                 # topological_layers(beats)
│   │   └── pipeline.py            # run_pipeline(config) → Bundle
│   │
│   └── bundle.py                  # BundleWriter: write story.json / characters.json / shots/
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # pytest fixtures (mock LLM, demo brief)
│   ├── fixtures/
│   │   ├── demo_brief.md          # small brief for smoke tests
│   │   ├── canonical_skeleton.json        # known-good skeleton output
│   │   ├── canonical_characters.json      # known-good character sheet
│   │   ├── canonical_script_short.md      # known-good short script
│   │   └── canonical_shots.json           # known-good director output
│   │
│   ├── test_config.py
│   ├── test_types.py
│   ├── llm/
│   │   ├── test_openrouter.py
│   │   ├── test_xai.py
│   │   └── test_prompts.py
│   ├── passes/
│   │   ├── test_skeleton.py
│   │   ├── test_script.py
│   │   ├── test_director.py
│   │   ├── test_assembler.py
│   │   └── test_image.py
│   ├── validation/
│   │   ├── test_vgai.py
│   │   └── test_schema.py
│   ├── orchestration/
│   │   ├── test_dag.py
│   │   └── test_pipeline.py
│   ├── test_bundle.py
│   ├── test_cli.py
│   └── test_e2e.py               # opt-in real API E2E (needs env var CRPG_LIVE=1)
│
└── docs/superpowers/
    ├── specs/2026-04-18-crpg-milestone-1-design.md
    └── plans/2026-04-18-crpg-milestone-1-plan.md    # THIS FILE
```

## Testing Strategy

- **Unit tests default**: mock HTTP with `pytest-httpx` (MockRouter). Fast, deterministic. 95% of tests.
- **VGAI / schema / DAG / assembler**: pure logic tests, no mocks.
- **E2E real-API test**: gated by `CRPG_LIVE=1` env var. One run per merge to verify no drift.

## Execution order notes

- Phase 0-1 unblock everything else.
- Phase 2 (LLM backend) is consumed by every pass — do it before Phase 4.
- Phase 3 (validation) is consumed by Director and Bundle — do it before Phases 4.4, 6.
- Phase 4 passes are independent once Phase 2-3 ready; can be developed in any order.
- Phase 6 orchestration requires all passes.
- Phase 7 CLI requires Phase 6.
- Phase 8 is the capstone E2E.

---

# Phase 0 — Project scaffolding

### Task 0.1: pyproject.toml + .env.example + .gitignore

**Files:**
- Create: `pyproject.toml`
- Create: `.env.example`
- Modify: `.gitignore` (add Python-specific entries)
- Create: `README.md` (stub)

- [ ] **Step 1: Write `pyproject.toml`**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "crpg"
version = "0.1.0"
description = "Creator CLI for interactive branching noir fiction with anime image generation"
readme = "README.md"
requires-python = ">=3.12"
license = { text = "Apache-2.0" }
dependencies = [
    "httpx >= 0.27",
    "pydantic >= 2.5",
    "click >= 8.1",
    "python-dotenv >= 1.0",
]

[project.optional-dependencies]
dev = [
    "pytest >= 8.0",
    "pytest-asyncio >= 0.23",
    "pytest-httpx >= 0.30",
    "pytest-cov >= 5.0",
    "ruff >= 0.4",
]

[project.scripts]
crpg = "crpg.cli:main"

[tool.hatch.build.targets.wheel]
packages = ["src/crpg"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
pythonpath = ["src"]

[tool.ruff]
line-length = 100
target-version = "py312"
```

- [ ] **Step 2: Write `.env.example`**

```
# OpenRouter key (paid tier recommended for parallel execution)
OPENROUTER_API_KEY=sk-or-v1-...

# xAI key for Grok Imagine Pro (image generation)
XAI_API_KEY=xai-...

# Optional: override default model
CRPG_TEXT_MODEL=moonshotai/kimi-k2-0905
CRPG_TEXT_PROVIDER=Groq

# Optional: concurrency budget (default 50 for paid tier)
CRPG_CONCURRENCY=50
```

- [ ] **Step 3: Extend `.gitignore`**

Append these lines to `.gitignore`:

```
# Python
.venv/
__pycache__/
*.pyc
.pytest_cache/
.coverage
.ruff_cache/
dist/
*.egg-info/

# Secrets & artifacts
.env
bundles/
```

- [ ] **Step 4: Write `README.md` stub**

```markdown
# crpg

Creator CLI for interactive branching noir fiction with anime image generation.

## Install

    pip install -e ".[dev]"

## Usage

    cp .env.example .env          # fill in keys
    crpg generate --brief brief.md --out bundle/

See `docs/superpowers/specs/2026-04-18-crpg-milestone-1-design.md` for architecture.
```

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml .env.example .gitignore README.md
git commit -m "chore: bootstrap pyproject + env template + gitignore"
```

---

### Task 0.2: Package skeleton with __init__.py files

**Files:** create empty `__init__.py` in every package directory.

- [ ] **Step 1: Create all package directories**

```bash
mkdir -p src/crpg/llm src/crpg/passes src/crpg/validation src/crpg/orchestration
mkdir -p tests/llm tests/passes tests/validation tests/orchestration tests/fixtures
```

- [ ] **Step 2: Create __init__.py files**

Run once:

```bash
touch src/crpg/__init__.py src/crpg/llm/__init__.py \
      src/crpg/passes/__init__.py src/crpg/validation/__init__.py \
      src/crpg/orchestration/__init__.py
touch tests/__init__.py tests/llm/__init__.py tests/passes/__init__.py \
      tests/validation/__init__.py tests/orchestration/__init__.py
```

Put in `src/crpg/__init__.py`:

```python
"""crpg — creator CLI for interactive noir fiction."""
__version__ = "0.1.0"
```

- [ ] **Step 3: Sanity test: package importable**

Create `tests/test_imports.py`:

```python
def test_package_imports():
    import crpg
    assert crpg.__version__ == "0.1.0"
```

- [ ] **Step 4: Install in dev mode + run**

```bash
pip install -e ".[dev]"
pytest tests/test_imports.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/ tests/
git commit -m "chore: package skeleton with empty modules"
```

---

### Task 0.3: conftest.py + demo_brief fixture

**Files:**
- Create: `tests/conftest.py`
- Create: `tests/fixtures/demo_brief.md`

- [ ] **Step 1: Write `tests/fixtures/demo_brief.md`**

```markdown
# Demo Brief

**Genre:** 都市 noir
**Setting:** 2026 年春, 上海静安区, 深夜雨幕
**Length:** short
**Detail richness:** detailed
**Structure:** bifurcating

## Protagonist
Su Wan, 28 岁女律师, 黑长发过肩中分, 白皙, 棕眸, 柔软下颌线。
今晚穿黑色包臀裙 + 透黑丝袜 + 黑色踝靴。红色指甲 / 红色趾甲 / 红色唇。

## Supporting
Kai, 32 岁男, 和 Su Wan 三年前案件对手律师撞脸。

## Scene
深夜 23:40 Su Wan 从写字楼下班, 地铁口被 Kai 搭讪, 花店买玫瑰, 认出熟悉面孔。
价值转换: 职业警觉 → 模糊失控。

## Branches
A: 她回绝, 独自回家, 出租车后座发现没删 Kai 电话 (克制但动摇)
B: 她去酒吧, 灯光暗, Kai 手指碰她膝盖上方黑丝, 意识到自己不想移开 (失控开始但克制)
```

- [ ] **Step 2: Write `tests/conftest.py`**

```python
import pathlib
import pytest

FIXTURES = pathlib.Path(__file__).parent / "fixtures"

@pytest.fixture
def demo_brief() -> str:
    return (FIXTURES / "demo_brief.md").read_text(encoding="utf-8")

@pytest.fixture
def fixture_path():
    """Directory for canonical JSON fixtures."""
    return FIXTURES
```

- [ ] **Step 3: Verify fixture loads**

Add `tests/test_fixtures.py`:

```python
def test_demo_brief_loads(demo_brief):
    assert "Su Wan" in demo_brief
    assert "bifurcating" in demo_brief
```

Run: `pytest tests/test_fixtures.py -v`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add tests/conftest.py tests/fixtures/demo_brief.md tests/test_fixtures.py
git commit -m "test: add demo_brief fixture + conftest"
```

---

# Phase 1 — Core types & config

### Task 1.1: Data models in types.py

**Files:**
- Create: `src/crpg/types.py`
- Create: `tests/test_types.py`

- [ ] **Step 1: Write failing test**

`tests/test_types.py`:

```python
from crpg.types import Base, Grooming, WardrobeItem, WardrobeState, Character, Beat, Story, Shot, ShotList

def test_character_roundtrip():
    c = Character(
        base=Base(age=28, ethnicity="汉族", hair="黑长发过肩中分",
                  skin="白皙", eyes="棕", jaw="柔软下颌线"),
        persistent_grooming=[Grooming(name="red_fingernails", anchor="hand")],
        wardrobe_states={
            "public_formal": WardrobeState(items=[
                WardrobeItem(name="black_pencil_skirt", anchor="torso"),
                WardrobeItem(name="sheer_black_tights", anchor="leg"),
            ])
        },
        mutex_groups=[["sheer_black_tights", "black_ankle_boots"]],
    )
    blob = c.model_dump_json()
    c2 = Character.model_validate_json(blob)
    assert c2 == c
    assert c2.base.age == 28

def test_beat_defaults():
    b = Beat(
        id="intro", type="narrative", synopsis="opening scene",
        value_before="calm", value_after="alert",
        target_word_count=2500, target_shot_count=5,
    )
    assert b.depends_on == []
    assert b.wardrobe_state is None

def test_invalid_anchor_rejected():
    import pytest
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        Grooming(name="x", anchor="invalid_region")
```

- [ ] **Step 2: Run test — expect ImportError**

```bash
pytest tests/test_types.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'crpg.types'`.

- [ ] **Step 3: Implement `src/crpg/types.py`**

```python
"""Core data models for the crpg pipeline."""
from typing import Literal
from pydantic import BaseModel, Field

Anchor = Literal[
    "face", "ear", "neck",
    "hand", "torso", "torso_back",
    "leg", "leg_upper", "foot",
]

BeatType = Literal[
    "narrative", "choice", "check", "merge", "act_break", "ending",
]

DetailRichness = Literal["concise", "standard", "detailed", "extreme"]
ContentLength = Literal["short", "medium", "long"]
Structure = Literal["linear", "bifurcating", "funnel", "web"]

class Base(BaseModel):
    age: int
    ethnicity: str
    hair: str
    skin: str
    eyes: str
    jaw: str

class Grooming(BaseModel):
    name: str
    anchor: Anchor
    sub_anchor: str | None = None
    removable_by: str | None = None

class WardrobeItem(BaseModel):
    name: str
    anchor: Anchor

class WardrobeState(BaseModel):
    items: list[WardrobeItem]
    removes: list[str] = Field(default_factory=list)

class Character(BaseModel):
    base: Base
    persistent_grooming: list[Grooming] = Field(default_factory=list)
    wardrobe_states: dict[str, WardrobeState] = Field(default_factory=dict)
    mutex_groups: list[list[str]] = Field(default_factory=list)

class Beat(BaseModel):
    id: str
    type: BeatType
    synopsis: str
    value_before: str = Field(alias="valueBefore")
    value_after: str = Field(alias="valueAfter")
    wardrobe_state: str | None = None
    target_word_count: int = Field(alias="targetWordCount")
    target_shot_count: int = Field(alias="targetShotCount")
    depends_on: list[str] = Field(default_factory=list)

    model_config = {"populate_by_name": True}

class Edge(BaseModel):
    from_: str = Field(alias="from")
    to: str
    condition: str | None = None

    model_config = {"populate_by_name": True}

class StoryMeta(BaseModel):
    title: str
    genre: str
    content_length: ContentLength = Field(alias="contentLength")
    detail_richness: DetailRichness = Field(alias="detailRichness")
    structure: Structure

    model_config = {"populate_by_name": True}

class Story(BaseModel):
    meta: StoryMeta
    beats: list[Beat]
    edges: list[Edge]

class Shot(BaseModel):
    shot_id: str
    camera_framing: str
    pose: str
    wardrobe_state_used: str
    vgai_injected_attrs: list[str]
    vgai_dropped_attrs_with_reason: list[str] | dict[str, str]
    final_prompt: str

class ShotList(BaseModel):
    beat_id: str
    shots: list[Shot]
```

- [ ] **Step 4: Run tests — expect PASS**

```bash
pytest tests/test_types.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add src/crpg/types.py tests/test_types.py
git commit -m "feat(types): pydantic models for Character, Beat, Story, Shot"
```

---

### Task 1.2: Config loader

**Files:**
- Create: `src/crpg/config.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Write failing test**

`tests/test_config.py`:

```python
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
```

- [ ] **Step 2: Run — expect FAIL**

```bash
pytest tests/test_config.py -v
```

Expected: ModuleNotFoundError.

- [ ] **Step 3: Implement `src/crpg/config.py`**

```python
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
```

- [ ] **Step 4: Run — expect PASS**

```bash
pytest tests/test_config.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add src/crpg/config.py tests/test_config.py
git commit -m "feat(config): ProjectConfig loader from env"
```

---

# Phase 2 — LLM backend

### Task 2.1: OpenRouter async client with provider pinning

**Files:**
- Create: `src/crpg/llm/openrouter.py`
- Create: `tests/llm/test_openrouter.py`

- [ ] **Step 1: Write failing test**

`tests/llm/test_openrouter.py`:

```python
import pytest
from crpg.llm.openrouter import OpenRouterClient, ChatResult

@pytest.mark.asyncio
async def test_chat_basic(httpx_mock):
    httpx_mock.add_response(
        url="https://openrouter.ai/api/v1/chat/completions",
        json={
            "choices": [{"message": {"content": "hello"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "cost": 0.001},
            "provider": "Groq",
        },
    )
    client = OpenRouterClient(api_key="sk-or-test", concurrency=2)
    res = await client.chat(
        model="moonshotai/kimi-k2-0905",
        system="you are helpful",
        user="say hello",
        provider_pin="Groq",
        temperature=0.7,
        max_tokens=100,
    )
    assert isinstance(res, ChatResult)
    assert res.content == "hello"
    assert res.provider == "Groq"
    assert res.cost == 0.001

@pytest.mark.asyncio
async def test_chat_sends_provider_pin(httpx_mock):
    httpx_mock.add_response(
        json={"choices":[{"message":{"content":"ok"}, "finish_reason":"stop"}], "usage":{}},
    )
    client = OpenRouterClient(api_key="sk-or-test", concurrency=2)
    await client.chat(model="x", system="s", user="u", provider_pin="Groq")
    req = httpx_mock.get_requests()[0]
    import json as j
    body = j.loads(req.read())
    assert body["provider"] == {"order": ["Groq"], "allow_fallbacks": True}

@pytest.mark.asyncio
async def test_chat_error(httpx_mock):
    httpx_mock.add_response(
        status_code=429,
        json={"error": {"message": "rate limit"}},
    )
    client = OpenRouterClient(api_key="sk-or-test", concurrency=2)
    with pytest.raises(RuntimeError, match="429"):
        await client.chat(model="x", system="s", user="u")
```

- [ ] **Step 2: Run — expect FAIL**

```bash
pytest tests/llm/test_openrouter.py -v
```

Expected: ModuleNotFoundError.

- [ ] **Step 3: Implement `src/crpg/llm/openrouter.py`**

```python
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
```

- [ ] **Step 4: Run — expect PASS**

```bash
pytest tests/llm/test_openrouter.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add src/crpg/llm/openrouter.py tests/llm/test_openrouter.py
git commit -m "feat(llm): async OpenRouter client with semaphore + provider pin"
```

---

### Task 2.2: Suffixes module (empirically-validated constants)

**Files:**
- Create: `src/crpg/llm/suffixes.py`
- Create: `tests/llm/test_suffixes.py`

- [ ] **Step 1: Write failing test**

`tests/llm/test_suffixes.py`:

```python
from crpg.llm.suffixes import (
    STRONG_SUFFIX, FEW_SHOT_SUFFIX, LENGTH_SUFFIX_SHORT,
    is_character_agnostic,
)

def test_suffixes_nonempty():
    assert len(STRONG_SUFFIX) > 500
    assert len(FEW_SHOT_SUFFIX) > 1500
    assert len(LENGTH_SUFFIX_SHORT) > 200

def test_suffixes_character_agnostic():
    # CRITICAL: suffixes must not reference Su Wan or her specific attrs
    forbidden = [
        "Su Wan", "sheer_black_tights", "black_ankle_boots",
        "stocking_toes", "red_toenails", "red_fingernails",
        "red_lipstick", "black_pencil_skirt", "public_formal",
    ]
    for s_name, s in [
        ("STRONG", STRONG_SUFFIX),
        ("FEW_SHOT", FEW_SHOT_SUFFIX),
        ("LENGTH_SHORT", LENGTH_SUFFIX_SHORT),
    ]:
        leaked = is_character_agnostic(s, forbidden)
        assert leaked == [], f"{s_name} leaked: {leaked}"

def test_strong_suffix_contains_framing_table():
    assert "ms_waist_up" in STRONG_SUFFIX
    assert "visible_regions" in STRONG_SUFFIX
    assert "MUST NOT" in STRONG_SUFFIX

def test_length_suffix_has_word_count():
    assert "2200" in LENGTH_SUFFIX_SHORT
    assert "2800" in LENGTH_SUFFIX_SHORT
```

- [ ] **Step 2: Run — expect FAIL**

```bash
pytest tests/llm/test_suffixes.py -v
```

Expected: ImportError.

- [ ] **Step 3: Implement `src/crpg/llm/suffixes.py`**

Copy `STRONG_SUFFIX_GENERIC` and `FEW_SHOT_SUFFIX_GENERIC` verbatim from `/tmp/director_generic_suffix_test.py` (already empirically validated 4/4 clean). Add `LENGTH_SUFFIX_SHORT` for Script hardening.

```python
"""System-prompt suffixes for provider hardening + length enforcement.

All suffixes are character-agnostic: they reference abstract placeholders
(attr_* tokens) and skill-level framing maps, not specific character attrs.

Empirically validated 2026-04-18: kimi-k2-0905 @Groq:
- STRONG + FEW_SHOT: Director 4/4 clean @ 4.3s (VGAI + base 6/6)
- LENGTH_SHORT: Script 2/3 hit 2200-2800 target (close miss)
"""

STRONG_SUFFIX = """

### CRITICAL RULE (output will be rejected if violated)

For every shot, before writing vgai_injected_attrs, verify each attribute's anchor region is in the framing's visible_regions set. Use this reference table:

| framing | visible_regions |
|---------|-----------------|
| ws_establishing | {} (empty — subject too small) |
| cu_face | {face, ear, neck} |
| ms_waist_up | {face, ear, neck, torso, hand} |
| three_quarter_knee_up | {face, ear, neck, torso, hand, leg_upper} |
| full_body_standing | {face, ear, neck, torso, hand, leg, foot} |
| hand_ecu | {hand} |
| feet_ecu | {foot} |
| back_reveal_walking | {torso_back, hand, leg, foot} |

Procedure for each shot:
1. Look up visible_regions for the chosen camera_framing.
2. For each attr from character_sheet.persistent_grooming ∪ wardrobe_state.items:
   - If attr.anchor ∈ visible_regions → may inject.
   - If attr.anchor ∉ visible_regions → MUST NOT inject; add to dropped list with reason.
3. ws_establishing means vgai_injected_attrs MUST be an empty list [] (subject too small for any detail).
4. Mutex check: for each pair in character_sheet.mutex_groups, if both would survive step 2, pick the visually dominant one for the pose; the other goes to dropped.

Violating step 1-4 makes the entire output invalid.
"""

FEW_SHOT_SUFFIX = """

### Canonical output pattern (abstract example — NOT copy these attr names)

Important: base identity (hair, skin, eye color, age, face shape) is ALWAYS in final_prompt regardless of framing. It is NEVER listed in vgai_injected_attrs or vgai_dropped (it's not a gated attribute).

Only GROOMING and WARDROBE items go through VGAI gating.

Suppose an abstract character with these GATED attrs:
- attr_LIP  (anchor: face)
- attr_NAIL (anchor: hand)
- attr_RING (anchor: hand)
- attr_SKIRT (anchor: torso)
- attr_HOSE  (anchor: leg)
- attr_TOENAIL (anchor: foot)
- attr_SHOE (anchor: foot)

And mutex_groups = [{attr_HOSE, attr_SHOE}, {attr_TOENAIL, attr_SHOE}].

Then the correct outputs look like:

```json
[
  {
    "shot_id": "example_ws",
    "camera_framing": "ws_establishing",
    "pose": "subject walks down street from a distance",
    "wardrobe_state_used": "some_state",
    "vgai_injected_attrs": [],
    "vgai_dropped_attrs_with_reason": ["all attrs dropped: ws_establishing visible_regions is empty"],
    "final_prompt": "<BASE IDENTITY DESCRIPTION>, walking down street, ws_establishing framing"
  },
  {
    "shot_id": "example_ms",
    "camera_framing": "ms_waist_up",
    "pose": "facing camera from waist up",
    "wardrobe_state_used": "some_state",
    "vgai_injected_attrs": ["attr_LIP", "attr_NAIL", "attr_RING", "attr_SKIRT"],
    "vgai_dropped_attrs_with_reason": [
      "attr_HOSE: leg not in visible_regions {face,ear,neck,torso,hand}",
      "attr_TOENAIL: foot not in visible_regions",
      "attr_SHOE: foot not in visible_regions"
    ],
    "final_prompt": "<BASE IDENTITY DESCRIPTION>, wearing attr_SKIRT, attr_LIP, attr_NAIL, attr_RING, ms_waist_up framing"
  },
  {
    "shot_id": "example_hand",
    "camera_framing": "hand_ecu",
    "pose": "extreme close-up on hand",
    "wardrobe_state_used": "some_state",
    "vgai_injected_attrs": ["attr_NAIL", "attr_RING"],
    "vgai_dropped_attrs_with_reason": [
      "attr_LIP: face not in visible_regions {hand}",
      "attr_SKIRT: torso not in visible_regions",
      "attr_HOSE: leg not in visible_regions",
      "attr_TOENAIL: foot not in visible_regions",
      "attr_SHOE: foot not in visible_regions"
    ],
    "final_prompt": "<BASE IDENTITY DESCRIPTION>, hand with attr_NAIL and attr_RING, hand_ecu framing"
  }
]
```

Notice: EVERY final_prompt begins with <BASE IDENTITY DESCRIPTION> (hair / skin / eye / age / face — copied verbatim from character_sheet.base), including the hand_ecu shot where no face is visible. Base identity is never gated by framing.

Apply the SAME pattern to the real character passed by the user. The attr names in your output MUST come from the real character_sheet, not from this abstract example.
"""

LENGTH_SUFFIX_SHORT = """

### 【硬性长度约束 — 未达标输出将被拒绝】
总字数必须 **2200-2800 字**。低于 2200 = 失败 = 必须继续展开直到达标。

各段最小字数（硬下限）：
- 主段 ≥ 1000 字
- A 支线 ≥ 450 字
- B 支线 ≥ 450 字

写完每段后在脑里数字数, 不够就继续展开（感官 / 心理 / 环境描写）。不要草草收尾。简洁不是美德, 字数不足才是失败。
"""

def is_character_agnostic(suffix: str, forbidden_terms: list[str]) -> list[str]:
    """Return list of forbidden terms that leaked into the suffix."""
    s = suffix.lower()
    return [t for t in forbidden_terms if t.lower() in s]
```

- [ ] **Step 4: Run — expect PASS**

```bash
pytest tests/llm/test_suffixes.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add src/crpg/llm/suffixes.py tests/llm/test_suffixes.py
git commit -m "feat(llm): character-agnostic hardening suffixes"
```

---

### Task 2.3: System prompts module

**Files:**
- Create: `src/crpg/llm/prompts.py`
- Create: `tests/llm/test_prompts.py`

- [ ] **Step 1: Write failing test**

`tests/llm/test_prompts.py`:

```python
from crpg.llm.prompts import (
    SKELETON_SYSTEM, DIRECTOR_SYSTEM,
    SCRIPT_SHORT_SYSTEM, SCRIPT_MAIN_SYSTEM,
    SCRIPT_BRANCH_A_SYSTEM, SCRIPT_BRANCH_B_SYSTEM,
)

def test_skeleton_mentions_schema():
    assert "story" in SKELETON_SYSTEM
    assert "characters" in SKELETON_SYSTEM
    assert "beats" in SKELETON_SYSTEM
    assert "snake_case" in SKELETON_SYSTEM  # optimization #1 from spec §10

def test_director_asks_for_json_array():
    assert "JSON" in DIRECTOR_SYSTEM
    assert "vgai_injected_attrs" in DIRECTOR_SYSTEM

def test_script_prompts_nonempty():
    for p in [SCRIPT_SHORT_SYSTEM, SCRIPT_MAIN_SYSTEM,
              SCRIPT_BRANCH_A_SYSTEM, SCRIPT_BRANCH_B_SYSTEM]:
        assert "双支线" in p or "主段" in p or "分支" in p or "支线" in p
```

- [ ] **Step 2: Run — expect FAIL**

Expected: ImportError.

- [ ] **Step 3: Implement `src/crpg/llm/prompts.py`**

```python
"""System prompts for each pipeline pass.

Skeleton: brief → Story + Characters JSON
Script short: single-call bifurcating prose (main + A + B in one output)
Script detailed: 3 separate prompts (main / branch_A / branch_B), concurrent
Director: beat prose + characters → shot list
"""

SKELETON_SYSTEM = """你是 crpg (互动 noir 小说) 的 Skeleton 生成器。
输入: 创作者 brief + 3 轴参数 (contentLength / detailRichness / structure)。
输出: 2 个 JSON: story + characters。

### story JSON schema
{
  "meta": {"title", "genre", "contentLength", "detailRichness", "structure"},
  "beats": [
    {
      "id": str,
      "type": "narrative"|"choice"|"check"|"merge"|"act_break"|"ending",
      "synopsis": str,
      "valueBefore": str,
      "valueAfter": str,
      "wardrobe_state": str,
      "targetWordCount": int,
      "targetShotCount": int,
      "depends_on": [beat_id, ...]
    }
  ],
  "edges": [{"from": beat_id, "to": beat_id, "condition": str}]
}

### characters JSON schema
{
  "<character_name>": {
    "base": {"age": int, "ethnicity": str, "hair": str, "skin": str, "eyes": str, "jaw": str},
    "persistent_grooming": [{"name": str, "anchor": str, "sub_anchor"?: str}],
    "wardrobe_states": {"<state>": {"items": [{"name": str, "anchor": str}], "removes"?: [...]}},
    "mutex_groups": [[name1, name2], ...]
  }
}

### CRITICAL naming convention
All `persistent_grooming[].name`, `wardrobe_states.*.items[].name`, `mutex_groups` entries
MUST be snake_case English (e.g. `red_fingernails`, `sheer_black_tights`, `black_ankle_boots`).
This matches Director's internal anchor map. Chinese descriptions go in a separate
`display_name` field if needed.

### Rules
1. targetWordCount by detailRichness:
   concise=1500, standard=2200, detailed=2500, extreme=3500
2. targetShotCount by detailRichness:
   concise=1-2, standard=2-3, detailed=4-6, extreme=6-10
3. Structure → edges:
   linear: single chain; bifurcating: main→{A,B}; funnel: many→climax; web: graph
4. Total beats by contentLength:
   short=3, medium=15-18, long=50-60
5. mutex_groups: physically impossible pairs (e.g. [sheer_black_tights, black_ankle_boots])
6. anchor values: face|ear|neck|hand|torso|torso_back|leg|leg_upper|foot

### Output format (strict)
Output a SINGLE JSON object, no markdown wrap:
{"story": {...}, "characters": {...}}
"""

DIRECTOR_SYSTEM = """你是一名 Director LLM, 把小说片段翻译为 Grok Imagine Pro 的生图 prompts。

### VGAI 规则（必守）
属性只在 anchor 身体区域在 framing.visible_regions 里时写入。

### 禁用话术
- 否定词: NOT X / never Y / hidden / covered by / without
- 位置微管理: every toe / each X / at the tips
- 层叠话术: visible through / showing beneath / hint of
- Dutch angle

### 关键原则 — default KEEP
当姿势暗示某个 anchor "可能"在画面内时, 默认保留属性。
以下理由不足以 drop:
- "pose-dependent" / "may not be primary focus" / "not guaranteed" / "depends on framing"
只在姿势明确隐藏 anchor 时 drop (pure sole-view / 头发完全遮耳 / 完全被物体遮挡)。

### 输出
JSON 数组, 每 shot 含:
  shot_id / camera_framing / pose / wardrobe_state_used /
  vgai_injected_attrs / vgai_dropped_attrs_with_reason / final_prompt

只输出 JSON 数组, 无 markdown 包装。base 身份 (发/肤/眼/年龄/脸) 永远在 final_prompt 开头
但不列入 vgai_injected_attrs (vgai_injected_attrs 只含 grooming + wardrobe items)。

character_sheet 和 framing-region 表会在 user 消息里给你。
"""

SCRIPT_SHORT_SYSTEM = """你是都市 noir 互动小说的生成器。遵守这几条硬约束:

1. 双支线硬结构: 主段 → 价值转变点 → 两条不同方向的分支 (A, B), 各 300-500 字。
2. 感官细节服从剧情: 可写衣物质感 / 光线 / 体温 / 气味 / 呼吸变化, 但每个细节必须推进情绪或揭示人物。
3. 克制暗示, 不写具体性器: 允许亲密触碰 / 亲吻 / 呼吸急促 / 肢体纠缠; 禁止性器名称与特写。
4. 主段需有价值转变 (安全→危险 / 距离→亲近 / 克制→失控); A/B 必须呈现真正不同的走向。
5. 纯中文散文, 无 markdown / 角色标签 / 旁白解说。
6. 总字数 2200-2800 字之间。

禁忌:
- "她的签名款" / "她一贯的" / "如往常般"
- 出戏型比喻 ("仿佛电影镜头")
- 价值转变点没到就 branch
"""

SCRIPT_MAIN_SYSTEM = """你是都市 noir 互动小说的生成器, 只写【主段】(细腻模式)。

【硬性长度】2000-2300 字。低于 2000 = 失败 = 继续展开。
【写什么】从 Su Wan 下班 → 地铁口被搭讪 → 走到花店 → Kai 买玫瑰 → 她辨认熟悉面孔。
【结束在哪里】价值转变点那一刻 (职业警觉 → 模糊的失控感), 她决定还没做出。不要推进到分支选择。

【约束】
- 感官细节服从剧情, 不做橱窗展示
- 克制暗示, 不写性器
- 禁 "她的签名款" / "她一贯的" / "如往常般"
- 纯中文散文, 无 markdown / 角色标签
"""

SCRIPT_BRANCH_A_SYSTEM = """你是都市 noir 互动小说的生成器, 只写【A 支线】(细腻模式)。

【上下文】主段已经写好 (见 user 消息), 停在价值转变点。你的任务: 承接主段末尾, 写 A 支线。

【硬性长度】1400-1700 字。低于 1400 = 失败 = 继续展开。
【内部结构】支线内部有小曲线: 决定的冲动 → 执行 → 决定后的余震。

【约束】
- 开头不要重复主段已交代的事
- 纯中文散文, 不要 markdown 标题 / "A 支线:" 标签
- 首字就进入承接点那一刻
"""

SCRIPT_BRANCH_B_SYSTEM = """你是都市 noir 互动小说的生成器, 只写【B 支线】(细腻模式)。

【上下文】主段已经写好 (见 user 消息), 停在价值转变点。你的任务: 承接主段末尾, 写 B 支线。

【硬性长度】1400-1700 字。低于 1400 = 失败 = 继续展开。
【内部结构】支线内部有小曲线: 进入 → 张力积累 → 价值转变。

【约束】
- 开头不要重复主段已交代的事
- 首字就进入承接点那一刻
- 克制, 不写性器名称与特写
- 纯中文散文
"""
```

- [ ] **Step 4: Run — expect PASS**

```bash
pytest tests/llm/test_prompts.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add src/crpg/llm/prompts.py tests/llm/test_prompts.py
git commit -m "feat(llm): system prompts for all pipeline passes"
```

---

# Phase 3 — Validation

### Task 3.1: VGAI validator

**Files:**
- Create: `src/crpg/validation/vgai.py`
- Create: `tests/validation/test_vgai.py`

- [ ] **Step 1: Write failing test**

`tests/validation/test_vgai.py`:

```python
import pytest
from crpg.validation.vgai import validate_shot, validate_shot_list, VgaiViolation
from crpg.types import Shot, Character, Base, Grooming, WardrobeItem, WardrobeState

@pytest.fixture
def char():
    return Character(
        base=Base(age=28, ethnicity="Chinese", hair="long black", skin="fair",
                  eyes="brown", jaw="soft"),
        persistent_grooming=[
            Grooming(name="red_fingernails", anchor="hand"),
            Grooming(name="red_toenails", anchor="foot"),
            Grooming(name="red_lipstick", anchor="face"),
        ],
        wardrobe_states={"public_formal": WardrobeState(items=[
            WardrobeItem(name="black_pencil_skirt", anchor="torso"),
            WardrobeItem(name="sheer_black_tights", anchor="leg"),
            WardrobeItem(name="black_ankle_boots", anchor="foot"),
        ])},
        mutex_groups=[["sheer_black_tights", "black_ankle_boots"]],
    )

def test_valid_hand_ecu(char):
    s = Shot(shot_id="s1", camera_framing="hand_ecu", pose="close-up hand",
             wardrobe_state_used="public_formal",
             vgai_injected_attrs=["red_fingernails"],
             vgai_dropped_attrs_with_reason=["red_toenails: foot not in visible"],
             final_prompt="hand with red fingernails")
    violations = validate_shot(s, char)
    assert violations == []

def test_vgai_violation_leg_in_ms_waist_up(char):
    s = Shot(shot_id="s2", camera_framing="ms_waist_up", pose="standing",
             wardrobe_state_used="public_formal",
             vgai_injected_attrs=["sheer_black_tights"],
             vgai_dropped_attrs_with_reason=[],
             final_prompt="...")
    violations = validate_shot(s, char)
    assert len(violations) == 1
    assert violations[0].attr == "sheer_black_tights"
    assert "leg" in violations[0].reason

def test_mutex_violation(char):
    s = Shot(shot_id="s3", camera_framing="full_body_standing", pose="stand",
             wardrobe_state_used="public_formal",
             vgai_injected_attrs=["sheer_black_tights", "black_ankle_boots"],
             vgai_dropped_attrs_with_reason=[],
             final_prompt="...")
    violations = validate_shot(s, char)
    assert any(v.kind == "mutex" for v in violations)

def test_back_reveal_skirt_allowed(char):
    # torso_back visibility should let torso-anchored items pass
    s = Shot(shot_id="s4", camera_framing="back_reveal_walking", pose="walking away",
             wardrobe_state_used="public_formal",
             vgai_injected_attrs=["black_pencil_skirt"],
             vgai_dropped_attrs_with_reason=[],
             final_prompt="...")
    violations = validate_shot(s, char)
    assert violations == []

def test_ws_establishing_empty_only(char):
    s = Shot(shot_id="s5", camera_framing="ws_establishing", pose="distant",
             wardrobe_state_used="public_formal",
             vgai_injected_attrs=["red_fingernails"],
             vgai_dropped_attrs_with_reason=[],
             final_prompt="...")
    violations = validate_shot(s, char)
    assert any("ws_establishing" in str(v.reason) for v in violations)
```

- [ ] **Step 2: Run — expect FAIL**

Expected: ImportError.

- [ ] **Step 3: Implement `src/crpg/validation/vgai.py`**

```python
"""VGAI (Visibility-Gated Attribute Injection) compliance auditor."""
from dataclasses import dataclass
from crpg.types import Shot, Character

# Framing → visible regions. Keep in sync with STRONG_SUFFIX table.
# torso_back is treated as satisfying torso for wrap-around wardrobe items
# like pencil skirts that are visible both front and back.
REGION_MAP: dict[str, set[str]] = {
    "cu_face": {"face", "ear", "neck"},
    "ms_waist_up": {"face", "ear", "neck", "torso", "hand"},
    "three_quarter_knee_up": {"face", "ear", "neck", "torso", "hand", "leg_upper"},
    "full_body_standing": {"face", "ear", "neck", "torso", "hand", "leg", "foot"},
    "feet_ecu": {"foot"},
    "hand_ecu": {"hand"},
    "back_reveal_walking": {"torso", "torso_back", "hand", "leg", "foot"},
    "ws_establishing": set(),
}

@dataclass(slots=True)
class VgaiViolation:
    shot_id: str
    kind: str  # "vgai" | "mutex" | "ws_nonempty" | "unknown_framing" | "unknown_attr"
    attr: str | None
    reason: str

def _build_attr_map(character: Character, wardrobe_state: str) -> dict[str, str]:
    """Return {attr_name: anchor} combining persistent grooming + requested wardrobe state."""
    attrs: dict[str, str] = {g.name: g.anchor for g in character.persistent_grooming}
    ws = character.wardrobe_states.get(wardrobe_state)
    if ws:
        for item in ws.items:
            attrs[item.name] = item.anchor
        for removed in ws.removes:
            attrs.pop(removed, None)
    return attrs

def validate_shot(shot: Shot, character: Character) -> list[VgaiViolation]:
    violations: list[VgaiViolation] = []
    visible = REGION_MAP.get(shot.camera_framing)
    if visible is None:
        return [VgaiViolation(shot.shot_id, "unknown_framing", None,
                              f"unknown framing: {shot.camera_framing}")]
    attr_anchor = _build_attr_map(character, shot.wardrobe_state_used)

    # ws_establishing must have empty vgai_injected_attrs
    if shot.camera_framing == "ws_establishing" and shot.vgai_injected_attrs:
        for a in shot.vgai_injected_attrs:
            violations.append(VgaiViolation(
                shot.shot_id, "ws_nonempty", a,
                "ws_establishing visible_regions is empty; no attrs may inject"))

    # VGAI check: each injected attr's anchor must be in visible_regions
    for attr in shot.vgai_injected_attrs:
        anchor = attr_anchor.get(attr)
        if anchor is None:
            violations.append(VgaiViolation(
                shot.shot_id, "unknown_attr", attr,
                f"attr {attr!r} not in character_sheet"))
            continue
        if shot.camera_framing == "ws_establishing":
            continue  # already flagged above
        if anchor not in visible:
            violations.append(VgaiViolation(
                shot.shot_id, "vgai", attr,
                f"{attr} (anchor={anchor}) not in visible_regions {sorted(visible)}"))

    # Mutex check
    injected = set(shot.vgai_injected_attrs)
    for group in character.mutex_groups:
        common = set(group) & injected
        if len(common) >= 2:
            violations.append(VgaiViolation(
                shot.shot_id, "mutex", None,
                f"mutex pair {sorted(common)} both injected"))

    return violations

def validate_shot_list(shots: list[Shot], character: Character) -> list[VgaiViolation]:
    out: list[VgaiViolation] = []
    for s in shots:
        out.extend(validate_shot(s, character))
    return out
```

- [ ] **Step 4: Run — expect PASS**

```bash
pytest tests/validation/test_vgai.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add src/crpg/validation/vgai.py tests/validation/test_vgai.py
git commit -m "feat(validation): VGAI compliance + mutex auditor"
```

---

### Task 3.2: Skeleton/story schema validator

**Files:**
- Create: `src/crpg/validation/schema.py`
- Create: `tests/validation/test_schema.py`

- [ ] **Step 1: Write failing test**

`tests/validation/test_schema.py`:

```python
import pytest
from crpg.validation.schema import parse_skeleton_output, SchemaError

def test_parse_good_skeleton():
    raw = '''{"story": {
      "meta": {"title":"t","genre":"noir","contentLength":"short",
               "detailRichness":"detailed","structure":"bifurcating"},
      "beats": [{"id":"intro","type":"narrative","synopsis":"s",
                 "valueBefore":"calm","valueAfter":"alert",
                 "targetWordCount":2500,"targetShotCount":5,
                 "wardrobe_state":"public_formal","depends_on":[]}],
      "edges": []
    },
    "characters": {
      "Su Wan": {
        "base":{"age":28,"ethnicity":"汉","hair":"h","skin":"s","eyes":"e","jaw":"j"},
        "persistent_grooming":[{"name":"red_fingernails","anchor":"hand"}],
        "wardrobe_states":{"public_formal":{"items":[
          {"name":"black_pencil_skirt","anchor":"torso"}], "removes":[]}},
        "mutex_groups":[]
      }
    }}'''
    story, chars = parse_skeleton_output(raw)
    assert story.meta.title == "t"
    assert "Su Wan" in chars

def test_parse_code_fenced():
    raw = '```json\n{"story":{"meta":{"title":"t","genre":"n","contentLength":"short","detailRichness":"standard","structure":"linear"},"beats":[],"edges":[]},"characters":{}}\n```'
    story, chars = parse_skeleton_output(raw)
    assert story.meta.title == "t"

def test_parse_invalid_json_raises():
    with pytest.raises(SchemaError, match="JSON"):
        parse_skeleton_output("not json")

def test_parse_missing_top_keys():
    with pytest.raises(SchemaError, match="story"):
        parse_skeleton_output('{"characters":{}}')
```

- [ ] **Step 2: Run — expect FAIL**

Expected: ImportError.

- [ ] **Step 3: Implement `src/crpg/validation/schema.py`**

```python
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
```

- [ ] **Step 4: Run — expect PASS**

```bash
pytest tests/validation/test_schema.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add src/crpg/validation/schema.py tests/validation/test_schema.py
git commit -m "feat(validation): skeleton + director output parsers"
```

---

# Phase 4 — Pipeline passes

### Task 4.1: Skeleton pass

**Files:**
- Create: `src/crpg/passes/skeleton.py`
- Create: `tests/passes/test_skeleton.py`
- Create: `tests/fixtures/canonical_skeleton.json`

- [ ] **Step 1: Create canonical fixture**

Run the actual Skeleton LLM once locally (or copy from `research/model-comparison-2026-04-18/open-source-broad/skeleton_test/iter2.json`) and save sanitized to `tests/fixtures/canonical_skeleton.json`. Must contain `story` + `characters` keys.

Alternative: hand-craft a minimal valid one. Use the test structure below as template:

```json
{
  "story": {
    "meta": {"title":"Rainy Noir","genre":"都市 noir","contentLength":"short",
             "detailRichness":"detailed","structure":"bifurcating"},
    "beats": [
      {"id":"intro","type":"narrative","synopsis":"Su Wan 下班入雨夜",
       "valueBefore":"calm","valueAfter":"alert","wardrobe_state":"public_formal",
       "targetWordCount":2500,"targetShotCount":5,"depends_on":[]},
      {"id":"main","type":"narrative","synopsis":"花店递玫瑰",
       "valueBefore":"alert","valueAfter":"unstable","wardrobe_state":"public_formal",
       "targetWordCount":2500,"targetShotCount":5,"depends_on":["intro"]},
      {"id":"A_decline","type":"ending","synopsis":"独自回家",
       "valueBefore":"unstable","valueAfter":"alert","wardrobe_state":"public_formal",
       "targetWordCount":1500,"targetShotCount":4,"depends_on":["main"]},
      {"id":"B_accept","type":"ending","synopsis":"去酒吧",
       "valueBefore":"unstable","valueAfter":"out_of_control","wardrobe_state":"public_formal",
       "targetWordCount":1500,"targetShotCount":4,"depends_on":["main"]}
    ],
    "edges": [
      {"from":"intro","to":"main"},
      {"from":"main","to":"A_decline","condition":"decline"},
      {"from":"main","to":"B_accept","condition":"accept"}
    ]
  },
  "characters": {
    "Su Wan": {
      "base":{"age":28,"ethnicity":"Chinese","hair":"long black center-parted","skin":"fair","eyes":"brown","jaw":"soft"},
      "persistent_grooming":[
        {"name":"red_fingernails","anchor":"hand"},
        {"name":"red_toenails","anchor":"foot"},
        {"name":"red_lipstick","anchor":"face"}
      ],
      "wardrobe_states":{"public_formal":{"items":[
        {"name":"black_pencil_skirt","anchor":"torso"},
        {"name":"sheer_black_tights","anchor":"leg"},
        {"name":"black_ankle_boots","anchor":"foot"}
      ],"removes":[]}},
      "mutex_groups":[["sheer_black_tights","black_ankle_boots"]]
    }
  }
}
```

- [ ] **Step 2: Write failing test**

`tests/passes/test_skeleton.py`:

```python
import pathlib, json
import pytest
from crpg.passes.skeleton import run_skeleton
from crpg.llm.openrouter import OpenRouterClient

@pytest.mark.asyncio
async def test_skeleton_calls_groq(httpx_mock, fixture_path):
    canonical = (fixture_path / "canonical_skeleton.json").read_text(encoding="utf-8")
    httpx_mock.add_response(
        url="https://openrouter.ai/api/v1/chat/completions",
        json={"choices":[{"message":{"content":canonical},"finish_reason":"stop"}],
              "usage":{"cost":0.003},"provider":"Groq"},
    )
    client = OpenRouterClient(api_key="sk-or-test", concurrency=2)
    story, chars = await run_skeleton(client, brief="my brief")
    assert story.meta.title == "Rainy Noir"
    assert "Su Wan" in chars
    assert len(story.beats) == 4
    req = httpx_mock.get_requests()[0]
    body = json.loads(req.read())
    assert body["provider"]["order"] == ["Groq"]
    assert body["model"] == "moonshotai/kimi-k2-0905"

@pytest.mark.asyncio
async def test_skeleton_parse_error_raises(httpx_mock):
    httpx_mock.add_response(json={"choices":[{"message":{"content":"not json"},"finish_reason":"stop"}], "usage":{}})
    client = OpenRouterClient(api_key="sk-or-test", concurrency=2)
    with pytest.raises(Exception):
        await run_skeleton(client, brief="bad")
```

- [ ] **Step 3: Run — expect FAIL**

Expected: ImportError.

- [ ] **Step 4: Implement `src/crpg/passes/skeleton.py`**

```python
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
```

- [ ] **Step 5: Run — expect PASS**

```bash
pytest tests/passes/test_skeleton.py -v
```

Expected: 2 passed.

- [ ] **Step 6: Commit**

```bash
git add src/crpg/passes/skeleton.py tests/passes/test_skeleton.py tests/fixtures/canonical_skeleton.json
git commit -m "feat(passes): Pass 1 Skeleton (brief → Story+Characters)"
```

---

### Task 4.2: Script pass (short + detailed modes)

**Files:**
- Create: `src/crpg/passes/script.py`
- Create: `tests/passes/test_script.py`
- Create: `tests/fixtures/canonical_script_short.md`

- [ ] **Step 1: Create fixture**

`tests/fixtures/canonical_script_short.md`:

```
雨丝像细针扎在南京西路上。Su Wan 把风衣领口竖到最高。
(...主段 ~800 字, 省略)


她后退半步, 说不顺路。车门关上之前, 她看了一眼花店的方向。
(...A 支线 ~400 字, 省略)


她接过玫瑰, 跟着他穿过巷口。暖黄色的灯光在他肩上落下。
(...B 支线 ~400 字, 省略)
```

- [ ] **Step 2: Write failing test**

`tests/passes/test_script.py`:

```python
import pytest, json
from crpg.passes.script import run_script_short, run_script_detailed
from crpg.llm.openrouter import OpenRouterClient

@pytest.mark.asyncio
async def test_script_short_single_call(httpx_mock, fixture_path):
    text = (fixture_path / "canonical_script_short.md").read_text(encoding="utf-8")
    httpx_mock.add_response(
        json={"choices":[{"message":{"content":text},"finish_reason":"stop"}],
              "usage":{"cost":0.005},"provider":"Groq"},
    )
    client = OpenRouterClient(api_key="sk-or-test", concurrency=2)
    out = await run_script_short(client, beat_user_prompt="write this short bifurcation")
    assert "雨丝" in out

@pytest.mark.asyncio
async def test_script_detailed_three_calls(httpx_mock):
    # main call
    httpx_mock.add_response(
        json={"choices":[{"message":{"content":"主段文本..."},"finish_reason":"stop"}], "usage":{}},
    )
    # A branch
    httpx_mock.add_response(
        json={"choices":[{"message":{"content":"A 支线文本..."},"finish_reason":"stop"}], "usage":{}},
    )
    # B branch
    httpx_mock.add_response(
        json={"choices":[{"message":{"content":"B 支线文本..."},"finish_reason":"stop"}], "usage":{}},
    )
    client = OpenRouterClient(api_key="sk-or-test", concurrency=5)
    main, a, b = await run_script_detailed(client, scene_brief="scene setup...")
    assert main == "主段文本..."
    assert a == "A 支线文本..."
    assert b == "B 支线文本..."
    assert len(httpx_mock.get_requests()) == 3
```

- [ ] **Step 3: Run — expect FAIL**

Expected: ImportError.

- [ ] **Step 4: Implement `src/crpg/passes/script.py`**

```python
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
```

- [ ] **Step 5: Run — expect PASS**

```bash
pytest tests/passes/test_script.py -v
```

Expected: 2 passed.

- [ ] **Step 6: Commit**

```bash
git add src/crpg/passes/script.py tests/passes/test_script.py tests/fixtures/canonical_script_short.md
git commit -m "feat(passes): Pass 2 Script (short single-call + detailed segmented)"
```

---

### Task 4.3: Director pass

**Files:**
- Create: `src/crpg/passes/director.py`
- Create: `tests/passes/test_director.py`
- Create: `tests/fixtures/canonical_shots.json`

- [ ] **Step 1: Create fixture**

`tests/fixtures/canonical_shots.json`:

```json
[
  {"shot_id":"s1","camera_framing":"ms_waist_up","pose":"standing at florist",
   "wardrobe_state_used":"public_formal",
   "vgai_injected_attrs":["red_lipstick","red_fingernails","black_pencil_skirt"],
   "vgai_dropped_attrs_with_reason":["sheer_black_tights: leg not in visible_regions","black_ankle_boots: foot not in visible"],
   "final_prompt":"28 y.o. Chinese woman, long black hair, fair skin, red lipstick, red fingernails, black pencil skirt, standing at a florist, ms_waist_up"},
  {"shot_id":"s2","camera_framing":"hand_ecu","pose":"receiving card",
   "wardrobe_state_used":"public_formal",
   "vgai_injected_attrs":["red_fingernails"],
   "vgai_dropped_attrs_with_reason":["red_lipstick: face not in visible_regions"],
   "final_prompt":"close-up hand with red fingernails receiving a card, hand_ecu"}
]
```

- [ ] **Step 2: Write failing test**

`tests/passes/test_director.py`:

```python
import pytest, json
from crpg.passes.director import run_director
from crpg.llm.openrouter import OpenRouterClient
from crpg.types import Character, Base, Grooming, WardrobeItem, WardrobeState

@pytest.fixture
def su_wan():
    return Character(
        base=Base(age=28, ethnicity="Chinese", hair="long black", skin="fair",
                  eyes="brown", jaw="soft"),
        persistent_grooming=[
            Grooming(name="red_fingernails", anchor="hand"),
            Grooming(name="red_lipstick", anchor="face"),
        ],
        wardrobe_states={"public_formal": WardrobeState(items=[
            WardrobeItem(name="black_pencil_skirt", anchor="torso"),
            WardrobeItem(name="sheer_black_tights", anchor="leg"),
            WardrobeItem(name="black_ankle_boots", anchor="foot"),
        ])},
        mutex_groups=[["sheer_black_tights", "black_ankle_boots"]],
    )

@pytest.mark.asyncio
async def test_director_returns_shots(httpx_mock, fixture_path, su_wan):
    canonical = (fixture_path / "canonical_shots.json").read_text(encoding="utf-8")
    httpx_mock.add_response(
        json={"choices":[{"message":{"content":canonical},"finish_reason":"stop"}],
              "usage":{"cost":0.004},"provider":"Groq"},
    )
    client = OpenRouterClient(api_key="sk-or-test", concurrency=2)
    shots = await run_director(
        client,
        beat_id="intro",
        beat_prose="主段文本",
        character_name="Su Wan", character=su_wan,
        wardrobe_state="public_formal",
        target_shot_count=2,
    )
    assert len(shots) == 2
    assert shots[0].camera_framing == "ms_waist_up"
    assert shots[0].vgai_injected_attrs == ["red_lipstick","red_fingernails","black_pencil_skirt"]

@pytest.mark.asyncio
async def test_director_user_message_includes_character(httpx_mock, fixture_path, su_wan):
    canonical = (fixture_path / "canonical_shots.json").read_text(encoding="utf-8")
    httpx_mock.add_response(
        json={"choices":[{"message":{"content":canonical},"finish_reason":"stop"}], "usage":{}},
    )
    client = OpenRouterClient(api_key="sk-or-test", concurrency=2)
    await run_director(
        client, beat_id="intro", beat_prose="p", character_name="Su Wan",
        character=su_wan, wardrobe_state="public_formal", target_shot_count=2,
    )
    req = httpx_mock.get_requests()[0]
    body = json.loads(req.read())
    # User message must carry character info for the model to reference names
    user_text = body["messages"][1]["content"]
    assert "Su Wan" in user_text
    assert "red_fingernails" in user_text
```

- [ ] **Step 3: Run — expect FAIL**

Expected: ImportError.

- [ ] **Step 4: Implement `src/crpg/passes/director.py`**

```python
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
```

- [ ] **Step 5: Run — expect PASS**

```bash
pytest tests/passes/test_director.py -v
```

Expected: 2 passed.

- [ ] **Step 6: Commit**

```bash
git add src/crpg/passes/director.py tests/passes/test_director.py tests/fixtures/canonical_shots.json
git commit -m "feat(passes): Pass 3 Director (beat+character → shot list)"
```

---

### Task 4.4: Assembler (pure function)

**Files:**
- Create: `src/crpg/passes/assembler.py`
- Create: `tests/passes/test_assembler.py`

- [ ] **Step 1: Write failing test**

`tests/passes/test_assembler.py`:

```python
from crpg.passes.assembler import assemble_image_prompt, ANIME_PREAMBLE
from crpg.types import Shot

def test_anime_preamble_prepended():
    shot = Shot(shot_id="s1", camera_framing="cu_face", pose="face",
                wardrobe_state_used="public_formal",
                vgai_injected_attrs=["red_lipstick"],
                vgai_dropped_attrs_with_reason=[],
                final_prompt="28 y.o. woman face close-up")
    prompt = assemble_image_prompt(shot)
    assert prompt.startswith(ANIME_PREAMBLE)
    assert "28 y.o. woman face close-up" in prompt

def test_assembler_is_pure():
    shot = Shot(shot_id="s1", camera_framing="cu_face", pose="p",
                wardrobe_state_used="public_formal",
                vgai_injected_attrs=[], vgai_dropped_attrs_with_reason=[],
                final_prompt="x")
    p1 = assemble_image_prompt(shot)
    p2 = assemble_image_prompt(shot)
    assert p1 == p2  # deterministic, no state
```

- [ ] **Step 2: Run — expect FAIL**

Expected: ImportError.

- [ ] **Step 3: Implement `src/crpg/passes/assembler.py`**

```python
"""Pass 4: Prompt Assembler — pure function from Shot → Grok image prompt string."""
from crpg.types import Shot

ANIME_PREAMBLE = (
    "anime illustration style, clean line art, cel-shaded, 2D rendering, "
    "soft bokeh background, high-detail foreground subject, "
)

def assemble_image_prompt(shot: Shot) -> str:
    """Prepend ANIME_PREAMBLE to the Director-generated final_prompt.

    This is deliberately minimal: Director already produced a complete prompt.
    Assembler only adds the anime-style preamble (once per shot).
    """
    return ANIME_PREAMBLE + shot.final_prompt
```

- [ ] **Step 4: Run — expect PASS**

```bash
pytest tests/passes/test_assembler.py -v
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add src/crpg/passes/assembler.py tests/passes/test_assembler.py
git commit -m "feat(passes): Pass 4 Assembler (pure fn shot → Grok prompt)"
```

---

# Phase 5 — Image generation

### Task 5.1: xAI Grok Imagine async client

**Files:**
- Create: `src/crpg/llm/xai.py`
- Create: `tests/llm/test_xai.py`

- [ ] **Step 1: Write failing test**

`tests/llm/test_xai.py`:

```python
import pytest, base64
from crpg.llm.xai import XaiImageClient

FAKE_PNG_B64 = base64.b64encode(b"\x89PNG\r\n\x1a\n" + b"\x00" * 64).decode()

@pytest.mark.asyncio
async def test_generate_image(httpx_mock):
    httpx_mock.add_response(
        url="https://api.x.ai/v1/images/generations",
        json={"data":[{"b64_json": FAKE_PNG_B64}]},
    )
    client = XaiImageClient(api_key="xai-test", concurrency=3)
    png_bytes = await client.generate(prompt="test prompt", model="grok-imagine-pro")
    assert png_bytes.startswith(b"\x89PNG")

@pytest.mark.asyncio
async def test_xai_error(httpx_mock):
    httpx_mock.add_response(status_code=500, json={"error":{"message":"oops"}})
    client = XaiImageClient(api_key="xai-test", concurrency=3)
    with pytest.raises(RuntimeError, match="500"):
        await client.generate(prompt="p")
```

- [ ] **Step 2: Run — expect FAIL**

Expected: ImportError.

- [ ] **Step 3: Implement `src/crpg/llm/xai.py`**

```python
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
        model: str = "grok-imagine-pro",
        size: str = "1024x1024",
        n: int = 1,
        client: httpx.AsyncClient | None = None,
    ) -> bytes:
        """Generate one image. Returns PNG bytes."""
        payload = {"model": model, "prompt": prompt, "n": n, "size": size,
                   "response_format": "b64_json"}
        async with self._sem:
            owns = client is None
            c = client or httpx.AsyncClient(timeout=self._timeout)
            try:
                r = await c.post(self._endpoint, json=payload, headers=self._headers)
                if r.status_code != 200:
                    raise RuntimeError(f"xAI {r.status_code}: {r.text[:400]}")
                body = r.json()
            finally:
                if owns:
                    await c.aclose()
        b64_str = body["data"][0]["b64_json"]
        return base64.b64decode(b64_str)
```

- [ ] **Step 4: Run — expect PASS**

```bash
pytest tests/llm/test_xai.py -v
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add src/crpg/llm/xai.py tests/llm/test_xai.py
git commit -m "feat(llm): xAI Grok Imagine async client"
```

---

### Task 5.2: Image batch runner

**Files:**
- Create: `src/crpg/passes/image.py`
- Create: `tests/passes/test_image.py`

- [ ] **Step 1: Write failing test**

`tests/passes/test_image.py`:

```python
import pytest, asyncio, base64
from pathlib import Path
from crpg.passes.image import render_shots_to_disk
from crpg.types import Shot
from crpg.llm.xai import XaiImageClient

FAKE_PNG_B64 = base64.b64encode(b"\x89PNG\r\n\x1a\n" + b"\x00" * 64).decode()

@pytest.mark.asyncio
async def test_render_shots_writes_png_files(tmp_path, httpx_mock):
    # 3 shots → 3 API calls
    for _ in range(3):
        httpx_mock.add_response(json={"data":[{"b64_json": FAKE_PNG_B64}]})
    client = XaiImageClient(api_key="xai-test", concurrency=3)
    shots = [
        Shot(shot_id=f"s{i}", camera_framing="cu_face", pose="p",
             wardrobe_state_used="w",
             vgai_injected_attrs=[], vgai_dropped_attrs_with_reason=[],
             final_prompt=f"prompt {i}")
        for i in range(3)
    ]
    out_dir = tmp_path / "shots" / "intro"
    paths = await render_shots_to_disk(
        client, shots=shots, out_dir=out_dir, prompts=[f"prompt_{i}" for i in range(3)],
    )
    assert len(paths) == 3
    for p in paths:
        assert p.exists()
        assert p.read_bytes().startswith(b"\x89PNG")
    # Sorted by shot_id
    assert paths[0].name == "shot-001.png"
    assert paths[2].name == "shot-003.png"
```

- [ ] **Step 2: Run — expect FAIL**

Expected: ImportError.

- [ ] **Step 3: Implement `src/crpg/passes/image.py`**

```python
"""Pass 5: Image batch — render shot prompts to PNG files."""
import asyncio
from pathlib import Path
from crpg.types import Shot
from crpg.llm.xai import XaiImageClient

async def render_shots_to_disk(
    client: XaiImageClient,
    *,
    shots: list[Shot],
    out_dir: Path,
    prompts: list[str],
    model: str = "grok-imagine-pro",
) -> list[Path]:
    """Render each shot's prompt to a PNG under out_dir/shot-NNN.png.

    Returns list of written paths, ordered same as input shots.
    Concurrency is bounded by the XaiImageClient's semaphore.
    """
    if len(shots) != len(prompts):
        raise ValueError(f"shot/prompt count mismatch: {len(shots)} vs {len(prompts)}")
    out_dir.mkdir(parents=True, exist_ok=True)

    async def _one(i: int, prompt: str) -> Path:
        png_bytes = await client.generate(prompt=prompt, model=model)
        path = out_dir / f"shot-{i+1:03d}.png"
        path.write_bytes(png_bytes)
        return path

    tasks = [_one(i, p) for i, p in enumerate(prompts)]
    return list(await asyncio.gather(*tasks))
```

- [ ] **Step 4: Run — expect PASS**

```bash
pytest tests/passes/test_image.py -v
```

Expected: 1 passed.

- [ ] **Step 5: Commit**

```bash
git add src/crpg/passes/image.py tests/passes/test_image.py
git commit -m "feat(passes): Pass 5 Image batch (prompts → PNG files)"
```

---

# Phase 6 — Orchestration

### Task 6.1: DAG topological layers

**Files:**
- Create: `src/crpg/orchestration/dag.py`
- Create: `tests/orchestration/test_dag.py`

- [ ] **Step 1: Write failing test**

`tests/orchestration/test_dag.py`:

```python
import pytest
from crpg.orchestration.dag import topological_layers, CycleError
from crpg.types import Beat

def mk(id_, deps=()):
    return Beat(id=id_, type="narrative", synopsis="",
                valueBefore="x", valueAfter="y",
                targetWordCount=100, targetShotCount=1, depends_on=list(deps))

def test_linear_chain():
    beats = [mk("a"), mk("b", ["a"]), mk("c", ["b"])]
    layers = topological_layers(beats)
    assert [{x.id for x in L} for L in layers] == [{"a"}, {"b"}, {"c"}]

def test_bifurcation():
    beats = [mk("main"), mk("A", ["main"]), mk("B", ["main"])]
    layers = topological_layers(beats)
    assert [{x.id for x in L} for L in layers] == [{"main"}, {"A", "B"}]

def test_independent_beats_parallel():
    beats = [mk("x"), mk("y"), mk("z")]
    layers = topological_layers(beats)
    assert [{x.id for x in L} for L in layers] == [{"x", "y", "z"}]

def test_cycle_raises():
    beats = [mk("a", ["b"]), mk("b", ["a"])]
    with pytest.raises(CycleError):
        topological_layers(beats)

def test_unknown_dep_raises():
    beats = [mk("a", ["nonexistent"])]
    with pytest.raises(ValueError, match="nonexistent"):
        topological_layers(beats)
```

- [ ] **Step 2: Run — expect FAIL**

Expected: ImportError.

- [ ] **Step 3: Implement `src/crpg/orchestration/dag.py`**

```python
"""Topological scheduling for beat execution."""
from crpg.types import Beat

class CycleError(Exception):
    pass

def topological_layers(beats: list[Beat]) -> list[list[Beat]]:
    """Group beats into concurrency layers: each layer's beats have no unresolved deps.

    Beats within a layer can run in parallel. Layers run sequentially.
    Raises CycleError on cycles, ValueError on missing deps.
    """
    by_id = {b.id: b for b in beats}
    for b in beats:
        for dep in b.depends_on:
            if dep not in by_id:
                raise ValueError(f"beat {b.id!r} depends on unknown beat {dep!r}")

    remaining = {b.id for b in beats}
    satisfied: set[str] = set()
    layers: list[list[Beat]] = []
    while remaining:
        ready = [b for b in beats if b.id in remaining
                 and all(d in satisfied for d in b.depends_on)]
        if not ready:
            raise CycleError(f"cycle detected; unresolved beats: {sorted(remaining)}")
        layers.append(ready)
        for b in ready:
            remaining.discard(b.id)
            satisfied.add(b.id)
    return layers
```

- [ ] **Step 4: Run — expect PASS**

```bash
pytest tests/orchestration/test_dag.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add src/crpg/orchestration/dag.py tests/orchestration/test_dag.py
git commit -m "feat(orchestration): DAG topological layers for beat concurrency"
```

---

### Task 6.2: Bundle writer

**Files:**
- Create: `src/crpg/bundle.py`
- Create: `tests/test_bundle.py`

- [ ] **Step 1: Write failing test**

`tests/test_bundle.py`:

```python
import json, pytest
from pathlib import Path
from crpg.bundle import BundleWriter, BundleMeta
from crpg.types import Story, StoryMeta, Beat, Character, Base

def test_bundle_writer_creates_files(tmp_path):
    story = Story(
        meta=StoryMeta(title="t", genre="n", contentLength="short",
                       detailRichness="detailed", structure="bifurcating"),
        beats=[Beat(id="intro", type="narrative", synopsis="s",
                    valueBefore="x", valueAfter="y",
                    targetWordCount=100, targetShotCount=1)],
        edges=[],
    )
    chars = {"Su Wan": Character(
        base=Base(age=28, ethnicity="Chinese", hair="h", skin="s", eyes="e", jaw="j"),
    )}
    meta = BundleMeta(
        generated_at="2026-04-18T15:00:00Z",
        text_model="kimi-k2-0905",
        text_provider="Groq",
        image_model="grok-imagine-pro",
        suffix_versions={"STRONG": "v1", "FEW_SHOT": "v1", "LENGTH_SHORT": "v1"},
    )
    writer = BundleWriter(out_dir=tmp_path / "bundle")
    writer.write(story=story, characters=chars, meta=meta)
    assert (tmp_path / "bundle" / "story.json").exists()
    assert (tmp_path / "bundle" / "characters.json").exists()
    assert (tmp_path / "bundle" / "meta.json").exists()
    assert (tmp_path / "bundle" / "shots").is_dir()

    # Reloadable
    loaded_story = json.loads((tmp_path / "bundle" / "story.json").read_text())
    assert loaded_story["meta"]["title"] == "t"
    loaded_chars = json.loads((tmp_path / "bundle" / "characters.json").read_text())
    assert "Su Wan" in loaded_chars
    loaded_meta = json.loads((tmp_path / "bundle" / "meta.json").read_text())
    assert loaded_meta["text_model"] == "kimi-k2-0905"

def test_bundle_shot_dir(tmp_path):
    writer = BundleWriter(out_dir=tmp_path / "bundle")
    d = writer.shots_dir(beat_id="intro")
    assert d == tmp_path / "bundle" / "shots" / "intro"
    assert d.exists()
```

- [ ] **Step 2: Run — expect FAIL**

Expected: ImportError.

- [ ] **Step 3: Implement `src/crpg/bundle.py`**

```python
"""BundleWriter — writes story.json / characters.json / shots/ / meta.json."""
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from crpg.types import Story, Character

@dataclass
class BundleMeta:
    generated_at: str
    text_model: str
    text_provider: str
    image_model: str
    suffix_versions: dict[str, str] = field(default_factory=dict)
    git_sha: str | None = None

class BundleWriter:
    def __init__(self, out_dir: Path) -> None:
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        (self.out_dir / "shots").mkdir(exist_ok=True)

    def shots_dir(self, *, beat_id: str) -> Path:
        d = self.out_dir / "shots" / beat_id
        d.mkdir(parents=True, exist_ok=True)
        return d

    def write(
        self,
        *,
        story: Story,
        characters: dict[str, Character],
        meta: BundleMeta,
    ) -> None:
        (self.out_dir / "story.json").write_text(
            story.model_dump_json(indent=2, by_alias=True), encoding="utf-8",
        )
        chars_blob = {name: c.model_dump(mode="json", by_alias=True) for name, c in characters.items()}
        (self.out_dir / "characters.json").write_text(
            json.dumps(chars_blob, ensure_ascii=False, indent=2), encoding="utf-8",
        )
        (self.out_dir / "meta.json").write_text(
            json.dumps(asdict(meta), ensure_ascii=False, indent=2), encoding="utf-8",
        )
```

- [ ] **Step 4: Run — expect PASS**

```bash
pytest tests/test_bundle.py -v
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add src/crpg/bundle.py tests/test_bundle.py
git commit -m "feat(bundle): BundleWriter for story.json/characters.json/shots/"
```

---

### Task 6.3: Pipeline orchestrator

**Files:**
- Create: `src/crpg/orchestration/pipeline.py`
- Create: `tests/orchestration/test_pipeline.py`

- [ ] **Step 1: Write failing test**

`tests/orchestration/test_pipeline.py`:

```python
import json, pytest, base64
from pathlib import Path
from crpg.orchestration.pipeline import run_pipeline, PipelineInputs
from crpg.config import ProjectConfig

FAKE_PNG_B64 = base64.b64encode(b"\x89PNG\r\n\x1a\n" + b"\x00" * 64).decode()

@pytest.mark.asyncio
async def test_pipeline_e2e_mocked(tmp_path, httpx_mock, demo_brief, fixture_path):
    skeleton_json = (fixture_path / "canonical_skeleton.json").read_text(encoding="utf-8")
    script_text = (fixture_path / "canonical_script_short.md").read_text(encoding="utf-8")
    shots_json = (fixture_path / "canonical_shots.json").read_text(encoding="utf-8")

    # Responses added in order of expected calls:
    # 1. Skeleton
    httpx_mock.add_response(
        url="https://openrouter.ai/api/v1/chat/completions",
        json={"choices":[{"message":{"content":skeleton_json},"finish_reason":"stop"}], "usage":{}},
    )
    # 4 beats × (1 script + 1 director) = 8 more chat calls
    # But canonical_skeleton has 4 beats (intro, main, A_decline, B_accept)
    # Each beat does 1 script + 1 director call in this plan; we'll re-use canonicals.
    for _ in range(4):
        # Script per beat
        httpx_mock.add_response(
            url="https://openrouter.ai/api/v1/chat/completions",
            json={"choices":[{"message":{"content":script_text},"finish_reason":"stop"}], "usage":{}},
        )
        # Director per beat
        httpx_mock.add_response(
            url="https://openrouter.ai/api/v1/chat/completions",
            json={"choices":[{"message":{"content":shots_json},"finish_reason":"stop"}], "usage":{}},
        )
    # Image generation: each director returns 2 shots, 4 beats = 8 images
    for _ in range(8):
        httpx_mock.add_response(
            url="https://api.x.ai/v1/images/generations",
            json={"data":[{"b64_json": FAKE_PNG_B64}]},
        )

    cfg = ProjectConfig(
        openrouter_key="sk-or-test", xai_key="xai-test",
        text_model="moonshotai/kimi-k2-0905", text_provider="Groq",
        concurrency=10,
    )
    out = tmp_path / "bundle"
    inputs = PipelineInputs(brief=demo_brief, out_dir=out)
    result = await run_pipeline(cfg, inputs)
    assert result.bundle_path == out
    assert (out / "story.json").exists()
    assert (out / "characters.json").exists()
    assert (out / "meta.json").exists()
    # All beats have shots dirs with rendered PNGs
    assert len(list((out / "shots").iterdir())) == 4
```

- [ ] **Step 2: Run — expect FAIL**

Expected: ImportError.

- [ ] **Step 3: Implement `src/crpg/orchestration/pipeline.py`**

```python
"""End-to-end pipeline orchestrator."""
import asyncio
import datetime as dt
from dataclasses import dataclass
from pathlib import Path
from crpg.config import ProjectConfig
from crpg.llm.openrouter import OpenRouterClient
from crpg.llm.xai import XaiImageClient
from crpg.passes.skeleton import run_skeleton
from crpg.passes.script import run_script_short, run_script_detailed
from crpg.passes.director import run_director
from crpg.passes.assembler import assemble_image_prompt
from crpg.passes.image import render_shots_to_disk
from crpg.orchestration.dag import topological_layers
from crpg.types import Beat, Story, Character, Shot
from crpg.bundle import BundleWriter, BundleMeta

@dataclass
class PipelineInputs:
    brief: str
    out_dir: Path

@dataclass
class PipelineResult:
    bundle_path: Path
    shot_count: int

def _format_beat_user_prompt(beat: Beat, story: Story) -> str:
    return (
        f"Beat id: {beat.id}\n"
        f"Type: {beat.type}\n"
        f"Synopsis: {beat.synopsis}\n"
        f"Value transition: {beat.value_before} → {beat.value_after}\n"
        f"Target word count: {beat.target_word_count}\n"
        f"Story meta: {story.meta.model_dump_json(by_alias=True)}"
    )

async def _process_beat(
    beat: Beat,
    *,
    story: Story,
    characters: dict[str, Character],
    or_client: OpenRouterClient,
    xai_client: XaiImageClient,
    writer: BundleWriter,
) -> int:
    # For M1 we pick the first character as the POV character
    # (multi-POV is future work). Name is the key in characters dict.
    pov_name, pov_char = next(iter(characters.items()))
    wardrobe_state = beat.wardrobe_state or next(iter(pov_char.wardrobe_states.keys()))

    # Script pass: short or detailed based on story.meta
    beat_user = _format_beat_user_prompt(beat, story)
    if story.meta.detail_richness in ("detailed", "extreme"):
        main, a, b = await run_script_detailed(or_client, scene_brief=beat_user)
        prose = f"{main}\n\n\n{a}\n\n\n{b}"
    else:
        prose = await run_script_short(or_client, beat_user_prompt=beat_user)

    # Director pass
    shots = await run_director(
        or_client,
        beat_id=beat.id, beat_prose=prose,
        character_name=pov_name, character=pov_char,
        wardrobe_state=wardrobe_state,
        target_shot_count=beat.target_shot_count,
    )

    # Assembler (pure) + Image batch
    prompts = [assemble_image_prompt(s) for s in shots]
    out_dir = writer.shots_dir(beat_id=beat.id)
    await render_shots_to_disk(
        xai_client, shots=shots, out_dir=out_dir, prompts=prompts,
    )
    return len(shots)

async def run_pipeline(cfg: ProjectConfig, inputs: PipelineInputs) -> PipelineResult:
    or_client = OpenRouterClient(api_key=cfg.openrouter_key, concurrency=cfg.concurrency)
    xai_client = XaiImageClient(api_key=cfg.xai_key, concurrency=min(cfg.concurrency, 20))
    writer = BundleWriter(out_dir=inputs.out_dir)

    # Pass 1: Skeleton
    story, characters = await run_skeleton(or_client, brief=inputs.brief,
                                           model=cfg.text_model, provider=cfg.text_provider)

    # Passes 2-5 in DAG order
    layers = topological_layers(story.beats)
    total_shots = 0
    for layer in layers:
        results = await asyncio.gather(*[
            _process_beat(b, story=story, characters=characters,
                          or_client=or_client, xai_client=xai_client, writer=writer)
            for b in layer
        ])
        total_shots += sum(results)

    # Write bundle metadata
    meta = BundleMeta(
        generated_at=dt.datetime.now(dt.UTC).isoformat(),
        text_model=cfg.text_model,
        text_provider=cfg.text_provider,
        image_model="grok-imagine-pro",
        suffix_versions={"STRONG": "v1", "FEW_SHOT": "v1", "LENGTH_SHORT": "v1"},
    )
    writer.write(story=story, characters=characters, meta=meta)
    return PipelineResult(bundle_path=inputs.out_dir, shot_count=total_shots)
```

- [ ] **Step 4: Run — expect PASS**

```bash
pytest tests/orchestration/test_pipeline.py -v
```

Expected: 1 passed.

- [ ] **Step 5: Commit**

```bash
git add src/crpg/orchestration/pipeline.py tests/orchestration/test_pipeline.py
git commit -m "feat(orchestration): end-to-end pipeline with DAG-parallel beats"
```

---

# Phase 7 — CLI

### Task 7.1: CLI entry point with click

**Files:**
- Create: `src/crpg/cli.py`
- Create: `src/crpg/__main__.py`
- Create: `tests/test_cli.py`

- [ ] **Step 1: Write failing test**

`tests/test_cli.py`:

```python
import pytest
from click.testing import CliRunner
from crpg.cli import main

def test_cli_help():
    runner = CliRunner()
    r = runner.invoke(main, ["--help"])
    assert r.exit_code == 0
    assert "generate" in r.output

def test_cli_generate_requires_brief():
    runner = CliRunner()
    r = runner.invoke(main, ["generate"])
    assert r.exit_code != 0
    assert "--brief" in r.output or "Missing option" in r.output

def test_cli_generate_missing_file(tmp_path):
    runner = CliRunner()
    r = runner.invoke(main, ["generate", "--brief", str(tmp_path / "nope.md"),
                             "--out", str(tmp_path / "bundle")])
    assert r.exit_code != 0
```

- [ ] **Step 2: Run — expect FAIL**

Expected: ImportError.

- [ ] **Step 3: Implement `src/crpg/cli.py`**

```python
"""crpg CLI entry point."""
import asyncio
from pathlib import Path
import click
from crpg.config import load_config
from crpg.orchestration.pipeline import run_pipeline, PipelineInputs

@click.group()
@click.version_option()
def main() -> None:
    """crpg — creator CLI for interactive noir fiction with anime images."""

@main.command()
@click.option("--brief", type=click.Path(exists=True, dir_okay=False, path_type=Path),
              required=True, help="Path to creator brief (markdown)")
@click.option("--out", "out_dir", type=click.Path(file_okay=False, path_type=Path),
              required=True, help="Output directory for story bundle")
def generate(brief: Path, out_dir: Path) -> None:
    """Generate a story bundle from a brief."""
    cfg = load_config()
    brief_text = brief.read_text(encoding="utf-8")
    inputs = PipelineInputs(brief=brief_text, out_dir=out_dir)
    click.echo(f"▶ Generating to {out_dir} (model={cfg.text_model} @ {cfg.text_provider})")
    result = asyncio.run(run_pipeline(cfg, inputs))
    click.echo(f"✓ Done. {result.shot_count} shots written to {result.bundle_path}")
```

- [ ] **Step 4: Implement `src/crpg/__main__.py`**

```python
"""Enable `python -m crpg`."""
from crpg.cli import main

if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run — expect PASS**

```bash
pytest tests/test_cli.py -v
```

Expected: 3 passed.

- [ ] **Step 6: Commit**

```bash
git add src/crpg/cli.py src/crpg/__main__.py tests/test_cli.py
git commit -m "feat(cli): click-based generate command"
```

---

# Phase 8 — E2E & docs

### Task 8.1: Live-API E2E smoke test + README polish

**Files:**
- Create: `tests/test_e2e.py`
- Modify: `README.md`

- [ ] **Step 1: Write E2E test (skipped by default)**

`tests/test_e2e.py`:

```python
import os, pytest
from pathlib import Path
from crpg.config import load_config
from crpg.orchestration.pipeline import run_pipeline, PipelineInputs

pytestmark = pytest.mark.skipif(
    os.environ.get("CRPG_LIVE") != "1",
    reason="set CRPG_LIVE=1 to run live API E2E",
)

@pytest.mark.asyncio
async def test_e2e_short_detailed(tmp_path):
    """One run against real Groq + Grok Imagine. Expensive; opt-in."""
    cfg = load_config()
    brief = Path(__file__).parent / "fixtures" / "demo_brief.md"
    inputs = PipelineInputs(brief=brief.read_text(encoding="utf-8"),
                            out_dir=tmp_path / "bundle")
    result = await run_pipeline(cfg, inputs)
    assert (result.bundle_path / "story.json").exists()
    assert (result.bundle_path / "characters.json").exists()
    assert (result.bundle_path / "meta.json").exists()
    # At least one beat produced shots
    shot_dirs = list((result.bundle_path / "shots").iterdir())
    assert len(shot_dirs) > 0
    # At least one PNG was rendered
    pngs = [p for d in shot_dirs for p in d.iterdir() if p.suffix == ".png"]
    assert len(pngs) > 0
    assert pngs[0].read_bytes().startswith(b"\x89PNG")
```

- [ ] **Step 2: Run — expect SKIPPED (default)**

```bash
pytest tests/test_e2e.py -v
```

Expected: SKIPPED.

- [ ] **Step 3: Flesh out README.md**

```markdown
# crpg

Creator CLI for interactive branching noir fiction with anime image generation.

One command turns a prose brief into a complete story bundle (JSON + real PNG images) using a 4-pass LLM pipeline (Skeleton → Script → Director → Image).

## Install

```bash
pip install -e ".[dev]"
```

## Configure

```bash
cp .env.example .env
# edit .env: set OPENROUTER_API_KEY (paid tier) and XAI_API_KEY
```

## Use

```bash
crpg generate --brief tests/fixtures/demo_brief.md --out bundle/
```

Output:

```
bundle/
├── story.json          # beats + edges + meta
├── characters.json     # character sheets with VGAI anchors
├── shots/
│   ├── intro/shot-001.png ...
│   ├── main/shot-001.png ...
│   └── ...
└── meta.json           # generation timestamp, LLM versions
```

## Pipeline

1. **Skeleton** — kimi-k2-0905 @Groq: brief → story structure + character sheets
2. **Script** — kimi-k2-0905 @Groq: per-beat prose (short: single-call; detailed: main→A‖B segmented)
3. **Director** — kimi-k2-0905 @Groq (+ STRONG + FEW_SHOT hardening): per-beat VGAI-gated shot list
4. **Assembler** — pure fn: prepend ANIME_PREAMBLE to Director prompts
5. **Image** — Grok Imagine Pro (xAI direct): render each prompt to PNG

Beats execute concurrently in topological layers (DAG schedule). Paid OpenRouter concurrency=50.

## Tests

```bash
pytest                              # unit tests (mocked LLM)
CRPG_LIVE=1 pytest tests/test_e2e.py  # live API smoke (costs ~$0.05 per run)
```

## Design

See `docs/superpowers/specs/2026-04-18-crpg-milestone-1-design.md` for full architecture + empirical test results.
```

- [ ] **Step 4: Run full suite — all pass or skip**

```bash
pytest -v
```

Expected: all unit tests pass, E2E skipped.

- [ ] **Step 5: Commit**

```bash
git add tests/test_e2e.py README.md
git commit -m "test(e2e): opt-in live-API smoke + README polish"
```

---

## Post-implementation checklist

After all tasks complete, run:

```bash
# 1. Full unit suite
pytest -v

# 2. Coverage check
pytest --cov=crpg --cov-report=term-missing

# 3. Lint
ruff check src tests

# 4. Optional live E2E
CRPG_LIVE=1 pytest tests/test_e2e.py -v
```

If live E2E produces a valid bundle with real PNGs, Milestone 1 is shippable.

---

## Self-review of this plan

**Spec coverage**:
- §1 Goal (CLI) → Task 7.1
- §2 Pipeline (4 passes + assembler + image) → Tasks 4.1, 4.2, 4.3, 4.4, 5.1, 5.2
- §3 Models (k2-0905 @Groq with suffixes) → Tasks 2.1, 2.2, 2.3
- §4 3-axis config → stored in Story.meta, used by script.py to choose short vs detailed
- §5 Concurrency model (Semaphore + DAG) → Tasks 2.1, 6.1, 6.3
- §6 Framework (httpx, not OpenAI Agents SDK) → documented in tech stack header; Agents SDK was considered but skipped as overkill for a linear pipeline. This is a minor spec deviation flagged here; implementation is simpler and uses the same OpenAI-compatible API.
- §7 Bundle format → Task 6.2 (BundleWriter)
- §8 Success criteria → covered by test_pipeline + test_e2e
- §9 Out-of-scope → respected; no tasks cover reader, auth, publishing, moderation, payment
- §10 Known optimizations — #1 snake_case in Skeleton prompt ✓ (Task 2.3 prompt has it); #2 shared LLM endpoint ✓ (single OpenRouterClient); #6 ANIME_PREAMBLE in assembler.py ✓ (Task 4.4)
- §11 deferred Q4 — unchanged, out of scope

**Placeholder scan**: searched for TBD / TODO / "similar to" / "fill in" — none present.

**Type consistency**: `OpenRouterClient.chat` signature consistent across all callers (skeleton, script, director). `Character` / `Beat` / `Shot` / `ShotList` types used consistently. `BundleWriter.shots_dir(beat_id=...)` matches call site in `pipeline._process_beat`.

**One flagged deviation**: Spec §6 says "OpenAI Agents SDK". Plan uses plain httpx because the pipeline has no agent behavior (no tool calls, no handoffs, no multi-turn) — a thin httpx layer is simpler and ships the same functionality. Called out in the tech-stack header. If later milestones add tool-calling or handoffs, migrate to openai-agents SDK then.
