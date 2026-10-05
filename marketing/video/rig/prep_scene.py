#!/usr/bin/env python3
"""
prep_scene.py — one scene: illustration -> sprite (RGBA cutout) + QA sheet + plate
                 + a motion-spec skeleton whose frame 0 is the ORIGINAL position.

Run inside the rig venv:
  ./.venv/bin/python prep_scene.py <illustration.png> <workdir> <scene-id>

Workdir layout (created if missing):
  <workdir>/sprites/<scene>-cut.png        cropped RGBA, alpha>ALPHA_KEEP
  <workdir>/sprites/qa-<scene>.png         original | sprite-on-magenta | alpha
  <workdir>/plates/<scene>-plate.png       hole inpainted, outside pixels original
  <workdir>/plates/preview-<scene>-plate.png  same, hole outlined
  <workdir>/<scene>.json                   motion spec, frame 0 == original art

Why the threshold matters: rembg's u2net will happily pull in faint dust,
speed-smear and texture. Keeping only alpha > ALPHA_KEEP (220) leaves the hole
it has to inpaint as small as the character really is.
"""
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image

ALPHA_KEEP = 220
DILATE = 16
PLATE_THRESH = 8
# rembg also grabs bright scenery sometimes (scene-20's moon is one connected
# blob 35% of the character's area, so a "blob smaller than the character" rule
# keeps it, and the plate then inpaints the moon out of the sky). Default is
# therefore LARGEST COMPONENT ONLY: the character. Anything else the cutout
# grabbed is reported, and keeping it (a second character, a moving prop) is a
# deliberate per-scene choice, not a silent default.
KEEP_FRAC = 1.0
KEEP_MIN_PX = 1500


def keep_components(alpha_bool, frac=KEEP_FRAC, min_px=KEEP_MIN_PX):
    """Largest connected alpha component (+ peers), so the sprite is the character."""
    import cv2

    n, labels, stats, _ = cv2.connectedComponentsWithStats(
        alpha_bool.astype(np.uint8), connectivity=8)
    if n <= 2:
        return alpha_bool, []
    areas = stats[1:, cv2.CC_STAT_AREA]
    biggest = int(areas.max())
    keep = np.zeros(n, dtype=bool)
    keep[1:] = areas >= max(min_px, frac * biggest)
    dropped = sorted((int(a) for a, k in zip(areas, keep[1:]) if not k), reverse=True)
    return keep[labels], dropped


def cutout(src, out_png, qa_png, full_png):
    from rembg import remove

    orig = Image.open(src).convert("RGB")
    full = remove(orig).convert("RGBA")

    alpha = full.split()[-1].point(lambda v: 255 if v > ALPHA_KEEP else 0)
    kept, dropped = keep_components(np.asarray(alpha) > 0)
    if dropped:
        print(f"[keep] dropped {len(dropped)} non-character alpha blob(s), "
              f"largest {dropped[0]} px (the character's is the kept component)")
    alpha = Image.fromarray(np.where(kept, 255, 0).astype(np.uint8))
    full.putalpha(alpha)
    bbox = alpha.getbbox()
    if bbox is None:
        raise SystemExit(f"{src}: cutout empty after alpha>{ALPHA_KEEP} — rembg failed here")
    # TWO artifacts, deliberately:
    #   <scene>-cut-full.png  full-frame RGBA -> build_plate.py (it masks in
    #                         illustration coordinates, so a cropped sprite
    #                         would be stretched to full frame and inflate the
    #                         hole to ~2/3 of the picture)
    #   <scene>-cut.png       cropped to the character -> rig.py (its x/y are
    #                         fractions of the ORIGINAL frame, so a cropped
    #                         sprite lands exactly where the art had it)
    full.save(full_png)
    sprite = full.crop(bbox)
    sprite.save(out_png)

    # QA sheet: what the plate has to rebuild (magenta = character) + the alpha
    magenta = Image.new("RGB", orig.size, (255, 0, 255))
    magenta.paste(sprite, (bbox[0], bbox[1]), sprite)
    mask = Image.merge("RGB", (alpha, alpha, alpha))
    sheet = Image.new("RGB", (orig.width * 3 + 20, orig.height), (20, 20, 20))
    for i, im in enumerate((orig, magenta, mask)):
        sheet.paste(im, (i * (orig.width + 10), 0))
    sheet.save(qa_png)

    W, H = orig.size
    bx0, by0, bx1, by1 = bbox
    solid = (np.asarray(alpha) > 0)
    return {
        "size": (W, H),
        "bbox": bbox,
        "sprite": (bx1 - bx0, by1 - by0),
        # anchor [0.5, 1.0] => sprite centre-x / bottom sit on the path point
        "origin": ((bx0 + (bx1 - bx0) / 2.0) / W, by1 / H),
        "coverage": float(solid.sum()) / (W * H),
    }


