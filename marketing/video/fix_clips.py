#!/usr/bin/env python3
"""fix_clips.py — render the missing scene 5 departure, and re-render scene 6's clips
from the corrected art (no invented board)."""
import base64, json, os, subprocess, time

TOKEN = open(os.path.expanduser("~/Projects/ironwood-book-factory/reference-implementation/.replicate_token")).read().strip()
REV = "/Users/evanpaliotta/Projects/ironwood-series-archive/book-01-adventures/video/review"
ASP = REV + "/aspect"; CLIPS = REV + "/clips"
CAM = " Camera completely static and locked, no zoom, no pan. Preserve the illustration's exact art style, colors and composition."

def b64(p): return "data:image/png;base64," + base64.b64encode(open(p,"rb").read()).decode()

def grok(art, prompt, dur, out, tag):
    json.dump({"input": {"image": b64(art), "prompt": prompt + CAM, "duration": dur,
                         "resolution": "720p", "aspect_ratio": "16:9"}}, open(f"/tmp/fx_{tag}.json","w"))
    r = subprocess.run(["curl","-s","-X","POST","-H","Authorization: Bearer "+TOKEN,"-H","Content-Type: application/json",
        "-H","User-Agent: hermes","--data-binary",f"@/tmp/fx_{tag}.json",
        "https://api.replicate.com/v1/models/xai/grok-imagine-video/predictions"], capture_output=True, text=True)
    d = json.loads(r.stdout)
    if "id" not in d: print(tag, "SUBMIT FAIL", str(d)[:150]); return
    while True:
        r = subprocess.run(["curl","-s","-H","Authorization: Bearer "+TOKEN,"-H","User-Agent: hermes",
            f"https://api.replicate.com/v1/predictions/{d['id']}"],capture_output=True,text=True)
        d = json.loads(r.stdout)
        if d.get("status") in ("succeeded","failed","canceled"): break
        time.sleep(8)
    o = d.get("output"); url = o if isinstance(o,str) else (o[0] if isinstance(o,list) and o else None)
    if not url: print(tag, "FAILED", d.get("status"), str(d.get("error"))[:100]); return
    subprocess.run(["curl","-sL","-o",out,url]); print(tag, "ok", os.path.getsize(out))

# 1) scene 5 departure (was never rendered): the tire slows, he climbs out and looks back up
grok(f"{ASP}/S05-wide.png",
     "The tire keeps rolling down the grassy slope to the right and gradually slows, then stops; the little boy climbs out of the tire, wobbles a little, and looks back up the long hill with a puzzled face.",
     6, f"{CLIPS}/S05-leave.mp4", "s05leave")

# 2) scene 6, from the corrected art (no board on the sand)
grok(f"{ASP}/S06-wide-fixed.png",
     "He steps back from the foaming water as the wave recedes; two seagulls lift off and pass him; he stands with a hand to his chin looking out at the ocean, puzzled.",
     6, f"{CLIPS}/S06-leave.mp4", "s06leave")
grok(f"{ASP}/S06-wide-fixed.png",
     "He turns and walks away from the water, back up the beach over the sand and out of the frame.",
     5, f"{CLIPS}/S06-arrive-raw.mp4", "s06arr")
# reverse the arrival so it ENDS on the still
subprocess.run(["ffmpeg","-y","-loglevel","error","-i",f"{CLIPS}/S06-arrive-raw.mp4","-vf","reverse","-an",
                "-c:v","libx264","-pix_fmt","yuv420p","-crf","18", f"{CLIPS}/S06-arrive.mp4"], check=True)
print("scene 6 arrival reversed into place")
print("fixes complete")
