#!/usr/bin/env python3
"""count_suns.py — QA helper: count bright sky blobs (sun-like) in a clip frame.

Compares an original illustration against sampled frames of a generated clip, so
"there are two suns" is a measured claim. Needs the sheet of frames already
extracted (strip.py) or will pull frames itself.

  python count_suns.py <original.png> <clip.mp4> [n_frames=6]
"""
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image
import cv2

THRESH = 235
MIN_PX = 40


def blobs(img):
    if img.width != 1024:
        img = img.resize((1024, 1024), Image.LANCZOS)
    a = np.asarray(img.convert("RGB")).astype(int)
    bright = (a[:, :, 0] > THRESH) & (a[:, :, 1] > THRESH * 0.85) & (a[:, :, 2] < THRESH * 0.95)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(bright.astype(np.uint8), 8)
    out = []
    for i in range(1, n):
        x, y, w, h, area = stats[i]
        if area >= MIN_PX:
            out.append((int(x), int(y), int(w), int(h), int(area)))
    return sorted(out, key=lambda b: -b[4])


def main():
    orig, clip = sys.argv[1], sys.argv[2]
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    o = blobs(Image.open(orig))
    print(f"ORIGINAL  sky-bright blobs: {len(o)}  {o[:4]}")
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                "-of", "csv=p=0", clip], capture_output=True, text=True).stdout.strip())
    for i in range(n):
        t = dur * (i + 0.5) / n
        with tempfile.NamedTemporaryFile(suffix=".png", delete=True) as f:
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.3f}",
                            "-i", clip, "-frames:v", "1", f.name], check=True)
            b = blobs(Image.open(f.name))
        print(f"frame {i} @{t:4.1f}s  sky-bright blobs: {len(b)}  {b[:4]}")


if __name__ == "__main__":
    main()
