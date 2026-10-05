#!/usr/bin/env python3
"""stage_a_wide_art.py — re-block scenes 3-21 to 16:9 from their real art.

Each prompt is written FROM the scene's inventory (what the illustration actually contains),
never from memory of the story. Output: aspect/S{nn}-wide.png
"""
import base64, json, os, subprocess, time, sys

TOKEN = open(os.path.expanduser("~/Projects/ironwood-book-factory/reference-implementation/.replicate_token")).read().strip()
ILL = "/Users/evanpaliotta/Projects/ironwood-series-archive/book-01-adventures/illustrations/final"
OUT = "/Users/evanpaliotta/Projects/ironwood-series-archive/book-01-adventures/video/review/aspect"

# scene -> (source file, inventory sentence for the prompt)
SCENES = {
 3: ("scene-03-meets-miss-kitty.png", "a small boy in a yellow-striped shirt and jeans crouching on a mountain path, petting an orange tabby cat; tall sunflowers, red poppies and lavender around them; two butterflies; pine trees and a mountain ahead; blue sky"),
 4: ("scene-04-mountaintop.png", "a small boy standing on a rocky summit with both arms raised in triumph; an orange tabby cat sitting beside him; a single black tire leaning nearby; green hills, a coastline and a red barn far below; blue sky with soft clouds"),
 5: ("scene-05-rolling-tire.png", "a small boy riding inside a single black tire as it rolls down a grassy hillside, arms up and laughing, motion and kicked-up grass; mountains behind"),
 6: ("scene-06-beach-waves.png", "a sandy beach with one large wave breaking and foaming; a small boy standing and watching the wave; seagulls; scattered rocks; soft cloudy sky"),
 7: ("scene-07-sea-and-mountains.png", "a small boy standing on a rocky ledge looking out over the coast: the ocean, cliffs, distant blue mountains, sunlit clouds"),
 8: ("scene-08-waterfall.png", "a jungle waterfall pouring into a pool with mist rising; a small boy standing on the rocks at the pool looking up at the falls; dense green foliage"),
 9: ("scene-09-deep-in-thought.png", "a small boy sitting cross-legged on the sand with his chin resting on his fist, thoughtful; ocean waves, a low sun, two seagulls and distant hills"),
 10: ("scene-10-falling-coconut.png", "a sandy beach with tall palm trees; a single coconut falling through the air with small motion marks; a small boy below looking up startled; the sea and clouds behind"),
 11: ("scene-11-big-questions.png", "a golden meadow at sunset with tall grass; a small boy standing with his hands in his pockets, looking up; two bees; a planet visible in the dusk sky; a low warm sun"),
 12: ("scene-12-walking-away-sad.png", "a sandy dune path at sunset; a small boy walking toward the viewer looking sad and tired; dune grass; a seagull; the sea behind him"),
 13: ("scene-13-spooky-sign.png", "a dark forest path at night with a wooden arrow sign on a post pointing to the right; a small boy standing wide-eyed; glowing eyes in the dark trees; fireflies; flowers at the path edge"),
 14: ("scene-14-spooky-trail.png", "a moonlit forest trail at night; a small boy walking toward the viewer; two owls perched in the branches; one bat flying; one snake on the path; a big moon; fireflies"),
 15: ("scene-15-finds-book.png", "a forest clearing at night with an open glowing book resting on a tree stump; a small boy leaning toward it reaching out; a small sign on the left; trees around"),
 16: ("scene-16-world-of-wonders.png", "a magical clearing: huge stacks of books on both sides; a parrot perched on the left stack; a lion cub sitting; an easel holding a painting of a waterfall; a globe; a stream at the boy's feet; a small boy standing at the centre; a moon and stars in the sky; jungle foliage"),
 17: ("scene-17-door-to-magic.png", "inside a plain room with blue walls, an open wooden door; a small boy holding the door handle and looking out; a light switch on the wall; beyond the door a fantastical vista of nebula sky, cliffs, a waterfall and a green valley with a winding river"),
 18: ("scene-18-magnifying-glass.png", "a garden path with tall sunflowers; a small boy crouching and holding a magnifying glass up to his eye; a ladybug in front of him; a monarch butterfly resting on a flower; other flowers and grass"),
 19: ("scene-19-telescope.png", "a sunflower field at dusk; a small boy crouching at a telescope; Saturn and the Milky Way in the darkening sky; hills behind"),
 20: ("scene-20-walking-home.png", "night on a grassy field with a wooden bed standing outdoors and a red barn with a weathervane; a small boy walking away up a dirt path with his back to the viewer; a puppy, a small brown animal and a piglet on the grass; a full moon and stars"),
 21: ("scene-21-asleep-dreaming.png", "night on a grassy field; a small boy asleep in a wooden bed with a patchwork quilt; a rooster perched on the bedpost; three puppies and a piglet asleep on the grass; a full moon and stars"),
}
TEMPLATE = ("Re-compose this exact scene as a wider 16:9 cinematic frame for an animated film. "
            "Keep exactly the same moment, the same characters and the same art style: {inv}. "
            "The camera is pulled back to show more of the setting on both sides, with generous space around the characters. "
            "Match the original illustration's exact painterly children's-book style, palette, lighting and proportions. "
            "No new characters, no new animals, no added objects, no added text.")

def b64(p): return "data:image/png;base64," + base64.b64encode(open(p,"rb").read()).decode()

def submit(n, src):
    payload = {"input": {"input_image": b64(ILL+"/"+src), "prompt": TEMPLATE.format(inv=SCENES[n][1]),
                         "aspect_ratio": "16:9", "output_format": "png"}}
    fn = f"/tmp/wide_{n}.json"
    json.dump(payload, open(fn,"w"))
    r = subprocess.run(["curl","-s","-X","POST","-H","Authorization: Bearer "+TOKEN,"-H","Content-Type: application/json",
        "-H","User-Agent: hermes","--data-binary",f"@{fn}",
        "https://api.replicate.com/v1/models/black-forest-labs/flux-kontext-pro/predictions"], capture_output=True, text=True)
    d = json.loads(r.stdout)
    return d.get("id")

def wait(pid, timeout=420):
    t0=time.time()
    while time.time()-t0<timeout:
        r = subprocess.run(["curl","-s","-H","Authorization: Bearer "+TOKEN,"-H","User-Agent: hermes",
            f"https://api.replicate.com/v1/predictions/{pid}"],capture_output=True,text=True)
        d = json.loads(r.stdout)
        if d.get("status") in ("succeeded","failed","canceled"): return d
        time.sleep(5)
    return {"status":"timeout"}

only = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else sorted(SCENES)
for n in only:
    src = SCENES[n][0]
    pid = submit(n, src)
    if not pid:
        print(f"S{n:02d} SUBMIT FAIL"); continue
    d = wait(pid)
    o = d.get("output")
    url = o if isinstance(o,str) else (o[0] if isinstance(o,list) and o else None)
    if d.get("status") != "succeeded" or not url:
        print(f"S{n:02d} {d.get('status')} {str(d.get('error'))[:120]}"); continue
    fn = f"{OUT}/S{n:02d}-wide.png"
    subprocess.run(["curl","-sL","-o",fn,url])
    print(f"S{n:02d} ok {os.path.getsize(fn)}")
