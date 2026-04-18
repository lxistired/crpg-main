#!/usr/bin/env python3
"""Phase 2: stress-test the winners at temp=0.7 (production setting).

Only exp4 (strong suffix) and exp6 (few-shot) passed clean. We need to verify
they hold at temp=0.7 (realistic production temp) — not just temp=0.
Also try the combined form (strong suffix + few-shot).
"""
import asyncio, pathlib, time, json, httpx, datetime
import sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from runner import call, audit_vgai, STRONG_SUFFIX, FEW_SHOT_SUFFIX, OUT

async def run_one(client, label, extra_payload, extra_system):
    return await call(client, label, extra_payload, extra_system)

async def main():
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    jobs_spec = []
    # exp7: strong_suffix at temp=0.7  x 4
    for i in range(1, 5):
        jobs_spec.append((f"exp7_strong_t07_iter{i}",
                          {"temperature": 0.7}, STRONG_SUFFIX))
    # exp8: few_shot at temp=0.7  x 4
    for i in range(1, 5):
        jobs_spec.append((f"exp8_fewshot_t07_iter{i}",
                          {"temperature": 0.7}, FEW_SHOT_SUFFIX))
    # exp9: combined strong+fewshot at temp=0.7  x 4
    for i in range(1, 5):
        jobs_spec.append((f"exp9_combined_t07_iter{i}",
                          {"temperature": 0.7}, STRONG_SUFFIX + FEW_SHOT_SUFFIX))

    limits = httpx.Limits(max_connections=20, max_keepalive_connections=20)
    async with httpx.AsyncClient(limits=limits) as client:
        jobs = [run_one(client, lbl, ep, es) for lbl, ep, es in jobs_spec]
        results = await asyncio.gather(*jobs)

    summary = []
    for r in results:
        lbl = r["label"]
        raw_path = OUT / f"{lbl}_{ts}.json"
        if r.get("ok"):
            content = r["content"]
            viols, n, ok, _ = audit_vgai(content)
            (OUT / f"{lbl}_{ts}_content.txt").write_text(content, encoding="utf-8")
            meta = {k: v for k, v in r.items() if k != "content"}
            meta["violations"] = viols
            meta["violation_count"] = len(viols)
            meta["n_shots"] = n
            meta["parse_ok"] = ok
            raw_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
            summary.append({
                "label": lbl,
                "ok": True,
                "elapsed": round(r["elapsed"], 2),
                "completion_tokens": r.get("completion_tokens"),
                "parse_ok": ok,
                "n_shots": n,
                "violation_count": len(viols),
                "violation_types": sorted({v["type"] for v in viols}),
            })
        else:
            raw_path.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
            summary.append({
                "label": lbl, "ok": False,
                "elapsed": round(r.get("elapsed", 0), 2),
                "status": r.get("status"),
                "error": str(r.get("error",""))[:200],
            })

    (OUT / f"_summary2_{ts}.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Phase 2 summary: _summary2_{ts}.json  ({len(summary)} results)")

if __name__ == "__main__":
    asyncio.run(main())
