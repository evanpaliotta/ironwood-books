#!/usr/bin/env python3
"""strip.py — QA filmstrip: N frames pulled across a rendered clip, tiled 1 row.

  python strip.py <clip.mp4> <out.png> [n=8]
"""
import subprocess
import sys
import tempfile

from PIL import Image

TILE = 270
LABEL = 22


def main():
    clip, out = sys.argv[1], sys.argv[2]
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", clip], capture_output=True, text=True).stdout.strip())

    sheet = Image.new("RGB", (TILE * n, TILE + LABEL), (18, 18, 18))
    for i in range(n):
        t = dur * (i + 0.5) / n
        with tempfile.NamedTemporaryFile(suffix=".png", delete=True) as f:
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.3f}",
                            "-i", clip, "-frames:v", "1", f.name], check=True)
            im = Image.open(f.name).convert("RGB")
        im.thumbnail((TILE - 4, TILE - 4), Image.LANCZOS)
        sheet.paste(im, (i * TILE + (TILE - im.width) // 2, LABEL))
    sheet.save(out)
    print(f"{n} frames across {dur:.2f}s -> {out}")


if __name__ == "__main__":
    main()
