"""Agent factory for the crpg main agent.

The agent's system prompt PRE-LOADS all skill content (skeleton / script /
director SKILL.md + every reference file) and expects the brief to arrive
as the first user message. Skills are authoritative but are NOT read via
tool calls — they are already in context, which eliminates 4 tool types
(`read_brief`, `read_skill`, `list_skill_references`, `read_skill_reference`)
and shrinks the tool count to 9. Fewer tools = less tool-call-mode bias
pulling long-form outputs short.
"""
from __future__ import annotations

import os
from pathlib import Path

from agents import Agent, ModelSettings
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from openai import AsyncOpenAI

from crpg.agent.state import AgentState
from crpg.agent.tools import (
    ALL_TOOLS,
    FREEFORM_SOLO_TOOLS,
    FREEFORM_COMBO_TOOLS,
    HYBRID_SOLO_TOOLS,
    HYBRID_COMBO_TOOLS,
    MINIMAL_COMBO_TOOLS,
)
from crpg.config import ProjectConfig


# Benchmarking profiles — each maps to (model_id, base_url, api_key env var).
PROFILES: dict[str, dict[str, str]] = {
    "minimax-baseline": {
        "model_id": "MiniMax-M2.7-HighSpeed",
        "base_url": "https://api.minimaxi.com/v1",
        "api_key_env": "MINIMAX_API_KEY",
    },
    "grok-xai": {
        "model_id": "grok-4-1-fast-non-reasoning",
        "base_url": "https://api.x.ai/v1",
        "api_key_env": "XAI_API_KEY",
    },
    "grok-xai-reasoning": {
        "model_id": "grok-4-1-fast-reasoning",
        "base_url": "https://api.x.ai/v1",
        "api_key_env": "XAI_API_KEY",
    },
    "gpt-oss-120b-nitro": {
        "model_id": "openai/gpt-oss-120b:nitro",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
    },
    "m25-nitro": {
        "model_id": "minimax/minimax-m2.5:nitro",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
    },
    "qwen3-32b-groq": {
        "model_id": "qwen/qwen3-32b",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "extra_body": {
            "provider": {"only": ["groq"], "allow_fallbacks": False}
        },
    },
    "kimi-k2.5-baseten": {
        "model_id": "moonshotai/kimi-k2.5",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "extra_body": {
            "provider": {"only": ["BaseTen"], "allow_fallbacks": False}
        },
    },
    "grok-combo": {
        "model_id": "grok-4-1-fast-reasoning",
        "base_url": "https://api.x.ai/v1",
        "api_key_env": "XAI_API_KEY",
    },
    "grok-xai-4.2-reasoning": {
        "model_id": "grok-4.20-0309-reasoning",
        "base_url": "https://api.x.ai/v1",
        "api_key_env": "XAI_API_KEY",
    },
    "grok-combo-4.2": {
        "model_id": "grok-4.20-0309-reasoning",
        "base_url": "https://api.x.ai/v1",
        "api_key_env": "XAI_API_KEY",
    },
}


# Canonical Style Preamble — byte-identical prefix required at the start of
# every shot's `final_prompt` (Director Principle 0). Embedded in freeform-mode
# instructions so the agent produces shot prompts with consistent visual DNA
# even without the write_beat_shots tool enforcing byte-lock.
STYLE_PREAMBLE = """Modern Japanese seinen manga / anime illustration, \
digital painterly style with cel-shaded highlights and confident expressive \
line work. Cinematic noir color grade: saturated teal shadows, crimson \
accents, rich deep blacks, subtle amber practical lights. Slight organic \
film grain. Anamorphic 2.39 lens philosophy with gentle horizontal flare on \
bright points. Shallow depth of field separating subject from wet urban \
atmosphere. Single warm key light with cool ambient fill. Volumetric haze \
where street-level neon catches rain. Composition: cinematic — rule of \
thirds bias, off-center subject, negative space lets the setting breathe. \
Frame reads as a still from a mid-2020s Chinese urban noir film rather \
than a stock illustration."""


# ---------------------------------------------------------------------------
# Skill corpus injection
# ---------------------------------------------------------------------------

_SKILL_NAMES = ("skeleton", "script", "director")


