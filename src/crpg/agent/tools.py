"""Function tools for the main agent.

Every tool accepts `ctx: RunContextWrapper[AgentState]` as the first arg to
reach shared state (bundle writer, xAI client, cached story/chars).

All tool bodies are small and side-effect-disciplined: persist to disk via
BundleWriter, update state counters, return a short string to the agent so
its context window doesn't accumulate giant payloads.
"""
from __future__ import annotations

import base64
import json
import re
from pathlib import Path
from typing import Any, Literal

from agents import RunContextWrapper, function_tool
from pydantic import ValidationError

from crpg.agent.state import AgentState
from crpg.types import Character, Shot, Story
from crpg.validation.vgai import validate_shot_list


# ---------- skill reading ---------------------------------------------------

_VALID_SKILLS = {"skeleton", "script", "director"}
_SAFE_REF = re.compile(r"^[A-Za-z0-9_-]+$")
_SAFE_NAME = re.compile(r"^[A-Za-z0-9_-]+$")

# Some models (MiniMax, in practice) occasionally JSON-encode dict params as
# strings instead of passing native objects. Accept both forms.
def _coerce_to_obj(v: Any) -> Any:
    if isinstance(v, str):
        try:
            return json.loads(v)
        except json.JSONDecodeError:
            return v
    return v


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
def write_story(ctx: RunContextWrapper[AgentState], story: Any) -> str:
    """Persist the Skeleton-stage story skeleton to bundle/story.json.

    Args:
        story: a dict matching the crpg Story schema (meta + beats + edges).
            A JSON-encoded string is also accepted. See
            skills/skeleton/SKILL.md for the exact shape including the
            required `poeticMode` field in meta.

    Returns a short success/error summary. On validation error, the full
    pydantic message is included so you can fix and retry.
    """
    story = _coerce_to_obj(story)
    if not isinstance(story, dict):
        return f"VALIDATION_ERROR: story must be an object, got {type(story).__name__}"
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
        f"{len(story_model.edges)} edges. meta.poeticMode={story_model.meta.poetic_mode}."
    )


