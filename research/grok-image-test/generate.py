#!/usr/bin/env python3
"""Generate 5 storyboard images via xAI grok-imagine-image.

Reads GROK_API_KEY from /Users/lxxxxxx/个人项目/crpg/.env.local.
Writes images to scene-{n}-{slug}.png and a JSON log to generation-log.json.
Never echoes the API key.
"""

import base64
import json
import os
import pathlib
import sys
import time
import urllib.request
import urllib.error

ROOT = pathlib.Path("/Users/lxxxxxx/个人项目/crpg/research/grok-image-test")
ENV_FILE = pathlib.Path("/Users/lxxxxxx/个人项目/crpg/.env.local")
ENDPOINT = "https://api.x.ai/v1/images/generations"
MODEL = "grok-imagine-image"

def load_key():
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line.startswith("GROK_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("GROK_API_KEY not found")

SCENES = [
    {
        "slug": "act1_start",
        "aspect_ratio": "16:9",
        "prompt": (
            "Cinematic noir establishing shot of a modern Chinese police interrogation room at night. "
            "Red neon from a window across the alley slices through white venetian blinds, casting long diagonal bars of crimson light across a concrete floor and a steel table. "
            "In the foreground, a woman in her late twenties sits with her legs elegantly crossed: a tight black pencil skirt hitched just above the knees, sheer black stockings catching the neon, and at the end of one crossed leg a single high-heeled pump dangling from burgundy-red painted toenails that gleam like a drop of dark blood. "
            "Her posture is composed, predatory, amused. "
            "In the background, blurred through one-way glass, a male detective sits half-silhouetted, watching her, tie loosened, exhaustion on his face. "
            "Shot on anamorphic lens, shallow depth of field, 35mm film grain, teal-and-crimson color grade, moody volumetric haze from a single overhead pendant lamp. "
            "Mood: power inversion, sexual tension, hunter becoming hunted. Photorealistic, ultra-detailed, cinematic aspect ratio."
        ),
    },
    {
        "slug": "act1_choice",
        "aspect_ratio": "21:9",
        "prompt": (
            "Midnight inside a Chinese municipal police station, a long empty corridor lit by flickering fluorescent tubes overhead and an amber emergency lamp at the far end. "
            "Linoleum floor reflects the sickly yellow light like dirty water. "
            "Mid-ground: a male plainclothes detective in his mid-thirties, rumpled white shirt and dark trousers, stands frozen, a vibrating phone glowing in his hand, his face half-lit, half-shadowed — two halves of the same man at war. "
            "Far end of the corridor: the silhouette of a woman waiting, one hand against the wall, the back line of a tight black pencil skirt and sheer black stockings catching the amber light, a single visible burgundy-red toenail from an off-heeled foot glowing like a lit match in the darkness. "
            "Shot from a low oblique angle, deep focus, heavy film grain, slight anamorphic lens flare from the emergency lamp, teal shadows and amber highlights. "
            "Mood: threshold moment, career versus desire, silence before betrayal. Photorealistic cinematic frame, noir atmosphere."
        ),
    },
    {
        "slug": "branchA2_apartment_mirror",
        "aspect_ratio": "3:2",
        "prompt": (
            "Interior of a small high-floor old-city Chinese apartment bathroom at 2 a.m. White ceramic tiles and a single bare bulb above the sink. "
            "A large round mirror has just been swung open on a hidden hinge, revealing a waterproof pouch tucked into the wall cavity. "
            "A woman in her late twenties stands before the mirror, her reflection fractured across its edge: she wears a long unbuttoned white dress shirt loose over her shoulders, a black pencil skirt pulled snug around her hips, sheer black stockings, and burgundy-red toenails bright against the cold white tile floor. "
            "Her back is half-turned; her face in the mirror is calm, tired, reading a stack of documents. "
            "Outside the window, the sprawling neon skyline of a Chinese megacity glows in purples, reds and cyans, refracting through water drops on the glass. "
            "In the doorway, out of focus, a man in a damp shirt watches her, one hand on the frame. "
            "Shot: medium, shallow depth of field, soft skin tones, 35mm photorealism, cinematic color grade, sensual but restrained, mirror symbolism of double identity. Tastefully suggestive, chest and lower body fully concealed by clothing."
        ),
    },
    {
        "slug": "branchB_nightclub_backstage",
        "aspect_ratio": "16:9",
        "prompt": (
            "Backstage corridor of an upscale Chinese nightclub, shot through an open dressing-room door. "
            "Front-of-house glamour meets backstage decay: left side of frame shows the faded floral wallpaper peeling near the ceiling, a cheap vanity mirror ringed with half-burnt bulbs, spilled makeup, a cigarette burn on the formica; right side, through the far doorway, a hot blur of magenta and gold stage lights and glittering dresses. "
            "At the vanity sits Mei-jie, a severe Chinese woman in her early fifties, hair lacquered into a tight chignon, a long emerald silk cheongsam slit to the thigh, lighting a thin cigarette — the flame reflected twice in her tired eyes. "
            "Standing beside her: Su Wan, back to camera, tight black pencil skirt and sheer black stockings catching the mirror light, burgundy-red toenails visible in strappy heels, one hand resting lightly on the vanity. "
            "In the doorway: Lin Ze, out-of-place detective in a rumpled jacket, watching, uneasy. "
            "Shot: wide 35mm, warm tungsten and cold neon mixed lighting, heavy atmosphere of old-world vice, film grain, cinematic noir. Mood: the glamour is a mask."
        ),
    },
    {
        "slug": "branchB_video_reveal",
        "aspect_ratio": "21:9",
        "prompt": (
            "Close-up cinematic shot inside a dark nightclub back office, darkness broken only by the pale blue glow of a boxy old CRT monitor. "
            "On the screen, a grainy surveillance frame plays: a middle-aged Chinese plainclothes detective caught mid-sentence in an underlit meeting room, timestamp burned into the bottom corner reading a date from five years ago. "
            "Foreground: a man's hand, knuckles scarred, trembling slightly as it hovers in front of the screen, the CRT light painting his skin ghostly blue. "
            "Behind his shoulder, partially out of focus, a woman watches him — the curve of her cheek, a single strand of hair, the hint of a black stocking-clad leg crossed beneath her, one burgundy-red toenail catching the monitor's blue light like a cold ember. "
            "The rest of the room is swallowed in black. "
            "Shot: extreme shallow depth of field, 35mm, heavy film grain, monochrome-blue lighting with a single warm red accent. "
            "Mood: grief, revelation, the moment a betrayal is finally seen. Photorealistic, ultra-detailed, cinematic."
        ),
    },
]

def call_api(api_key, prompt, aspect_ratio, resolution="2k"):
    body = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "n": 1,
        "response_format": "b64_json",
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
    }).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8")), None
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        # Never log the api key; strip any echo just in case
        raw = raw.replace(api_key, "<REDACTED>")
        return None, f"HTTP {e.code}: {raw[:500]}"
    except Exception as e:
        return None, f"ERR: {type(e).__name__}: {str(e)[:300]}"

