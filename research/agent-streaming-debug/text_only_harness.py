"""Text-only agent harness — stubs xAI (fake PNG) so text pipeline can be
validated cheaply. Measures:
  - prose word-count window hit rate
  - structure + 3-axis emission
  - wardrobe visual_description populated
  - anchor calls happen in correct order (before any shot)

Usage:
  .venv/bin/python research/agent-streaming-debug/text_only_harness.py <brief_path> [out_dir]

Default brief: tests/fixtures/demo_brief.md
Default out_dir: /tmp/crpg-text-only
"""
import asyncio, os, sys, time, argparse
from pathlib import Path
from dotenv import load_dotenv

PROJECT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT / "src"))
load_dotenv(PROJECT / ".env")

from agents import Runner, set_tracing_disabled
set_tracing_disabled(True)

from crpg.agent.main_agent import (
    build_main_agent,
    build_handoff_agents,
    build_handoff_planner_agents,
    build_skeleton_planner_agent,
    build_director_planner_agent,
    STYLE_PREAMBLE,
)
from crpg.agent.director_plan import DirectorPlan, StoryPlan, BeatPlan, CharacterPlan
from crpg.agent.tools import (
    _do_render_anchor,
    _do_save_shot_prompt,
    _do_render_image,
    _do_freeform_script_worker,
)


# Anchor preamble variant — appended after STYLE_PREAMBLE for anchor renders
# so the anchor has a low-noise latent that transfers cleanly to shots.
_ANCHOR_PREAMBLE_SUFFIX = (
    "\n\nAnchor shot for cross-scene character consistency. Neutral pose, "
    "minimal background (muted gradient or plain studio wall), subject "
    "centered, full face clearly readable, outfit details crisply visible, "
    "even lighting preserving color accuracy."
)


def _compose_shot_final_prompt(body: str) -> str:
    """Prepend the canonical Style Preamble to the planner-emitted shot body."""
    return STYLE_PREAMBLE + "\n\n" + body.lstrip()


def _compose_anchor_prompt(body: str) -> str:
    """Prepend Style Preamble + anchor-preamble variant to the planner body."""
    return STYLE_PREAMBLE + _ANCHOR_PREAMBLE_SUFFIX + "\n\n" + body.lstrip()


def _compose_story_markdown(plan: StoryPlan) -> str:
    """Serialize StoryPlan to a human-readable markdown file for bundle debug."""
    lines = [f"# {plan.meta.title}", ""]
    m = plan.meta
    lines.append(
        f"**Genre**: {m.genre}  |  **Length**: {m.content_length}  |  "
        f"**Detail**: {m.detail_richness}  |  **Structure**: {m.structure}  |  "
        f"**Poetic**: {m.poetic_mode}"
    )
    lines.append("")
    lines.append(f"**Controlling idea**: {m.controlling_idea}")
    lines.append("")
    lines.append(f"**Antagonism**: {m.antagonism}")
    lines.append("")
    if plan.edges:
        lines.append("## Edges")
        for e in plan.edges:
            lines.append(f"- {e}")
        lines.append("")
    lines.append("## Beats")
    for b in plan.beats:
        lines.append(f"### {b.id} · {b.node_type}")
        lines.append(f"- **synopsis**: {b.synopsis}")
        lines.append(f"- **value**: {b.value_before} → {b.value_after}")
        lines.append(f"- **target_word_count**: {b.target_word_count}")
        lines.append(f"- **wardrobe_state**: {b.wardrobe_state}")
        if b.prior_beat_cues:
            lines.append(f"- **prior_cues**: {' / '.join(b.prior_beat_cues)}")
        if b.tone:
            lines.append(f"- **tone**: {b.tone}")
        lines.append("")
    return "\n".join(lines)


def _compose_characters_markdown(plan: StoryPlan) -> str:
    """Serialize StoryPlan characters to a markdown file for bundle debug."""
    lines = ["# Characters", ""]
    for c in plan.characters:
        lines.append(f"## {c.name} ({c.display_name})")
        lines.append(f"- **base**: {c.base}")
        if c.persistent_grooming:
            lines.append(f"- **persistent_grooming**: {c.persistent_grooming}")
        lines.append("- **wardrobe_states**:")
        for w in c.wardrobe_states:
            lines.append(f"  - `{w.name}` covers={w.covers}")
            lines.append(f"    - visual: {w.visual_description}")
        lines.append("")
    return "\n".join(lines)


def _character_lookup(plan: StoryPlan) -> dict[str, CharacterPlan]:
    return {c.name: c for c in plan.characters}


