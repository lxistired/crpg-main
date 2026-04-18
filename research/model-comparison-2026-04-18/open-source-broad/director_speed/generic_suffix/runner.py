#!/usr/bin/env python3
"""Test GENERIC hardening suffix on Groq kimi-k2-0905.

Design principle: zero character-specific hardcoding.
- STRONG_SUFFIX_GENERIC: derived from framing-region-map only (skill-level static config)
- FEW_SHOT_SUFFIX_GENERIC: uses abstract attr_FOO/anchor tokens

This suffix should work for ANY character sheet / wardrobe state.
We pass Su Wan as user input (external data), but the suffix never names her attrs.
"""
import asyncio, pathlib, time, json, httpx, re, sys

OUT = pathlib.Path("/Users/lxxxxxx/个人项目/crpg/research/model-comparison-2026-04-18/open-source-broad/director_speed/generic_suffix")
OUT.mkdir(parents=True, exist_ok=True)
OR_KEY = "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"
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

# Load DIRECTOR_SYSTEM + DIRECTOR_USER from original test
src = pathlib.Path("/tmp/broad_opensource_test.py").read_text()
ns: dict = {"__name__": "bot"}
exec(src.replace("asyncio.run(main())", "pass"), ns)
DIRECTOR_SYSTEM = ns["DIRECTOR_SYSTEM"]
DIRECTOR_USER = ns["DIRECTOR_USER"]

# ============================================================
# GENERIC STRONG_SUFFIX
# Derived purely from framing-region-map (skill-level config),
# contains zero character-specific attr names or wardrobe states.
# ============================================================
STRONG_SUFFIX_GENERIC = """

### CRITICAL RULE (output will be rejected if violated)

For every shot, before writing vgai_injected_attrs, verify each attribute's anchor region is in the framing's visible_regions set. Use this reference table:

| framing | visible_regions |
|---------|-----------------|
| ws_establishing | {} (empty — subject too small) |
| cu_face | {face, ear, neck} |
| ms_waist_up | {face, ear, neck, torso, hand} |
| three_quarter_knee_up | {face, ear, neck, torso, hand, leg_upper} |
| full_body_standing | {face, ear, neck, torso, hand, leg, foot} |
| hand_ecu | {hand} |
| feet_ecu | {foot} |
| back_reveal_walking | {torso_back, hand, leg, foot} |

Procedure for each shot:
1. Look up visible_regions for the chosen camera_framing.
2. For each attr from character_sheet.persistent_grooming ∪ wardrobe_state.items:
   - If attr.anchor ∈ visible_regions → may inject.
   - If attr.anchor ∉ visible_regions → MUST NOT inject; add to dropped list with reason.
3. ws_establishing means vgai_injected_attrs MUST be an empty list [] (subject too small for any detail).
4. Mutex check: for each pair in character_sheet.mutex_groups, if both would survive step 2, pick the visually dominant one for the pose; the other goes to dropped.

Violating step 1-4 makes the entire output invalid.
"""

