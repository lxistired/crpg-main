"""Live E2E — run the main agent against the demo brief.

Opt-in: set CRPG_LIVE=1 to run (costs real API money).
"""
import os
import pytest
from pathlib import Path

from crpg.agent.runner import run_agent

pytestmark = pytest.mark.skipif(
    os.environ.get("CRPG_LIVE") != "1",
    reason="set CRPG_LIVE=1 to run live API E2E",
)


@pytest.mark.asyncio
async def test_e2e_demo_brief(tmp_path):
    """Dispatch the main agent against the demo brief; expect a complete bundle."""
    brief = (Path(__file__).parent / "fixtures" / "demo_brief.md").read_text(encoding="utf-8")
    result = await run_agent(brief=brief, out_dir=tmp_path / "bundle", max_turns=300)

    # Agent signaled completion
    assert result.finished, f"agent did not call finish_bundle; summary={result.finish_summary!r}"

    # Bundle artifacts
    bundle = result.bundle_dir
    assert (bundle / "story.json").exists(), "story.json missing"
    assert (bundle / "characters.json").exists(), "characters.json missing"

    # Prose + shots landed
    assert result.beats_with_prose >= 1
    assert result.beats_with_shots >= 1

    # At least one PNG rendered
    shot_dirs = list((bundle / "shots").iterdir())
    pngs = [p for d in shot_dirs if d.is_dir() for p in d.iterdir() if p.suffix == ".png"]
    assert len(pngs) >= 1, f"no images rendered; result={result}"
    assert pngs[0].read_bytes().startswith(b"\x89PNG")
