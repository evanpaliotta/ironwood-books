#!/usr/bin/env python3
"""qa_gate.py — automated QA for a generated scene clip.

Implements the checks the video-generation literature actually uses, adapted to this
pipeline's failure classes:

  STRUCTURE  (per-region change vs frame 0)  -> catches things APPEARING or vanishing
             (a barn materialising). Size-thresholded so ambient additions that only
             ADD to a scene (a bird, a butterfly, drifting grass) pass.
  FLOW       (Farneback optical flow, warp-residual) -> catches melting/unstable
             geometry, and reports the "dynamic degree" so a nearly-frozen clip is caught.
  DIRECTION  (subject bbox area trend) -> catches a subject moving the WRONG WAY for the
             manifest (approaching when it should retreat, e.g. the path into the dark).
  FIDELITY   (frame 0 vs the source art) -> catches a clip that doesn't start on the still.
  SEMANTIC   (6-frame strip written for a vision model / human) -> wardrobe, population,
             mouth movement, and whether the motion reads as natural vs REVERSED.
             (No local metric can judge these; the strip exists so the judgement is made
             from a sequence, not a still.)

usage: qa_gate.py <clip.mp4> [--art still.png] [--expect approach|retreat|none] [--label S04]
"""
import argparse, json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw

try:
    import cv2
except ImportError:
    cv2 = None

WORK = "/tmp/qa_gate"

def frames(clip, n=24, size=(648, 352)):
    os.makedirs(WORK, exist_ok=True)
    d = float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",clip],
                             capture_output=True, text=True).stdout.strip())
    out = []
    for i in range(n):
        t = min(d - 0.06, d * i / n)
        p = f"{WORK}/f{i:02d}.png"
        subprocess.run(["ffmpeg","-y","-loglevel","error","-ss",f"{t:.3f}","-i",clip,"-frames:v","1",
                        "-vf",f"scale={size[0]}:{size[1]}",p], check=True)
        out.append(np.asarray(Image.open(p).convert("RGB")).astype(np.float32))
    return out, d

def moving_union(fr, thresh=2.5):
    """Union of the regions that MOVE across the clip — the subject(s) — so a background
    change can be told apart from the boy simply moving (which is expected).
    Threshold matters: at 1.2 px/frame the model's global drift makes almost the WHOLE
    frame read as 'moving' and real background appearances get masked out (measured on
    scene 1: the barn region was hidden at 1.2, exposed at 2.5)."""
    if cv2 is None:
        return None
    H, W = fr[0].shape[:2]
    acc = np.zeros((H, W), bool)
    for i in range(0, len(fr) - 1, 2):
        a = cv2.cvtColor(fr[i].astype(np.uint8), cv2.COLOR_RGB2GRAY)
        b = cv2.cvtColor(fr[i+1].astype(np.uint8), cv2.COLOR_RGB2GRAY)
        fl = cv2.calcOpticalFlowFarneback(a, b, None, 0.5, 3, 21, 3, 5, 1.2, 0)
        mag = np.sqrt(fl[..., 0]**2 + fl[..., 1]**2)
        acc |= (mag > thresh)
    acc = cv2.dilate(acc.astype(np.uint8), np.ones((13, 13), np.uint8), iterations=1).astype(bool)
    return acc