# ============================================================
# GENERIC FEW_SHOT_SUFFIX
# Uses an abstract placeholder character, no Su Wan specifics,
# demonstrates the VGAI pattern across 3 representative framings.
# ============================================================
FEW_SHOT_SUFFIX_GENERIC = """

### Canonical output pattern (abstract example — NOT copy these attr names)

Important: base identity (hair, skin, eye color, age, face shape) is ALWAYS in final_prompt regardless of framing. It is NEVER listed in vgai_injected_attrs or vgai_dropped (it's not a gated attribute).

Only GROOMING and WARDROBE items go through VGAI gating.

Suppose an abstract character with these GATED attrs:
- attr_LIP  (anchor: face)
- attr_NAIL (anchor: hand)
- attr_RING (anchor: hand)
- attr_SKIRT (anchor: torso)
- attr_HOSE  (anchor: leg)
- attr_TOENAIL (anchor: foot)
- attr_SHOE (anchor: foot)

And mutex_groups = [{attr_HOSE, attr_SHOE}, {attr_TOENAIL, attr_SHOE}].

Then the correct outputs look like:

```json
[
  {
    "shot_id": "example_ws",
    "camera_framing": "ws_establishing",
    "pose": "subject walks down street from a distance",
    "wardrobe_state_used": "some_state",
    "vgai_injected_attrs": [],
    "vgai_dropped_attrs_with_reason": ["all attrs dropped: ws_establishing visible_regions is empty"],
    "final_prompt": "<BASE IDENTITY DESCRIPTION>, walking down street, ws_establishing framing"
  },
  {
    "shot_id": "example_ms",
    "camera_framing": "ms_waist_up",
    "pose": "facing camera from waist up",
    "wardrobe_state_used": "some_state",
    "vgai_injected_attrs": ["attr_LIP", "attr_NAIL", "attr_RING", "attr_SKIRT"],
    "vgai_dropped_attrs_with_reason": [
      "attr_HOSE: leg not in visible_regions {face,ear,neck,torso,hand}",
      "attr_TOENAIL: foot not in visible_regions",
      "attr_SHOE: foot not in visible_regions"
    ],
    "final_prompt": "<BASE IDENTITY DESCRIPTION>, wearing attr_SKIRT, attr_LIP, attr_NAIL, attr_RING, ms_waist_up framing"
  },
  {
    "shot_id": "example_hand",
    "camera_framing": "hand_ecu",
    "pose": "extreme close-up on hand",
    "wardrobe_state_used": "some_state",
    "vgai_injected_attrs": ["attr_NAIL", "attr_RING"],
    "vgai_dropped_attrs_with_reason": [
      "attr_LIP: face not in visible_regions {hand}",
      "attr_SKIRT: torso not in visible_regions",
      "attr_HOSE: leg not in visible_regions",
      "attr_TOENAIL: foot not in visible_regions",
      "attr_SHOE: foot not in visible_regions"
    ],
    "final_prompt": "<BASE IDENTITY DESCRIPTION>, hand with attr_NAIL and attr_RING, hand_ecu framing"
  }
]
```

Notice: EVERY final_prompt begins with `<BASE IDENTITY DESCRIPTION>` (hair / skin / eye / age / face — copied verbatim from character_sheet.base), including the hand_ecu shot where no face is visible. Base identity is never gated by framing.

Apply the SAME pattern to the real character passed by the user. The attr names in your output MUST come from the real character_sheet, not from this abstract example.
"""

# ============================================================
# Now: test Director on Groq with DIRECTOR_SYSTEM + these 2 GENERIC suffixes.
# The DIRECTOR_USER prompt describes Su Wan. If the generic suffix is truly
# character-agnostic, the model must infer from DIRECTOR_SYSTEM (character block)
# which attrs to use, and apply the VGAI pattern. 0 Su Wan-specific names in suffix.
# ============================================================

async def call(client, label, iter_idx):
    payload = {
        "model": "moonshotai/kimi-k2-0905",
        "messages": [
            {"role": "system", "content": DIRECTOR_SYSTEM + STRONG_SUFFIX_GENERIC + FEW_SHOT_SUFFIX_GENERIC},
            {"role": "user", "content": DIRECTOR_USER},
        ],
        "temperature": 0.7,
        "max_tokens": 8000,
        "provider": {"order": ["Groq"], "allow_fallbacks": False},
    }
    t0 = time.time()
    try:
        r = await client.post(
            ENDPOINT, json=payload,
            headers={
                "Authorization": f"Bearer {OR_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://crpg.local",
                "X-Title": "crpg-generic-suffix-test",
            }, timeout=180,
        )
        elapsed = time.time() - t0
        if r.status_code != 200:
            return {"ok": False, "label": label, "iter": iter_idx,
                    "status": r.status_code, "error": r.text[:400], "elapsed": elapsed}
        body = r.json()
        msg = body["choices"][0].get("message", {})
        content = msg.get("content") or msg.get("reasoning") or ""
        usage = body.get("usage", {})
        return {"ok": True, "label": label, "iter": iter_idx,
                "content": content, "chars": len(content),
                "elapsed": elapsed,
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "cost": usage.get("cost", 0),
                "provider": body.get("provider", "?")}
    except Exception as e:
        return {"ok": False, "label": label, "iter": iter_idx,
                "error": f"{type(e).__name__}: {e}",
                "elapsed": time.time() - t0}

# ============================================================
# Audit (reuse logic)
# ============================================================
REGION_MAP = {
    'cu_face': {'face','ear','neck'},
    'ms_waist_up': {'face','ear','neck','torso','hand'},
    'three_quarter_knee_up': {'face','ear','neck','torso','hand','leg_upper'},
    'full_body_standing': {'face','ear','neck','torso','hand','leg','foot'},
    'feet_ecu': {'foot'}, 'hand_ecu': {'hand'},
    'back_reveal_walking': {'torso_back','hand','leg','foot'},
    'ws_establishing': set(),
}
ATTR_ANCHOR = {'red_fingernails':'hand','red_toenails':'foot','red_lipstick':'face',
    'black_pencil_skirt':'torso','sheer_black_tights':'leg','stocking_toes':'foot','black_ankle_boots':'foot'}
