#!/usr/bin/env python3
"""
check_frame0.py — does frame 0 of the render actually reproduce the original art?

rig.py --verify proves the pixels NOT covered by a sprite equal the PLATE. That
check cannot catch a mis-placed sprite: a shifted sprite just uncovers inpainted
plate, so the verify passes while frame 0 no longer matches the illustration.
This measures the other half:

  frame 0 (rendered)  vs  the original illustration

The only place frame 0 is ALLOWED to differ is the plate's reconstructed hole —
the region the inpainter had to invent where the character used to be. Every
pixel outside that hole must be identical. That is the honest, complete claim.

Placement comes from rig.place_at, so this cannot drift from the renderer.

  python check_frame0.py <scene.json> <original-illustration.png> [diff-out.png]
"""
import json
import sys

import numpy as np
from PIL import Image, ImageFilter

HERE = __file__.rsplit("/", 1)[0]
sys.path.insert(0, HERE)
import rig  # noqa: E402


def main():
    scene = json.load(open(sys.argv[1]))
    orig_path = sys.argv[2] if len(sys.argv) > 2 else scene.get("original")
    if not orig_path:
        raise SystemExit("no original illustration given (arg or scene['original'])")
    W, H = scene.get("width", 1920), scene.get("height", 1080)

    plate_src = Image.open(scene["plate"]).convert("RGB")
    orig_src = Image.open(orig_path).convert("RGB")
    if plate_src.size != orig_src.size:
        orig_src = orig_src.resize(plate_src.size, Image.LANCZOS)

    s = max(W / plate_src.width, H / plate_src.height)
    p2 = plate_src.resize((int(plate_src.width * s), int(plate_src.height * s)), Image.LANCZOS)
    o2 = orig_src.resize((int(orig_src.width * s), int(orig_src.height * s)), Image.LANCZOS)
    l, t = (p2.width - W) // 2, (p2.height - H) // 2
    plate_out = p2.crop((l, t, l + W, t + H))
    orig_out = o2.crop((l, t, l + W, t + H))

    # the hole the inpainter rebuilt (source res -> output res). Dilated by 4 px
    # because LANCZOS has a ~3 px support: pixels just OUTSIDE the hole are
    # pulled toward the hole's differing values, so a strict 0-delta test needs
    # that bleed included. Measured without it: 106 px at delta 1.
    hole = (np.abs(np.asarray(plate_src).astype(int)
                   - np.asarray(orig_src).astype(int)).max(axis=2) > 0)
    hole_img = Image.fromarray((hole * 255).astype(np.uint8))
    hole_img = hole_img.filter(ImageFilter.MaxFilter(9))
    hole_img = hole_img.resize((int(plate_src.width * s), int(plate_src.height * s)),
                               Image.NEAREST).crop((l, t, l + W, t + H))
    allowed = np.asarray(hole_img) > 0

    spec = scene["layers"][0]
    sprite = rig.fit(rig.load_layer(spec, W, H), s)
    anchor_px = rig.character_anchor(sprite, spec.get("anchor", [0.5, 1.0]))
    s_img, px, py = rig.place_at(spec, sprite, anchor_px, 0.0, l, t)
    frame = plate_out.copy()
    frame.paste(s_img, (px, py), s_img)

    d = np.abs(np.asarray(frame).astype(int) - np.asarray(orig_out).astype(int)).max(axis=2)
    diff = d > 0
    outside = diff & ~allowed
    print(f"output frame     {W}x{H} (art {plate_src.size[0]}px scaled {s:.4f}x, crop offset {l},{t})")
    print(f"sprite paste     x={px} y={py} size={s_img.width}x{s_img.height} "
          f"[t=0 transform {'IDENTITY (no resample)' if (px, py) == (0, 0) else 'ACTIVE'}]")
    print(f"reconstructed hole (frame 0 may differ here) = {100*allowed.mean():.2f}% of frame, "
          f"max delta in it = {int(d[allowed].max()) if allowed.any() else 0}")
    print(f"OUTSIDE the hole  max delta = {int(d[~allowed].max()) if (~allowed).any() else 0}, "
          f"px differing = {int(outside.sum())} ({100*outside.mean():.3f}% of frame)")
    if int(outside.sum()) == 0:
        print("frame0: IDENTICAL TO THE ORIGINAL ART OUTSIDE THE RECONSTRUCTED HOLE")
    else:
        out = sys.argv[3] if len(sys.argv) > 3 else "/tmp/frame0-diff.png"
        Image.fromarray(np.clip(d * 3, 0, 255).astype(np.uint8)).save(out)
        print(f"frame0: DIFFERS OUTSIDE THE HOLE -> heat map {out}")
        sys.exit(2)


if __name__ == "__main__":
    main()
