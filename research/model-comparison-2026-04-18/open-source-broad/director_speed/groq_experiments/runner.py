#!/usr/bin/env python3
"""Groq kimi-k2-0905 schema diagnostic experiments.

Runs 6 experiments x 2 concurrent = 12 calls (+ baseline = 14).
Every result written to timestamped file. No printing of long data.
"""
import asyncio, pathlib, time, json, httpx, sys, re, datetime

OUT = pathlib.Path("/Users/lxxxxxx/个人项目/crpg/research/model-comparison-2026-04-18/open-source-broad/director_speed/groq_experiments")
OUT.mkdir(parents=True, exist_ok=True)

OR_KEY = "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"
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "moonshotai/kimi-k2-0905"

# Load original Director prompts
src = pathlib.Path("/tmp/broad_opensource_test.py").read_text()
src_noexec = src.replace("asyncio.run(main())", "pass")
ns: dict = {"__name__": "bot"}
exec(src_noexec, ns)
DIRECTOR_SYSTEM = ns["DIRECTOR_SYSTEM"]
DIRECTOR_USER = ns["DIRECTOR_USER"]

# ============================================================
# VGAI audit logic
# ============================================================
REGION_MAP = {
    'cu_face': {'face','ear','neck'},
    'ms_waist_up': {'face','ear','neck','torso','hand'},
    'three_quarter_knee_up': {'face','ear','neck','torso','hand','leg_upper'},
    'full_body_standing': {'face','ear','neck','torso','hand','leg','foot'},
    'feet_ecu': {'foot'},
    'hand_ecu': {'hand'},
    'back_reveal_walking': {'torso_back','hand','leg','foot'},
    'ws_establishing': set(),
}
ATTR_ANCHOR = {
    'red_fingernails':'hand','red_toenails':'foot','red_lipstick':'face',
    'black_pencil_skirt':'torso','sheer_black_tights':'leg',
    'stocking_toes':'foot','black_ankle_boots':'foot',
}
MUTEX = [{'stocking_toes','black_ankle_boots'},{'sheer_black_tights','bare_legs'}]

def audit_vgai(content: str):
    """Return (violations:list, n_shots, parse_ok, shots)."""
    # Trim: many models wrap with markdown fence
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    # Try parse
    try:
        shots = json.loads(text)
    except Exception:
        # Attempt to extract JSON array
        m = re.search(r"\[\s*\{.*\}\s*\]", text, re.DOTALL)
        if not m:
            return [{"type":"parse_fail","raw_preview":text[:200]}], 0, False, None
        try:
            shots = json.loads(m.group(0))
        except Exception as e:
            return [{"type":"parse_fail","error":str(e),"raw_preview":m.group(0)[:200]}], 0, False, None
    if not isinstance(shots, list):
        return [{"type":"not_array"}], 0, False, None

    violations = []
    for i, shot in enumerate(shots):
        if not isinstance(shot, dict):
            violations.append({"type":"not_dict","shot_idx":i})
            continue
        framing = shot.get("camera_framing","")
        injected = shot.get("vgai_injected_attrs", []) or []
        shot_id = shot.get("shot_id", f"#{i}")
        visible = REGION_MAP.get(framing, None)
        if visible is None:
            violations.append({"type":"unknown_framing","shot_id":shot_id,"framing":framing})
            continue
        for attr in injected:
            anchor = ATTR_ANCHOR.get(attr)
            if anchor is None:
                continue  # unknown attr, skip
            # Special case: back_reveal_walking + black_pencil_skirt is known false positive
            if framing == "back_reveal_walking" and attr == "black_pencil_skirt":
                continue
            # leg_upper is subset of leg
            ok = False
            if anchor in visible:
                ok = True
            elif anchor == "leg" and "leg_upper" in visible:
                ok = True
            elif anchor == "torso" and "torso_back" in visible:
                ok = True
            if not ok:
                violations.append({
                    "type":"anchor_not_visible",
                    "shot_id":shot_id,
                    "framing":framing,
                    "attr":attr,
                    "anchor":anchor,
                    "visible":sorted(visible),
                })
        # mutex check
        inj_set = set(injected)
        for pair in MUTEX:
            both = inj_set & pair
            if len(both) >= 2:
                violations.append({
                    "type":"mutex_both_injected",
                    "shot_id":shot_id,
                    "pair":sorted(both),
                })
    return violations, len(shots), True, shots


