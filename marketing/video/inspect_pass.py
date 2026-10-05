#!/usr/bin/env python3
"""inspect_pass.py — is a rendered pass showing art or the paper back?"""
import sys

import numpy as np
from PIL import Image

for p in sys.argv[1:]:
    im = np.asarray(Image.open(p).convert("RGBA"))
    a = im[..., 3]
    rgb = im[..., :3]
    print(p.split("/")[-1],
          f"alpha min/max/mean {a.min()}/{a.max()}/{a.mean():.0f}",
          f"rgb mean {rgb.reshape(-1,3).mean(0).round(0)}",
          f"rgb std {rgb.reshape(-1,3).std(0).round(0)}")
