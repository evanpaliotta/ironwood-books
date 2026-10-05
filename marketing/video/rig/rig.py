#!/usr/bin/env python3
"""
rig.py — layered 2.5D character rig for the Ironwood read-aloud videos.

The point: the BACKGROUND IS NEVER GENERATED. It is the original illustration,
pasted through pixel-for-pixel. Only the character sprite(s) move, along a
keyframed path with easing. So "the kid slides down the hill while the
background stays consistent" is true by construction, not by hoping a model
behaves. Cost: $0, deterministic, exactly timed to the narration.

Usage:
    python rig.py scene.json                 # render
    python rig.py scene.json --verify        # render + assert plate pixels untouched
    python check_frame0.py scene.json <original.png>   # assert frame 0 == the art

scene.json:
{
  "plate": "plates/scene-05-plate.png",     # original illustration w/ hole inpainted
  "out": "out/scene-05.mp4",
  "dur": 6.0,                               # seconds
  "fps": 24,
  "width": 1080, "height": 1080,            # output size (plate is scaled to fit)
  "layers": [
    {
      "image": "sprites/scene-05-cut-full.png",  # FULL-FRAME RGBA cutout, see below
      "anchor": [0.5, 1.0],                 # which point of the CHARACTER rides the path
      "path": [                             # x,y = fractions of the ORIGINAL art frame
        {"t": 0.0, "x": 0.4487, "y": 0.8711},   # <- the character's original spot:
        {"t": 0.6, "x": 0.4487, "y": 0.8711},   #    at t=0 this MUST be the original
        {"t": 4.0, "x": 0.6200, "y": 0.9400},   #    position, so frame 0 == the art
        {"t": 6.0, "x": 0.6600, "y": 0.9300}
      ],
      "scale":   [1.0, 1.08],               # lerped across the whole clip
      "rotate":  [0.0, -6.0],               # degrees, lerped (leans into motion)
      "squash":  [1.0, 1.0],                # vertical squash (impact/deform)
    }
  ]
}

Easing between path points is ease-in-out (smoothstep) — that is what reads as
"animated" instead of "sliding". Add a hold (two identical points) when a
character should be still while the narration talks over them.

WHY THE SPRITE IS FULL-FRAME (not cropped to the character):
the plate is the whole illustration resized to the output frame. A cropped
sprite is a *separate* image, so resizing it puts its pixels through a different
resampling phase than the plate and every high-contrast edge of the character —
outlines, stripes, the tire tread — lands a fraction of a pixel off. Measured on
scene-05: 6.4% of the frame differed, max channel delta 231, all of it along the
character's edges. Full-frame sprite + the plate's own scale = identical phase =
frame 0 is bit-exact, and it stays exact across the whole opening hold because
the identity transform short-circuits the resample entirely.
"""
import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image


def smoothstep(a, b, s):
    t = 0.0 if b == a else max(0.0, min(1.0, (s - a) / (b - a)))
    return t * t * (3.0 - 2.0 * t)


def lerp(a, b, t):
    return a + (b - a) * t


def value_at(points, key, t, default):
    """Piecewise ease-in-out interpolation of a scalar/pair across path time."""
    if not points:
        return default
    keys = [p for p in points if key in p]
    if not keys:
        return default
    if t <= points[0].get("t", 0.0) and key in points[0]:
        return points[0][key]
    prev = None
    for p in points:
        if key not in p:
            continue
        if p["t"] >= t:
            if prev is None:
                return p[key]
            e = smoothstep(prev["t"], p["t"], t)
            if isinstance(p[key], (list, tuple)):
                return [lerp(prev[key][i], p[key][i], e) for i in range(len(p[key]))]
            return lerp(prev[key], p[key], e)
        prev = p
    return prev[key]


def position_at(path, t):
    pts = [p for p in path if "x" in p and "y" in p]
    if not pts:
        raise ValueError("layer has no x/y path points")
    key_pts = [{"t": p["t"], "x": p["x"], "y": p["y"]} for p in pts]
    x = value_at(key_pts, "x", t, pts[0]["x"])
    y = value_at(key_pts, "y", t, pts[0]["y"])
    return x, y


def load_layer(spec, frame_w, frame_h):
    img = Image.open(spec["image"]).convert("RGBA")
    return img


def fit(sprite, scale):
    """Sprites are scaled by the SAME factor as the plate. Miss this and a 1024
    sprite in a 1080 frame is ~5.5% too big and lands off its original spot:
    frame 0 no longer equals the original art, and --verify still passes, because
    that check only looks at pixels the sprite does NOT cover."""
    return sprite.resize((max(1, int(round(sprite.width * scale))),
                          max(1, int(round(sprite.height * scale)))), Image.LANCZOS)


def character_anchor(sprite, anchor):
    """The character's anchor point in sprite-canvas pixels: the alpha bbox
    located by the anchor fractions (default centre-x, bottom)."""
    a = np.asarray(sprite.split()[-1])
    bbox = Image.fromarray(a).getbbox()
    if bbox is None:
        raise ValueError("sprite has no opaque pixels")
    x0, y0, x1, y1 = bbox
    return (x0 + anchor[0] * (x1 - x0), y0 + anchor[1] * (y1 - y0))