def _load_skill_corpus(project_root: Path) -> str:
    """Read every SKILL.md + references/*.md for all 3 skills and return a
    single long string. Injected as part of the agent's system prompt so
    the agent doesn't need to round-trip tool calls to fetch skill content.
    Files are delimited by clear headers so the agent can locate sections
    mentally (no tool call required)."""
    parts: list[str] = []
    skills_dir = project_root / "skills"
    for skill in _SKILL_NAMES:
        base = skills_dir / skill
        skill_md = base / "SKILL.md"
        if skill_md.exists():
            parts.append(f"\n\n===== SKILL: {skill} =====\n\n")
            parts.append(skill_md.read_text(encoding="utf-8"))
        refs_dir = base / "references"
        if refs_dir.exists():
            for ref in sorted(refs_dir.glob("*.md")):
                parts.append(
                    f"\n\n===== SKILL REFERENCE: {skill}/{ref.stem} =====\n\n"
                )
                parts.append(ref.read_text(encoding="utf-8"))
    return "".join(parts)


# ---------------------------------------------------------------------------
# Instruction bodies (skill content is NOT duplicated here — it's appended
# at build time by build_main_agent via _load_skill_corpus)
# ---------------------------------------------------------------------------

INSTRUCTIONS = """You are the crpg main agent. You own three skills whose
full content appears below this instruction block in the system prompt:
- "skeleton" — turn the user brief into a story structure (beats + edges
  + characters)
- "script"   — write Chinese prose for each beat
- "director" — design image shots for each beat and self-audit via VGAI

The brief you must act on arrives in the first user message. All skill
rules are already in your context — consult them in-place, never claim
they are unavailable. Do NOT invent rules from prior training.

## Workflow (follow this order strictly)

1. Read the brief (first user message). Choose structure preset,
   detailRichness, poeticMode from brief + skeleton/SKILL.md guidance.
2. Emit in ONE call each:
   - `write_story(story)` — full structure with meta (required fields
     include `poeticMode`), beats, edges. On VALIDATION_ERROR, fix & retry.
   - `write_characters(characters)` — every named character appearing in
     ANY beat, in a SINGLE call (POV + all NPCs). Every wardrobe_state
     item MUST populate `visual_description` (30-80 word canonical string
     per Visual DNA Layer 3) and `covers` list. For high-prior garments
     also populate `disambiguation_layers`.
3. For each beat in topological order:
   Write Chinese prose respecting `detailRichness`, `poeticMode`, and
   `targetWordCount`. `write_beat_prose` REJECTS prose outside ±10% of
   targetWordCount (CJK characters only) — expand or trim and re-emit.
4. ANCHORS (before any shot) — for EACH named character, emit TWO renders:
   - `render_anchor(char, "body", body_prompt)` — neutral pose, full
     outfit visible, minimal background; prompt = Style Preamble verbatim
     + anchor preamble variant + base identity + every wardrobe item's
     `visual_description` verbatim.
   - `render_anchor(char, "face", face_prompt)` — portrait CU, clean
     neutral backdrop, face clearly readable.
   Do NOT include scene-specific cues; anchors must transfer across scenes.
5. For each beat:
   a. Design the shot list respecting `targetShotCount` and applying all
      Director principles 0, 0b, 0c, 0d (style preamble verbatim,
      Direction Layer, anchor_ref per framing, wardrobe visual_description
      verbatim).
   b. `validate_vgai(shots, character_name, extra_character_names=[...])` —
      pass EVERY character appearing in any of these shots via
      extra_character_names.
   c. If DIRTY, fix (drop attrs whose anchor is not in visible_regions;
      drop occluded grooming; never use see-through rationalizations) and
      re-validate until CLEAN.
   d. `write_beat_shots(beat_id, shots)`.
   e. `render_image(beat_id, shot_id, final_prompt, aspect_ratio,
      anchor_ref)` for each shot. Pick anchor_ref:
      - cu_face / ms_waist_up / any portrait crop → `<char>:face`
      - full_body_standing / three_quarter_knee_up / back_reveal_walking
        → `<char>:body`
      - ws_establishing → omit anchor_ref (subject too small)
      - multi-character frame → use POV character's anchor
      On MODERATION_BLOCKED the shot is skipped; continue without aborting.
6. Call `finish_bundle(summary)` when every beat has prose + shots +
   (renderable) images done.

## Hard rules

- Do NOT inline skill text in your replies — the skills are already in
  context above.
- Do NOT output narrative prose in free-form replies. Prose goes only
  through `write_beat_prose`.
- Do NOT call `render_image` before `validate_vgai` returns CLEAN for
  that shot's parent beat.
- Do NOT call `render_image` with an anchor_ref before the corresponding
  `render_anchor` has been called.
- Every `final_prompt` for a shot MUST begin with the Style Preamble
  byte-for-byte (Director Principle 0) and include a Direction section
  (Principle 0b).
- Chinese bracket quotes 「」 for any dialogue inside prose. Never ASCII "".
- Snake_case English for all grooming/wardrobe/mutex names.

If a tool returns an error, read it, fix the cause, retry the same tool.
Three retries of the same tool → move on and surface in `finish_bundle`.
"""


