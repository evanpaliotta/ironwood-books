#!/usr/bin/env python3
"""compose_turn_wide.py — 16:9 variant of compose_turn.py: same logic, wide frames.

usage: compose_turn_wide.py --dir /tmp/turnw --from a.png --to b.png --out turn.mp4 [--verify]
"""
import argparse
import glob
import os
import subprocess
import tempfile

import numpy as np
from PIL import Image


def load_wide(path, size):
    im = Image.open(path).convert("RGB").resize(size, Image.LANCZOS)
    return np.asarray(im).astype(np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--from", dest="src", required=True)
    ap.add_argument("--to", dest="dst", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--shadow", type=float, default=0.55)
    ap.add_argument("--roll", type=float, default=0.13)
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    W, H = (int(x) for x in args.size.split("x"))

    pages = sorted(glob.glob(os.path.join(args.dir, "page_*.png")))
    if not pages:
        raise SystemExit(f"no page_####.png in {args.dir}")

    art_a = load_wide(args.src, (W, H))
    art_b = load_wide(args.dst, (W, H))

    tmp = tempfile.mkdtemp(prefix="composew-")
    import math
    n = len(pages)
    R = args.roll

    def gate(i):
        pe = (i / max(1, n - 1))
        pe = pe * pe * (3 - 2 * pe)
        # roll centre c runs W/2 -> -(W/2+2R); right edge = c + R; gate on presence in-frame
        c = W / 2 - (W + 2 * R) * pe
        return max(0.0, min(1.0, (c + R + W / 2) / (0.2 * W)))

    for i, png in enumerate(pages):
        if i == 0:
            Image.fromarray(np.clip(art_a, 0, 255).astype(np.uint8)).save(os.path.join(tmp, "f00000.png"))
            continue
        if i == n - 1:
            Image.fromarray(np.clip(art_b, 0, 255).astype(np.uint8)).save(os.path.join(tmp, f"f{n-1:05d}.png"))
            continue
        page = np.asarray(Image.open(png).convert("RGBA").resize((W, H), Image.LANCZOS)).astype(np.float32)
        alpha = (page[..., 3:4] / 255.0)
        sh_png = png.replace("page_", "shadow_")
        if os.path.exists(sh_png):
            sh = np.asarray(Image.open(sh_png).convert("RGBA").resize((W, H), Image.LANCZOS)).astype(np.float32)
            shadow = (sh[..., 3:4] / 255.0) * args.shadow * gate(i)
        else:
            shadow = np.zeros_like(alpha)
        frame = art_b * (1.0 - shadow)
        frame = frame * (1 - alpha) + page[..., :3] * alpha
        Image.fromarray(np.clip(frame, 0, 255).astype(np.uint8)).save(os.path.join(tmp, f"f{i:05d}.png"))

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(args.fps),
                    "-i", os.path.join(tmp, "f%05d.png"), "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-crf", "16", "-movflags", "+faststart", args.out], check=True)
    print(f"composed {n} frames -> {args.out}")

    if args.verify:
        first = np.asarray(Image.open(os.path.join(tmp, "f00000.png"))).astype(int)
        last = np.asarray(Image.open(os.path.join(tmp, f"f{n-1:05d}.png"))).astype(int)
        d0 = int(np.abs(first - art_a.astype(int)).max())
        d1 = int(np.abs(last - art_b.astype(int)).max())
        print(f"verify: frame 0 vs outgoing art    max delta = {d0}")
        print(f"verify: last frame vs incoming art max delta = {d1}")
        print("verify: ENDS EXACT" if d0 <= 2 and d1 <= 2 else "verify: ENDS DIFFER - INSPECT")


if __name__ == "__main__":
    main()
