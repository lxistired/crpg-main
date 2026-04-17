#!/usr/bin/env python3
"""Pipeline simulation Stage 3 — Concurrent Grok Imagine generation.

Reads merged stage2-prompts.json (anchor + 19 shots).
Stage A: Generate anchor image first (serial).
Stage B: All 19 shots in parallel (asyncio + semaphore).

Anchor applied as image_url for shots marked use_anchor=true.
No anchor for the others (text-to-image only).

Concurrency limited to 8 to avoid xAI rate limits.
API key never echoed. Failed shots logged with redacted errors.
"""
import asyncio
import base64
import json
import pathlib
import time
from typing import Any

import httpx

ROOT = pathlib.Path("/Users/lxxxxxx/个人项目/crpg/research/pipeline-simulation")
SHOTS_DIR = ROOT / "shots"
ENV_FILE = pathlib.Path("/Users/lxxxxxx/个人项目/crpg/.env.local")
ENDPOINT = "https://api.x.ai/v1/images/generations"

MAX_CONCURRENCY = 8  # xAI rate limit unknown, keep conservative
TIMEOUT_SECONDS = 180
MAX_RETRIES = 3


def load_key() -> str:
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line.startswith("GROK_API_KEY="):
            return line.split("=", 1)[1].strip().strip("'").strip('"')
    raise RuntimeError("GROK_API_KEY not found")


def normalize_shot(shot: dict) -> dict:
    """Normalize shot fields across different agents' JSON schemas."""
    normalized = dict(shot)
    # Some agents used 'image_prompt' instead of 'prompt'
    if "prompt" not in normalized and "image_prompt" in normalized:
        normalized["prompt"] = normalized.pop("image_prompt")
    # Default resolution and model if missing
    normalized.setdefault("resolution", "2k")
    normalized.setdefault("model", "grok-imagine-image-pro")
    normalized.setdefault("use_anchor", False)
    # Guard against unsupported 21:9
    if normalized.get("aspect_ratio") == "21:9":
        normalized["aspect_ratio"] = "19.5:9"
    return normalized


def load_merged_prompts() -> dict:
    """Merge 5 per-node stage2 prompts files into one dict."""
    merged = {"anchor": None, "shots": []}
    node_files = [
        "stage2-prompts-act1_start.json",
        "stage2-prompts-act1_choice.json",
        "stage2-prompts-branchA2_scene1.json",
        "stage2-prompts-branchB_scene1.json",
        "stage2-prompts-branchB_scene2.json",
    ]
    for fn in node_files:
        path = ROOT / fn
        if not path.exists():
            raise FileNotFoundError(f"Missing {path}")
        data = json.loads(path.read_text())
        if "anchor" in data and data["anchor"]:
            merged["anchor"] = normalize_shot(data["anchor"])
        if "shots" in data:
            for s in data["shots"]:
                merged["shots"].append(normalize_shot(s))
    assert merged["anchor"] is not None, "anchor missing from act1_start file"
    assert len(merged["shots"]) == 19, f"expected 19 shots, got {len(merged['shots'])}"
    # sanity: every shot has a prompt
    for s in merged["shots"]:
        assert "prompt" in s, f"shot {s.get('shot_id')} missing prompt"
    return merged


