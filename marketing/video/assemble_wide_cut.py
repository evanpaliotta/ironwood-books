#!/usr/bin/env python3
"""assemble_wide_cut.py — wide 16:9 cut assembled on the NARRATION CLOCK.

Inputs are narration-timings-v3-final.json (master clock) + per-scene wide clips +
the wide page turn (/tmp/turnw.mp4). Timeline:
  0.00-13.33  scene 1 (clip, trimmed to slot)
  13.68-14.68 page turn (inside the 1.8s pause)
  15.13-27.58 scene 2 (clip, trimmed to slot)
Audio: the v3-final narration, untouched.
"""
import json, os, subprocess, sys

REV = "/Users/evanpaliotta/Projects/ironwood-series-archive/book-01-adventures/video/review"
T = json.load(open(REV + "/narration-timings-v3-final.json"))
s1, s2 = T[0], T[1]
S1_END = s1["start_s"] + s1["duration_s"]      # 13.33
S2_START = s2["start_s"]                        # 15.13
S2_END = S2_START + s2["duration_s"]            # 27.58
TURN_IN, TURN_OUT = S1_END + 0.35, S2_START - 0.45
END = S2_END + 1.2

work = "/tmp/widecut"; os.makedirs(work, exist_ok=True)
OUT = REV + "/clips/wide-cut-v3.mp4"
turn = "/tmp/ptw2.mp4"
c1 = REV + "/clips/beat-s1c-wide.mp4"
c2 = REV + "/clips/beat-s2-wide.mp4"
narr = REV + "/Curious Kid Book 1 narration - Marcus (v3-final).m4a"

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FAIL:", " ".join(cmd)[:200]); print(r.stderr[-1500:]); sys.exit(1)

def seg(src, out, dur, still=None):
    if still:
        run(["ffmpeg","-y","-loglevel","error","-loop","1","-framerate","24","-i",still,
             "-t",str(dur),"-r","24","-c:v","libx264","-pix_fmt","yuv420p","-crf","18",out])
    else:
        run(["ffmpeg","-y","-loglevel","error","-i",src,"-t",str(dur),"-r","24",
             "-c:v","libx264","-pix_fmt","yuv420p","-crf","18",out])

seg(c1, work+"/seg1.mp4", S1_END)                       # scene 1 trimmed to its slot
seg(turn, work+"/seg2.mp4", TURN_OUT - TURN_IN)         # the turn (1.0s)
seg(c2, work+"/seg3.mp4", S2_END - S2_START)            # scene 2 trimmed to slot
seg(None, work+"/seg4.mp4", END - S2_END, still=REV+"/aspect/S2-wide-final.png")  # settle hold

open(work+"/list.txt","w").write("".join(f"file '{work}/seg{i}.mp4'\n" for i in (1,2,3,4)))
run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",work+"/list.txt",
     "-c:v","libx264","-pix_fmt","yuv420p","-crf","18", work+"/video.mp4"])

# audio: narration + page-turn sfx at TURN_IN
run(["ffmpeg","-y","-loglevel","error","-i",narr,"-t",str(END),"-c:a","aac","-b:a","160k", work+"/vo.m4a"])
run(["ffmpeg","-y","-loglevel","error","-i",work+"/video.mp4","-i",work+"/vo.m4a","-i",REV+"/sfx/page-turn-cc0.mp3",
     "-filter_complex",f"[2:a]volume=0.85,adelay={int(TURN_IN*1000)}|{int(TURN_IN*1000)}[s];[1:a][s]amix=inputs=2:duration=first:normalize=0[a]",
     "-map","0:v","-map","[a]","-c:v","copy","-c:a","aac","-b:a","160k","-movflags","+faststart", OUT])
d = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",OUT],
                   capture_output=True, text=True).stdout.strip()
print("done:", OUT, os.path.getsize(OUT), "bytes,", d, "s")
print(f"clock: scene1 0-{S1_END:.2f} | turn {TURN_IN:.2f}-{TURN_OUT:.2f} | scene2 {S2_START:.2f}-{S2_END:.2f}")