def main():
    api_key = load_key()
    log = []
    total_cost_ticks = 0
    for i, scene in enumerate(SCENES, start=1):
        out_path = ROOT / f"scene-{i}-{scene['slug']}.png"
        print(f"[{i}/5] {scene['slug']} ({scene['aspect_ratio']})", flush=True)
        last_err = None
        for attempt in range(1, 4):
            t0 = time.time()
            data, err = call_api(api_key, scene["prompt"], scene["aspect_ratio"])
            elapsed = time.time() - t0
            if err:
                last_err = err
                print(f"  attempt {attempt}: {err[:220]}", flush=True)
                # content-policy -> soften prompt for next attempt
                if "content" in err.lower() or "policy" in err.lower() or "safety" in err.lower():
                    # replace explicit motifs with tamer equivalents for retries
                    softer = scene["prompt"].replace("unbuttoned white dress shirt", "loose white blouse").replace("sensual", "intimate").replace("predatory", "composed")
                    scene["prompt"] = softer
                time.sleep(2)
                continue
            # success
            b64 = data["data"][0].get("b64_json")
            if not b64:
                last_err = f"no b64_json in response: keys={list(data['data'][0].keys())}"
                print(f"  attempt {attempt}: {last_err}", flush=True)
                continue
            img_bytes = base64.b64decode(b64)
            out_path.write_bytes(img_bytes)
            cost = data.get("usage", {}).get("cost_in_usd_ticks", 0)
            total_cost_ticks += cost
            revised = data["data"][0].get("revised_prompt", "")
            print(f"  OK {out_path.name} ({len(img_bytes)//1024} KB, {elapsed:.1f}s, cost_ticks={cost})", flush=True)
            log.append({
                "scene_index": i,
                "slug": scene["slug"],
                "file": out_path.name,
                "bytes": len(img_bytes),
                "elapsed_sec": round(elapsed, 2),
                "cost_ticks": cost,
                "attempts": attempt,
                "revised_prompt": revised,
                "aspect_ratio": scene["aspect_ratio"],
                "status": "success",
            })
            break
        else:
            log.append({
                "scene_index": i,
                "slug": scene["slug"],
                "file": None,
                "attempts": 3,
                "status": "failed",
                "last_error": last_err,
                "aspect_ratio": scene["aspect_ratio"],
            })
    # write log
    (ROOT / "generation-log.json").write_text(
        json.dumps({
            "model": MODEL,
            "endpoint": ENDPOINT,
            "total_cost_usd": total_cost_ticks / 1e10,
            "total_cost_ticks": total_cost_ticks,
            "entries": log,
        }, indent=2, ensure_ascii=False),
    )
    print(f"\nTotal cost: ${total_cost_ticks / 1e10:.4f} ({total_cost_ticks} ticks)")
    ok = sum(1 for e in log if e["status"] == "success")
    print(f"Success: {ok}/5")

if __name__ == "__main__":
    main()