def spec(out_json, scene, plate, out_mp4, dur, origin, sprite_name, original=None):
    x, y = origin
    doc = {
        "plate": plate,
        "out": out_mp4,
        # the source illustration, so check_frame0.py can prove frame 0 == the art
        "original": original,
        "dur": dur,
        "fps": 24,
        "width": 1080,
        "height": 1080,
        "layers": [{
            # FULL-FRAME cutout, not the cropped one: it goes through the same
            # resample as the plate, so frame 0 is bit-exact (see rig.py).
            "image": sprite_name,
            "anchor": [0.5, 1.0],
            "path": [
                {"t": 0.0, "x": round(x, 4), "y": round(y, 4), "scale": 1.0, "rotate": 0.0, "squash": 1.0},
                {"t": min(0.6, dur * 0.15), "x": round(x, 4), "y": round(y, 4), "scale": 1.0, "rotate": 0.0, "squash": 1.0},
                {"t": dur, "x": round(x, 4), "y": round(y, 4), "scale": 1.0, "rotate": 0.0, "squash": 1.0},
            ],
        }],
    }
    json.dump(doc, open(out_json, "w"), indent=2)
    open(out_json, "a").write("\n")


def main():
    src, work, scene = sys.argv[1], os.path.abspath(sys.argv[2]), sys.argv[3]
    dur = float(sys.argv[4]) if len(sys.argv) > 4 else 6.0
    rig = os.path.dirname(os.path.abspath(__file__))
    for d in ("sprites", "plates", "out"):
        os.makedirs(os.path.join(work, d), exist_ok=True)

    sprite = os.path.join(work, "sprites", f"{scene}-cut.png")
    full_cut = os.path.join(work, "sprites", f"{scene}-cut-full.png")
    qa = os.path.join(work, "sprites", f"qa-{scene}.png")
    plate = os.path.join(work, "plates", f"{scene}-plate.png")

    info = cutout(src, sprite, qa, full_cut)
    print(f"[{scene}] cutout {info['sprite'][0]}x{info['sprite'][1]} px, "
          f"bbox {info['bbox']}, coverage {100*info['coverage']:.1f}% of frame "
          f"(alpha>{ALPHA_KEEP})")
    print(f"[{scene}] origin (sprite at its original spot) = "
          f"x={info['origin'][0]:.4f} y={info['origin'][1]:.4f}")

    r = subprocess.run([sys.executable, os.path.join(rig, "build_plate.py"),
                        src, full_cut, plate, str(DILATE), str(PLATE_THRESH)],
                       capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode != 0:
        print(r.stderr.strip())
        raise SystemExit(f"[{scene}] build_plate.py failed")

    # outline the hole on a copy so it is obvious what was regenerated
    p = np.asarray(Image.open(plate).convert("RGB")).copy()
    o = np.asarray(Image.open(src).convert("RGB"))
    hole = (np.abs(p.astype(int) - o.astype(int)).sum(axis=2) > 0)
    edge = hole & ~np.pad(hole, 1, constant_values=False)[1:-1, 1:-1]
    p[edge] = (255, 0, 255)
    Image.fromarray(p).save(os.path.join(work, "plates", f"preview-{scene}-plate.png"))
    print(f"[{scene}] hole outline -> plates/preview-{scene}-plate.png")

    spec(os.path.join(work, f"{scene}.json"), scene,
         os.path.relpath(plate, work), f"out/{scene}-rig.mp4", dur,
         info["origin"], os.path.relpath(full_cut, work), os.path.abspath(src))
    print(f"[{scene}] spec -> {scene}.json (hold-only skeleton; motion to be authored)")


if __name__ == "__main__":
    main()
