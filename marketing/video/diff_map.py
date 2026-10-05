#!/usr/bin/env python3
"""diff_map.py — how does a rendered pass differ from the art? Where and how?"""
import sys

import numpy as np
from PIL import Image

a = np.asarray(Image.open(sys.argv[1]).convert("RGB")).astype(int)
b = np.asarray(Image.open(sys.argv[2]).convert("RGB")).astype(int)
if a.shape != b.shape:
    b_img = Image.open(sys.argv[2]).convert("RGB").resize((a.shape[1], a.shape[0]), Image.LANCZOS)
    b = np.asarray(b_img).astype(int)
d = np.abs(a - b).max(axis=2)
print(f"max delta {d.max()}  mean {d.mean():.1f}  px>8: {(d>8).sum()} ({100*(d>8).mean():.1f}%)")
# quadrant means to spot flips/shifts
H, W = d.shape
for name, sl in (("top-left", (slice(0, H//2), slice(0, W//2))),
                 ("top-right", (slice(0, H//2), slice(W//2, W))),
                 ("bot-left", (slice(H//2, H), slice(0, W//2))),
                 ("bot-right", (slice(H//2, H), slice(W//2, W)))):
    print(f"  {name}: mean delta {d[sl].mean():.1f}")
# mirror tests
dh = np.abs(a - b[:, ::-1]).max()
dv = np.abs(a - b[::-1]).max()
print(f"  horizontal mirror delta {dh.max()} | vertical mirror delta {dv.max()}")
# brightness ratio
print(f"  mean a {a.reshape(-1,3).mean(0).round(1)} vs b {b.reshape(-1,3).mean(0).round(1)}")
Image.fromarray(np.clip(d*3, 0, 255).astype(np.uint8)).save("/tmp/diffmap.png")
print("  diff map -> /tmp/diffmap.png")
