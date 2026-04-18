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