def subject_mask(fr):
    """Track the SUBJECT as the largest coherent motion blob per frame and exclude the
    union of its boxes. Reason this replaced a plain flow threshold: an element that
    APPEARS (the scene-1 barn) generates flow at the moment it appears, so a flow-mask
    hides exactly the thing we are hunting."""
    if cv2 is None:
        return None
    H, W = fr[0].shape[:2]
    boxes = []
    for i in range(0, len(fr) - 1, 2):
        a = cv2.cvtColor(fr[i].astype(np.uint8), cv2.COLOR_RGB2GRAY)
        b = cv2.cvtColor(fr[i+1].astype(np.uint8), cv2.COLOR_RGB2GRAY)
        fl = cv2.calcOpticalFlowFarneback(a, b, None, 0.5, 3, 21, 3, 5, 1.2, 0)
        mag = np.sqrt(fl[..., 0]**2 + fl[..., 1]**2)
        m = (mag > max(1.5, float(np.percentile(mag, 97)))).astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
        n, lab, stats, cent = cv2.connectedComponentsWithStats(m, 8)
        best, best_area = None, 0
        for k in range(1, n):
            area = stats[k, cv2.CC_STAT_AREA]
            if area > best_area:
                best, best_area = stats[k, :4], area
        if best is not None and best_area > 0.002 * H * W:
            boxes.append(best)
    mask = np.zeros((H, W), bool)
    for x, y, w, h in boxes:
        pad = int(0.05 * W)
        mask[max(0, y-pad):min(H, y+h+pad), max(0, x-pad):min(W, x+w+pad)] = True
    return mask

def background_changes(a, b, moving, thresh=20, min_area_frac=0.015):
    """Regions that change OUTSIDE the moving subject: an element appearing/vanishing in
    the background. Size-thresholded at 1.5% so ambient additions (a bird, butterflies,
    drifting grass) pass while a building or a person is flagged. The caller then crops
    each flagged region and has a VISION MODEL classify it structural vs ambient —
    Evan's rule: additions that enrich the scene are welcome, new structures are not."""
    d = np.abs(a - b).max(axis=2)
    mask = (d > thresh)
    if moving is not None:
        mask &= ~moving
    mask = mask.astype(np.uint8)
    if cv2 is None:
        return [], float(mask.mean())
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((9,9), np.uint8))
    n, lab, stats, cent = cv2.connectedComponentsWithStats(mask, 8)
    H, W = mask.shape
    big = []
    for i in range(1, n):
        area = stats[i, cv2.CC_STAT_AREA]
        if area / (H * W) >= min_area_frac:
            big.append({"area_pct": round(100*area/(H*W), 2),
                        "bbox": [int(v) for v in stats[i, :4]],
                        "cx": round(float(cent[i][0]/W), 3), "cy": round(float(cent[i][1]/H), 3)})
    return big, float(mask.mean())

def flow_stats(fr):
    if cv2 is None or len(fr) < 3:
        return {}
    mags, resid, areas = [], [], []
    for i in range(len(fr) - 1):
        a = cv2.cvtColor(fr[i].astype(np.uint8), cv2.COLOR_RGB2GRAY)
        b = cv2.cvtColor(fr[i+1].astype(np.uint8), cv2.COLOR_RGB2GRAY)
        fl = cv2.calcOpticalFlowFarneback(a, b, None, 0.5, 3, 21, 3, 5, 1.2, 0)
        mag = np.sqrt(fl[...,0]**2 + fl[...,1]**2)
        mags.append(float(mag.mean()))
        h, w = a.shape
        grid = np.stack(np.meshgrid(np.arange(w), np.arange(h))).astype(np.float32)
        mapx = (grid[0] + fl[...,0]); mapy = (grid[1] + fl[...,1])
        warped = cv2.remap(fr[i].astype(np.float32), mapx, mapy, cv2.INTER_LINEAR)
        resid.append(float(np.abs(warped - fr[i+1]).mean()))
        # subject extent: the moving region
        moving = (mag > max(0.6, float(np.percentile(mag, 92)))).astype(np.uint8)
        n, lab, stats, cent = cv2.connectedComponentsWithStats(moving, 8)
        best = 0
        for k in range(1, n):
            best = max(best, stats[k, cv2.CC_STAT_AREA])
        areas.append(best / float(h*w))
    return {"flow_mag_mean": round(float(np.mean(mags)), 2),
            "warp_residual_mean": round(float(np.mean(resid)), 2),
            "moving_area_start": round(float(np.mean(areas[:4])), 4),
            "moving_area_end": round(float(np.mean(areas[-4:])), 4)}