def _compose_worker_prompt(beat: BeatPlan, plan: StoryPlan) -> str:
    """Build the worker_prompt for one beat from StoryPlan data.

    The worker gets everything it needs to write prose: synopsis verbatim
    (with mandated quotes), value turn, wardrobe state (full visual),
    prior-beat cues, tone, length target.
    """
    # Resolve wardrobe state — find the matching item in any character.
    wardrobe_lines: list[str] = []
    for c in plan.characters:
        for w in c.wardrobe_states:
            if w.name == beat.wardrobe_state:
                wardrobe_lines.append(
                    f"{c.display_name} · {w.name}: {w.visual_description}"
                )
    cues = "; ".join(beat.prior_beat_cues) if beat.prior_beat_cues else "(无)"
    wardrobe_block = "\n".join(wardrobe_lines) if wardrobe_lines else "(未指定)"
    return (
        f"为{plan.meta.genre}故事第 {beat.id} 拍撰写中文散文 "
        f"（目标 {beat.target_word_count} 汉字，±10% 窗口）。\n\n"
        f"Synopsis (verbatim, 包含所有「」/『』 必须保留):\n"
        f"{beat.synopsis}\n\n"
        f"Value turn: {beat.value_before} → {beat.value_after}\n"
        f"Node type: {beat.node_type}\n"
        f"Tone: {beat.tone or '(未指定)'}\n\n"
        f"Wardrobe state (请自然融入, 不要复述清单):\n{wardrobe_block}\n\n"
        f"Prior-beat continuity cues: {cues}\n\n"
        f"Controlling idea: {plan.meta.controlling_idea}\n"
        f"Poetic mode: {'ON' if plan.meta.poetic_mode else 'OFF'}\n"
    )


def _compose_director_input(plan: StoryPlan) -> str:
    """Director agent's input message — StoryPlan JSON + prose note."""
    import json as _json
    story_json = plan.model_dump_json(indent=2)
    beat_ids = [b.id for b in plan.beats]
    return (
        "Skeleton + Script phases are complete. Below is the StoryPlan JSON "
        "you need to plan shots for. For every named character, emit two "
        "anchors (body + face). For every beat in StoryPlan.beats, emit "
        "3-6 shots.\n\n"
        "Prose has already been written to the bundle (you do not need to "
        f"emit or reference prose). Beats with prose: {beat_ids}\n\n"
        "=== StoryPlan JSON ===\n"
        f"{story_json}\n"
    )
from crpg.agent.state import AgentState
from crpg.bundle import BundleWriter
from crpg.config import load_config

# Minimal valid PNG (1×1 transparent) for stub
FAKE_PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000d49444154789c626000000000050001a5f4570f0000000049454e44ae426082"
)

class StubXaiImageClient:
    async def generate(self, *, prompt, aspect_ratio="16:9", resolution="2k", **kwargs):
        has_anchor = kwargs.get("image_url") is not None
        tag = "ANCHOR-REF" if has_anchor else "NO-ANCHOR"
        print(f"  [STUB-xai {tag}] ar={aspect_ratio} prompt[:60]={prompt[:60]!r}",
              file=sys.stderr, flush=True)
        await asyncio.sleep(0.01)
        return FAKE_PNG