# ============================================================
# API call helper
# ============================================================
async def call(client, label, extra_payload, extra_system=None):
    messages = [
        {"role": "system", "content": (DIRECTOR_SYSTEM + (extra_system or ""))},
        {"role": "user", "content": DIRECTOR_USER},
    ]
    payload = {
        "model": MODEL,
        "messages": messages,
        "provider": {"order": ["Groq"], "allow_fallbacks": False},
    }
    # default baseline params
    payload.setdefault("temperature", 0.7)
    payload.setdefault("max_tokens", 8000)
    # apply overrides
    payload.update(extra_payload)
    t0 = time.time()
    try:
        r = await client.post(
            ENDPOINT, json=payload,
            headers={
                "Authorization": f"Bearer {OR_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://crpg.local",
                "X-Title": "crpg-groq-diag",
            }, timeout=180,
        )
        elapsed = time.time() - t0
        if r.status_code != 200:
            return {"ok": False, "label": label, "status": r.status_code,
                    "error": r.text[:600], "elapsed": elapsed,
                    "payload_keys": list(payload.keys())}
        body = r.json()
        msg = body["choices"][0].get("message", {})
        content = msg.get("content") or msg.get("reasoning") or ""
        usage = body.get("usage", {})
        return {"ok": True, "label": label, "content": content,
                "elapsed": elapsed, "chars": len(content),
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "cost": usage.get("cost", 0),
                "provider_returned": body.get("provider", "?"),
                "payload_keys": list(payload.keys()),
                "finish_reason": body["choices"][0].get("finish_reason"),
                }
    except Exception as e:
        return {"ok": False, "label": label,
                "error": f"{type(e).__name__}: {e}",
                "elapsed": time.time() - t0,
                "payload_keys": list(payload.keys())}


# ============================================================
# Experiment definitions
# ============================================================
# A minimal JSON schema for the 6-shot output
JSON_SCHEMA = {
    "name": "director_shots",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "shots": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "shot_id": {"type": "string"},
                        "camera_framing": {
                            "type": "string",
                            "enum": list(REGION_MAP.keys()),
                        },
                        "pose": {"type": "string"},
                        "wardrobe_state_used": {"type": "string"},
                        "vgai_injected_attrs": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "vgai_dropped_attrs_with_reason": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "final_prompt": {"type": "string"},
                    },
                    "required": ["shot_id","camera_framing","pose","wardrobe_state_used",
                                 "vgai_injected_attrs","vgai_dropped_attrs_with_reason","final_prompt"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["shots"],
        "additionalProperties": False,
    },
}

STRONG_SUFFIX = """

### CRITICAL RULE (output will be rejected if violated)
For every shot, before writing vgai_injected_attrs, check:
  anchor_of(attr) must be in framing.visible_regions (per the table above).
For ms_waist_up the visible_regions are {face, ear, neck, torso, hand} — you MUST NOT inject sheer_black_tights (anchor=leg), black_ankle_boots (anchor=foot), stocking_toes (anchor=foot) or red_toenails (anchor=foot) in a ms_waist_up shot. Violating this makes the output invalid.
For ws_establishing the visible_regions are empty {} — vgai_injected_attrs MUST be [].
For hand_ecu only hand-anchored attrs (red_fingernails). For cu_face only face/ear/neck anchored attrs (red_lipstick). For feet_ecu only foot-anchored attrs.
"""

