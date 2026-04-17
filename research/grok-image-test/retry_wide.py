#!/usr/bin/env python3
"""Retry scenes 2 and 5 with a supported ultrawide aspect ratio (19.5:9)."""
import base64, json, pathlib, time, urllib.request, urllib.error, sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from generate import SCENES, ENDPOINT, MODEL, ROOT, load_key, call_api

def main():
    api_key = load_key()
    # Scenes that failed with 21:9 — switch to 19.5:9
    targets = [(2, SCENES[1]), (5, SCENES[4])]
    extra = []
    for i, scene in targets:
        scene = dict(scene)
        scene["aspect_ratio"] = "19.5:9"
        out_path = ROOT / f"scene-{i}-{scene['slug']}.png"
        print(f"[retry {i}] {scene['slug']} @ 19.5:9")
        last_err = None
        for attempt in range(1, 4):
            t0 = time.time()
            data, err = call_api(api_key, scene["prompt"], scene["aspect_ratio"])
            elapsed = time.time() - t0
            if err:
                last_err = err
                print(f"  attempt {attempt}: {err[:220]}")
                time.sleep(2)
                continue
            b64 = data["data"][0].get("b64_json")
            img_bytes = base64.b64decode(b64)
            out_path.write_bytes(img_bytes)
            cost = data.get("usage", {}).get("cost_in_usd_ticks", 0)
            print(f"  OK {out_path.name} ({len(img_bytes)//1024} KB, {elapsed:.1f}s, cost_ticks={cost})")
            extra.append({
                "scene_index": i, "slug": scene["slug"], "file": out_path.name,
                "bytes": len(img_bytes), "elapsed_sec": round(elapsed, 2),
                "cost_ticks": cost, "attempts": attempt,
                "aspect_ratio": "19.5:9", "status": "success",
                "revised_prompt": data["data"][0].get("revised_prompt", ""),
            })
            break

    # merge into existing log
    log_path = ROOT / "generation-log.json"
    log = json.loads(log_path.read_text())
    # Replace failed entries with successful ones by scene_index
    by_idx = {e["scene_index"]: e for e in log["entries"]}
    for e in extra:
        by_idx[e["scene_index"]] = e
    log["entries"] = sorted(by_idx.values(), key=lambda e: e["scene_index"])
    log["total_cost_ticks"] = sum(e.get("cost_ticks", 0) for e in log["entries"] if e.get("status") == "success")
    log["total_cost_usd"] = log["total_cost_ticks"] / 1e10
    log_path.write_text(json.dumps(log, indent=2, ensure_ascii=False))
    print(f"\nTotal cost so far: ${log['total_cost_usd']:.4f}")

if __name__ == "__main__":
    main()
