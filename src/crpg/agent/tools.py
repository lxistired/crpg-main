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

    **PASS AS NATIVE JSON OBJECT — do NOT stringify with JSON.stringify first.**
    The tool accepts both dict and JSON-string but string mode risks MiniMax
    truncation on long content. Native dict is ~30-90s faster per call.

    Args:
        story: a dict matching the crpg Story schema (meta + beats + edges).
            See skills/skeleton/SKILL.md for the exact shape including the
            required `poeticMode` field in meta.

    Returns a short success/error summary. On validation error, the full
    pydantic message is included so you can fix and retry.
    """
    story = _coerce_to_obj(story)
    if isinstance(story, str):
        # We got a string that failed JSON parse — likely truncated from double-encoding
        return (
            f"VALIDATION_ERROR: the `story` argument arrived as a string, and that "
            f"string did not parse as JSON (likely truncated at MiniMax output token "
            f"limit because double-encoding doubles the character count). "
            f"RETRY by passing `story` as a NATIVE JSON object, not a stringified JSON."
        )
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

    **PASS AS NATIVE JSON OBJECT — do NOT stringify with JSON.stringify first.**
    Double-encoding doubles the character count, risking output truncation.

    Args:
        characters: dict mapping character_name → character data. Include
            EVERY named character appearing in the story (POV + all NPCs
            referenced in beats), in a SINGLE call — do not call this tool
            twice to add characters one-at-a-time.

    Each wardrobe_states[*].items[*] MUST populate `visual_description`
    (verbatim canonical string, no paraphrasing — Visual DNA Layer 3). For
    high-prior garments (sheer hosiery, qipao, JK uniform, etc.), also
    populate `disambiguation_layers` (Layer 10).

    Returns success/error summary with pydantic error detail on failure.
    """
    characters = _coerce_to_obj(characters)
    if isinstance(characters, str):
        return (
            f"VALIDATION_ERROR: the `characters` argument arrived as a string that "
            f"failed JSON parse (likely truncation from double-encoding). "
            f"RETRY with `characters` as a NATIVE JSON object, not a stringified JSON."
        )
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

# Regex matching a single CJK Unified Ideograph (the "real" Chinese characters)
_CJK_CHAR = re.compile(r"[\u4e00-\u9fff]")

# Patterns that indicate the agent is hallucinating a self-reported word count
# ("（约二百五十字）" / "共约 2500 字" / "约2500字数" etc.) to fool length checks.
_WORD_COUNT_SELF_REPORT = re.compile(
    r"[（(]\s*(?:约|共约|大约|约?计)?\s*[一二三四五六七八九十百千万零两0-9]+\s*字"
    r"(?:数|符|元)?[^）)]*[）)]"
)

# Phrases the agent has been caught using to elide key dialogue in crisis scenes
# (daisy V6 Anti-Melodrama + Game Writing Rule R8). If any appear in a beat's
# prose, the tool rejects — elision violates "dialogue is gameplay".
_DIALOGUE_ELISION_MARKERS = [
    "她不记得具体说了什么",
    "她记不清他说了什么",
    "他不记得她说了什么",
    "那些话她后来记不清",
    "那些话他后来记不清",
    "他们谈了很久",
    "他们聊了一会儿",
    "模糊的对话",
    "无意义的对话",
    "只是些无关紧要的话",
    "只是闲聊",
]


def _cjk_char_count(text: str) -> int:
    """Count CJK ideographs only — ignore ASCII, punctuation, whitespace,
    and common agent hallucinations like word-count self-reports."""
    # Strip self-report parentheticals first so they don't inflate
    cleaned = _WORD_COUNT_SELF_REPORT.sub("", text)
    return len(_CJK_CHAR.findall(cleaned))


def _extract_mandated_quotes(synopsis: str) -> list[str]:
    """Return any quoted lines in the beat synopsis that MUST appear verbatim
    in the prose. Looks for Chinese bracket quotes 「」 and 『』."""
    out: list[str] = []
    # Simple non-greedy match — stops at first matching close bracket
    for m in re.finditer(r"「([^」]+)」", synopsis):
        out.append(m.group(1))
    for m in re.finditer(r"『([^』]+)』", synopsis):
        out.append(m.group(1))
    return out


