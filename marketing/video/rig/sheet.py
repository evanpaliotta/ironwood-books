#!/usr/bin/env python3
"""sheet.py — contact sheet of scene illustrations (or cutouts) for one-glance QA.

  python sheet.py out.png <img> [<img> ...]        # grid, scene id drawn on each tile
"""
import sys

from PIL import Image, ImageDraw

TILE = 400
COLS = 5


def main():
    out, files = sys.argv[1], sys.argv[2:]
    rows = (len(files) + COLS - 1) // COLS
    sheet = Image.new("RGB", (COLS * TILE, rows * TILE), (24, 24, 24))
    d = ImageDraw.Draw(sheet)
    for i, f in enumerate(files):
        im = Image.open(f).convert("RGB")
        im.thumbnail((TILE - 8, TILE - 8), Image.LANCZOS)
        x, y = (i % COLS) * TILE, (i // COLS) * TILE
        sheet.paste(im, (x + (TILE - im.width) // 2, y + (TILE - im.height) // 2))
        label = f.split("/")[-1].replace("scene-", "").replace(".png", "")
        d.rectangle([x + 4, y + 4, x + 16 + 8 * len(label), y + 26], fill=(0, 0, 0))
        d.text((x + 8, y + 8), label, fill=(255, 255, 0))
    sheet.save(out)
    print(f"{len(files)} tiles -> {out}")


if __name__ == "__main__":
    main()
