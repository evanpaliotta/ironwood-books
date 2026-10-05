#!/usr/bin/env python3
"""stage_b_clips.py — render the arrive + leave clips for scenes 3-21.

For every scene we render the LEAVE forward from the still (Grok), and the ARRIVE by
generating the reverse action from the still and playing that clip BACKWARDS — so the
arrival lands exactly on the still by construction. Scenes whose line opens on the art's
moment (3) have no arrival at all.

Output: clips/S{nn}-leave.mp4, clips/S{nn}-arrive.mp4 (already reversed)
"""
import base64, json, os, subprocess, time, sys

TOKEN = open(os.path.expanduser("~/Projects/ironwood-book-factory/reference-implementation/.replicate_token")).read().strip()
REV = "/Users/evanpaliotta/Projects/ironwood-series-archive/book-01-adventures/video/review"
ART = REV + "/aspect"
CLIPS = REV + "/clips"
os.makedirs(CLIPS, exist_ok=True)
T = {s["scene"]: s for s in json.load(open(REV + "/narration-timings-v3-final.json"))}

CAM = " Camera completely static and locked, no zoom, no pan. Preserve the illustration's exact art style, colors and composition."

# scene: (arrive_away_prompt or None, leave_prompt)
P = {
 3: (None, "He straightens up from his crouch, glances up toward the mountain peak, and sets off walking along the path away from the camera, the orange tabby cat trotting along the path behind him. Exactly one cat, no other animals."),
 4: ("He lowers his arms, climbs back down off the summit rocks away from the camera, the cat following him.",
     "He lowers his arms, kneels down and pets the cat beside him, then stands with his hands on his hips looking out over the hills and the coastline below, and sweeps one arm across the whole view."),
 5: (None,  # arrival handled separately (Kling)
     "The tire keeps rolling down the slope to the right and slows, then stops; the boy climbs out of the tire, wobbles a little and looks back up the long hill with a puzzled face."),
 6: ("He turns and walks back up the beach away from the water, over the sand and out of the frame.",
     "He steps back from the foaming water as the wave recedes, seagulls lift off and pass him, and he stands with a hand to his chin looking out at the ocean."),
 7: ("He turns away from the view, steps back down off the rocky ledge away from the camera and out of the frame.",
     "He turns his head slowly taking in the coast, sits down on the ledge with his chin resting on his hand, then picks a small flower and holds it up against the view, comparing them."),
 8: ("He turns and walks back along the rocks away from the waterfall, out of the frame.",
     "He crouches at the edge of the pool, dips one hand into the water, looks from the pool up to the falling water and around at the jungle, then stands and wipes his hand on his jeans."),
 9: ("He stands up from the sand and walks away along the beach away from the camera, out of the frame.",
     "He tilts his head as his thoughts whirl, draws a question mark in the sand with one finger, then straightens, lifts his chin and nods once."),
 10:("He turns and walks back along the sand under the palms away from the camera, out of the frame.",
     "The coconut drops and thumps into the sand; he steps back startled, then leans in to inspect it and looks up at the palm with a puzzled face. Exactly one coconut."),
 11:("He turns and walks back out of the meadow away from the camera, out of the frame.",
     "He points up at the planet in the sky, then the two bees drift around near his head as he follows them with his eyes and paces a few slow thoughtful steps. Exactly two bees."),
 12:("He turns and walks back up the path away from the camera, over the dune and out of the frame.",
     "He stops dead and cries out with his arms dropping to his sides, then his face softens, he lifts his head, smiles faintly and walks on toward the camera."),
 13:("He turns and walks briskly back along the dark path away from the camera, out of the frame.",
     "He reads the sign, follows where it points with his eyes, swallows, takes a breath and steps forward along the dark path toward the camera. Exactly one sign."),
 14:("He turns and walks slowly back down the trail away from the camera, into the dark trees.",
     "A snake slides across the path in front of him; he freezes, edges around it, glances back over his shoulder, then keeps walking slowly toward the camera. Exactly one snake, two owls, one bat."),
 15:("He turns and walks back down the trail away from the stump, into the dark trees.",
     "He opens the glowing book with both hands and warm light spills upward over his face as he stares in wonder."),
 16:("He turns and steps back out through the stream, walking away from the camera into the foliage.",
     "The parrot flutters across to another stack of books and the lion cub tilts its head; the boy turns slowly on the spot taking it all in, then looks up as the stars twinkle. Exactly one parrot, one lion cub."),
 17:("He steps back from the door, turns and walks away across the room, out of frame.",
     "He pushes the door wide open and steps forward out over the threshold; the starfield turns slowly and his hair stirs in the wind."),
 18:("He stands up and walks back down the garden path away from the camera, out of frame.",
     "He pauses and goes still; the ladybug walks onto his finger and he lifts it to eye level smiling, while a monarch butterfly lands on the sunflower behind him and opens its wings. Exactly one ladybug, one butterfly."),
 19:("He stands up from the telescope, picks it up and carries it away across the field away from the camera.",
     "He leans back from the eyepiece with wide eyes, then points up at Saturn with a grin as the stars twinkle."),
 20:("He turns and walks back down the path away from the bed toward the dunes, the animals following him.",
     "He reaches the bed, leaps in under the quilt with one bounce, settles with his hands behind his head looking up at the moon, and the animals curl up on the grass beside the bed."),
 21:("He sits up in the bed and swings his legs out, about to get out.",
     "Everything breathes softly: his chest rises and falls, the puppies and piglet stir in their sleep, the rooster ruffles its feathers and tucks its head down, the stars twinkle and fireflies drift."),
}