def log(msg, t0):
    print(f"[T+{time.time()-t0:.1f}s] {msg}", file=sys.stderr, flush=True)


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("brief", nargs="?",
                    default=str(PROJECT / "tests/fixtures/demo_brief.md"))
    ap.add_argument("out_dir", nargs="?",
                    default="/tmp/crpg-text-only")
    ap.add_argument("--max-turns", type=int, default=400)
    ap.add_argument("--profile", default="minimax-baseline",
                    help="model profile: minimax-baseline | grok-xai | "
                         "grok-xai-reasoning | gpt-oss-120b-nitro | "
                         "m25-nitro | qwen3-32b-nitro")
    ap.add_argument("--skip-director", action="store_true",
                    help="Load TEXT_ONLY_INSTRUCTIONS: stop after Script "
                         "phase, skip anchor/shots/vgai/render_image. Pure "
                         "text pipeline benchmark.")
    ap.add_argument("--combo", action="store_true",
                    help="Load COMBO_INSTRUCTIONS: reasoning orchestrator + "
                         "fast worker (invoke_script_worker for prose).")
    ap.add_argument("--freeform", action="store_true",
                    help="FREEFORM SOLO mode: only render_image tool; "
                         "everything else output as markdown text. Capture "
                         "agent text to freeform_output.md.")
    ap.add_argument("--freeform-combo", action="store_true",
                    help="FREEFORM COMBO mode: render_image + "
                         "freeform_script_worker; main writes non-prose "
                         "sections as markdown; worker writes prose.")
    ap.add_argument("--hybrid", action="store_true",
                    help="HYBRID SOLO mode: prose as markdown + structured "
                         "Director tools (render_anchor, write_beat_shots, "
                         "validate_vgai, render_image).")
    ap.add_argument("--hybrid-combo", action="store_true",
                    help="HYBRID COMBO mode: freeform_script_worker for "
                         "prose + structured Director tools.")
    ap.add_argument("--minimal-combo", action="store_true",
                    help="MINIMAL COMBO mode: 4 tools total — "
                         "freeform_script_worker + save_shot_prompt + "
                         "render_anchor + render_image. Lenient Style "
                         "Preamble check, no other validation.")
    ap.add_argument("--handoff-grok", action="store_true",
                    help="HANDOFF mode: two-agent pipeline "
                         "(skeleton_script_agent → director_agent) using "
                         "build_handoff_agents. Ignores --profile; use "
                         "--ss-profile / --director-profile to override.")
    ap.add_argument("--handoff-planner", action="store_true",
                    help="PLANNER mode (Path D): SS agent hands off to a "
                         "director_planner_agent that emits one DirectorPlan "
                         "JSON. Python loop then renders anchors + shots in "
                         "parallel without further LLM calls.")
    ap.add_argument("--ss-profile", default="grok-xai",
                    help="handoff: skeleton+script agent profile")
    ap.add_argument("--director-profile", default="grok-xai-reasoning",
                    help="handoff: director agent profile")
    args = ap.parse_args()

    cfg = load_config()
    brief = Path(args.brief).read_text(encoding="utf-8")
    out_dir = Path(args.out_dir)
    if out_dir.exists():
        import shutil; shutil.rmtree(out_dir)

    state = AgentState(
        project_root=PROJECT,
        bundle_writer=BundleWriter(out_dir=out_dir),
        xai_client=StubXaiImageClient(),
        brief=brief,
    )
    T0 = time.time()
    tool_counts: dict[str, int] = {}
    freeform_chunks: list[str] = []

    async def _stream_run(agent, input_text, label):
        """Run one agent to completion, log events, return RunResultStreaming."""
        log(f"=== stage: {label}", T0)
        r = Runner.run_streamed(
            agent, input=input_text, context=state, max_turns=args.max_turns,
        )
        async for event in r.stream_events():
            if type(event).__name__ != "RunItemStreamEvent":
                continue
            item = event.item
            it_name = type(item).__name__
            if it_name == "ToolCallItem":
                name = getattr(item.raw_item, "name", "?")
                tool_counts[name] = tool_counts.get(name, 0) + 1
                args_snippet = getattr(item.raw_item, "arguments", "")[:100]
                log(f"[{label}] CALL {name}  {args_snippet}", T0)
            elif it_name == "ToolCallOutputItem":
                out = str(item.output)[:180]
                marker = ""
                for m in ("REJECT", "VALIDATION_ERROR", "DIRTY", "MODERATION", "ERROR"):
                    if m in out:
                        marker = f" ← {m}"
                        break
                log(f"[{label}]   RESULT {out}{marker}", T0)
            elif it_name == "MessageOutputItem":
                raw = getattr(item, "raw_item", None)
                content = getattr(raw, "content", None) if raw else None
                text = ""
                if isinstance(content, str):
                    text = content
                elif isinstance(content, list):
                    for block in content:
                        t = getattr(block, "text", None)
                        if t:
                            text += t
                if text:
                    freeform_chunks.append(text)
                    log(f"[{label}] MSG ({len(text)} chars): {text[:80]!r}…", T0)
        return r

    if args.handoff_planner:
        # -----------------------------------------------------------------
        # Path D v2: 4-stage Python orchestration.
        #   Stage 1: skeleton_planner_agent → StoryPlan (structured JSON)
        #   Stage 2: Python asyncio.gather N parallel prose workers
        #   Stage 3: director_planner_agent → DirectorPlan (structured JSON)
        #   Stage 4: Python asyncio.gather anchor + shot render
        # No SDK handoff; each stage is its own Runner.run / helper call.
        # -----------------------------------------------------------------
        log(f"starting run (PLANNER v2); "
            f"skeleton_profile={args.director_profile}; "
            f"director_profile={args.director_profile}; "
            f"brief={args.brief}", T0)
        skeleton_agent = build_skeleton_planner_agent(
            cfg, project_root=PROJECT, profile=args.director_profile,
        )
        director_agent = build_director_planner_agent(
            cfg, project_root=PROJECT, profile=args.director_profile,
        )

        # Stage 1: skeleton_planner
        initial_input = (
            "# Brief\n\n" + brief.strip()
            + "\n\nEmit a complete StoryPlan JSON now."
        )
        sk_run = await _stream_run(skeleton_agent, initial_input, "skeleton")
        story_plan = sk_run.final_output
        if not isinstance(story_plan, StoryPlan):
            log(f"=== SKELETON ERROR: final_output type "
                f"{type(story_plan).__name__}, expected StoryPlan. "
                f"repr: {repr(story_plan)[:300]}", T0)
        else:
            log(f"=== SKELETON OK: {len(story_plan.beats)} beats, "
                f"{len(story_plan.characters)} characters", T0)
            (out_dir / "story_markdown.md").write_text(
                _compose_story_markdown(story_plan), encoding="utf-8",
            )
            (out_dir / "characters_markdown.md").write_text(
                _compose_characters_markdown(story_plan), encoding="utf-8",
            )
            state.story_emitted = True
            state.characters_emitted = True
            if state.characters_data is None:
                state.characters_data = {}

            # Stage 2: parallel prose workers
            log(f"=== stage: workers ({len(story_plan.beats)} beats, "
                f"Semaphore=5)", T0)
            sem = asyncio.Semaphore(5)

            async def _one_worker(b):
                async with sem:
                    prompt = _compose_worker_prompt(b, story_plan)
                    r = await _do_freeform_script_worker(
                        state, beat_id=b.id,
                        target_chars=b.target_word_count,
                        worker_prompt=prompt,
                    )
                    log(f"  worker[{b.id}] {r[:140]}", T0)
                    return r

            await asyncio.gather(
                *[_one_worker(b) for b in story_plan.beats],
                return_exceptions=True,
            )

            # Stage 3: director_planner
            director_input = _compose_director_input(story_plan)
            dr_run = await _stream_run(
                director_agent, director_input, "director",
            )
            dplan = dr_run.final_output
            if not isinstance(dplan, DirectorPlan):
                log(f"=== DIRECTOR ERROR: final_output type "
                    f"{type(dplan).__name__}, expected DirectorPlan. "
                    f"repr: {repr(dplan)[:300]}", T0)
            else:
                log(f"=== DIRECTOR OK: {len(dplan.anchors)} anchors, "
                    f"{len(dplan.shots)} shots", T0)

                # Stage 4: parallel anchors + shots
                log(f"=== rendering {len(dplan.anchors)} anchors in parallel",
                    T0)
                anchor_results = await asyncio.gather(
                    *[
                        _do_render_anchor(
                            state,
                            character_name=a.character_name,
                            anchor_type=a.anchor_type,
                            prompt=_compose_anchor_prompt(a.body),
                        )
                        for a in dplan.anchors
                    ],
                    return_exceptions=True,
                )
                for a, res in zip(dplan.anchors, anchor_results):
                    status = (
                        "OK" if isinstance(res, str) and res.startswith("OK")
                        else "ERR"
                    )
                    log(f"  ANCHOR[{status}] {a.character_name}:"
                        f"{a.anchor_type}  {str(res)[:120]}", T0)

                log(f"=== saving {len(dplan.shots)} shot prompts", T0)
                composed = [
                    (s, _compose_shot_final_prompt(s.body))
                    for s in dplan.shots
                ]
                for s, fp in composed:
                    res = _do_save_shot_prompt(
                        state, beat_id=s.beat_id, shot_id=s.shot_id,
                        final_prompt=fp, aspect_ratio=s.aspect_ratio,
                        anchor_ref=s.anchor_ref,
                    )
                    if not res.startswith("OK"):
                        log(f"  SAVE[ERR] {s.beat_id}/{s.shot_id}  "
                            f"{res[:120]}", T0)

                log(f"=== rendering {len(dplan.shots)} shot images in parallel",
                    T0)
                render_results = await asyncio.gather(
                    *[
                        _do_render_image(
                            state, beat_id=s.beat_id, shot_id=s.shot_id,
                            prompt=fp, aspect_ratio=s.aspect_ratio,
                            anchor_ref=s.anchor_ref,
                        )
                        for s, fp in composed
                    ],
                    return_exceptions=True,
                )
                ok_count = sum(
                    1 for r in render_results
                    if isinstance(r, str) and r.startswith("OK")
                )
                log(f"=== renders: {ok_count}/{len(dplan.shots)} OK", T0)
                for s, res in zip(dplan.shots, render_results):
                    if not (isinstance(res, str) and res.startswith("OK")):
                        log(f"  RENDER[ERR] {s.beat_id}/{s.shot_id}  "
                            f"{str(res)[:120]}", T0)
                state.finished = True
                state.finish_summary = (
                    f"PLANNER v2: {len(dplan.anchors)} anchors, "
                    f"{len(dplan.shots)} shots, {ok_count} rendered, "
                    f"{len(state.failed_shots)} failed"
                )
    else:
        # --- Legacy single-agent flow (minimal-combo, handoff-grok, etc.) ---
        if args.handoff_grok:
            agent = build_handoff_agents(
                cfg, project_root=PROJECT,
                skeleton_script_profile=args.ss_profile,
                director_profile=args.director_profile,
            )
            log(f"starting run (HANDOFF); ss_profile={args.ss_profile}; "
                f"director_profile={args.director_profile}; "
                f"brief={args.brief}; max_turns={args.max_turns}", T0)
        else:
            agent = build_main_agent(
                cfg, project_root=PROJECT, profile=args.profile,
                skip_director=args.skip_director, combo=args.combo,
                freeform=args.freeform, freeform_combo=args.freeform_combo,
                hybrid=args.hybrid, hybrid_combo=args.hybrid_combo,
                minimal_combo=args.minimal_combo,
            )
            log(f"starting run; profile={args.profile}; "
                f"skip_director={args.skip_director}; combo={args.combo}; "
                f"freeform={args.freeform}; "
                f"freeform_combo={args.freeform_combo}; "
                f"hybrid={args.hybrid}; hybrid_combo={args.hybrid_combo}; "
                f"brief={args.brief}; max_turns={args.max_turns}", T0)
        initial_input = (
            "# Brief\n\n" + brief.strip() + "\n\n"
            "Follow the workflow and emit a complete bundle."
        )
        await _stream_run(agent, initial_input, "main")
        if (args.freeform or args.freeform_combo) and freeform_chunks:
            out_path = out_dir / "freeform_output.md"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(
                "\n\n---\n\n".join(freeform_chunks), encoding="utf-8"
            )
            total_chars = sum(len(c) for c in freeform_chunks)
            log(f"=== FREEFORM OUTPUT written to {out_path} "
                f"({len(freeform_chunks)} chunks, {total_chars} chars total)",
                T0)

    log(f"=== DONE finished={state.finished}", T0)
    log(f"beats_with_prose={sorted(state.beats_with_prose)}", T0)
    log(f"beats_with_shots={sorted(state.beats_with_shots)}", T0)
    log(f"anchors={ {c: list(d) for c, d in state.anchors.items()} }", T0)
    log(f"failed_shots={state.failed_shots}", T0)
    log(f"tool_counts={tool_counts}", T0)

    # Audit prose word counts
    if state.story_data:
        log("=== PROSE WORD-COUNT AUDIT ===", T0)
        prose_dir = out_dir / "prose"
        for beat in state.story_data.get("beats", []):
            bid = beat["id"]
            target = beat.get("targetWordCount") or beat.get("target_word_count")
            f = prose_dir / f"{bid}.md"
            if not f.exists():
                log(f"  {bid}: MISSING prose", T0)
                continue
            text = f.read_text(encoding="utf-8")
            actual = len(text)
            if target:
                pct = int(actual / target * 100)
                low = int(target * 0.9)
                high = int(target * 1.1)
                ok = "✓" if low <= actual <= high else "✗"
                log(f"  {ok} {bid}: {actual}/{target} ({pct}%, window [{low}, {high}])", T0)
            else:
                log(f"  ? {bid}: {actual} chars (no target)", T0)

    # Audit characters
    if state.characters_data:
        log("=== CHARACTERS AUDIT ===", T0)
        for cname, c in state.characters_data.items():
            states = c.get("wardrobe_states", {})
            for sname, ws in states.items():
                for item in ws.get("items", []):
                    has_visual = bool(item.get("visual_description", "").strip())
                    has_covers = "covers" in item
                    mark = "✓" if has_visual else "✗"
                    log(f"  {mark} {cname}.{sname}.{item['name']}  "
                        f"visual_description={'Y' if has_visual else 'N'}  "
                        f"covers={item.get('covers', [])}", T0)

asyncio.run(main())