COMBO_INSTRUCTIONS = """You are the crpg main agent in COMBO mode. Skill
content (skeleton / script / director with all references) is pre-loaded
in the system prompt below this block. The brief arrives in the first
user message.

In combo mode, you delegate Script (prose writing) to a fast worker model
via the `invoke_script_worker` tool. You do NOT call `write_beat_prose`
yourself.

## Workflow

1. Read the brief (first user message).
2. Emit in ONE call each:
   - `write_story(story)` — meta (with poeticMode) + beats + edges.
   - `write_characters(characters)` — every character in a SINGLE call.
     Every wardrobe item needs `visual_description` (30-80 words) and
     `covers` list.
3. For each beat in topological order:
   - Build a worker brief containing: the beat's synopsis VERBATIM
     (including any 「」/『』 quoted lines that must appear), valueBefore
     → valueAfter, wardrobe_state, 1-2 prior-beat continuity cues,
     explicit CJK length target, tone / stakes. Do NOT paste script
     skill rules — the worker reads them itself.
   - Call `invoke_script_worker(beat_id, worker_prompt)`. Returns OK or
     REJECT. On REJECT, adjust the worker_prompt (add dialogue count,
     sensory anchors, action beats, re-emphasise mandated quotes) and
     retry. Max 4 retries per beat.
4. For EACH character emit two anchor renders:
   `render_anchor(char, "body", body_prompt)` and
   `render_anchor(char, "face", face_prompt)`. No scene-specific cues.
5. For each beat:
   a. Design shots respecting Director principles 0 / 0b / 0c / 0d.
   b. `validate_vgai(shots, character_name, extra_character_names=[...])`.
      Fix DIRTY violations (drop attrs outside visible_regions / occluded
      grooming, never paper over occlusion with see-through
      rationalisations).
   c. `write_beat_shots(beat_id, shots)`.
   d. `render_image` for each shot with correct anchor_ref.
6. `finish_bundle(summary)` when every beat has prose + shots.

## Hard rules

- Do NOT inline skill text into replies — skills are already in context.
- Do NOT call `write_beat_prose` — only `invoke_script_worker` for prose.
- Do NOT output narrative prose yourself — the worker does that.
- Every `final_prompt` must begin with the Style Preamble byte-for-byte
  and include a Direction section.
- Chinese bracket quotes 「」 for dialogue referenced in worker briefs.

If a tool errors, read it, fix the cause, retry. Three retries on the
same tool → move on and surface in `finish_bundle`.
"""


FREEFORM_INSTRUCTIONS = """You are the crpg main agent in FREE-FORM TEXT mode.

All skill content (skeleton + script + director + references, ~105KB) is
pre-loaded in the system prompt below this block. The brief arrives in
the first user message.

You output the complete bundle as MARKDOWN TEXT in your response messages.
Do NOT look for a `write_story` / `write_characters` / `write_beat_prose`
/ `write_beat_shots` tool — there isn't one. The ONLY tool available is
`render_image`, for generating images after you have designed the shots.

Treat any reference in the skills to "call write_X tool" as "output the
equivalent section in markdown instead".

## Required output structure

Output the full bundle as a single long markdown document (can span
multiple assistant turns if needed). Use these top-level sections:

```
# Story
## Meta
- controllingIdea / structure / detailRichness / contentLength / poeticMode

## Beats
- For each beat: id, type, synopsis (with any 「」 mandated lines),
  valueBefore → valueAfter, wardrobe_state, targetWordCount, targetShotCount

## Edges
- from_beat → to_beat (condition)

# Characters
- For each: name, base identity, persistent_grooming,
  wardrobe_states (each state's items with visual_description 30-80 words
  and covers list).

# Prose
## Beat <id>
<Chinese prose, ±10% of targetWordCount (CJK chars), dialogue in 「」.
Include all synopsis 「」 quotes verbatim.>

# Shots
## Beat <id>
### Shot 1
- framing, subject, aspect_ratio, anchor_ref
- final_prompt: <begins with Style Preamble byte-for-byte, includes
  Direction section>

(Then call `render_image(beat_id, shot_id, final_prompt, aspect_ratio,
anchor_ref)` once per shot.)

# End of Bundle
```

Follow all daisy V6 rules in the pre-loaded skills:
- CJK character window ±10% of targetWordCount
- Mandated synopsis quotes 「」 verbatim in prose
- Style Preamble byte-for-byte at start of every final_prompt
- Direction Layer on every shot
- Occlusion gate for attribute injection (drop attrs whose anchor is
  covered by a wardrobe item's `covers`)
- Chinese bracket quotes 「」 for all dialogue; never ASCII ""

## Style Preamble (paste at start of EVERY shot's final_prompt, verbatim)

```
""" + STYLE_PREAMBLE + """
```

Every final_prompt must begin with this exact block (no rewording). Follow
with Character identity, Direction Layer tell, scene specifics, framing —
see skills/director/references/style-preamble.md for the skeleton.

Be complete — every beat needs prose AND shots. Close with
`# End of Bundle`.
"""


