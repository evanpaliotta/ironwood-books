#!/usr/bin/env python3
"""regen_batch.py — regenerate scenes as ONE continuous clip each, from the still.

Prompts are ASSEMBLED from the per-scene manifest (wardrobe / population / static anchors /
motion), never hand-written. Two build routes:
  grok   : one forward generation starting at the still (default)
  kling  : one forward generation from a SYNTHESIZED earlier frame to the still (scene 4's
           climb) or from an earlier to a later frame (scene 5's through-roll) — the still
           then occurs naturally inside the clip, so there is no join at all.

usage: regen_batch.py 4 5 6 7 8
"""
import base64, json, os, subprocess, sys, time

TOKEN = open(os.path.expanduser("~/Projects/ironwood-book-factory/reference-implementation/.replicate_token")).read().strip()
REV = "/Users/evanpaliotta/Projects/ironwood-series-archive/book-01-adventures/video/review"
ASP = REV + "/aspect"; OUT = REV + "/regen"
os.makedirs(OUT, exist_ok=True)
T = {s["scene"]: s for s in json.load(open(REV + "/narration-timings-v3-final.json"))}

WARDROBE = ("The little boy wears his yellow-and-white horizontally striped short-sleeve shirt, blue jeans rolled at the cuff, and brown boots. ")
CAM = (" Camera completely static and locked, no zoom, no pan. Preserve the illustration's exact art style, colors, composition and proportions. "
       "His mouth stays relaxed; the characters do not speak or mouth words.")

