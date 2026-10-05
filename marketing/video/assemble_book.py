#!/usr/bin/env python3
"""assemble_book.py — build the full Book 1 read-aloud video.

Per scene: the arrival clip (if any) + the departure clip, trimmed/padded to that scene's
narration slot. Between scenes: a page turn rendered from the ACTUAL last frame of the
outgoing scene into the ACTUAL first frame of the incoming scene (so the cuts are seamless),
sitting inside the 1.8s pause per the narration timings.

Timeline = narration-timings-v3-final.json exactly (0.8s lead-in, slots, 1.8s gaps).
Output: review/clips/book1-full-animation.mp4
"""
import json, os, subprocess, sys, glob

REV = "/Users/evanpaliotta/Projects/ironwood-series-archive/book-01-adventures/video/review"
CLIPS = REV + "/clips"
WORK = "/tmp/bookbuild"
os.makedirs(WORK, exist_ok=True)
T = json.load(open(REV + "/narration-timings-v3-final.json"))
NARR = REV + "/Curious Kid Book 1 narration - Marcus (v3-final).m4a"
SFX = REV + "/sfx/page-turn-cc0.mp3"
OUT = CLIPS + "/book1-full-animation.mp4"
LEAD_IN, GAP, TAIL = 0.80, 1.8, 3.0

def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        print("FAIL:", " ".join(cmd)[:220]); print(r.stderr[-1200:]); sys.exit(1)
    return r

def dur(f):
    return float(run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f]).stdout.strip())

def concat(files, out, reencode=True):
    lst = WORK + "/lst_" + os.path.basename(out) + ".txt"
    with open(lst,"w") as fh:
        for f in files: fh.write(f"file '{f}'\n")
    if reencode:
        run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",lst,
             "-c:v","libx264","-pix_fmt","yuv420p","-crf","18","-r","24",out])
    else:
        run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",lst,"-c","copy",out])

def freeze(src_frame, seconds, out):
    run(["ffmpeg","-y","-loglevel","error","-loop","1","-framerate","24","-i",src_frame,
         "-t",str(seconds),"-r","24","-c:v","libx264","-pix_fmt","yuv420p","-crf","18",out])

def last_frame(video, out):
    run(["ffmpeg","-y","-loglevel","error","-sseof","-0.06","-i",video,"-frames:v","1",out])

def first_frame(video, out):
    run(["ffmpeg","-y","-loglevel","error","-i",video,"-frames:v","1",out])

# ---------- scene sources ----------
def scene_clips(n):
    """ordered list of clips for scene n"""
    if n == 1: return [CLIPS + "/beat-s1c-wide.mp4"]
    if n == 2: return [CLIPS + "/beat-s2-wide.mp4"]
    if n == 3: return [CLIPS + "/S03-full.mp4"]
    arr = f"{CLIPS}/S{n:02d}-arrive.mp4"; lv = f"{CLIPS}/S{n:02d}-leave.mp4"
    out = []
    if os.path.exists(arr): out.append(arr)
    if os.path.exists(lv): out.append(lv)
    return out

def build_scene(n):
    slot = T[n-1]["duration_s"]
    seg = f"{WORK}/seg{n:02d}.mp4"
    clips = scene_clips(n)
    if not clips:
        print(f"scene {n}: NO CLIPS"); return None
    joined = clips[0] if len(clips) == 1 else None
    if len(clips) > 1:
        joined = f"{WORK}/join{n:02d}.mp4"; concat(clips, joined)
    d = dur(joined)
    if d >= slot:
        run(["ffmpeg","-y","-loglevel","error","-i",joined,"-t",str(slot),"-r","24",
             "-c:v","libx264","-pix_fmt","yuv420p","-crf","18",seg])
    else:
        # hold the final frame to fill the slot (the pose settles)
        last_frame(joined, f"{WORK}/last{n:02d}.png")
        pad = max(0.1, round(slot - d, 2))
        tailc = f"{WORK}/tail{n:02d}.mp4"
        freeze(f"{WORK}/last{n:02d}.png", pad, tailc)
        concat([joined, tailc], seg)
    return seg

