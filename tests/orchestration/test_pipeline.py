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

    def add_script(n: int = 1) -> None:
        for _ in range(n):
            httpx_mock.add_response(
                url="https://openrouter.ai/api/v1/chat/completions",
                json={"choices":[{"message":{"content":script_text},"finish_reason":"stop"}], "usage":{}},
            )

    def add_director(n: int = 1) -> None:
        for _ in range(n):
            httpx_mock.add_response(
                url="https://openrouter.ai/api/v1/chat/completions",
                json={"choices":[{"message":{"content":shots_json},"finish_reason":"stop"}], "usage":{}},
            )

    # Responses added in order of expected calls:
    # detailRichness="detailed" → run_script_detailed per beat (3 calls: main, branch_A, branch_B)
    #
    # DAG layers from canonical_skeleton.json:
    #   Layer 1: [intro]            — sequential: 3 script + 1 director
    #   Layer 2: [main]             — sequential: 3 script + 1 director
    #   Layer 3: [A_decline, B_accept] — concurrent pair via asyncio.gather:
    #       asyncio interleaving: A.main, B.main (sequential awaits), then
    #       A.branch_A+A.branch_B+B.branch_A+B.branch_B (all 4 concurrent),
    #       then A.director, B.director.
    #       So: 2 main-script + 4 branch-script + 2 director (in that layered order).

    # 1. Skeleton
    httpx_mock.add_response(
        url="https://openrouter.ai/api/v1/chat/completions",
        json={"choices":[{"message":{"content":skeleton_json},"finish_reason":"stop"}], "usage":{}},
    )
    # Layer 1: intro (3 script + 1 director)
    add_script(3)
    add_director(1)
    # Layer 2: main (3 script + 1 director)
    add_script(3)
    add_director(1)
    # Layer 3: A_decline + B_accept concurrent
    #   Step 1: each beat awaits main-script sequentially → 2 main calls
    add_script(2)
    #   Step 2: all branch calls run concurrently → 4 branch calls (all prose, order irrelevant)
    add_script(4)
    #   Step 3: each beat awaits director sequentially → 2 director calls
    add_director(2)

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
