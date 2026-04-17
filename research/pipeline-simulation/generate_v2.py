#!/usr/bin/env python3
"""Stage 3 v2 — concurrent generation of 12 medium-heavy shots. Reuses v1 anchor."""
import asyncio, base64, json, pathlib, time, httpx

ROOT = pathlib.Path("/Users/lxxxxxx/个人项目/crpg/research/pipeline-simulation")
SHOTS_V2 = ROOT / "shots-v2"
SHOTS_V1 = ROOT / "shots"
ENV = pathlib.Path("/Users/lxxxxxx/个人项目/crpg/.env.local")
ENDPOINT = "https://api.x.ai/v1/images/generations"

def load_key():
    for l in ENV.read_text().splitlines():
        if l.strip().startswith("GROK_API_KEY="):
            return l.split("=", 1)[1].strip().strip("'").strip('"')

async def gen(client, key, shot, anchor_uri, sem):
    async with sem:
        ar = shot["aspect_ratio"].replace("21:9", "19.5:9")
        payload = {
            "model": shot.get("model", "grok-imagine-image-pro"),
            "prompt": shot["prompt"],
            "n": 1,
            "response_format": "b64_json",
            "aspect_ratio": ar,
            "resolution": shot.get("resolution", "2k"),
        }
        if shot.get("use_anchor"):
            payload["image_url"] = anchor_uri
        t0 = time.time()
        for attempt in range(3):
            try:
                r = await client.post(
                    ENDPOINT, json=payload,
                    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                    timeout=180,
                )
                r.raise_for_status()
                body = r.json()
                img = base64.b64decode(body["data"][0]["b64_json"])
                out = SHOTS_V2 / f"{shot['shot_id']}.png"
                out.write_bytes(img)
                return {"shot_id": shot["shot_id"], "status": "ok", "bytes": len(img), "elapsed": round(time.time() - t0, 1), "attempt": attempt + 1}
            except Exception as e:
                if attempt == 2:
                    return {"shot_id": shot["shot_id"], "status": "fail", "error": str(e).replace(key, "***")[:300], "elapsed": round(time.time() - t0, 1)}
                await asyncio.sleep(2 * (attempt + 1))

async def main():
    SHOTS_V2.mkdir(exist_ok=True)
    key = load_key()
    anchor_bytes = (SHOTS_V1 / "anchor_00.png").read_bytes()
    anchor_uri = "data:image/png;base64," + base64.b64encode(anchor_bytes).decode()
    (SHOTS_V2 / "anchor_00.png").write_bytes(anchor_bytes)
    shots = json.loads((ROOT / "stage2-prompts-v2.json").read_text())["shots"]
    print(f"[{time.strftime('%H:%M:%S')}] Launching {len(shots)} shots with concurrency 8 (anchor reused from v1)")
    sem = asyncio.Semaphore(8)
    async with httpx.AsyncClient() as client:
        t0 = time.time()
        results = await asyncio.gather(*[gen(client, key, s, anchor_uri, sem) for s in shots])
        total = time.time() - t0
    log = {
        "total_sec": round(total, 1),
        "shots": results,
        "ok": sum(1 for r in results if r["status"] == "ok"),
        "fail": sum(1 for r in results if r["status"] == "fail"),
    }
    (ROOT / "stage3-v2-log.json").write_text(json.dumps(log, indent=2, ensure_ascii=False))
    print(f"[{time.strftime('%H:%M:%S')}] Done in {total:.1f}s — ok={log['ok']} fail={log['fail']}")

if __name__ == "__main__":
    asyncio.run(main())