def b64(p): return "data:image/png;base64," + base64.b64encode(open(p,"rb").read()).decode()

def submit_grok(img, prompt, dur, tag):
    fn = f"/tmp/g_{tag}.json"
    json.dump({"input": {"image": b64(img), "prompt": prompt + CAM, "duration": dur,
                         "resolution": "720p", "aspect_ratio": "16:9"}}, open(fn,"w"))
    r = subprocess.run(["curl","-s","-X","POST","-H","Authorization: Bearer "+TOKEN,"-H","Content-Type: application/json",
        "-H","User-Agent: hermes","--data-binary",f"@{fn}",
        "https://api.replicate.com/v1/models/xai/grok-imagine-video/predictions"], capture_output=True, text=True)
    d = json.loads(r.stdout)
    if "id" not in d: print("SUBMIT FAIL", tag, str(d)[:150]); return None
    return d["id"]

def wait(pid, timeout=600):
    t0=time.time()
    while time.time()-t0<timeout:
        r = subprocess.run(["curl","-s","-H","Authorization: Bearer "+TOKEN,"-H","User-Agent: hermes",
            f"https://api.replicate.com/v1/predictions/{pid}"],capture_output=True,text=True)
        d = json.loads(r.stdout)
        if d.get("status") in ("succeeded","failed","canceled"): return d
        time.sleep(8)
    return {"status":"timeout"}

def save(d, fn):
    o = d.get("output"); url = o if isinstance(o,str) else (o[0] if isinstance(o,list) and o else None)
    if not url: return False
    subprocess.run(["curl","-sL","-o",fn,url]); return True

only = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else [s for s in P if s != 5]
for n in only:
    art = f"{ART}/S{n:02d}-wide.png"
    if not os.path.exists(art):
        print(f"S{n:02d} NO ART"); continue
    slot = T[n]["duration_s"]
    leave_d = max(5, min(9, round(slot*0.55)))
    arr_d = max(4, min(7, round(slot*0.45)))
    away, leave = P[n]
    if leave:
        pid = submit_grok(art, leave, leave_d, f"{n}leave")
        if pid and save(wait(pid), f"{CLIPS}/S{n:02d}-leave.mp4"):
            print(f"S{n:02d} leave ok")
        else:
            print(f"S{n:02d} leave FAIL")
    if away:
        pid = submit_grok(art, away, arr_d, f"{n}arr")
        raw = f"/tmp/S{n:02d}-arrive-raw.mp4"
        if pid and save(wait(pid), raw):
            # play it backwards so the arrival ENDS exactly on the still
            subprocess.run(["ffmpeg","-y","-loglevel","error","-i",raw,"-vf","reverse","-an",
                            "-c:v","libx264","-pix_fmt","yuv420p","-crf","18", f"{CLIPS}/S{n:02d}-arrive.mp4"], check=True)
            print(f"S{n:02d} arrive ok (reversed)")
        else:
            print(f"S{n:02d} arrive FAIL")
print("stage B complete")
