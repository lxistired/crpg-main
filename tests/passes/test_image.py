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
