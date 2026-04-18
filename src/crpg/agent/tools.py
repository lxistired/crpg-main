"""Function tools for the main agent.

Every tool accepts `ctx: RunContextWrapper[AgentState]` as the first arg to
reach shared state (bundle writer, xAI client, cached story/chars).

All tool bodies are small and side-effect-disciplined: persist to disk via
BundleWriter, update state counters, return a short string to the agent so
its context window doesn't accumulate giant payloads.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from agents import RunContextWrapper, function_tool
from pydantic import ValidationError

from crpg.agent.state import AgentState
from crpg.bundle import BundleMeta
from crpg.types import Character, Shot, Story
from crpg.validation.vgai import validate_shot_list


# ---------- skill reading ---------------------------------------------------

_VALID_SKILLS = {"skeleton", "script", "director"}
_SAFE_REF = re.compile(r"^[A-Za-z0-9_-]+$")


def _skills_dir(ctx: RunContextWrapper[AgentState]) -> Path:
    return ctx.context.project_root / "skills"


@function_tool
def read_skill(ctx: RunContextWrapper[AgentState], name: str) -> str:
    """Read a crpg skill's SKILL.md.

    Args:
        name: one of "skeleton", "script", "director".

    Returns the full SKILL.md content. Call this BEFORE doing work for that
    skill. Your own memory of rules is not authoritative — the file is.
    """
    if name not in _VALID_SKILLS:
        return f"ERROR: unknown skill {name!r}. Valid: {sorted(_VALID_SKILLS)}"
    path = _skills_dir(ctx) / name / "SKILL.md"
    if not path.exists():
        return f"ERROR: {path} not found"
    return path.read_text(encoding="utf-8")


@function_tool
def list_skill_references(ctx: RunContextWrapper[AgentState], skill: str) -> str:
    """List available reference files for a skill.

    Args:
        skill: one of "skeleton", "script", "director".

    Returns newline-separated short reference names (pass any of them to
    read_skill_reference).
    """
    if skill not in _VALID_SKILLS:
        return f"ERROR: unknown skill {skill!r}"
    refs_dir = _skills_dir(ctx) / skill / "references"
    if not refs_dir.exists():
        return f"(no references directory for {skill})"
    names: list[str] = []
    for p in sorted(refs_dir.iterdir()):
        if p.is_file() and p.suffix in {".md", ".yaml", ".yml"}:
            names.append(p.stem)
    return "\n".join(names) if names else "(empty)"


@function_tool
def read_skill_reference(ctx: RunContextWrapper[AgentState], skill: str, ref_name: str) -> str:
    """Read a reference file from a skill's references/ directory.

    Args:
        skill: one of "skeleton", "script", "director".
        ref_name: short reference name (no extension), e.g. "vgai" or
            "mckee-principles".

    Returns the file content. The skill decides whether the file is .md or
    .yaml — this tool finds either.
    """
    if skill not in _VALID_SKILLS:
        return f"ERROR: unknown skill {skill!r}"
    if not _SAFE_REF.fullmatch(ref_name):
        return f"ERROR: invalid ref_name {ref_name!r} (use A-Za-z0-9_- only)"
    refs_dir = _skills_dir(ctx) / skill / "references"
    for ext in (".md", ".yaml", ".yml"):
        candidate = refs_dir / f"{ref_name}{ext}"
        if candidate.exists():
            return candidate.read_text(encoding="utf-8")
    return f"ERROR: reference {ref_name!r} not found under {refs_dir}"


# ---------- brief ------------------------------------------------------------

@function_tool
def read_brief(ctx: RunContextWrapper[AgentState]) -> str:
    """Return the user's original brief verbatim."""
    return ctx.context.brief


# ---------- story / characters emission --------------------------------------

