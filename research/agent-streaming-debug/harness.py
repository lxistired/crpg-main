"""Live agent run with event streaming so we see every tool call in real time."""
import asyncio, os, sys, time
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, "/Users/lxxxxxx/个人项目/crpg/src")
load_dotenv("/Users/lxxxxxx/个人项目/crpg/.env")

from agents import Runner, set_tracing_disabled
set_tracing_disabled(True)

from crpg.agent.main_agent import build_main_agent
from crpg.agent.state import AgentState
from crpg.bundle import BundleWriter
from crpg.config import load_config
from crpg.llm.xai import XaiImageClient

def log(msg):
    print(f"[T+{time.time()-T0:.1f}s] {msg}", file=sys.stderr, flush=True)

T0 = time.time()

async def main():
    cfg = load_config()
    brief = (Path("/Users/lxxxxxx/个人项目/crpg/tests/fixtures/demo_brief.md")
             .read_text(encoding="utf-8"))
    out_dir = Path("/Users/lxxxxxx/个人项目/crpg/bundles/e2e-agent-2026-04-18")
    if out_dir.exists():
        import shutil; shutil.rmtree(out_dir)

    state = AgentState(
        project_root=Path("/Users/lxxxxxx/个人项目/crpg"),
        bundle_writer=BundleWriter(out_dir=out_dir),
        xai_client=XaiImageClient(api_key=cfg.xai_key, endpoint=cfg.xai_endpoint),
        brief=brief,
    )
    agent = build_main_agent(cfg)
    log("starting streaming run")

    run = Runner.run_streamed(
        agent,
        input="Begin. Read the brief, follow the workflow, emit a complete bundle.",
        context=state,
        max_turns=300,
    )
    async for event in run.stream_events():
        et = type(event).__name__
        if et == "RunItemStreamEvent":
            item = event.item
            it_name = type(item).__name__
            if it_name == "ToolCallItem":
                name = getattr(item.raw_item, "name", "?")
                args = getattr(item.raw_item, "arguments", "")
                log(f"CALL {name}  args={args[:120]}")
            elif it_name == "ToolCallOutputItem":
                out = str(item.output)[:150]
                log(f"RESULT {out}")
            elif it_name == "MessageOutputItem":
                try:
                    txt = item.raw_item.content[0].text
                    # Skip giant prose (written to disk anyway); only snippet
                    log(f"MSG {txt[:100]}...")
                except Exception:
                    pass
        elif et == "RawResponsesStreamEvent":
            # Too noisy; skip
            pass

    log(f"DONE finished={state.finished} beats_prose={len(state.beats_with_prose)} "
        f"beats_shots={len(state.beats_with_shots)} imgs={state.images_rendered}")
    if state.finish_summary:
        log(f"SUMMARY {state.finish_summary}")

asyncio.run(main())
