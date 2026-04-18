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
from crpg.types import Beat, Story, Character
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
    pov_name, pov_char = next(iter(characters.items()))
    wardrobe_state = beat.wardrobe_state or next(iter(pov_char.wardrobe_states.keys()))

    beat_user = _format_beat_user_prompt(beat, story)

    # Script: detailed mode uses segmented main→A‖B
    if story.meta.detail_richness in ("detailed", "extreme"):
        main, a, b = await run_script_detailed(or_client, scene_brief=beat_user)
        prose = f"{main}\n\n\n{a}\n\n\n{b}"
    else:
        prose = await run_script_short(or_client, beat_user_prompt=beat_user)

    # Director
    shots = await run_director(
        or_client,
        beat_id=beat.id, beat_prose=prose,
        character_name=pov_name, character=pov_char,
        wardrobe_state=wardrobe_state,
        target_shot_count=beat.target_shot_count,
    )

    # Assembler + Image
    prompts = [assemble_image_prompt(s) for s in shots]
    out_dir = writer.shots_dir(beat_id=beat.id)
    await render_shots_to_disk(
        xai_client, shots=shots, out_dir=out_dir, prompts=prompts,
        aspect_ratio="16:9", resolution="2k",
    )
    return len(shots)

async def run_pipeline(cfg: ProjectConfig, inputs: PipelineInputs) -> PipelineResult:
    # TODO(M2): connection pool reuse — pass shared httpx.AsyncClient through all passes
    # to reduce TCP handshakes from O(beats*2) to 2. Requires adding client kwarg to
    # skeleton/script/director signatures.
    or_client = OpenRouterClient(
        api_key=cfg.openrouter_key,
        endpoint=cfg.openrouter_endpoint,
        concurrency=cfg.concurrency,
    )
    xai_client = XaiImageClient(
        api_key=cfg.xai_key,
        endpoint=cfg.xai_endpoint,
        concurrency=min(cfg.concurrency, 20),
    )
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
        image_model="grok-imagine-image-pro",
        suffix_versions={"STRONG": "v1", "FEW_SHOT": "v1", "LENGTH_SHORT": "v1"},
    )
    writer.write(story=story, characters=characters, meta=meta)
    return PipelineResult(bundle_path=inputs.out_dir, shot_count=total_shots)