@function_tool(strict_mode=False)
def write_story(ctx: RunContextWrapper[AgentState], story: dict) -> str:
    """Persist the Skeleton-stage story skeleton to bundle/story.json.

    Args:
        story: a dict matching the crpg Story schema (meta + beats + edges).
            See skills/skeleton/SKILL.md for the exact shape.

    Returns a short success/error summary. On validation error, the full
    pydantic message is included so you can fix and retry.
    """
    try:
        story_model = Story.model_validate(story)
    except ValidationError as e:
        return f"VALIDATION_ERROR:\n{e.json(indent=2)[:2000]}"
    state = ctx.context
    state.bundle_writer.out_dir.mkdir(parents=True, exist_ok=True)
    (state.bundle_writer.out_dir / "story.json").write_text(
        story_model.model_dump_json(indent=2, by_alias=True), encoding="utf-8",
    )
    state.story_data = story
    state.story_emitted = True
    return (
        f"OK story.json written with {len(story_model.beats)} beats and "
        f"{len(story_model.edges)} edges."
    )


@function_tool(strict_mode=False)
def write_characters(ctx: RunContextWrapper[AgentState], characters: dict) -> str:
    """Persist the Skeleton-stage character sheets to bundle/characters.json.

    Args:
        characters: a dict mapping character_name → character data. See
            skills/skeleton/SKILL.md and references/mutex-coverage.md for
            the exact shape including `covers` on every wardrobe item.

    Returns success/error summary with pydantic error detail on failure.
    """
    state = ctx.context
    parsed: dict[str, Character] = {}
    for name, blob in characters.items():
        try:
            parsed[name] = Character.model_validate(blob)
        except ValidationError as e:
            return f"VALIDATION_ERROR character {name!r}:\n{e.json(indent=2)[:2000]}"
    chars_blob = {n: c.model_dump(mode="json", by_alias=True) for n, c in parsed.items()}
    (state.bundle_writer.out_dir / "characters.json").write_text(
        json.dumps(chars_blob, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    state.characters_data = characters
    state.characters_emitted = True
    return f"OK characters.json written for {list(parsed.keys())}"


# ---------- prose + shots ----------------------------------------------------

@function_tool
def write_beat_prose(ctx: RunContextWrapper[AgentState], beat_id: str, prose: str) -> str:
    """Persist one beat's prose to bundle/prose/<beat_id>.md.

    Args:
        beat_id: the beat id as it appears in story.beats.
        prose: Chinese prose; Chinese bracket quotes 「」 for any dialogue.

    Returns the relative path written (and word count).
    """
    state = ctx.context
    path = state.bundle_writer.write_beat_prose(beat_id=beat_id, prose=prose)
    state.beats_with_prose.add(beat_id)
    rel = path.relative_to(state.bundle_writer.out_dir)
    return f"OK wrote {rel}  ({len(prose)} chars)"


@function_tool(strict_mode=False)
def write_beat_shots(ctx: RunContextWrapper[AgentState], beat_id: str, shots: list[dict]) -> str:
    """Persist one beat's shot list to bundle/shots/<beat_id>/shots.json.

    Args:
        beat_id: the beat id from story.beats.
        shots: list of Shot dicts (shot_id, camera_framing, pose,
            wardrobe_state_used, vgai_injected_attrs,
            vgai_dropped_attrs_with_reason, final_prompt).

    Returns success/error. Validates every shot through the Shot pydantic
    model; on failure returns the offending index and error.
    """
    state = ctx.context
    parsed: list[Shot] = []
    for i, s in enumerate(shots):
        try:
            parsed.append(Shot.model_validate(s))
        except ValidationError as e:
            return f"VALIDATION_ERROR shot[{i}]:\n{e.json(indent=2)[:1500]}"
    path = state.bundle_writer.write_beat_shots(beat_id=beat_id, shots=parsed)
    state.beats_with_shots.add(beat_id)
    rel = path.relative_to(state.bundle_writer.out_dir)
    return f"OK wrote {rel}  ({len(parsed)} shots)"


# ---------- VGAI self-audit --------------------------------------------------

@function_tool(strict_mode=False)
def validate_vgai(
    ctx: RunContextWrapper[AgentState],
    shots: list[dict],
    character_name: str,
) -> str:
    """Run VGAI compliance audit on a shot list for one character.

    Args:
        shots: list of Shot dicts (same shape as write_beat_shots expects).
        character_name: must exist in the characters you wrote via
            write_characters.

    Returns:
        "CLEAN: 0 violations" on success, or a newline-separated list of
        violations (kind, shot_id, attr, reason). Director should fix and
        re-validate before calling render_image.
    """
    state = ctx.context
    if state.characters_data is None:
        return "ERROR: no characters yet — call write_characters first"
    if character_name not in state.characters_data:
        return f"ERROR: character {character_name!r} not in {list(state.characters_data)}"
    try:
        char_model = Character.model_validate(state.characters_data[character_name])
    except ValidationError as e:
        return f"ERROR: cached character schema invalid: {e}"
    try:
        shot_models = [Shot.model_validate(s) for s in shots]
    except ValidationError as e:
        return f"VALIDATION_ERROR shot schema:\n{e.json(indent=2)[:1500]}"
    violations = validate_shot_list(shot_models, char_model)
    if not violations:
        return f"CLEAN: 0 violations across {len(shot_models)} shots"
    lines = [f"DIRTY: {len(violations)} violations"]
    for v in violations[:40]:  # cap output
        lines.append(f"  [{v.kind}] shot={v.shot_id} attr={v.attr!r} — {v.reason}")
    if len(violations) > 40:
        lines.append(f"  ... and {len(violations) - 40} more")
    return "\n".join(lines)


# ---------- image rendering --------------------------------------------------

@function_tool
async def render_image(
    ctx: RunContextWrapper[AgentState],
    beat_id: str,
    shot_id: str,
    prompt: str,
    aspect_ratio: str = "16:9",
    resolution: str = "2k",
) -> str:
    """Render one shot via Grok Imagine Pro and save to the bundle.

    Args:
        beat_id: beat this shot belongs to.
        shot_id: unique shot id.
        prompt: final_prompt string — you already assembled it including
            base identity, pose, wardrobe, gated attrs, and framing.
        aspect_ratio: Grok supports 1:1 / 3:2 / 4:3 / 16:9 / 19.5:9 / 9:16 / 3:4.
        resolution: "1k" / "2k". Default "2k".

    Returns the written PNG path (relative to bundle root) or an error. Call
    validate_vgai first and make sure the shot is clean.
    """
    state = ctx.context
    if state.xai_client is None:
        return "ERROR: xai_client not initialized in agent state"
    shots_dir = state.bundle_writer.shots_dir(beat_id=beat_id)
    safe_shot = re.sub(r"[^A-Za-z0-9_-]", "_", shot_id)
    png_path = shots_dir / f"{safe_shot}.png"
    try:
        png_bytes = await state.xai_client.generate(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
        )
    except Exception as e:
        return f"RENDER_ERROR: {type(e).__name__}: {e}"
    png_path.write_bytes(png_bytes)
    state.images_rendered += 1
    rel = png_path.relative_to(state.bundle_writer.out_dir)
    return f"OK rendered {rel}  ({len(png_bytes)} bytes)"


# ---------- completion signal ------------------------------------------------

@function_tool
def finish_bundle(
    ctx: RunContextWrapper[AgentState],
    summary: str,
) -> str:
    """Signal that the bundle is complete. Call this ONLY when all beats
    have prose, all beats have shots, and all shots are rendered.

    Args:
        summary: short human-readable summary of what was produced
            (e.g. "10 beats, 36 shots, bifurcating noir").

    Returns OK and causes the runner to emit meta.json + story.md and stop.
    """
    state = ctx.context
    # Write meta + story.md as finalization
    from crpg.types import Story as _Story  # avoid circular import at module load
    if state.story_data is None:
        return "ERROR: cannot finish — story.json not written yet"
    story_model = _Story.model_validate(state.story_data)
    state.bundle_writer.write_story_md(story=story_model)
    state.finish_summary = summary
    state.finished = True
    return (
        f"OK bundle finished. beats_with_prose={len(state.beats_with_prose)}, "
        f"beats_with_shots={len(state.beats_with_shots)}, "
        f"images={state.images_rendered}. Summary: {summary}"
    )


# ---------- bundle of tools for Agent construction ---------------------------

ALL_TOOLS = [
    read_brief,
    read_skill,
    list_skill_references,
    read_skill_reference,
    write_story,
    write_characters,
    write_beat_prose,
    write_beat_shots,
    validate_vgai,
    render_image,
    finish_bundle,
]