FREEFORM_COMBO_INSTRUCTIONS = """You are the crpg main agent in FREE-FORM
COMBO mode.

Skills pre-loaded in system prompt. Brief in first user message.

Same output structure as free-form solo, EXCEPT for prose:
- Do NOT write Chinese prose in your response text.
- For each beat, call `freeform_script_worker(beat_id, target_chars,
  worker_prompt)`. The worker writes Chinese prose to the bundle
  directly. Your message body never contains the prose text.

Tools available: `render_image` + `freeform_script_worker`.

Your worker_prompt for each beat must include:
- Synopsis verbatim (especially any 「」/『』 mandated quoted lines)
- valueBefore → valueAfter
- wardrobe_state
- 1-2 prior-beat continuity cues (so prose flows)
- target_chars (matches the third argument you pass)
- Tone / stakes

Output everything else (story meta, beats, characters, shots,
`render_image` calls) as markdown text per the free-form solo structure.

## Style Preamble (paste at start of EVERY shot's final_prompt, verbatim)

```
""" + STYLE_PREAMBLE + """
```

Every final_prompt must begin with this exact block (no rewording). Follow
with Character identity, Direction Layer tell, scene specifics, framing.

Close with `# End of Bundle`.
"""


HYBRID_INSTRUCTIONS = """You are the crpg main agent in HYBRID SOLO mode.

Skill content pre-loaded. Brief in first user message.

In this mode you split work across THREE output channels:
1. **Structure + prose**: output as markdown text (story meta, beats
   with Chinese prose inline, characters, edges) in your response messages.
2. **Director phase**: use the real structured tools — `render_anchor`,
   `write_beat_shots`, `validate_vgai`, `render_image`. These enforce
   Style Preamble byte-lock, occlusion gate, and VGAI validation.
3. **Close** with `# End of Bundle` markdown marker.

Tools available: `render_image`, `render_anchor`, `write_beat_shots`,
`validate_vgai`.

## Workflow

1. Read brief. Output `# Story` section (meta + beats list + edges).
2. Output `# Characters` section — each character's base identity,
   persistent_grooming, wardrobe_states (items with visual_description
   30-80 words and covers list).
3. For each beat in order, output `## Beat <id>` then the Chinese prose
   directly in markdown. Hit targetWordCount ±10% (CJK only). Include
   「」 mandated quotes verbatim.
4. For each named character call `render_anchor(char, "body", prompt)`
   and `render_anchor(char, "face", prompt)`. No scene cues in anchors.
5. For each beat, design shots per Director principles, then:
   - `validate_vgai(shots, character_name, extra_character_names=[...])`
   - fix DIRTY until CLEAN
   - `write_beat_shots(beat_id, shots)`
   - `render_image(...)` per shot
6. `# End of Bundle` marker.

Hard rules (from pre-loaded skills):
- Style Preamble byte-for-byte at start of every final_prompt
  (write_beat_shots enforces).
- Direction Layer on every shot.
- Anchors rendered before shots that reference them.
- Chinese bracket quotes 「」 for dialogue.
"""