# scene: (route, population, static anchors, motion)
M = {
 3:("grok","Exactly one child — only the little boy — and exactly one orange tabby cat. No other people, no other animals.",
    "the sunflowers, red poppies, pine trees, the mountain ahead, the path and the sky",
    "Crouched, he strokes the cat's chin and it leans into his hand; he touches a yellow flower beside him; butterflies flutter past; then he straightens up, glances toward the mountain peak and walks away from the viewer along the path, with the orange cat trotting along behind him."),
 4:("kling","Exactly one child — only the little boy — and exactly one orange tabby cat. No other people, no other animals.",
    "the summit rock, the leaning black tire, the hills, the coastline and the sky",
    "He climbs up the last rocks onto the summit with the cat beside him, plants his feet on the rock, stands up and raises both arms high in triumph, then lowers his arms and kneels to stroke the cat."),
 5:("kling","Exactly one child — only the little boy. No animals, no other people.",
    "the grassy slope, the mountains behind, the distant barn and the sky",
    "The black tire with the little boy riding inside rolls down the grassy slope from far away, spinning faster as it comes through the middle of the frame and continues past and away toward the beach in the distance, grass flying. He stays in the tire the whole time and never gets out."),
 6:("grok","Exactly one child — only the little boy — plus two seagulls. No other people, no other animals.",
    "the leaning wooden board, the rocks, the headland, the sea and the clouds",
    "The wave crashes and foams toward his feet, then recedes; the two seagulls lift off and pass him; he steps back from the water and stands with a hand to his chin, looking out at the ocean, puzzled."),
 7:("grok","Exactly one child — only the little boy. No animals, no other people.",
    "the rock ledge, the sea, the cliffs, the distant mountains and the sunlit clouds",
    "He turns his head slowly, taking in the whole coast; then he sits down on the ledge with his chin resting on his hand; then he picks a small flower and holds it up against the view, comparing them."),
 8:("grok","Exactly one child — only the little boy. No animals, no other people.",
    "the waterfall, the pool, the jungle foliage and the rocks",
    "The falls pour down with mist drifting; he crouches at the edge of the pool and dips one hand into the water; he looks from the pool up to the falling water and around at the jungle; then he stands and wipes his hand on his jeans."),
 9:("grok","Exactly one child — only the little boy — plus two seagulls. No other people.",
    "the sand, the sea, the low sun and the distant hills",
    "Sitting cross-legged with his chin resting on his fist, he tilts his head as his thoughts whirl; he draws a question mark in the sand with one finger; then he straightens up, lifts his chin and nods once. The waves lap and the gulls glide."),
 10:("grok","Exactly one child — only the little boy. No other people, no other animals. Exactly one coconut.",
     "the palms, the sand, the sea and the clouds",
     "He walks along the sand under the palms, glancing up at the coconuts; a single coconut detaches and falls through the air; he steps back startled with his arms up; the coconut thumps into the sand; he leans in to inspect it and looks up at the palm, puzzled."),
 11:("grok","Exactly one child — only the little boy. Exactly two bees. No other people or animals.",
     "the meadow, the tall grass, the planet in the dusk sky and the low sun",
     "He stands with his hands in his pockets looking up at the planet; he points up at it; the two bees drift in and circle near his head as he follows them with his eyes and paces a few slow thoughtful steps."),
 12:("grok","Exactly one child — only the little boy — plus one seagull. No other people, no other animals.",
     "the dune path, the dune grass, the sea behind him and the sunset sky",
     "He walks toward the viewer along the dune path, shoulders slumped and looking sad; he stops and cries out with his arms dropping to his sides; then his face softens, he lifts his head, smiles faintly and keeps walking toward the viewer."),
 13:("grok","Exactly one child — only the little boy. No animals, no other people.",
     "the wooden signpost, the dark trees, the glowing eyes, the fireflies and the path",
     "He stands at the signpost and reads it; then he turns away and walks AWAY from the viewer, up the path deeper into the darkness, getting smaller as he goes. He never walks toward the viewer."),
 14:("grok","Exactly one child — only the little boy — plus exactly two owls, one bat and one snake. No other people or animals.",
     "the moon, the trees, the fireflies and the trail",
     "He walks slowly toward the viewer along the moonlit trail; the two owls' heads turn to follow him; the bat flutters past; the snake slides across the path in front of him; he freezes, edges carefully around it, and keeps walking slowly toward the viewer."),
 15:("grok","Exactly one child — only the little boy. No animals, no other people.",
     "the tree stump, the glowing book, the small sign and the dark trees",
     "He leans in over the glowing book on the stump, reaches out with both hands, opens it, and warm light spills upward over his face as he stares in wonder."),
 16:("grok","Exactly one child — only the little boy — plus exactly one parrot and one lion cub. No other people or animals.",
     "the tall stacks of books on both sides, the easel with its painting, the globe, the stream, the moon, the stars and the jungle foliage",
     "He steps forward through the stream looking around in awe; the parrot flutters across to another stack of books; the lion cub tilts its head at him; he turns slowly on the spot taking everything in, then looks up as the stars twinkle."),
 17:("grok","Exactly one child — only the little boy. No animals, no other people.",
     "the room walls, the light switch, the door frame and the vista beyond the door",
     "He grips the door handle, pushes the door wide open, steps forward out over the threshold, and stands looking into the starfield as the nebula turns and his hair stirs in the wind."),
 18:("grok","Exactly one child — only the little boy — plus exactly one ladybug and one monarch butterfly. No other people or animals.",
     "the sunflowers, the garden path and the grass",
     "He crouches with the magnifying glass held up to his eye and goes still; the ladybug walks onto his finger and he lifts it to eye level, smiling; behind him a monarch butterfly lands on a sunflower and slowly opens its wings."),
 19:("grok","Exactly one child — only the little boy. No animals, no other people.",
     "the telescope, the sunflower field, Saturn and the Milky Way",
     "He kneels at the telescope and peers through the eyepiece; then he leans back with wide eyes; then he points up at Saturn with a grin as the stars twinkle."),
 20:("grok","Exactly one child — only the little boy — plus exactly one puppy, one piglet and one small brown animal on the grass. No other people or animals.",
     "the wooden bed, the red barn with its weathervane, the full moon, the stars and the grass",
     "He walks away from the viewer up the path toward the bed under the moon; he reaches the bed and leaps in under the quilt with a bounce; he settles with his hands behind his head looking up at the moon; the animals curl up on the grass beside the bed."),
 21:("grok","Exactly one child — only the little boy, asleep — plus exactly one rooster on the bedpost, three puppies and one piglet asleep on the grass. No other people or animals.",
     "the wooden bed, the rooster, the patchwork quilt, the full moon, the stars and the grass",
     "He is asleep; his chest rises and falls slowly and the quilt shifts gently; the puppies and piglet breathe in their sleep; the rooster ruffles its feathers and tucks its head down; fireflies drift and the stars turn slowly."),
}

