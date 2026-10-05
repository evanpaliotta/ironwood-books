#!/usr/bin/env python3
"""
generate_clip.py — one scene, one full-frame image-to-video generation.

Usage:
  python3 generate_clip.py <scene-id> <illustration.png> <prompt> [model] [duration] [last_frame]

Defaults: model = kwaivgi/kling-v2.5-turbo-pro, duration = 5 (integer; string
"5" 422s on some models). Output -> <scene-dir>/clips/<scene-id>-<model>.mp4
plus a QA filmstrip of first/mid/last frames next to it.

The prompt must be written FROM the scene (motion brief): what the character
does relative to the setting, what ambient motion fits, what must not change.
Requires REPLICATE_API_TOKEN in ~/.zshenv (chmod 600; never echoed).
"""
import base64
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request

DEFAULT_MODEL = "kwaivgi/kling-v2.5-turbo-pro"
VIDEO_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "video")


FIRST_FRAME_KEYS = ("first_frame_image", "image", "first_frame", "start_image")
LAST_FRAME_KEYS = ("last_frame_image", "last_frame", "end_image")
DURATION_KEYS = ("duration", "dur", "video_duration")


def model_input_schema(model, token):
    """The model's input property names, so the payload adapts instead of 422ing.

    Fetched with curl: Replicate 403s python-urllib's default user agent.
    """
    r = subprocess.run(
        ["curl", "-s", "-H", f"Authorization: Bearer {token}",
         f"https://api.replicate.com/v1/models/{model}"],
        capture_output=True, text=True, check=True)
    d = json.loads(r.stdout)
    s = (d.get("latest_version") or {}).get("openapi_schema") or {}
    props = (((s.get("components") or {}).get("schemas") or {}).get("Input") or {}).get("properties") or {}
    return d, props


def pick(props, keys):
    for k in keys:
        if k in props:
            return k
    return None


def main():
    scene, img, prompt = sys.argv[1], os.path.abspath(sys.argv[2]), sys.argv[3]
    model = sys.argv[4] if len(sys.argv) > 4 else DEFAULT_MODEL
    duration = int(sys.argv[5]) if len(sys.argv) > 5 else 5
    last_frame = os.path.abspath(sys.argv[6]) if len(sys.argv) > 6 else None

    token = None
    for line in open(os.path.expanduser("~/.zshenv")):
        if line.startswith("export REPLICATE_API_TOKEN=") or line.startswith("REPLICATE_API_TOKEN="):
            token = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not token:
        raise SystemExit("REPLICATE_API_TOKEN not found in ~/.zshenv")

    book = os.path.join(VIDEO_ROOT, "book01")
    os.makedirs(os.path.join(book, "clips"), exist_ok=True)
    short = model.split("/")[-1]
    out = os.path.join(book, "clips", f"{scene}-{short}.mp4")

    meta, props = model_input_schema(model, token)
    img_key = pick(props, FIRST_FRAME_KEYS)
    if not img_key:
        raise SystemExit(f"{model}: no first-frame input found in {sorted(props)}")
    dur_key = pick(props, DURATION_KEYS)
    if dur_key and "enum" in props[dur_key]:
        allowed = sorted(props[dur_key]["enum"], key=lambda v: abs(int(v) - duration))
        duration = int(allowed[0])

    data_uri = "data:image/png;base64," + base64.b64encode(open(img, "rb").read()).decode()
    inp = {img_key: data_uri, "prompt": prompt}
    if dur_key:
        inp[dur_key] = duration
    if last_frame:
        lf_key = pick(props, LAST_FRAME_KEYS)
        if not lf_key:
            print(f"[{scene}] WARN {model} has no last-frame input; ignoring it")
        else:
            inp[lf_key] = "data:image/png;base64," + base64.b64encode(open(last_frame, "rb").read()).decode()
    print(f"[{scene}] payload keys: {sorted(inp)} | duration={duration}")

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump({"input": inp}, f)
        payload = f.name

    req = urllib.request.Request(
        f"https://api.replicate.com/v1/models/{model}/predictions",
        data=open(payload, "rb").read(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST")
    r = json.load(urllib.request.urlopen(req))
    pid, urls = r.get("id"), r.get("urls", {})
    get_url = urls.get("get", f"https://api.replicate.com/v1/predictions/{pid}")
    print(f"[{scene}] submitted {model} prediction {pid}")

    t0 = time.time()
    while True:
        time.sleep(8)
        req = urllib.request.Request(get_url, headers={"Authorization": f"Bearer {token}"})
        p = json.load(urllib.request.urlopen(req))
        status = p.get("status")
        if status in ("succeeded", "failed", "canceled"):
            break
        if time.time() - t0 > 900:
            print(f"[{scene}] TIMED OUT waiting; prediction {pid} still running")
            sys.exit(3)
    if status != "succeeded":
        raise SystemExit(f"[{scene}] prediction {status}: {p.get('error')}")

    video_url = p["output"] if isinstance(p["output"], str) else p["output"][-1]
    tmp = out + ".part"
    urllib.request.urlretrieve(video_url, tmp)
    os.replace(tmp, out)
    size = os.path.getsize(out)
    print(f"[{scene}] DONE {out} ({size/1e6:.1f} MB, {time.time()-t0:.0f}s)")

    os.unlink(payload)
    # QA filmstrip: first / mid / last tile
    strip = out.replace(".mp4", "-qa.png")
    subprocess.run([os.path.join(VIDEO_ROOT, "rig", ".venv", "bin", "python"),
                    os.path.join(VIDEO_ROOT, "rig", "strip.py"), out, strip, "6"], check=False)
    print(f"[{scene}] NOTE actual cost: check the Replicate billing page for prediction {pid}")


if __name__ == "__main__":
    main()