async def call_grok_imagine(
    client: httpx.AsyncClient,
    key: str,
    prompt: str,
    aspect_ratio: str,
    resolution: str,
    model: str,
    image_url: str | None = None,
    attempt: int = 1,
) -> dict:
    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "n": 1,
        "response_format": "b64_json",
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
    }
    if image_url:
        payload["image_url"] = image_url

    try:
        resp = await client.post(
            ENDPOINT,
            json=payload,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            timeout=TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
        body = resp.json()
        return {"ok": True, "body": body}
    except httpx.HTTPStatusError as e:
        err_body = e.response.text.replace(key, "***REDACTED***")
        if attempt < MAX_RETRIES:
            await asyncio.sleep(2 * attempt)
            return await call_grok_imagine(
                client, key, prompt, aspect_ratio, resolution, model, image_url, attempt + 1
            )
        return {"ok": False, "status": e.response.status_code, "error": err_body[:1000]}
    except Exception as e:
        if attempt < MAX_RETRIES:
            await asyncio.sleep(2 * attempt)
            return await call_grok_imagine(
                client, key, prompt, aspect_ratio, resolution, model, image_url, attempt + 1
            )
        return {"ok": False, "status": 0, "error": str(e).replace(key, "***REDACTED***")[:1000]}


async def process_shot(
    sem: asyncio.Semaphore,
    client: httpx.AsyncClient,
    key: str,
    shot: dict,
    anchor_data_uri: str | None,
) -> dict:
    async with sem:
        t0 = time.time()
        image_url = anchor_data_uri if shot.get("use_anchor") else None
        result = await call_grok_imagine(
            client,
            key,
            shot["prompt"],
            shot["aspect_ratio"],
            shot["resolution"],
            shot["model"],
            image_url=image_url,
        )
        elapsed = time.time() - t0

        if not result["ok"]:
            return {
                "shot_id": shot["shot_id"],
                "status": "failed",
                "error": result.get("error"),
                "http_status": result.get("status"),
                "elapsed_sec": round(elapsed, 2),
            }

        body = result["body"]
        img_b64 = body["data"][0]["b64_json"]
        out_path = SHOTS_DIR / f"{shot['shot_id']}.png"
        out_path.write_bytes(base64.b64decode(img_b64))
        return {
            "shot_id": shot["shot_id"],
            "node_id": shot.get("node_id", "anchor" if "anchor" in shot["shot_id"] else "?"),
            "status": "success",
            "file": str(out_path.name),
            "bytes": out_path.stat().st_size,
            "elapsed_sec": round(elapsed, 2),
            "use_anchor": shot.get("use_anchor", False),
            "cost_ticks": body["data"][0].get("cost"),
        }


async def main() -> None:
    SHOTS_DIR.mkdir(parents=True, exist_ok=True)
    key = load_key()
    merged = load_merged_prompts()

    t_start = time.time()

    async with httpx.AsyncClient(http2=False) as client:
        # Stage A: generate anchor (skip if already exists on disk)
        anchor = merged["anchor"]
        anchor_path = SHOTS_DIR / f"{anchor['shot_id']}.png"
        if anchor_path.exists() and anchor_path.stat().st_size > 100_000:
            print(f"[{time.strftime('%H:%M:%S')}] Anchor already exists, reusing {anchor_path.name}")
            anchor_result = {
                "shot_id": anchor["shot_id"],
                "status": "success",
                "file": anchor_path.name,
                "bytes": anchor_path.stat().st_size,
                "elapsed_sec": 0,
                "reused": True,
            }
        else:
            print(f"[{time.strftime('%H:%M:%S')}] Stage A: generating anchor...")
            sem_anchor = asyncio.Semaphore(1)
            anchor_result = await process_shot(sem_anchor, client, key, anchor, None)
            if anchor_result["status"] != "success":
                print(f"Anchor failed: {anchor_result}")
                (ROOT / "stage3-generation-log.json").write_text(
                    json.dumps({"anchor": anchor_result, "shots": []}, indent=2, ensure_ascii=False)
                )
                return
            print(f"[{time.strftime('%H:%M:%S')}] Anchor done in {anchor_result['elapsed_sec']}s ({anchor_result['bytes']} bytes)")

        # Read anchor as base64 data URI for image-to-image
        anchor_bytes = (SHOTS_DIR / f"{anchor['shot_id']}.png").read_bytes()
        anchor_b64 = base64.b64encode(anchor_bytes).decode()
        anchor_data_uri = f"data:image/png;base64,{anchor_b64}"

        # Stage B: all 19 shots in parallel
        print(f"[{time.strftime('%H:%M:%S')}] Stage B: launching {len(merged['shots'])} shots with concurrency {MAX_CONCURRENCY}...")
        sem = asyncio.Semaphore(MAX_CONCURRENCY)
        tasks = [process_shot(sem, client, key, shot, anchor_data_uri) for shot in merged["shots"]]
        results = await asyncio.gather(*tasks)

    t_total = time.time() - t_start

    # Write log
    log = {
        "anchor": anchor_result,
        "shots": results,
        "total_elapsed_sec": round(t_total, 2),
        "max_concurrency": MAX_CONCURRENCY,
        "success_count": sum(1 for r in results if r["status"] == "success"),
        "fail_count": sum(1 for r in results if r["status"] == "failed"),
        "anchor_use_count": sum(1 for r in results if r.get("use_anchor")),
    }
    (ROOT / "stage3-generation-log.json").write_text(
        json.dumps(log, indent=2, ensure_ascii=False)
    )

    print()
    print(f"[{time.strftime('%H:%M:%S')}] Done. Total wall-clock: {t_total:.1f}s")
    print(f"  Success: {log['success_count']}/{len(results)}")
    print(f"  Failed:  {log['fail_count']}")
    print(f"  Saved to: {SHOTS_DIR}")


if __name__ == "__main__":
    asyncio.run(main())