MUTEX = [{'stocking_toes','black_ankle_boots'},{'sheer_black_tights','bare_legs'}]

def strip_fence(s):
    s = s.strip()
    if s.startswith("```"):
        s = re.sub(r"^```\w*\s*", "", s)
        s = re.sub(r"\s*```\s*$", "", s)
    return s.strip()

def audit_content(content):
    try:
        data = json.loads(strip_fence(content))
    except Exception as e:
        return {"parse_ok": False, "err": str(e)[:120]}
    if not isinstance(data, list):
        return {"parse_ok": False, "err": "not-list"}
    real_issues = 0
    base_hit = 0
    violations = []
    for i, s in enumerate(data):
        cf = s.get('camera_framing','')
        inj = s.get('vgai_injected_attrs', [])
        if isinstance(inj, list):
            names = [x if isinstance(x,str) else (x.get('name') or x.get('attr') or x.get('id')) for x in inj]
            names = [n for n in names if n]
            vis = REGION_MAP.get(cf, None)
            if vis is None:
                violations.append(f"shot#{i}: unknown framing {cf!r}")
                continue
            for a in names:
                anc = ATTR_ANCHOR.get(a)
                if anc and anc not in vis:
                    # skip the back-reveal skirt false-positive
                    if cf == 'back_reveal_walking' and a == 'black_pencil_skirt':
                        continue
                    real_issues += 1
                    violations.append(f"shot#{i}[{cf}]: {a} (anchor={anc}) not in {sorted(vis)}")
            sset = set(names)
            for pair in MUTEX:
                if pair.issubset(sset):
                    real_issues += 1
                    violations.append(f"shot#{i}[{cf}]: MUTEX {sorted(pair)}")
        fp = (s.get('final_prompt') or '').lower()
        if any(k in fp for k in ['su wan','28','chinese','black hair','brown eye','fair skin','pale skin']):
            base_hit += 1
    return {"parse_ok": True, "shots": len(data),
            "real_violations": real_issues, "base_consistency": f"{base_hit}/{len(data)}",
            "violations": violations}

async def main():
    N_ITER = 4
    limits = httpx.Limits(max_connections=10, max_keepalive_connections=10)
    async with httpx.AsyncClient(limits=limits) as client:
        jobs = [call(client, "generic_suffix", i) for i in range(1, N_ITER + 1)]
        results = await asyncio.gather(*jobs)

    summary = []
    for r in results:
        if r.get("ok"):
            content = r["content"]
            fn = OUT / f"iter{r['iter']}.json"
            fn.write_text(content, encoding="utf-8")
            audit = audit_content(content)
            r_meta = {k: v for k, v in r.items() if k != "content"}
            r_meta["audit"] = audit
            print(f"iter{r['iter']}: {r['elapsed']:.1f}s, chars={r['chars']}, "
                  f"parse={audit.get('parse_ok')}, violations={audit.get('real_violations')}, "
                  f"base={audit.get('base_consistency')}")
            for v in audit.get("violations", [])[:3]:
                print(f"   - {v}")
        else:
            r_meta = r
            print(f"iter{r['iter']}: ERR {r.get('status','?')} {str(r.get('error',''))[:120]}")
        summary.append(r_meta)
    (OUT / "_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    # quick check: suffix itself contains no Su Wan / her attr names
    suffix_all = STRONG_SUFFIX_GENERIC + FEW_SHOT_SUFFIX_GENERIC
    su_wan_names = ["su wan", "sheer_black_tights", "black_ankle_boots",
                    "stocking_toes", "red_toenails", "red_fingernails",
                    "red_lipstick", "black_pencil_skirt", "public_formal"]
    leaks = [n for n in su_wan_names if n.lower() in suffix_all.lower()]
    print()
    print(f"Suffix char-agnostic check: {'PASS' if not leaks else 'LEAK: ' + str(leaks)}")
    print(f"Total suffix chars: {len(suffix_all)} (strong={len(STRONG_SUFFIX_GENERIC)} + few_shot={len(FEW_SHOT_SUFFIX_GENERIC)})")

asyncio.run(main())
