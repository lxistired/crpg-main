#!/usr/bin/env python3
"""Run VGAI test: 22 shots concurrently. No anchor (cleaner test)."""
import asyncio, base64, json, pathlib, time, sys, httpx

ROOT = pathlib.Path("/Users/lxxxxxx/个人项目/crpg")
TEST = ROOT / "research/pipeline-simulation/vgating-test"
SHOTS_DIR = TEST / "shots"
ENV = ROOT / ".env.local"
ENDPOINT = "https://api.x.ai/v1/images/generations"

sys.path.insert(0, str(TEST))
from shots_vgating import SHOTS, build_prompt


def load_key():
    for l in ENV.read_text().splitlines():
        if l.strip().startswith("GROK_API_KEY="):
            return l.split("=", 1)[1].strip().strip("'").strip('"')


async def gen(client, key, sid, frame_key, attr_keys, sem):
    async with sem:
        aspect = "1:1" if "ecu" in frame_key and "leg_ecu" not in frame_key and "feet_ecu" not in frame_key and "hand_ecu" not in frame_key else "16:9"
        if "full_body" in frame_key:
            aspect = "9:16"  # vertical for full body
        payload = {
            "model": "grok-imagine-image-pro",
            "prompt": build_prompt(frame_key, attr_keys),
            "n": 1,
            "response_format": "b64_json",
            "aspect_ratio": aspect,
            "resolution": "2k",
        }
        t0 = time.time()
        last_err = None
        for attempt in range(4):
            try:
                r = await client.post(
                    ENDPOINT, json=payload,
                    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                    timeout=240,
                )
                r.raise_for_status()
                body = r.json()
                img = base64.b64decode(body["data"][0]["b64_json"])
                out = SHOTS_DIR / f"{sid}.png"
                out.write_bytes(img)
                elapsed = round(time.time() - t0, 1)
                print(f"  ✓ {sid:<35} {elapsed}s, {len(img)/1e6:.1f}MB (try {attempt+1})")
                return {"id": sid, "status": "ok", "elapsed": elapsed, "attempts": attempt + 1}
            except Exception as e:
                last_err = str(e).replace(key, "***")[:300]
                if attempt < 3:
                    await asyncio.sleep(3 * (attempt + 1))
        print(f"  ✗ {sid:<35} FAIL: {last_err[:80]}")
        return {"id": sid, "status": "fail", "error": last_err}


async def main():
    SHOTS_DIR.mkdir(exist_ok=True)
    key = load_key()
    sem = asyncio.Semaphore(8)
    async with httpx.AsyncClient() as client:
        t0 = time.time()
        print(f"[{time.strftime('%H:%M:%S')}] Launching {len(SHOTS)} VGAI shots (concurrency 8)...")
        results = await asyncio.gather(*(
            gen(client, key, sid, fk, ak, sem) for sid, fk, ak in SHOTS
        ))
        elapsed = round(time.time() - t0, 1)
        ok = sum(1 for r in results if r["status"] == "ok")
        fail = sum(1 for r in results if r["status"] == "fail")
        (TEST / "run-log.json").write_text(json.dumps({
            "elapsed_sec": elapsed, "ok": ok, "fail": fail, "cost_usd": round(len(SHOTS)*0.07, 2),
            "results": results,
        }, indent=2))
        print(f"\n[{time.strftime('%H:%M:%S')}] Done in {elapsed}s — OK {ok}/{len(SHOTS)}, FAIL {fail}, cost ${round(len(SHOTS)*0.07,2)}")


if __name__ == "__main__":
    asyncio.run(main())