@function_tool(strict_mode=False)
def write_characters(ctx: RunContextWrapper[AgentState], characters: Any) -> str:
    """Persist ALL named characters' sheets to bundle/characters.json in ONE call.

    Args:
        characters: dict mapping character_name → character data. Include
            EVERY named character appearing in the story (POV + all NPCs
            referenced in beats), in a SINGLE call — do not call this tool
            twice to add characters one-at-a-time. A JSON-encoded string is
            also accepted.

    Each wardrobe_states[*].items[*] MUST populate `visual_description`
    (verbatim canonical string, no paraphrasing — Visual DNA Layer 3). For
    high-prior garments (sheer hosiery, qipao, JK uniform, etc.), also
    populate `disambiguation_layers` (Layer 10).

    Returns success/error summary with pydantic error detail on failure.
    """
    characters = _coerce_to_obj(characters)
    if not isinstance(characters, dict):
        return f"VALIDATION_ERROR: characters must be an object, got {type(characters).__name__}"
    state = ctx.context
    parsed: dict[str, Character] = {}
    for name, blob in characters.items():
        try:
            parsed[name] = Character.model_validate(blob)
        except ValidationError as e:
            return f"VALIDATION_ERROR character {name!r}:\n{e.json(indent=2)[:2000]}"
    # Soft check: warn if any wardrobe item lacks visual_description
    missing: list[str] = []
    for name, c in parsed.items():
        for state_name, ws in c.wardrobe_states.items():
            for it in ws.items:
                if not it.visual_description.strip():
                    missing.append(f"{name}.{state_name}.{it.name}")
    chars_blob = {n: c.model_dump(mode="json", by_alias=True) for n, c in parsed.items()}
    (state.bundle_writer.out_dir / "characters.json").write_text(
        json.dumps(chars_blob, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    state.characters_data = characters
    state.characters_emitted = True
    msg = f"OK characters.json written for {list(parsed.keys())}"
    if missing:
        msg += (
            f". WARNING: {len(missing)} wardrobe items missing visual_description "
            f"(byte-for-byte canonical string). Items: {missing[:8]}"
            f"{'...' if len(missing) > 8 else ''}. Fix and re-emit if quality matters."
        )
    return msg


# ---------- prose ------------------------------------------------------------

@function_tool
def write_beat_prose(
    ctx: RunContextWrapper[AgentState],
    beat_id: str,
    prose: str,
) -> str:
    """Persist one beat's prose to bundle/prose/<beat_id>.md.

    HARD CHECK: prose length must be within ±10% of beat.targetWordCount
    (measured in Chinese characters — `len(prose)` with CJK chars counting
    as 1 each). If outside the window, the tool REJECTS the prose and
    returns a diagnostic so the agent expands or trims and re-emits.

    Args:
        beat_id: the beat id as it appears in story.beats.
        prose: Chinese prose; Chinese bracket quotes 「」 for any dialogue.

    Returns the relative path written (and length) or a rejection reason.
    """
    state = ctx.context
    target: int | None = None
    if state.story_data is not None:
        for b in state.story_data.get("beats", []):
            if b.get("id") == beat_id:
                target = b.get("targetWordCount") or b.get("target_word_count")
                break
    length = len(prose)
    if target is not None:
        low = int(target * 0.9)
        high = int(target * 1.1)
        if length < low:
            return (
                f"REJECTED prose/{beat_id}.md — length {length} chars is below target "
                f"window [{low}, {high}] (targetWordCount={target}). Expand the scene "
                f"with more sensory detail / dialogue / action ticks until you hit the "
                f"window. Do NOT pad with filler; add meaningful beats per daisy V6 "
                f"Game Writing Rules. Then call write_beat_prose again with the longer prose."
            )
        if length > high:
            return (
                f"REJECTED prose/{beat_id}.md — length {length} chars exceeds upper bound "
                f"{high} (targetWordCount={target}). Trim to ≤ {high} while preserving "
                f"the value shift; cut adjective vomit and unnecessary transitions."
            )
    path = state.bundle_writer.write_beat_prose(beat_id=beat_id, prose=prose)
    state.beats_with_prose.add(beat_id)
    rel = path.relative_to(state.bundle_writer.out_dir)
    pct = f" ({length}/{target}, {int(length / target * 100)}% of target)" if target else f" ({length} chars)"
    return f"OK wrote {rel}{pct}"


# ---------- shot list --------------------------------------------------------

@function_tool(strict_mode=False)
def write_beat_shots(
    ctx: RunContextWrapper[AgentState],
    beat_id: str,
    shots: Any,
) -> str:
    """Persist one beat's shot list to bundle/shots/<beat_id>/shots.json.

    Args:
        beat_id: the beat id from story.beats.
        shots: list of Shot dicts (or a JSON-encoded list-string). Each shot:
            shot_id, camera_framing, pose, wardrobe_state_used,
            vgai_injected_attrs, vgai_dropped_attrs_with_reason, final_prompt.
            Optional: aspect_ratio (str), anchor_ref (e.g. "su_wan:face"),
            characters_in_frame (list[str]).

    Returns success/error. Validates every shot through the Shot pydantic
    model; on failure returns the offending index and error so you can fix
    and re-emit.
    """
    shots = _coerce_to_obj(shots)
    if not isinstance(shots, list):
        return f"VALIDATION_ERROR: shots must be a list, got {type(shots).__name__}"
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
    shots: Any,
    character_name: str,
    extra_character_names: list[str] | None = None,
) -> str:
    """Run VGAI / mutex / occlusion audit on a shot list.

    Args:
        shots: list of Shot dicts (same shape as write_beat_shots expects).
        character_name: the primary character for this shot list (its
            wardrobe_state drives mutex + occlusion audits).
        extra_character_names: any OTHER characters also present in any of
            these shots (supporting cast). Their attrs will be accepted as
            known without triggering `unknown_attr`.

    Returns:
        "CLEAN: 0 violations" or a newline list of violations (kind,
        shot_id, attr, reason). Fix and re-validate before render_image.
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
    extras: dict[str, Character] = {}
    for extra in extra_character_names or []:
        if extra not in state.characters_data:
            return f"ERROR: extra character {extra!r} not in characters_data"
        try:
            extras[extra] = Character.model_validate(state.characters_data[extra])
        except ValidationError as e:
            return f"ERROR: cached character {extra!r} schema invalid: {e}"
    shots = _coerce_to_obj(shots)
    if not isinstance(shots, list):
        return f"VALIDATION_ERROR: shots must be a list, got {type(shots).__name__}"
    try:
        shot_models = [Shot.model_validate(s) for s in shots]
    except ValidationError as e:
        return f"VALIDATION_ERROR shot schema:\n{e.json(indent=2)[:1500]}"
    violations = validate_shot_list(shot_models, char_model, extra_characters=extras or None)
    if not violations:
        return f"CLEAN: 0 violations across {len(shot_models)} shots"
    lines = [f"DIRTY: {len(violations)} violations"]
    for v in violations[:40]:
        lines.append(f"  [{v.kind}] shot={v.shot_id} attr={v.attr!r} — {v.reason}")
    if len(violations) > 40:
        lines.append(f"  ... and {len(violations) - 40} more")
    return "\n".join(lines)


# ---------- anchor + image rendering -----------------------------------------

_MODERATION_MARKERS = (
    "moderation", "content_policy", "safety", "blocked", "policy_violation",
    "inappropriate", "filtered",
)


def _looks_like_moderation(err_text: str) -> bool:
    low = err_text.lower()
    return any(m in low for m in _MODERATION_MARKERS)


def _safe(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "_", name)


@function_tool
async def render_anchor(
    ctx: RunContextWrapper[AgentState],
    character_name: str,
    anchor_type: str,
    prompt: str,
) -> str:
    """Render one canonical anchor image for a character (body or face).

    Call this TWICE per named character BEFORE rendering any shot: once with
    anchor_type='body' (3/4 length, neutral pose, full outfit visible,
    minimal background) and once with anchor_type='face' (tight portrait
    cu, clean neutral background). Subsequent shot renders will reference
    these anchors via Shot.anchor_ref = "<char>:body" or "<char>:face".

    Design the prompt for TRANSFER: minimal scene cues, plain/neutral
    background, clear lighting, character-descriptor-heavy. DO NOT include
    scene-specific setting ("subway entrance at night", "inside flower
    shop") — that defeats the anchor's cross-scene purpose.

    Args:
        character_name: must be a key in characters.json.
        anchor_type: "body" or "face".
        prompt: full prompt including the style preamble + character base
            + wardrobe visual_description strings verbatim.

    Returns relative path + size, or an error.
    """
    state = ctx.context
    if anchor_type not in ("body", "face"):
        return f"ERROR: anchor_type must be 'body' or 'face', got {anchor_type!r}"
    if state.characters_data is None or character_name not in state.characters_data:
        return (
            f"ERROR: character {character_name!r} not found — call write_characters first"
        )
    if state.xai_client is None:
        return "ERROR: xai_client not initialized"
    anchors_dir = state.bundle_writer.out_dir / "_anchors"
    anchors_dir.mkdir(exist_ok=True)
    png_path = anchors_dir / f"{_safe(character_name)}_{anchor_type}.png"
    aspect = "9:16" if anchor_type == "body" else "3:4"
    try:
        png_bytes = await state.xai_client.generate(
            prompt=prompt,
            aspect_ratio=aspect,
            resolution="2k",
        )
    except Exception as e:
        return f"RENDER_ERROR: {type(e).__name__}: {e}"
    png_path.write_bytes(png_bytes)
    state.anchors.setdefault(character_name, {})[anchor_type] = png_path
    rel = png_path.relative_to(state.bundle_writer.out_dir)
    return (
        f"OK anchor saved to {rel} ({len(png_bytes)} bytes). "
        f"Use anchor_ref='{character_name}:{anchor_type}' in render_image."
    )


@function_tool
async def render_image(
    ctx: RunContextWrapper[AgentState],
    beat_id: str,
    shot_id: str,
    prompt: str,
    aspect_ratio: str = "16:9",
    resolution: str = "2k",
    anchor_ref: str | None = None,
) -> str:
    """Render one shot via Grok Imagine Pro and save to the bundle.

    Args:
        beat_id: beat this shot belongs to.
        shot_id: unique shot id.
        prompt: final_prompt string.
        aspect_ratio: 1:1 / 3:2 / 4:3 / 16:9 / 19.5:9 / 9:16 / 3:4.
        resolution: "1k" or "2k".
        anchor_ref: optional "<character>:<body|face>" to pass that anchor's
            PNG as image_url (identity lock). Skip for ws_establishing
            shots (subject too small for anchor to matter). For cu_face /
            ms_waist_up prefer <char>:face; for full_body /
            three_quarter_knee_up / back_reveal_walking prefer <char>:body.

    Auto-retries up to 3 times on Grok moderation blocks. On final moderation
    failure, records the shot in state.failed_shots and returns a MODERATION
    status — the agent continues the bundle without this image.
    """
    state = ctx.context
    if state.xai_client is None:
        return "ERROR: xai_client not initialized in agent state"
    shots_dir = state.bundle_writer.shots_dir(beat_id=beat_id)
    png_path = shots_dir / f"{_safe(shot_id)}.png"

    # Resolve anchor_ref → base64 data URI if present
    image_url: str | None = None
    if anchor_ref is not None:
        if ":" not in anchor_ref:
            return f"ERROR: anchor_ref must be '<char>:<body|face>', got {anchor_ref!r}"
        anchor_char, _, anchor_type = anchor_ref.partition(":")
        char_anchors = state.anchors.get(anchor_char)
        if not char_anchors or anchor_type not in char_anchors:
            return (
                f"ERROR: anchor {anchor_ref!r} not yet rendered — call "
                f"render_anchor({anchor_char!r}, {anchor_type!r}, ...) first"
            )
        anchor_png = char_anchors[anchor_type]
        try:
            b64 = base64.b64encode(anchor_png.read_bytes()).decode("ascii")
            image_url = f"data:image/png;base64,{b64}"
        except Exception as e:
            return f"ERROR: could not read anchor {anchor_png}: {e}"

    last_err = ""
    for attempt in range(3):
        try:
            png_bytes = await state.xai_client.generate(
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                resolution=resolution,
                image_url=image_url,
            )
            png_path.write_bytes(png_bytes)
            state.images_rendered += 1
            rel = png_path.relative_to(state.bundle_writer.out_dir)
            note = f" (anchor={anchor_ref})" if anchor_ref else ""
            return f"OK rendered {rel}  ({len(png_bytes)} bytes){note}"
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
            if not _looks_like_moderation(last_err):
                return f"RENDER_ERROR: {last_err}"
            # moderation → brief backoff + retry
            import asyncio
            await asyncio.sleep(0.5 * (attempt + 1))
    # all retries exhausted on moderation
    state.failed_shots.append({
        "beat_id": beat_id,
        "shot_id": shot_id,
        "reason": f"moderation blocked 3x: {last_err[:200]}",
    })
    return (
        f"MODERATION_BLOCKED {beat_id}/{shot_id} after 3 retries. "
        f"Marked failed in state.failed_shots; continue with next shot. "
        f"Last error: {last_err[:200]}"
    )


# ---------- completion signal ------------------------------------------------

@function_tool
def finish_bundle(
    ctx: RunContextWrapper[AgentState],
    summary: str,
) -> str:
    """Signal the bundle is complete. Call this when all beats have prose +
    shots and all renderable shots are saved (moderation-blocked shots are
    OK to skip — they are tracked in state.failed_shots).

    Args:
        summary: short human-readable summary ("10 beats, 36 shots,
            bifurcating noir").

    Returns OK and causes the runner to emit story.md and stop.
    """
    state = ctx.context
    from crpg.types import Story as _Story
    if state.story_data is None:
        return "ERROR: cannot finish — story.json not written yet"
    story_model = _Story.model_validate(state.story_data)
    state.bundle_writer.write_story_md(story=story_model)
    state.finish_summary = summary
    state.finished = True
    failed_note = (
        f" failed={len(state.failed_shots)} (see _anchors/ / shots/ for what made it)"
        if state.failed_shots else ""
    )
    return (
        f"OK bundle finished. beats_prose={len(state.beats_with_prose)}, "
        f"beats_shots={len(state.beats_with_shots)}, "
        f"anchors={sum(len(v) for v in state.anchors.values())}, "
        f"images={state.images_rendered},{failed_note}. Summary: {summary}"
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
    render_anchor,
    render_image,
    finish_bundle,
]
