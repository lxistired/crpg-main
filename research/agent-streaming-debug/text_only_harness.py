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

from crpg.agent.main_agent import build_main_agent
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
    agent = build_main_agent(cfg)
    T0 = time.time()
    log(f"starting text-only run; brief={args.brief}; max_turns={args.max_turns}", T0)

    run = Runner.run_streamed(
        agent,
        input="Begin. Read the brief, follow the workflow, emit a complete bundle.",
        context=state,
        max_turns=args.max_turns,
    )
    tool_counts: dict[str, int] = {}
    async for event in run.stream_events():
        if type(event).__name__ != "RunItemStreamEvent":
            continue
        item = event.item
        it_name = type(item).__name__
        if it_name == "ToolCallItem":
            name = getattr(item.raw_item, "name", "?")
            tool_counts[name] = tool_counts.get(name, 0) + 1
            args_snippet = getattr(item.raw_item, "arguments", "")[:100]
            log(f"CALL {name}  {args_snippet}", T0)
        elif it_name == "ToolCallOutputItem":
            out = str(item.output)[:180]
            # highlight failures / rejections
            marker = ""
            for m in ("REJECT", "VALIDATION_ERROR", "DIRTY", "MODERATION", "ERROR"):
                if m in out:
                    marker = f" ← {m}"
                    break
            log(f"  RESULT {out}{marker}", T0)

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
