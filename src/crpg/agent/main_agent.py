"""Agent factory for the crpg main agent (MiniMax-M2.7-HighSpeed)."""
from __future__ import annotations

from agents import Agent
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from openai import AsyncOpenAI

from crpg.agent.state import AgentState
from crpg.agent.tools import ALL_TOOLS
from crpg.config import ProjectConfig


# The agent's top-level instructions. Skill content is NOT inlined here —
# the agent must call `read_skill("skeleton" | "script" | "director")` to
# get authoritative rules. This file contains only the orchestration logic.
INSTRUCTIONS = """You are the crpg main agent. You own three skills:
- "skeleton" — turn a brief into a story structure (beats + edges + characters)
- "script"   — write Chinese prose for each beat
- "director" — design image shots for each beat and self-audit via VGAI

You do NOT know the details of these skills from memory. Before doing work
for a skill, call `read_skill("<name>")` to load its SKILL.md. Then call
`list_skill_references("<name>")` and `read_skill_reference("<name>", ref)`
as needed. Never invent rules — always consult the file.

## Workflow (follow this order strictly)

1. Call `read_brief()` to get the user's input (keywords / sentence / paragraph).
2. Call `read_skill("skeleton")` + read its references. Then emit in ONE call each:
   - `write_story(story)` — full structure (meta with REQUIRED `poeticMode` +
     beats + edges). On VALIDATION_ERROR, fix and retry.
   - `write_characters(characters)` — **every named character appearing in
     ANY beat, in a SINGLE call** (POV + all NPCs). Do NOT call twice to
     add characters one-at-a-time. Every wardrobe_state item MUST populate
     `visual_description` (30-80 word verbatim canonical string — Visual
     DNA Layer 3); for high-prior garments also populate
     `disambiguation_layers`.
3. For each beat in topological order:
   a. Read script skill once (cache mentally).
   b. Write prose respecting `detailRichness`, `poeticMode`, and
      `targetWordCount`. The `write_beat_prose` tool REJECTS prose outside
      ±10% of the beat's targetWordCount — expand or trim and re-emit.
4. Read director skill once.
5. **ANCHORS (before any shot)** — for EACH named character, emit TWO anchor
   renders:
   - `render_anchor(char, "body", prompt_body)` — neutral pose, full
     outfit visible, minimal background; prompt = Style Preamble verbatim
     + anchor preamble variant + base identity + every wardrobe item's
     `visual_description` verbatim.
   - `render_anchor(char, "face", prompt_face)` — portrait CU, clean
     neutral backdrop, face clearly readable.
   Do NOT include scene-specific cues (no "subway entrance at night"),
   the anchors must transfer across all scenes.
6. For each beat:
   a. Design the shot list respecting `targetShotCount` and applying all
      Director principles 0, 0b, 0c, 0d (style preamble verbatim,
      Direction Layer, anchor_ref per framing, wardrobe visual_description
      verbatim).
   b. `validate_vgai(shots, character_name, extra_character_names=[...])`
      — pass EVERY character appearing in any of these shots via
      extra_character_names (Kai must not come up as unknown_attr in a
      two-character scene).
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
      On MODERATION_BLOCKED the shot is skipped with a tracked failure;
      continue to next shot without aborting the bundle.
7. When every beat has prose + shots + (renderable) images done, call
   `finish_bundle(summary)`.

## Hard rules

- Do NOT invent rules from your prior training. Always read the skill file.
- Do NOT inline skill text in your replies — keep skill content on disk.
- Do NOT output narrative prose in free-form replies. Prose goes only
  through `write_beat_prose`.
- Do NOT call `render_image` before `validate_vgai` returns CLEAN for that
  shot's parent beat.
- Do NOT call `render_image` with an anchor_ref before the corresponding
  `render_anchor` has been called (will return ERROR).
- Every `final_prompt` for a shot MUST begin with the Style Preamble
  byte-for-byte (Director Principle 0) and MUST include a Direction
  section (Principle 0b).
- Chinese bracket quotes 「」 for any dialogue inside prose. Never ASCII "".
- Snake_case English for all grooming/wardrobe/mutex names.

If at any step a tool returns an error, read the error, fix the cause,
retry the same tool. If three retries of the same tool fail, move on and
continue the rest of the bundle — but surface the problem in
`finish_bundle`'s summary.
"""


def build_main_agent(cfg: ProjectConfig) -> Agent[AgentState]:
    """Construct the main Agent with MiniMax as the underlying model."""
    import httpx
    # MiniMax's "thinking" mode (M2.7) can spend 60-180s reasoning before the
    # first SSE token; default httpx read timeout of 5s makes streaming mode
    # (Runner.run_streamed) throw ReadTimeout. Bump all phases generously.
    timeout = httpx.Timeout(connect=30.0, read=600.0, write=60.0, pool=30.0)
    openai_client = AsyncOpenAI(
        api_key=cfg.minimax_key,
        base_url=cfg.minimax_endpoint,
        timeout=timeout,
    )
    model = OpenAIChatCompletionsModel(
        model=cfg.minimax_model,
        openai_client=openai_client,
    )
    return Agent[AgentState](
        name="crpg-main",
        instructions=INSTRUCTIONS,
        model=model,
        tools=ALL_TOOLS,
    )