def build_turn(a, b, out):
    la, fb = f"{WORK}/la.png", f"{WORK}/fb.png"
    last_frame(a, la); first_frame(b, fb)
    run(["python3", os.path.expanduser("~/Projects/ironwood-books/marketing/video/page_turn_wide.py"),
         "--from", la, "--to", fb, "--out", out, "--frames", "24", "--fps", "24"])

def main():
    segs = []
    for n in range(1, 22):
        s = build_scene(n)
        if not s: sys.exit(f"scene {n} failed")
        segs.append(s)
        print(f"scene {n:02d} built ({dur(s):.2f}s of {T[n-1]['duration_s']}s)")

    # gaps: 0.35s hold + 1.0s turn + 0.45s hold = 1.8s
    gaps = []
    for i in range(20):
        tn = f"{WORK}/turn{i+1:02d}.mp4"
        build_turn(segs[i], segs[i+1], tn)
        hold_a = f"{WORK}/holdA{i+1:02d}.mp4"; hold_b = f"{WORK}/holdB{i+1:02d}.mp4"
        last_frame(segs[i], f"{WORK}/la{i:02d}.png"); first_frame(segs[i+1], f"{WORK}/fb{i:02d}.png")
        freeze(f"{WORK}/la{i:02d}.png", 0.35, hold_a)
        freeze(f"{WORK}/fb{i:02d}.png", 0.45, hold_b)
        gap = f"{WORK}/gap{i+1:02d}.mp4"; concat([hold_a, tn, hold_b], gap)
        gaps.append(gap)
        print(f"turn {i+1:02d} -> {i+2:02d} built")

    lead = f"{WORK}/lead.mp4"
    first_frame(segs[0], f"{WORK}/f0.png"); freeze(f"{WORK}/f0.png", LEAD_IN, lead)
    tail = f"{WORK}/tail.mp4"
    last_frame(segs[-1], f"{WORK}/fN.png"); freeze(f"{WORK}/fN.png", TAIL, tail)

    order = [lead]
    for i, s in enumerate(segs):
        order.append(s)
        if i < len(gaps): order.append(gaps[i])
    order.append(tail)
    video = WORK + "/video.mp4"; concat(order, video)
    print("video timeline:", dur(video), "s")

    # audio: narration + a page-turn sfx at each gap
    t = LEAD_IN + T[0]["duration_s"]
    starts, acc = [], LEAD_IN
    for i in range(20):
        acc += T[i]["duration_s"]
        starts.append(round(acc + 0.35, 2))   # turn starts 0.35s into the gap
        acc += GAP
    inputs, fc, amix = [], [], []
    inputs += ["-i", NARR]
    for k, st in enumerate(starts, start=1):
        inputs += ["-i", SFX]
        fc.append(f"[{k}:a]volume=0.8,adelay={int(st*1000)}|{int(st*1000)}[s{k}]")
        amix.append(f"[s{k}]")
    filt = ";".join(fc) + f";[0:a]{''.join(amix)}amix=inputs={len(starts)+1}:duration=first:normalize=0,apad[a]"
    audio = WORK + "/audio.m4a"
    run(["ffmpeg","-y","-loglevel","error"] + inputs + ["-filter_complex", filt, "-map","[a]",
         "-t", str(dur(video)), "-c:a","aac","-b:a","160k", audio])
    total = dur(video)
    run(["ffmpeg","-y","-loglevel","error","-i",video,"-i",audio,"-map","0:v","-map","1:a",
         "-t",str(total),"-c:v","copy","-c:a","aac","-b:a","160k","-movflags","+faststart", OUT])
    print("FINAL:", OUT, f"{os.path.getsize(OUT)/1e6:.1f} MB", dur(OUT), "s")
    print("turn start times:", starts[:6], "...")

if __name__ == "__main__":
    main()