MINIMAL_COMBO_INSTRUCTIONS = """You are the crpg main agent in MINIMAL COMBO mode.

Skill content pre-loaded below. Brief in first user message.

**Skill reference disambiguation — READ THIS FIRST**:
The pre-loaded skills describe an old tool surface (`write_story` /
`write_characters` / `write_beat_prose` / `write_beat_shots` /
`validate_vgai`). Those tools DO NOT EXIST in this mode. When skill text
says "call write_X tool":
- `write_story` / `write_characters` → output the equivalent section as
  MARKDOWN TEXT in your assistant response (`# Story` and `# Characters`).
- `write_beat_prose` → call `freeform_script_worker` instead.
- `write_beat_shots` / `validate_vgai` → call `save_shot_prompt` directly
  per shot (lenient — no VGAI validation in this mode).

You have FOUR tools and no structural JSON enforcement — just persistence:
- `freeform_script_worker(beat_id, target_chars, worker_prompt)`: worker
  writes prose to bundle; you never see the prose text.
- `save_shot_prompt(beat_id, shot_id, final_prompt, aspect_ratio,
  anchor_ref)`: persists one shot. Lenient check — only validates that
  final_prompt begins with the canonical Style Preamble prefix; no
  Direction Layer / framing / occlusion enforcement.
- `render_anchor(char, kind, prompt)`: renders anchor image.
- `render_image(beat_id, shot_id, final_prompt, aspect_ratio,
  anchor_ref)`: renders scene image.

## Workflow

1. Read brief (first user message). Output `# Story` and `# Characters`
   markdown sections in your response text (no tool for this — output
   only; we don't need strict schemas here).
2. For each beat in topological order:
   a. Craft worker_prompt (synopsis verbatim with 「」/『』 mandated quotes,
      value shift, wardrobe, prior-beat cues, target_chars, tone).
   b. Call `freeform_script_worker(beat_id, target_chars, worker_prompt)`.
      Retry up to 2 times if worker underdelivers.
3. For each character, call `render_anchor(char, "body", body_prompt)`
   and `render_anchor(char, "face", face_prompt)`. No scene cues.
4. For each beat, design shots per Director skill. For each shot:
   a. Compose full final_prompt: canonical Style Preamble verbatim +
      Character identity + Direction Layer tell + Scene + Framing.
   b. Call `save_shot_prompt(beat_id, shot_id, final_prompt, ...)`.
   c. Call `render_image(beat_id, shot_id, final_prompt, ...)`.
5. Close output with `# End of Bundle`.

## Style Preamble (paste at start of EVERY shot final_prompt, verbatim)

```
""" + STYLE_PREAMBLE + """
```

Every call to `save_shot_prompt` must include this exact block as the
start of final_prompt — the tool rejects anything else.

Hard rules: Chinese bracket quotes 「」 for dialogue in worker_prompt.
Snake_case English for grooming/wardrobe names.
"""


HYBRID_COMBO_INSTRUCTIONS = """You are the crpg main agent in HYBRID COMBO mode.

Skill content pre-loaded. Brief in first user message.

Prose is delegated to a fast worker via `freeform_script_worker(beat_id,
target_chars, worker_prompt)`. You DO NOT write Chinese prose yourself.

Non-prose work uses the real structured tools: `render_anchor`,
`write_beat_shots`, `validate_vgai`, `render_image`.

Tools: `render_image`, `render_anchor`, `write_beat_shots`,
`validate_vgai`, `freeform_script_worker`.

## Workflow

1. Read brief. Output `# Story` and `# Characters` sections as markdown
   in your response text.
2. For each beat, craft a worker_prompt (synopsis verbatim with 「」/『』
   mandated quotes, value shift, wardrobe state, tone, target_chars,
   prior-beat continuity cues) and call
   `freeform_script_worker(beat_id, target_chars, worker_prompt)`. Worker
   writes prose to bundle directly — you never see the prose text.
3. For each named character, call `render_anchor` twice (body + face).
4. For each beat, design shots, validate_vgai → CLEAN → write_beat_shots
   → render_image per shot. Style Preamble byte-lock auto-enforced.
5. `# End of Bundle` marker.

Hard rules apply: Style Preamble byte-for-byte, Direction Layer, anchor
ordering, Chinese 「」 for dialogue.
"""