FEW_SHOT_SUFFIX = """

### 正确示例（务必模仿该粒度与严格度）
```
[{"shot_id":"ex_establishing","camera_framing":"ws_establishing","pose":"walks out of glass tower at dusk","wardrobe_state_used":"public_formal","vgai_injected_attrs":[],"vgai_dropped_attrs_with_reason":["all attrs dropped: ws_establishing visible_regions is empty"],"final_prompt":"28-year-old Chinese woman, black hair past shoulders, fair skin, walks out of glass office tower at dusk, urban street"},
{"shot_id":"ex_ms_florist","camera_framing":"ms_waist_up","pose":"leans to smell lilies at flower stall","wardrobe_state_used":"public_formal","vgai_injected_attrs":["black_pencil_skirt","red_fingernails","red_lipstick"],"vgai_dropped_attrs_with_reason":["sheer_black_tights: leg not in visible_regions [face,ear,neck,torso,hand]","black_ankle_boots: foot not in visible_regions","red_toenails: foot not in visible_regions","stocking_toes: foot not in visible_regions"],"final_prompt":"28-year-old Chinese woman, black hair, fair skin, red lipstick, red fingernails, black pencil skirt, leaning to smell lilies at subway flower stall"}]
```
对 ms_waist_up 永远不得包含 leg/foot anchored attrs。
"""

EXPERIMENTS = [
    # (exp_id, label, extra_payload, extra_system)
    ("exp0", "baseline_groq_t07_repro",     {"temperature": 0.7},                                                   None),
    ("exp1", "temp0_seed42",                {"temperature": 0, "seed": 42},                                         None),
    ("exp2", "json_object_mode",            {"temperature": 0, "seed": 42, "response_format": {"type": "json_object"}}, None),
    ("exp3", "json_schema_strict",          {"temperature": 0, "seed": 42, "response_format": {"type": "json_schema","json_schema": JSON_SCHEMA}}, None),
    ("exp4", "strong_system_suffix",        {"temperature": 0, "seed": 42},                                         STRONG_SUFFIX),
    ("exp5", "max_tokens_16k",              {"temperature": 0, "seed": 42, "max_tokens": 16000},                    None),
    ("exp6", "few_shot_example",            {"temperature": 0, "seed": 42},                                         FEW_SHOT_SUFFIX),
]

# ============================================================
# Orchestration
# ============================================================
async def run_exp(client, exp_id, label, extra_payload, extra_system, iter_idx):
    lbl = f"{exp_id}_{label}_iter{iter_idx}"
    return await call(client, lbl, extra_payload, extra_system)


async def main():
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    limits = httpx.Limits(max_connections=20, max_keepalive_connections=20)

    # Build job list: each experiment x 2 iterations
    jobs_spec = []
    for exp_id, label, extra_payload, extra_system in EXPERIMENTS:
        for i in (1, 2):
            jobs_spec.append((exp_id, label, extra_payload, extra_system, i))

    async with httpx.AsyncClient(limits=limits) as client:
        jobs = [run_exp(client, *spec) for spec in jobs_spec]
        results = await asyncio.gather(*jobs, return_exceptions=False)

    # Write every raw result
    summary = []
    for r in results:
        lbl = r["label"]
        raw_path = OUT / f"{lbl}_{ts}.json"
        # Save content (or error info) to separate file
        if r.get("ok"):
            content = r["content"]
            # Audit
            violations, n_shots, parse_ok, shots = audit_vgai(content)
            (OUT / f"{lbl}_{ts}_content.txt").write_text(content, encoding="utf-8")
            meta = {k: v for k, v in r.items() if k != "content"}
            meta["violations"] = violations
            meta["violation_count"] = len(violations)
            meta["n_shots"] = n_shots
            meta["parse_ok"] = parse_ok
            raw_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
            summary.append({
                "label": lbl,
                "ok": True,
                "elapsed": round(r["elapsed"], 2),
                "chars": r["chars"],
                "completion_tokens": r.get("completion_tokens"),
                "provider": r.get("provider_returned"),
                "finish_reason": r.get("finish_reason"),
                "parse_ok": parse_ok,
                "n_shots": n_shots,
                "violation_count": len(violations),
                "violation_types": sorted({v["type"] for v in violations}),
                "cost": r.get("cost", 0),
            })
        else:
            raw_path.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
            summary.append({
                "label": lbl,
                "ok": False,
                "elapsed": round(r.get("elapsed", 0), 2),
                "status": r.get("status"),
                "error": str(r.get("error", ""))[:200],
            })

    (OUT / f"_summary_{ts}.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Summary saved: _summary_{ts}.json ({len(summary)} results)")


if __name__ == "__main__":
    asyncio.run(main())
