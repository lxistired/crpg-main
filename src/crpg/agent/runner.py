"""Python entry point for running the main agent against a brief.

Only does orchestration plumbing: load config → build AgentState → build
Agent → Runner.run → wait for finish_bundle signal (or max_turns hit).
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agents import Runner, set_tracing_disabled

from crpg.agent.main_agent import build_main_agent
from crpg.agent.state import AgentState
from crpg.bundle import BundleWriter
from crpg.config import ProjectConfig, load_config
from crpg.llm.xai import XaiImageClient


# Disable the default OpenAI trace exporter; we don't send traces to OpenAI
# and the warning noise is distracting.
set_tracing_disabled(True)


@dataclass
class AgentRunResult:
    bundle_dir: Path
    finished: bool
    finish_summary: str
    beats_with_prose: int
    beats_with_shots: int
    images_rendered: int
    turns_used: int


async def run_agent(
    brief: str,
    out_dir: Path,
    *,
    cfg: ProjectConfig | None = None,
    project_root: Path | None = None,
    max_turns: int = 200,
) -> AgentRunResult:
    """Run the main agent against `brief`, writing bundle to `out_dir`.

    Args:
        brief: free-form text (keywords / sentence / paragraph).
        out_dir: where the bundle will be written.
        cfg: loaded ProjectConfig (defaults to load_config()).
        project_root: repo root so skills/ is findable (defaults to the
            package parent — works when crpg is a local editable install).
        max_turns: safety cap on agent iterations. Default 200.
    """
    cfg = cfg or load_config()
    project_root = project_root or _default_project_root()

    state = AgentState(
        project_root=project_root,
        bundle_writer=BundleWriter(out_dir=out_dir),
        xai_client=XaiImageClient(api_key=cfg.xai_key, endpoint=cfg.xai_endpoint),
        brief=brief,
    )
    agent = build_main_agent(cfg)

    initial_message = (
        "Begin. Read the brief via `read_brief()` first, then follow the "
        "workflow in your instructions. Emit a complete story bundle."
    )
    result = await Runner.run(
        agent,
        input=initial_message,
        context=state,
        max_turns=max_turns,
    )
    # Count turns from the new items: every MessageOutputItem from assistant = one turn
    turns = sum(1 for it in result.new_items if type(it).__name__ == "MessageOutputItem")
    return AgentRunResult(
        bundle_dir=out_dir,
        finished=state.finished,
        finish_summary=state.finish_summary,
        beats_with_prose=len(state.beats_with_prose),
        beats_with_shots=len(state.beats_with_shots),
        images_rendered=state.images_rendered,
        turns_used=turns,
    )


def _default_project_root() -> Path:
    # src/crpg/agent/runner.py → project root is 3 levels up
    return Path(__file__).resolve().parent.parent.parent.parent


def run_agent_sync(brief: str, out_dir: Path, **kwargs: Any) -> AgentRunResult:
    """Synchronous wrapper for CLI use."""
    return asyncio.run(run_agent(brief, out_dir, **kwargs))
