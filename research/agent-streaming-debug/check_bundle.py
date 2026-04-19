"""Auto quality check for a completed crpg bundle. Reads bundle directory +
log, produces a compact JSON-like report: outcome / wall time / tool counts
/ prose per-beat CJK % / Director quality / Style Preamble presence / etc.

Usage:
  .venv/bin/python research/agent-streaming-debug/check_bundle.py \
      /tmp/crpg-text-<profile> /tmp/crpg-text-<profile>.log
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CJK = re.compile(r"[\u4e00-\u9fff]")
STYLE_PREAMBLE_SIGNATURE = "seinen manga / anime illustration"  # 足够唯一


def cjk_count(text: str) -> int:
    return len(CJK.findall(text))


def parse_log(log_path: Path) -> dict:
    if not log_path.exists():
        return {"log_missing": True}
    text = log_path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    tool_counts: dict[str, int] = {}
    rejects = 0
    dirty = 0
    validation_errors = 0
    moderation = 0
    errors = 0
    done_finished = None
    freeform_msg_count = 0
    freeform_msg_chars = 0
    first_ts = None
    last_ts = None
    stack_trace = any("Traceback" in l for l in lines)

    for ln in lines:
        m = re.search(r"\[T\+([0-9.]+)s\]", ln)
        if m:
            ts = float(m.group(1))
            if first_ts is None:
                first_ts = ts
            last_ts = ts
        if "CALL " in ln:
            m2 = re.search(r"CALL (\S+)", ln)
            if m2:
                tool_counts[m2.group(1)] = tool_counts.get(m2.group(1), 0) + 1
        if "REJECT" in ln:
            rejects += 1
        if "DIRTY" in ln:
            dirty += 1
        if "VALIDATION_ERROR" in ln:
            validation_errors += 1
        if "MODERATION" in ln:
            moderation += 1
        if "ERROR" in ln and "RESULT" in ln:
            errors += 1
        if "=== DONE finished=" in ln:
            done_finished = "True" in ln
        if "MSG (" in ln:
            m3 = re.search(r"MSG \((\d+) chars\)", ln)
            if m3:
                freeform_msg_count += 1
                freeform_msg_chars += int(m3.group(1))

    return {
        "wall_time_s": round((last_ts or 0) - (first_ts or 0), 1),
        "first_ts": first_ts,
        "last_ts": last_ts,
        "done_finished": done_finished,
        "stack_trace": stack_trace,
        "tool_counts": tool_counts,
        "rejects": rejects,
        "dirty": dirty,
        "validation_errors": validation_errors,
        "moderation": moderation,
        "errors": errors,
        "freeform_msg_count": freeform_msg_count,
        "freeform_msg_chars": freeform_msg_chars,
    }


def audit_bundle(bundle_dir: Path) -> dict:
    out: dict = {}
    # prose
    prose_dir = bundle_dir / "prose"
    prose: dict[str, dict] = {}
    if prose_dir.exists():
        for md in sorted(prose_dir.glob("*.md")):
            content = md.read_text(encoding="utf-8", errors="replace")
            prose[md.stem] = {
                "cjk_chars": cjk_count(content),
                "raw_bytes": len(content.encode("utf-8")),
            }
    out["prose"] = prose

    # freeform_output.md — structural sections
    ff_path = bundle_dir / "freeform_output.md"
    if ff_path.exists():
        ff = ff_path.read_text(encoding="utf-8", errors="replace")
        out["freeform_output"] = {
            "chars": len(ff),
            "has_story": bool(re.search(r"^# Story\b", ff, re.M)),
            "has_characters": bool(re.search(r"^# Characters\b", ff, re.M)),
            "has_shots": bool(re.search(r"shot\b|Shots", ff, re.I)),
            "has_end_of_bundle": "# End of Bundle" in ff,
            "style_preamble_count": ff.count(STYLE_PREAMBLE_SIGNATURE),
        }
    else:
        out["freeform_output"] = {"missing": True}

    # story.json
    sj = bundle_dir / "story.json"
    if sj.exists():
        try:
            story = json.loads(sj.read_text(encoding="utf-8"))
            beats = story.get("beats", [])
            out["story"] = {
                "beats": [b.get("id") for b in beats],
                "targets": {b.get("id"): b.get("targetWordCount") or b.get("target_word_count") for b in beats},
            }
        except Exception as e:
            out["story"] = {"parse_error": str(e)[:100]}
    else:
        out["story"] = {"missing": True}

    # characters.json
    cj = bundle_dir / "characters.json"
    if cj.exists():
        try:
            chars = json.loads(cj.read_text(encoding="utf-8"))
            if isinstance(chars, dict):
                out["characters"] = list(chars.keys())
            elif isinstance(chars, list):
                out["characters"] = [c.get("name", "?") for c in chars]
        except Exception:
            out["characters"] = {"parse_error": True}
    else:
        out["characters"] = {"missing": True}

    # images (stubs)
    images_dir = bundle_dir / "images"
    if images_dir.exists():
        out["images_count"] = len(list(images_dir.rglob("*.png")))
    else:
        out["images_count"] = 0

    return out


def score(report: dict) -> dict:
    """Compute simple pass/fail health metrics."""
    log = report.get("log", {})
    bundle = report.get("bundle", {})
    prose = bundle.get("prose", {})
    ff = bundle.get("freeform_output", {})
    story = bundle.get("story", {})
    targets = story.get("targets", {}) if isinstance(story, dict) else {}

    # Per-beat prose %
    prose_pct: dict[str, int] = {}
    prose_in_window = 0
    prose_loose_pass = 0  # 60-130%
    prose_total = 0
    for beat_id, target in targets.items():
        p = prose.get(beat_id)
        if p and target:
            pct = int(p["cjk_chars"] / target * 100)
            prose_pct[beat_id] = pct
            prose_total += 1
            if 90 <= pct <= 110:
                prose_in_window += 1
            if 60 <= pct <= 130:
                prose_loose_pass += 1
    # Fallback if no story.json (freeform solo) — use 2500 as default target
    if not prose_pct and prose:
        for beat_id, p in prose.items():
            pct = int(p["cjk_chars"] / 2500 * 100)
            prose_pct[beat_id] = pct
            prose_total += 1
            if 90 <= pct <= 110:
                prose_in_window += 1
            if 60 <= pct <= 130:
                prose_loose_pass += 1

    return {
        "outcome": "DONE" if log.get("done_finished") is True
        else "NOT_DONE" if log.get("done_finished") is False
        else "CRASH" if log.get("stack_trace")
        else "UNKNOWN",
        "wall_time_s": log.get("wall_time_s"),
        "tool_count_total": sum(log.get("tool_counts", {}).values()),
        "rejects": log.get("rejects"),
        "dirty": log.get("dirty"),
        "errors": log.get("errors"),
        "prose_count": len(prose),
        "prose_per_beat_pct": prose_pct,
        "prose_in_strict_window": f"{prose_in_window}/{prose_total}",
        "prose_in_loose_60_130": f"{prose_loose_pass}/{prose_total}",
        "freeform_chars": ff.get("chars", 0) if isinstance(ff, dict) else 0,
        "has_story_section": ff.get("has_story") if isinstance(ff, dict) else None,
        "has_characters_section": ff.get("has_characters") if isinstance(ff, dict) else None,
        "has_end_of_bundle": ff.get("has_end_of_bundle") if isinstance(ff, dict) else None,
        "style_preamble_count": ff.get("style_preamble_count", 0) if isinstance(ff, dict) else 0,
        "images_count": bundle.get("images_count"),
        "tool_counts": log.get("tool_counts"),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("bundle_dir")
    ap.add_argument("log_path")
    ap.add_argument("--label", default="")
    args = ap.parse_args()
    report = {
        "label": args.label or Path(args.bundle_dir).name,
        "bundle": audit_bundle(Path(args.bundle_dir)),
        "log": parse_log(Path(args.log_path)),
    }
    report["score"] = score(report)
    print(json.dumps(report["score"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