@function_tool
def write_beat_prose(
    ctx: RunContextWrapper[AgentState],
    beat_id: str,
    prose: str,
) -> str:
    """Persist one beat's prose to bundle/prose/<beat_id>.md.

    HARD CHECKS (rejections):

    1. Length window: CJK character count must be within ±10% of
       beat.targetWordCount. **Only CJK ideographs count** (U+4E00–U+9FFF).
       ASCII, punctuation, whitespace, digits, and hallucinated word-count
       self-reports ("（约2500字）") do NOT count toward length.

    2. No dialogue elision: phrases like "她不记得具体说了什么" /
       "他们谈了很久" are BANNED (daisy V6 Game Writing Rule R8 — dialogue
       is gameplay, never elide key exchanges).

    3. No self-report footnotes: "（X字）" / "共约 X 字" style annotations
       are stripped silently (they don't count toward length) AND their
       presence warns the agent.

    4. Mandated dialogue: if the beat's synopsis contains quoted lines in
       「」 or 『』, those lines MUST appear verbatim in the prose. Skeleton
       places them there deliberately — they're load-bearing.

    Args:
        beat_id: the beat id as it appears in story.beats.
        prose: Chinese prose; Chinese bracket quotes 「」 for any dialogue.

    Returns the relative path written (and length) or a rejection reason.
    """
    state = ctx.context
    target: int | None = None
    synopsis: str = ""
    if state.story_data is not None:
        for b in state.story_data.get("beats", []):
            if b.get("id") == beat_id:
                target = b.get("targetWordCount") or b.get("target_word_count")
                synopsis = b.get("synopsis", "") or ""
                break

    # Check 2: dialogue elision
    for phrase in _DIALOGUE_ELISION_MARKERS:
        if phrase in prose:
            return (
                f"REJECTED prose/{beat_id}.md — 含禁用套路 {phrase!r}（对话 elision "
                f"违反 Game Writing Rule R8: dialogue 必须实写，不能省略或概述）。"
                f"把那句改成 2-3 行具体对白：对方说了什么可辨识的信息 / 暗示 / 试探，"
                f"Su Wan 回了什么，对方接了什么。每一行承载信息或张力。"
            )

    # Check 3: self-report footnote warning
    if _WORD_COUNT_SELF_REPORT.search(prose):
        return (
            f"REJECTED prose/{beat_id}.md — 检测到字数自报括号（如 '（约2500字）'）"
            f"这种 footnote 是 banned：它骗长度检查，但会被 sonnet 读者一眼识破。"
            f"把这类括号**整段删掉**，用真实的 prose 长度重新提交。"
        )

    # Check 4: mandated dialogue from synopsis
    mandated = _extract_mandated_quotes(synopsis)
    missing_lines: list[str] = []
    for line in mandated:
        if line not in prose:
            missing_lines.append(line)
    if missing_lines:
        quoted = "\n".join(f"    「{m}」" for m in missing_lines)
        return (
            f"REJECTED prose/{beat_id}.md — synopsis 里指定的以下台词没有逐字出现在 prose 中:\n"
            f"{quoted}\n"
            f"这些台词是 Skeleton 阶段定好的 value-shift 关键句，必须原文复制进对话里 "
            f"(用 「」包裹)。不能换措辞、不能删、不能只写动作不写台词。"
        )

    length = _cjk_char_count(prose)  # ← ONLY CJK ideographs
    if target is not None:
        low = int(target * 0.9)
        high = int(target * 1.1)
        # Track retry history per beat so we can escalate guidance.
        hist = state.prose_retry_history.setdefault(beat_id, [])
        hist.append(length)
        retry_count = len(hist)
        if length < low:
            deficit = low - length
            pct = int(length / target * 100)
            # Build an escalating, directive error message
            reasons = [
                f"你还需要至少 {deficit} 字（中文字符）才进窗口 [{low}, {high}]。"
                f"当前 {length}/{target}={pct}%，目标下限是 {low}。",
                "具体扩展方向（挑 2-3 个一起加）：",
                f"  - 对话：多 {max(1, deficit // 40)} 次 2-3 行的信息性/张力性对话交换（每行 ~30-50 字）",
                f"  - 感官锚：多 {max(1, deficit // 35)} 个具体的可触感官细节（气味 / 温度 / 质地 / 声音）——贴在动作里，不要独立段落",
                f"  - 动作锚：多 {max(1, deficit // 30)} 个 protagonist 做具体事情的动词瞬间（按灭屏幕 / 翻开某物 / 手指停顿）",
                "注意：不要用形容词堆砌或无效过渡词凑数；每一句必须推进情节、揭示人物、或建立张力。",
            ]
            if retry_count >= 3 and hist[-1] < hist[-2]:
                reasons.append(
                    "⚠ 你本轮比上轮还短了（oscillating）。请 STOP incrementing — 把上一版整段拿出来，"
                    "在里面 **加** 内容（上述 2-3 方向），不要重写。"
                )
            if retry_count >= 4:
                reasons.append(
                    f"⚠ 已 {retry_count} 次尝试。下次务必跨过 {low}；目标是一次到位 ~{int(target * 0.95)}，"
                    "避免无限重试。"
                )
            return (
                f"REJECTED prose/{beat_id}.md (attempt {retry_count}): "
                + " ".join(reasons)
            )
        if length > high:
            excess = length - high
            return (
                f"REJECTED prose/{beat_id}.md (attempt {retry_count}): "
                f"length {length} 超过上限 {high}，多了 {excess} 字。"
                f"Trim 而不是 rewrite：删掉重复的形容词、无效过渡（然后 / 接着 / 此时）、"
                f"和不推进情节的感官赘述。保留 value shift 关键句。目标 ~{int(target * 1.02)}。"
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
    if isinstance(shots, str):
        return (
            f"VALIDATION_ERROR: `shots` arrived as a string that failed JSON parse "
            f"(likely truncated from double-encoding). RETRY with `shots` as a "
            f"NATIVE JSON array of objects."
        )
    if not isinstance(shots, list):
        return f"VALIDATION_ERROR: shots must be a list, got {type(shots).__name__}"
    state = ctx.context
    parsed: list[Shot] = []
    for i, s in enumerate(shots):
        try:
            parsed.append(Shot.model_validate(s))
        except ValidationError as e:
            return f"VALIDATION_ERROR shot[{i}]:\n{e.json(indent=2)[:1500]}"

    # Principle 0 enforcement: every shot's final_prompt MUST start with the
    # canonical style preamble (first ~40 chars are a stable fingerprint). We
    # load the canonical block once from skills/director/references/style-preamble.md
    # and require each shot's prompt to contain its signature opening.
    canonical_prefix = _canonical_style_preamble_signature(ctx)
    if canonical_prefix:
        drift: list[tuple[int, str]] = []
        for i, s in enumerate(parsed):
            if canonical_prefix not in s.final_prompt[:400]:
                drift.append((i, s.final_prompt[:80]))
        if drift:
            bad = "\n".join(f"    shot[{i}] starts: {preview!r}" for i, preview in drift)
            return (
                f"REJECTED shots/{beat_id}/shots.json — {len(drift)} shot(s) do NOT begin "
                f"with the canonical Style Preamble (Principle 0). Every final_prompt must "
                f"start with the exact string found in skills/director/references/style-preamble.md "
                f"(verbatim, byte-for-byte — read it again if unsure).\n{bad}"
            )

    path = state.bundle_writer.write_beat_shots(beat_id=beat_id, shots=parsed)
    state.beats_with_shots.add(beat_id)
    rel = path.relative_to(state.bundle_writer.out_dir)
    return f"OK wrote {rel}  ({len(parsed)} shots)"


# cache to avoid re-reading the file on every shot
_STYLE_SIG_CACHE: dict[Path, str] = {}


def _canonical_style_preamble_signature(ctx: RunContextWrapper[AgentState]) -> str:
    """Extract a stable signature substring of the Style Preamble — the first
    meaningful line inside the ```...``` block in style-preamble.md. If any
    shot's final_prompt contains this signature, the preamble was copied.
    """
    path = ctx.context.project_root / "skills" / "director" / "references" / "style-preamble.md"
    if path in _STYLE_SIG_CACHE:
        return _STYLE_SIG_CACHE[path]
    if not path.exists():
        _STYLE_SIG_CACHE[path] = ""
        return ""
    text = path.read_text(encoding="utf-8")
    # Grab the first fenced code block after "## The preamble (copy this exact string)"
    marker = "## The preamble"
    idx = text.find(marker)
    if idx < 0:
        _STYLE_SIG_CACHE[path] = ""
        return ""
    block_start = text.find("```", idx)
    if block_start < 0:
        _STYLE_SIG_CACHE[path] = ""
        return ""
    block_start = text.find("\n", block_start) + 1
    block_end = text.find("```", block_start)
    if block_end < 0:
        _STYLE_SIG_CACHE[path] = ""
        return ""
    block = text[block_start:block_end].strip()
    # Use the first ~60 chars as signature — long enough to be specific,
    # short enough to survive minor whitespace variants.
    sig = " ".join(block.split())[:60]
    _STYLE_SIG_CACHE[path] = sig
    return sig


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
