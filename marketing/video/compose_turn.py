#!/usr/bin/env python3
"""
compose_turn.py — glue the Blender passes into the final transition, keeping the
ENDS exact.

Input:  <dir>/page_####.png   (RGBA: the turning sheet, unlit art + angle shading)
        <dir>/shadow_####.png (RGBA: only the shadow the sheet casts)
        the outgoing and incoming illustrations
Output: an mp4 of the turn + optional filmstrip.

Why composite instead of rendering the shadow in-scene: the bed must show the
INCOMING ILLUSTRATION EXACTLY on the last frame, which a lit 3D bed cannot do.
So the final frame is the incoming art with the catcher's shadow multiplied over
it, then the page pass composited on top. Frame 0 therefore equals the outgoing
art and the last frame equals the incoming art, with real soft shadow between.

  usage: compose_turn.py --dir /tmp/turn --from a.png --to b.png --out turn.mp4
"""
import argparse
import glob
import os
import subprocess
import tempfile

import numpy as np
from PIL import Image


def load_square(path, size):
    im = Image.open(path).convert("RGB")
    if im.size != (size, size):
        s = max(size / im.width, size / im.height)
        im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
        l, t = (im.width - size) // 2, (im.height - size) // 2
        im = im.crop((l, t, l + size, t + size))
    return np.asarray(im).astype(np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--from", dest="src", required=True)
    ap.add_argument("--to", dest="dst", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--size", type=int, default=1080)
    ap.add_argument("--shadow", type=float, default=0.55, help="shadow strength")
    ap.add_argument("--roll", type=float, default=0.10, help="roll radius used by the Blender render (for the shadow gate)")
    ap.add_argument("--still", default=None)
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()

    pages = sorted(glob.glob(os.path.join(args.dir, "page_*.png")))
    if not pages:
        raise SystemExit(f"no page_####.png in {args.dir}")

    art_a = load_square(args.src, args.size)
    art_b = load_square(args.dst, args.size)

    tmp = tempfile.mkdtemp(prefix="compose-")
    stills, keep = [], {int(len(pages) * k / 5) for k in range(6)}
    # Shadow gate: the roll casts a real shadow mid-turn, but near the END it sits
    # off-frame and its light still throws shadow into the frame (measured delta
    # 24 with a bare sine envelope), and near the START it isn't there yet. So the
    # shadow is gated by the roll's presence in-frame: full while its right edge
    # (c + R) is inside, fading over the last 0.2 frame-widths, zero after.
    import math

    n = len(pages)
    R = args.roll

    def gate(i):
        pe = (i / max(1, n - 1))
        pe = pe * pe * (3 - 2 * pe)
        c = 0.5 - (1.0 + 2 * R) * pe
        return max(0.0, min(1.0, (c + R + 0.5) / 0.2))
    for i, png in enumerate(pages):
        # The FIRST and LAST frames are the literal illustrations, not the render:
        # the 3D pass at p=0/p=1 is degenerate (flat sheet / roll off-frame), and
        # the render's texture resampling leaves ~1-2 delta noise + one stray hot
        # pixel at the seam. Splicing the exact art in removes the seam BY
        # CONSTRUCTION, and the cut against a scene clip is pixel-perfect.
        if i == 0:
            Image.fromarray(np.clip(art_a, 0, 255).astype(np.uint8)).save(
                os.path.join(tmp, "f00000.png"))
            continue
        if i == n - 1:
            Image.fromarray(np.clip(art_b, 0, 255).astype(np.uint8)).save(
                os.path.join(tmp, f"f{n-1:05d}.png"))
            continue
        page = np.asarray(Image.open(png).convert("RGBA")).astype(np.float32)
        if page.shape[0] != args.size:                       # match render size
            page = np.asarray(
                Image.open(png).convert("RGBA").resize((args.size, args.size), Image.LANCZOS)
            ).astype(np.float32)
        alpha = (page[..., 3:4] / 255.0)

        sh_png = png.replace("page_", "shadow_")
        if os.path.exists(sh_png):
            sh = np.asarray(Image.open(sh_png).convert("RGBA").resize(
                (args.size, args.size), Image.LANCZOS)).astype(np.float32)
            shadow = (sh[..., 3:4] / 255.0) * args.shadow * gate(i)
        else:
            shadow = np.zeros_like(alpha)

        # bed = incoming art, darkened by the sheet's shadow, then the sheet on top
        frame = art_b * (1.0 - shadow)
        frame = frame * (1 - alpha) + page[..., :3] * alpha
        out = np.clip(frame, 0, 255).astype(np.uint8)
        Image.fromarray(out).save(os.path.join(tmp, f"f{i:05d}.png"))
        if i in keep:
            stills.append(out)

    n = len(pages)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(args.fps),
                    "-i", os.path.join(tmp, "f%05d.png"), "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-crf", "16", "-movflags", "+faststart",
                    args.out], check=True)
    print(f"composed {n} frames -> {args.out}")

    if args.still and stills:
        tile = 360
        sheet = Image.new("RGB", (tile * len(stills), tile), (16, 16, 16))
        for i, st in enumerate(stills):
            im = Image.fromarray(st)
            im.thumbnail((tile - 4, tile - 4), Image.LANCZOS)
            sheet.paste(im, (i * tile + 2, 2))
        sheet.save(args.still)
        print(f"filmstrip -> {args.still}")

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
