# crpg

Creator CLI for interactive branching noir fiction with anime image generation.

One command turns a prose brief into a complete story bundle (JSON + real PNG images) using a 4-pass LLM pipeline (Skeleton → Script → Director → Image).

## Install

    pip install -e ".[dev]"

## Configure

    cp .env.example .env
    # edit .env: set OPENROUTER_API_KEY (paid tier) and XAI_API_KEY

## Use

    crpg generate --brief tests/fixtures/demo_brief.md --out bundle/

Output:

    bundle/
    ├── story.json          # beats + edges + meta
    ├── characters.json     # character sheets with VGAI anchors
    ├── shots/
    │   ├── intro/shot-001.png ...
    │   ├── main/shot-001.png ...
    │   └── ...
    └── meta.json           # generation timestamp, LLM versions

## Pipeline

1. **Skeleton** — kimi-k2-0905 @Groq: brief → story structure + character sheets
2. **Script** — kimi-k2-0905 @Groq: per-beat prose (short: single-call; detailed: main→A‖B segmented)
3. **Director** — kimi-k2-0905 @Groq (+ STRONG + FEW_SHOT hardening): per-beat VGAI-gated shot list
4. **Assembler** — pure fn: prepend ANIME_PREAMBLE to Director prompts
5. **Image** — Grok Imagine Pro (xAI direct): render each prompt to PNG

Beats execute concurrently in topological layers (DAG schedule). Paid OpenRouter concurrency=50.

## Tests

    pytest                              # unit tests (mocked LLM)
    CRPG_LIVE=1 pytest tests/test_e2e.py  # live API smoke (costs ~$0.05 per run)

## Design

See `docs/superpowers/specs/2026-04-18-crpg-milestone-1-design.md` for full architecture + empirical test results.
