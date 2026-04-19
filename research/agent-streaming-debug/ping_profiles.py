"""Ping every PROFILES endpoint with a minimal prompt.

Measures connectivity + TTFT + total time per profile. Does NOT use the
agents SDK — raw openai streaming call is enough to prove auth + network
work and to compare basic latency before spawning heavy concurrent tests.

Usage:
  .venv/bin/python research/agent-streaming-debug/ping_profiles.py
"""
from __future__ import annotations

import asyncio
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

PROJECT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT / "src"))
load_dotenv(PROJECT / ".env")

import httpx
from openai import AsyncOpenAI

from crpg.agent.main_agent import PROFILES


PROMPT = "Reply with a single word: pong."


async def ping(profile: str, cfg: dict) -> dict:
    """Ping a profile: first streaming for TTFT, then a non-stream call as
    authoritative proof the endpoint works. Captures both `delta.content`
    and `delta.reasoning_content` (some thinking models stream reasoning in
    the latter field while `content` stays empty)."""
    api_key = os.environ.get(cfg["api_key_env"])
    if not api_key:
        return {
            "profile": profile,
            "ok": False,
            "err": f"missing env var {cfg['api_key_env']}",
        }
    timeout = httpx.Timeout(connect=10.0, read=60.0, write=10.0, pool=10.0)
    client = AsyncOpenAI(
        api_key=api_key,
        base_url=cfg["base_url"],
        timeout=timeout,
    )

    # --- STREAM pass for TTFT ---
    t0 = time.perf_counter()
    ttft = None
    reasoning_ttft = None
    content_chunks = 0
    reasoning_chunks = 0
    text = []
    stream_err = None
    try:
        stream = await client.chat.completions.create(
            model=cfg["model_id"],
            messages=[{"role": "user", "content": PROMPT}],
            max_tokens=32,
            temperature=0.0,
            stream=True,
        )
        async for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            if not delta:
                continue
            if delta.content:
                if ttft is None:
                    ttft = time.perf_counter() - t0
                text.append(delta.content)
                content_chunks += 1
            rc = getattr(delta, "reasoning_content", None) or getattr(
                delta, "reasoning", None
            )
            if rc:
                if reasoning_ttft is None:
                    reasoning_ttft = time.perf_counter() - t0
                reasoning_chunks += 1
        stream_elapsed = time.perf_counter() - t0
    except Exception as e:
        stream_elapsed = time.perf_counter() - t0
        stream_err = f"{type(e).__name__}: {str(e)[:160]}"

    # --- NON-STREAM pass as authoritative connectivity probe ---
    t1 = time.perf_counter()
    ns_err = None
    ns_text = ""
    ns_reasoning = ""
    try:
        resp = await client.chat.completions.create(
            model=cfg["model_id"],
            messages=[{"role": "user", "content": PROMPT}],
            max_tokens=32,
            temperature=0.0,
        )
        msg = resp.choices[0].message
        ns_text = (msg.content or "").strip()
        ns_reasoning = (
            getattr(msg, "reasoning_content", None)
            or getattr(msg, "reasoning", None)
            or ""
        ).strip()
    except Exception as e:
        ns_err = f"{type(e).__name__}: {str(e)[:160]}"
    ns_elapsed = time.perf_counter() - t1

    if stream_err and ns_err:
        return {
            "profile": profile,
            "ok": False,
            "model": cfg["model_id"],
            "err": f"stream: {stream_err} | non-stream: {ns_err}",
        }
    return {
        "profile": profile,
        "ok": True,
        "model": cfg["model_id"],
        "ttft_s": round(ttft, 3) if ttft is not None else None,
        "reasoning_ttft_s": round(reasoning_ttft, 3)
        if reasoning_ttft is not None
        else None,
        "stream_total_s": round(stream_elapsed, 3),
        "content_chunks": content_chunks,
        "reasoning_chunks": reasoning_chunks,
        "text": "".join(text).strip()[:50],
        "ns_total_s": round(ns_elapsed, 3),
        "ns_text": ns_text[:50],
        "ns_reasoning_len": len(ns_reasoning),
        "stream_err": stream_err,
        "ns_err": ns_err,
    }


async def main() -> None:
    print(f"Pinging {len(PROFILES)} profiles with prompt: {PROMPT!r}\n", flush=True)
    tasks = [ping(p, cfg) for p, cfg in PROFILES.items()]
    results = await asyncio.gather(*tasks)

    print(f"{'profile':<22} {'status':<6} {'model':<42}")
    print("-" * 70)
    for r in results:
        if not r["ok"]:
            print(f"{r['profile']:<22} FAIL   {r.get('model','?'):<42}")
            print(f"    err: {r.get('err')}")
            continue
        print(f"{r['profile']:<22} OK     {r['model']:<42}")
        c_ttft = r.get("ttft_s")
        r_ttft = r.get("reasoning_ttft_s")
        print(
            f"    stream: content_ttft={c_ttft}s  reasoning_ttft={r_ttft}s  "
            f"total={r['stream_total_s']}s  "
            f"content_chunks={r['content_chunks']}  "
            f"reasoning_chunks={r['reasoning_chunks']}"
        )
        print(
            f"    non-stream: total={r['ns_total_s']}s  "
            f"content={r['ns_text']!r}  reasoning_chars={r['ns_reasoning_len']}"
        )
        if r.get("stream_err"):
            print(f"    stream_err: {r['stream_err']}")
        if r.get("ns_err"):
            print(f"    ns_err: {r['ns_err']}")


if __name__ == "__main__":
    asyncio.run(main())
