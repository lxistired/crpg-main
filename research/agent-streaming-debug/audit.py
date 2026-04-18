"""Audit the live agent bundle against VGAI + occlusion rules."""
import json, sys
from pathlib import Path
sys.path.insert(0, "/Users/lxxxxxx/个人项目/crpg/src")
from crpg.types import Character, Shot
from crpg.validation.vgai import validate_shot_list

B = Path("/Users/lxxxxxx/个人项目/crpg/bundles/e2e-agent-2026-04-18")
chars_blob = json.loads((B / "characters.json").read_text())
chars = {name: Character.model_validate(b) for name, b in chars_blob.items()}

print("=== CHARACTERS ===")
for name, c in chars.items():
    print(f"  {name}: wardrobe_states={list(c.wardrobe_states)}, mutex={c.mutex_groups}")
    for st, ws in c.wardrobe_states.items():
        for item in ws.items:
            print(f"    [{st}] {item.name} anchor={item.anchor} covers={item.covers}")

print("\n=== PER-BEAT AUDIT ===")
grand_total = 0
grand_violations = 0
for shot_dir in sorted((B / "shots").iterdir()):
    sj = shot_dir / "shots.json"
    if not sj.exists():
        continue
    shots_raw = json.loads(sj.read_text())
    shots = [Shot.model_validate(s) for s in shots_raw]
    # Each shot uses a wardrobe_state; we need the owner char (demo has 1 POV)
    pov = "su_wan"  # main char
    if pov not in chars:
        pov = next(iter(chars))
    viol = validate_shot_list(shots, chars[pov])
    grand_total += len(shots)
    grand_violations += len(viol)
    print(f"\n  [{shot_dir.name}] {len(shots)} shots, {len(viol)} violations")
    for s in shots:
        print(f"    {s.shot_id}  framing={s.camera_framing}  state={s.wardrobe_state_used}")
        print(f"      inject={s.vgai_injected_attrs}")
        dropped = s.vgai_dropped_attrs_with_reason
        if isinstance(dropped, list):
            for d in dropped[:3]:
                print(f"      drop: {d}")
            if len(dropped) > 3:
                print(f"      ... +{len(dropped)-3} more drops")
    for v in viol:
        print(f"    VIOL [{v.kind}] shot={v.shot_id} attr={v.attr} — {v.reason}")

print(f"\n=== TOTAL: {grand_total} shots, {grand_violations} violations ===")