def strip(clip, out, n=6):
    d = float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",clip],
                             capture_output=True, text=True).stdout.strip())
    tiles = []
    for i in range(n):
        t = min(d - 0.06, d * i / (n - 1))
        p = f"{WORK}/s{i}.png"
        subprocess.run(["ffmpeg","-y","-loglevel","error","-ss",f"{t:.3f}","-i",clip,"-frames:v","1",
                        "-vf","scale=430:242",p], check=True)
        tiles.append((t, Image.open(p).convert("RGB")))
    sheet = Image.new("RGB", (430*n + 10, 285), "white"); dr = ImageDraw.Draw(sheet)
    for i,(t,im) in enumerate(tiles):
        sheet.paste(im, (i*430+5, 26)); dr.text((i*430+8, 8), f"{t:.1f}s", fill="black")
    sheet.save(out)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clip")
    ap.add_argument("--art", default=None)
    ap.add_argument("--expect", default="none", choices=["approach","retreat","none"])
    ap.add_argument("--label", default="clip")
    a = ap.parse_args()
    fr, d = frames(a.clip)
    rep = {"clip": a.clip, "label": a.label, "duration": round(d,2), "checks": {}}

    # FIDELITY
    if a.art and os.path.exists(a.art):
        art = np.asarray(Image.open(a.art).convert("RGB").resize((fr[0].shape[1], fr[0].shape[0]))).astype(np.float32)
        dd = np.abs(art - fr[0])
        rep["checks"]["fidelity_frame0_vs_art"] = {"mean": round(float(dd.mean()),1),
                                                  "pct_gt30": round(float(100*(dd.max(axis=2)>30).mean()),1)}
    # STRUCTURE (things appearing / vanishing in the BACKGROUND, ignoring the subject's own movement)
    moving = subject_mask(fr)
    app = {}
    for tag, idx in (("1.5s", 3), ("3s", 7), ("mid", len(fr)//2), ("end", len(fr)-2)):
        big, frac = background_changes(fr[0], fr[idx], moving)
        app[tag] = {"regions_gt2pct": big, "changed_frac": round(frac,4)}
    rep["checks"]["structure"] = app
    # FLOW
    rep["checks"]["flow"] = flow_stats(fr)
    # DIRECTION
    f = rep["checks"]["flow"]
    if f:
        s, e = f["moving_area_start"], f["moving_area_end"]
        trend = "growing" if e > s*1.08 else ("shrinking" if e < s*0.90 else "stable")
        ok = (a.expect == "approach" and trend == "growing") or (a.expect == "retreat" and trend == "shrinking") \
             or (a.expect == "none")
        rep["checks"]["direction"] = {"subject_area_start": s, "subject_area_end": e,
                                      "trend": trend, "expected": a.expect, "ok": bool(ok)}
    rep["checks"]["strip"] = strip(a.clip, f"{WORK}/{a.label}-strip.png")
    # VERDICT on the mechanical checks
    flags = []
    for tag, v in app.items():
        for r in v["regions_gt2pct"]:
            if r["area_pct"] >= 8:      # a barn-sized appearance (ambient birds are <2%)
                flags.append(f"STRUCTURAL APPEARANCE {tag}: {r['area_pct']}% at ({r['cx']},{r['cy']})")
    if f:
        if f["flow_mag_mean"] < 0.35: flags.append(f"NEARLY STATIC clip (flow {f['flow_mag_mean']})")
        if f["warp_residual_mean"] > 14: flags.append(f"UNSTABLE/melting (warp residual {f['warp_residual_mean']})")
        if not rep["checks"]["direction"]["ok"]:
            flags.append(f"WRONG DIRECTION: subject {rep['checks']['direction']['trend']}, expected {a.expect}")
    rep["flags"] = flags
    rep["verdict"] = "FAIL" if flags else "PASS (mechanical checks)"
    print(json.dumps(rep, indent=1))
    print("\n=== VERDICT:", rep["verdict"])
    for x in flags: print("  !", x)
    print("strip:", rep["checks"]["strip"])

if __name__ == "__main__":
    main()
