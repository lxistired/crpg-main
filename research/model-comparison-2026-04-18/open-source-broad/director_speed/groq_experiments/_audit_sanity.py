#!/usr/bin/env python3
"""Sanity check: run audit against existing GOOD and BAD files."""
import pathlib, json
import sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from runner import audit_vgai

base = pathlib.Path("/Users/lxxxxxx/个人项目/crpg/research/model-comparison-2026-04-18/open-source-broad/director_speed")

for f in ["kimi-k2-0905-run1.json", "kimi-k2-0905-run2.json"]:
    p = base / f
    content = p.read_text(encoding="utf-8")
    viols, n, ok, shots = audit_vgai(content)
    out = {
        "file": f,
        "parse_ok": ok,
        "n_shots": n,
        "violation_count": len(viols),
        "violations": viols,
    }
    outp = pathlib.Path(__file__).parent / f"_sanity_{f.replace('.json','')}.json"
    outp.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{f}: parse_ok={ok} n_shots={n} violations={len(viols)}")