TEXT_ONLY_INSTRUCTIONS = """You are the crpg main agent in TEXT-ONLY mode.
Skill content is pre-loaded in the system prompt below this block. The
brief arrives in the first user message. You own only skeleton + script;
no director work.

## Workflow

1. Read the brief (first user message).
2. Emit in ONE call each:
   - `write_story(story)` — full structure with meta.poeticMode + beats +
     edges.
   - `write_characters(characters)` — every named character in a SINGLE
     call. Every wardrobe item MUST have `visual_description` (30-80
     words) and `covers` list.
3. For each beat in topological order, call `write_beat_prose(beat_id,
   prose)` with Chinese prose hitting ±10% of targetWordCount (CJK chars
   only). On REJECT, expand and retry.
4. When every beat has prose, call `finish_bundle(summary)`. DO NOT call
   render_anchor, write_beat_shots, validate_vgai, or render_image.

## Hard rules

- Do NOT inline skill text in your replies — skills are already in context.
- Do NOT output narrative prose in free-form replies. Prose goes only
  through `write_beat_prose`.
- Chinese bracket quotes 「」 for dialogue. Never ASCII "".
- Snake_case English for all grooming/wardrobe/mutex names.

If a tool errors, read it, fix the cause, retry. Three failed retries on
the same tool → move on, surface in finish_bundle.
"""


def build_main_agent(
    cfg: ProjectConfig,
    project_root: Path,
    profile: str = "minimax-baseline",
    skip_director: bool = False,
    combo: bool = False,
    freeform: bool = False,
    freeform_combo: bool = False,
    hybrid: bool = False,
    hybrid_combo: bool = False,
    minimal_combo: bool = False,
) -> Agent[AgentState]:
    """Construct the main Agent with the full skill corpus pre-loaded in
    system prompt. `profile` selects model/endpoint. Instruction variants
    (mutually exclusive): default / skip_director / combo / freeform /
    freeform_combo / hybrid / hybrid_combo / minimal_combo."""
    import httpx
    modes = [skip_director, combo, freeform, freeform_combo, hybrid, hybrid_combo, minimal_combo]
    if sum(modes) > 1:
        raise ValueError(
            "instruction modes are mutually exclusive; got "
            f"{[m for m,v in zip(['skip_director','combo','freeform','freeform_combo','hybrid','hybrid_combo','minimal_combo'], modes) if v]}"
        )

    if profile not in PROFILES:
        raise ValueError(
            f"unknown profile {profile!r}; choose one of {sorted(PROFILES)}"
        )
    prof = PROFILES[profile]
    api_key = os.environ.get(prof["api_key_env"])
    if not api_key:
        raise ValueError(
            f"profile {profile!r} requires env var {prof['api_key_env']}"
        )
    timeout = httpx.Timeout(connect=30.0, read=600.0, write=60.0, pool=30.0)
    openai_client = AsyncOpenAI(
        api_key=api_key,
        base_url=prof["base_url"],
        timeout=timeout,
    )
    model = OpenAIChatCompletionsModel(
        model=prof["model_id"],
        openai_client=openai_client,
    )

    if minimal_combo:
        base = MINIMAL_COMBO_INSTRUCTIONS
        suffix = "+minimal-combo"
        tools = MINIMAL_COMBO_TOOLS
    elif hybrid_combo:
        base = HYBRID_COMBO_INSTRUCTIONS
        suffix = "+hybrid-combo"
        tools = HYBRID_COMBO_TOOLS
    elif hybrid:
        base = HYBRID_INSTRUCTIONS
        suffix = "+hybrid"
        tools = HYBRID_SOLO_TOOLS
    elif freeform_combo:
        base = FREEFORM_COMBO_INSTRUCTIONS
        suffix = "+freeform-combo"
        tools = FREEFORM_COMBO_TOOLS
    elif freeform:
        base = FREEFORM_INSTRUCTIONS
        suffix = "+freeform"
        tools = FREEFORM_SOLO_TOOLS
    elif combo:
        base = COMBO_INSTRUCTIONS
        suffix = "+combo"
        tools = ALL_TOOLS
    elif skip_director:
        base = TEXT_ONLY_INSTRUCTIONS
        suffix = "+text-only"
        tools = ALL_TOOLS
    else:
        base = INSTRUCTIONS
        suffix = ""
        tools = ALL_TOOLS

    skill_corpus = _load_skill_corpus(project_root)
    full_instructions = (
        base
        + "\n\n"
        + "=" * 72
        + "\n"
        + "# SKILLS (authoritative — read below for rules; do not quote back)\n"
        + "=" * 72
        + skill_corpus
    )

    model_settings = (
        ModelSettings(extra_body=prof["extra_body"])
        if "extra_body" in prof
        else ModelSettings()
    )
    return Agent[AgentState](
        name=f"crpg-main[{profile}{suffix}]",
        instructions=full_instructions,
        model=model,
        model_settings=model_settings,
        tools=tools,
    )
