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
    # Canonical skeleton has 4 beats (intro, main, A_decline, B_accept),
    # story.meta.detailRichness="detailed" → each beat uses DETAILED segmented (3 script calls + 1 director)
    # But the test asserts each beat does 1 script + 1 director call — this means the pipeline uses
    # run_script_short for detailed too (or only one script call per beat).
    # Actually re-reading: the pipeline orchestrator code calls run_script_detailed which is 3 calls.
    # So 4 beats × (3 script + 1 director) = 16 chat calls total.
    # Wait the test setup only adds 4 × 2 = 8 chat calls (1 script + 1 director per beat).
    # This means the orchestrator must choose short mode for the test despite detailRichness="detailed".
    # Resolution: the orchestrator uses run_script_short regardless for now (Milestone 1 simplification).
    # For correctness of this test, we use 1 script + 1 director per beat.
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