def place_at(spec, sprite, anchor_px, t, left, top):
    """One layer at time t -> (image to composite at (0,0), 0, 0).

    Placement is an affine about the character's own anchor, so scale/rotate/
    squash pivot on the character's feet instead of the frame corner, and the
    target x,y is where that anchor lands. x,y are fractions of the ORIGINAL art
    frame; the sprite canvas is the plate-scaled art, so the crop offset (left,
    top) comes out here.
    """
    x, y = position_at(spec["path"], t)
    sc = value_at(spec["path"], "scale", t, 1.0)
    rot = value_at(spec["path"], "rotate", t, 0.0)
    squash = value_at(spec["path"], "squash", t, 1.0)
    tx = x * sprite.width - left
    ty = y * sprite.height - top
    ax, ay = anchor_px
    if (abs(sc - 1.0) < 1e-3 and abs(squash - 1.0) < 1e-3 and abs(rot) < 0.01
            and abs(tx - ax) < 0.5 and abs(ty - ay) < 0.5):
        # identity: skip the resample so a held frame is BIT-exact, not merely
        # close. This is what keeps frame 0 == the original illustration.
        return sprite, 0, 0
    th = math.radians(rot)
    sx, sy = sc, sc * squash
    ca, sa = math.cos(th) / sx, math.sin(th) / sy
    a, b = ca, sa
    c = ax - a * tx - b * ty
    d_, e = -math.sin(th) / sx, math.cos(th) / sy
    f = ay - d_ * tx - e * ty
    out = sprite.transform(sprite.size, Image.AFFINE, (a, b, c, d_, e, f),
                           resample=Image.BICUBIC, fillcolor=(0, 0, 0, 0))
    return out, 0, 0


def render(scene, out_dir):
    plate = Image.open(scene["plate"]).convert("RGB")
    W = scene.get("width", 1920)
    H = scene.get("height", 1080)
    fps = scene.get("fps", 24)
    dur = scene.get("dur", 5.0)
    n_frames = int(round(dur * fps))

    # cover-fit the plate to the output frame
    scale = max(W / plate.width, H / plate.height)
    plate = plate.resize((int(plate.width * scale), int(plate.height * scale)), Image.LANCZOS)
    left = (plate.width - W) // 2
    top = (plate.height - H) // 2
    plate = plate.crop((left, top, left + W, top + H))

    # SPRITES ARE SCALED BY THE SAME FACTOR AS THE PLATE (see fit()).
    layers = []
    for spec in scene.get("layers", []):
        sprite = fit(load_layer(spec, W, H), scale)
        anchor = spec.get("anchor", [0.5, 1.0])
        layers.append((spec, sprite, character_anchor(sprite, anchor)))

    untouched = scene.get("_verify", False)
    worst = 0
    checked_px = 0
    plate_arr = np.asarray(plate)

    for i in range(n_frames):
        t = i / fps
        frame = plate.copy()
        m = None
        for spec, sprite, anchor_px in layers:
            s, px, py = place_at(spec, sprite, anchor_px, t, left, top)
            frame.paste(s, (px, py), s)
            if untouched:
                # union of every sprite's alpha, pasted at the SAME coordinates
                # as the sprite: PIL clips both identically. max(0, px) would
                # shift the mask and report a false "background changed".
                if m is None:
                    m = Image.new("L", (W, H), 0)
                hm = Image.new("L", (W, H), 0)
                hm.paste(s.split()[-1], (px, py))
                m = Image.fromarray(np.maximum(np.asarray(m), np.asarray(hm)))
        if untouched and m is not None:
            # every frame must equal the plate wherever no sprite covers it
            cur = np.asarray(frame)
            free = np.asarray(m) == 0
            d = int(np.abs(cur[free].astype(int) - plate_arr[free].astype(int)).max())
            worst = max(worst, d)
            checked_px = max(checked_px, int(free.sum()))
        frame.save(os.path.join(out_dir, f"f{i:05d}.png"))

    return out_dir, n_frames, plate, m, worst, checked_px


def encode(out_dir, fps, out_path):
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-framerate", str(fps), "-i", os.path.join(out_dir, "f%05d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16",
        "-movflags", "+faststart", out_path,
    ]
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scene_json")
    ap.add_argument("--verify", action="store_true",
                    help="assert that pixels not covered by a sprite are identical to the plate")
    args = ap.parse_args()

    scene = json.load(open(args.scene_json))
    scene["_verify"] = args.verify
    tmp = tempfile.mkdtemp(prefix="rig-")
    try:
        out_dir, n_frames, plate, mask, worst, checked = render(scene, tmp)
        encode(out_dir, scene.get("fps", 24), scene["out"])
        print(f"rendered {n_frames} frames -> {scene['out']}")
        if args.verify and mask is not None:
            m_arr = np.asarray(mask)
            covered = int((m_arr > 0).sum())
            print(f"verify: checked {n_frames} frames; {checked} free px/frame; "
                  f"sprite coverage {100.0*covered/m_arr.size:.1f}% of frame")
            print(f"verify: max pixel delta outside the sprite, over ALL frames = {worst}")
            print("verify: BACKGROUND PIXEL-IDENTICAL (every frame)"
                  if worst == 0 else "verify: BACKGROUND DIFFERS — BUG")
            if worst != 0:
                sys.exit(2)
    finally:
        if not os.environ.get("RIG_KEEP_TMP"):
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
