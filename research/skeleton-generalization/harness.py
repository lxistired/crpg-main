#!/usr/bin/env python3
"""Skeleton generalization harness — runs 5 briefs, audits outputs."""
import asyncio, json, pathlib, sys, re
from datetime import datetime
sys.path.insert(0, "/Users/lxxxxxx/个人项目/crpg/src")
from crpg.config import load_config
from crpg.llm.openrouter import OpenRouterClient
from crpg.passes.skeleton import run_skeleton

OUT = pathlib.Path("/Users/lxxxxxx/个人项目/crpg/research/skeleton-generalization")
OUT.mkdir(parents=True, exist_ok=True)
BRIEFS_DIR = pathlib.Path("/Users/lxxxxxx/个人项目/crpg/tests/fixtures/skeleton_briefs")

VALID_ANCHORS = {"face","ear","neck","hand","torso","torso_back","leg","leg_upper","foot"}

# Physical mutex rules — pairs that CAN coexist (should NOT be mutex)
# Each key lists item-name substrings that layer without occlusion
LAYER_SAFE_PATTERNS = [
    # tights/stockings/pantyhose + any footwear that only covers foot/ankle
    (["tights","stockings","pantyhose","丝袜","stocking"],
     ["heels","pumps","shoes","boots","高跟","踝靴","马丁","绣花","sneakers"]),
    # fishnet + boots
    (["fishnet","网袜","网眼"],
     ["boots","马丁","踝靴"]),
    # gown + shoes (long gown covers feet but gown isn't a shoe)
    (["gown","礼服","旗袍","dress"],
     ["heels","pumps","shoes","高跟","绣花"]),
]

def _matches_any(name: str, patterns: list[str]) -> bool:
    low = name.lower()
    return any(p.lower() in low for p in patterns)

def audit_character_sheet(name: str, char: dict) -> list[str]:
    issues = []

    # 1. base exists
    if "base" not in char:
        issues.append(f"{name}: missing base")
    else:
        for k in ("age","ethnicity","hair","skin","eyes","jaw"):
            if k not in char["base"]:
                issues.append(f"{name}.base missing {k}")

    # 2. anchors valid
    for g in char.get("persistent_grooming",[]):
        if g.get("anchor") not in VALID_ANCHORS:
            issues.append(f"{name}.grooming[{g.get('name')}] bad anchor {g.get('anchor')}")
    for state, ws in char.get("wardrobe_states",{}).items():
        for it in ws.get("items",[]):
            if it.get("anchor") not in VALID_ANCHORS:
                issues.append(f"{name}.wardrobe[{state}][{it.get('name')}] bad anchor {it.get('anchor')}")

    # 3. mutex physicality — detect layer-safe pairs wrongly declared as mutex
    all_items = set()
    for g in char.get("persistent_grooming",[]): all_items.add(g.get("name",""))
    for state, ws in char.get("wardrobe_states",{}).items():
        for it in ws.get("items",[]):
            all_items.add(it.get("name",""))
    for pair in char.get("mutex_groups",[]):
        if not isinstance(pair, list) or len(pair) < 2:
            issues.append(f"{name}.mutex: invalid pair {pair}")
            continue
        a, b = pair[0], pair[1]
        # Check against layer-safe patterns both directions
        for group_a, group_b in LAYER_SAFE_PATTERNS:
            if _matches_any(a, group_a) and _matches_any(b, group_b):
                issues.append(f"{name}.mutex: FALSE MUTEX [{a}, {b}] — these layer (group_a+group_b)")
            elif _matches_any(b, group_a) and _matches_any(a, group_b):
                issues.append(f"{name}.mutex: FALSE MUTEX [{a}, {b}] — these layer (group_b+group_a)")

    # 4. mutex items reference existing attrs
    for pair in char.get("mutex_groups",[]):
        for n in pair:
            if n not in all_items and "bare" not in n.lower():
                issues.append(f"{name}.mutex references unknown {n!r}")

    return issues

def audit_story(story: dict) -> list[str]:
    issues = []
    if "meta" not in story: issues.append("story missing meta")
    if "beats" not in story: issues.append("story missing beats")
    beats = story.get("beats",[])
    if len(beats) < 2: issues.append(f"story has too few beats: {len(beats)}")
    beat_ids = {b.get("id") for b in beats}
    for b in beats:
        for dep in b.get("depends_on", []):
            if dep not in beat_ids:
                issues.append(f"beat {b.get('id')} depends on unknown {dep!r}")
    for e in story.get("edges",[]):
        if e.get("from") not in beat_ids or e.get("to") not in beat_ids:
            issues.append(f"edge {e} references unknown beat")
    return issues

async def run_brief(client, brief_name: str, brief_text: str) -> dict:
    try:
        story, chars = await run_skeleton(client, brief=brief_text)
        story_blob = story.model_dump(mode="json", by_alias=True)
        char_blobs = {n: c.model_dump(mode="json", by_alias=True) for n, c in chars.items()}

        char_issues = []
        for name, c in char_blobs.items():
            char_issues.extend(audit_character_sheet(name, c))
        story_issues = audit_story(story_blob)

        return {
            "brief": brief_name, "ok": True,
            "story_issues": story_issues,
            "char_issues": char_issues,
            "issue_count": len(story_issues) + len(char_issues),
            "story": story_blob,
            "characters": char_blobs,
        }
    except Exception as e:
        return {"brief": brief_name, "ok": False, "err": str(e)[:200]}

async def main():
    cfg = load_config()
    client = OpenRouterClient(api_key=cfg.openrouter_key, concurrency=5)
    briefs = []
    for p in sorted(BRIEFS_DIR.glob("*.md")):
        briefs.append((p.stem, p.read_text(encoding="utf-8")))
    print(f"running {len(briefs)} briefs concurrently...")
    results = await asyncio.gather(*[run_brief(client, n, t) for n, t in briefs])

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    round_dir = OUT / f"round_{ts}"
    round_dir.mkdir(parents=True, exist_ok=True)
    (round_dir / "_summary.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    total_issues = 0
    print(f"\n{'brief':<25} {'status':<8} {'issues':<8} {'story':<8} {'char':<8}")
    print("-"*60)
    for r in results:
        s_issues = len(r.get("story_issues",[]))
        c_issues = len(r.get("char_issues",[]))
        tag = "CLEAN" if r.get("ok") and r.get("issue_count",0)==0 else "FAIL"
        print(f"{r['brief']:<25} {tag:<8} {r.get('issue_count','-'):<8} {s_issues:<8} {c_issues:<8}")
        if r.get("ok") and r.get("issue_count",0) > 0:
            for i in r.get("char_issues",[])[:3]: print(f"    char: {i}")
            for i in r.get("story_issues",[])[:3]: print(f"    story: {i}")
        elif not r.get("ok"):
            print(f"    err: {r.get('err','')}")
        total_issues += r.get("issue_count",0) if r.get("ok") else 99
    print(f"\nTotal issues across all briefs: {total_issues}")
    print(f"Results: {round_dir}")

asyncio.run(main())