def b64(p): return "data:image/png;base64," + base64.b64encode(open(p,"rb").read()).decode()
def prompt(n):
    route, pop, static, motion = M[n]
    return (WARDROBE + pop + " These stay exactly as they are and never appear, move or change: " + static + ". "
            "Nothing new appears in the background at any moment. " + motion + CAM)

def run(model, payload, tag, out, timeout=900):
    json.dump({"input": payload}, open(f"/tmp/rg_{tag}.json","w"))
    r = subprocess.run(["curl","-s","-X","POST","-H","Authorization: Bearer "+TOKEN,"-H","Content-Type: application/json",
        "-H","User-Agent: hermes","--data-binary",f"@/tmp/rg_{tag}.json",
        f"https://api.replicate.com/v1/models/{model}/predictions"], capture_output=True, text=True)
    d = json.loads(r.stdout)
    if "id" not in d: print(f"  {tag} SUBMIT FAIL {str(d)[:180]}"); return False
    t0 = time.time()
    while time.time()-t0 < timeout:
        r = subprocess.run(["curl","-s","-H","Authorization: Bearer "+TOKEN,"-H","User-Agent: hermes",
            f"https://api.replicate.com/v1/predictions/{d['id']}"], capture_output=True, text=True)
        d = json.loads(r.stdout)
        if d.get("status") in ("succeeded","failed","canceled"): break
        time.sleep(8)
    o = d.get("output"); url = o if isinstance(o,str) else (o[0] if isinstance(o,list) and o else None)
    if not url: print(f"  {tag} FAILED {d.get('status')} {str(d.get('error'))[:120]}"); return False
    subprocess.run(["curl","-sL","-o",out,url]); print(f"  {tag} ok {os.path.getsize(out)}"); return True

def synth(n, note, name):
    """synthesize an earlier/later frame from the scene's art"""
    src = f"{ASP}/S{n:02d}-wide.png"
    p = (f"Show the same scene {note} Same characters, same wardrobe (yellow-and-white striped shirt, blue jeans, brown boots), "
         "same art style, palette and lighting. Exactly one child, no other people." + CAM)
    return run("black-forest-labs/flux-kontext-pro",
               {"input_image": b64(src), "prompt": p, "aspect_ratio": "16:9", "output_format": "png"},
               f"{n}synth", f"{ASP}/S{n:02d}-{name}.png", timeout=420)

def main():
    for n in [int(x) for x in sys.argv[1:]]:
        route, *_ = M[n]
        slot = T[n]["duration_s"]
        out = f"{OUT}/S{n:02d}.mp4"
        print(f"scene {n} [{route}] slot {slot}s -> {out}")
        if route == "grok":
            dur = max(5, min(15, int(round(slot)) + 1))
            run("xai/grok-imagine-video",
                {"image": b64(f"{ASP}/S{n:02d}-wide.png"), "prompt": prompt(n), "duration": dur,
                 "resolution": "720p", "aspect_ratio": "16:9"}, f"{n}g", out)
        else:
            if n == 4:
                synth(4, "a few seconds EARLIER in time: the little boy is below the summit rock, part-way up the last rocks, reaching up to climb, the orange cat close beside him, the summit rock above him with the black tire leaning on top.",
                      "pre", )
                start = f"{ASP}/S04-pre.png"; end = f"{ASP}/S04-wide.png"
            else:
                start = f"{ASP}/S05-prearrival.png" if os.path.exists(f"{ASP}/S05-prearrival.png") else None
                synth(5, "a few seconds LATER in time: the black tire with the boy inside is small in the distance at the far right of the frame, rolling away down the slope toward the bright beach and the sea at the horizon.",
                      "postend")
                end = f"{ASP}/S05-postend.png"
            if start and os.path.exists(start) and os.path.exists(end):
                run("kwaivgi/kling-v2.5-turbo-pro",
                    {"start_image": b64(start), "end_image": b64(end), "prompt": prompt(n),
                     "duration": 10, "aspect_ratio": "16:9"}, f"{n}k", out)
            else:
                print(f"  scene {n}: missing start/end frame, skipped")

if __name__ == "__main__":
    main()
