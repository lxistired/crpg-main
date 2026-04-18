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
