#!/usr/bin/env python3
"""page_turn_wide.py — 16:9 page-turn as a deterministic 2D curl wipe.

Model (same physics as the Blender roll, projected):
  - a roll of radius R (fraction of frame width) sits at x=c and travels right->left
  - left of the roll: the outgoing art, HORIZONTALLY COMPRESSED into the space
    between the left edge and the roll (so the page reads as being gathered up)
  - the roll band itself: warm paper with cylindrical shading + a dark seam at its
    trailing edge
  - right of the roll: the incoming art, revealed
  - a soft shadow to the right of the roll, gated to when the roll is in frame
Frame 0 == outgoing art and the last frame == incoming art EXACTLY (spliced, not
rendered), so the cut against a scene clip is pixel-perfect.

usage: page_turn_wide.py --from a.png --to b.png --out turn.mp4 [--verify]
"""
import argparse, subprocess, os, tempfile
import numpy as np
from PIL import Image


def load(p, size):
    return np.asarray(Image.open(p).convert("RGB").resize(size, Image.LANCZOS)).astype(np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="src", required=True)
    ap.add_argument("--to", dest="dst", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--frames", type=int, default=24)
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--roll", type=float, default=0.06, help="roll radius as fraction of width")
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args()
    W, H = (int(v) for v in a.size.split("x"))
    art_a = load(a.src, (W, H))
    art_b = load(a.dst, (W, H))
    n, R = a.frames, int(a.roll * W)
    tmp = tempfile.mkdtemp(prefix="ptw-")

    # soft shadow profile to the right of the roll
    xs = np.arange(W)
    for i in range(n):
        if i == 0:
            img = art_a
        elif i == n - 1:
            img = art_b
        else:
            p = i / (n - 1)
            e = p * p * (3 - 2 * p)                     # ease in/out
            left_edge = int(W * (1.0 - e))              # right boundary of the flat (outgoing) part: W -> 0
            c = left_edge - R                           # roll centre
            img = art_b.copy()
            # incoming art darkened by the roll's shadow just to its right
            if 0 <= left_edge < W:
                span = int(0.06 * W)
                for k in range(span):
                    x = left_edge + k
                    if x >= W:
                        break
                    s = (1.0 - k / span) ** 1.5 * 0.55
                    img[:, x] *= (1.0 - s)
            # the outgoing page, compressed into [0, left_edge)
            if left_edge > 1:
                src_x = np.linspace(0, W - 1, left_edge)
                cols = art_a[:, src_x.astype(int)]
                img[:, :left_edge] = cols
            # the roll band: warm paper with cylindrical shading, edge seams, paper grain
            x0 = max(0, left_edge - R)
            x1 = min(W, left_edge + R)
            if x1 > x0:
                width = x1 - x0
                xx = (np.arange(width) - width / 2) / max(1, width / 2)
                shade = np.sqrt(np.clip(1.0 - xx ** 2, 0.0, 1.0))
                rng = np.random.default_rng(11)
                grain = rng.normal(0, 3.0, (H, width))
                base = np.stack([np.full((H, width), 246.0), np.full((H, width), 238.0), np.full((H, width), 219.0)], axis=0)
                base *= (0.52 + 0.48 * shade)[None, :]
                base += grain[None, :, :]
                # subtle vertical variation so the band is not flat
                yv = np.linspace(0.94, 1.06, H)[:, None]
                base *= yv[None, :, :]
                img[:, x0:x1] = np.clip(base, 0, 255).transpose(1, 2, 0)
                # darker seams at both edges of the roll
                for k, xedge in ((3, x1 - 1), (4, x0)):
                    if 0 <= xedge < W:
                        img[:, max(0, xedge - 2):xedge + 1] *= (0.62 if k == 3 else 0.72)
                if x0 > 0:
                    img[:, max(0, x0 - 5):x0] *= 0.6          # shadow the roll casts back onto the outgoing page
        out = np.clip(img, 0, 255).astype(np.uint8)
        Image.fromarray(out).save(os.path.join(tmp, f"f{i:05d}.png"))

    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(a.fps),
                    "-i", os.path.join(tmp, "f%05d.png"), "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-crf", "16", a.out], check=True)
    print(f"rendered {n} frames -> {a.out}")
    if a.verify:
        f0 = np.asarray(Image.open(os.path.join(tmp, "f00000.png"))).astype(int)
        fl = np.asarray(Image.open(os.path.join(tmp, f"f{n-1:05d}.png"))).astype(int)
        print("verify: frame 0 vs outgoing art   max delta =", int(np.abs(f0 - art_a).max()))
        print("verify: last frame vs incoming art max delta =", int(np.abs(fl - art_b).max()))


if __name__ == "__main__":
    main()
