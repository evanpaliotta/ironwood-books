#!/usr/bin/env python3
"""manifest.py — the single source of truth for the regeneration.

ONE MODEL (Grok Imagine), ONE METHOD (one clip per scene, beginning on the still's pose,
playing forward, no joins, no reversal, no holds). The prompt for every scene is ASSEMBLED
from this manifest — never hand-written — so no rule depends on memory mid-run.

Fields per scene:
  slot      narration slot in seconds (from narration-timings-v3-final.json)
  dur       Grok duration to request = ceil(slot) + 1 (trim back to the slot; the +1 removes
            any need for an end hold)
  start     what the ART shows — the pose the clip must begin on (verified against the art)
  beats     the ordered actions from that pose forward (one clause per beat)
  dir       expected direction of travel for the gate: approach | retreat | none
  pop       population, with counts (stated positively; no negative prompts exist)
  static    the background anchors that must not move or appear
"""
import json, math, os

TIM = "/Users/evanpaliotta/Projects/ironwood-series-archive/book-01-adventures/video/review/narration-timings-v3-final.json"
T = {s["scene"]: s["duration_s"] for s in json.load(open(TIM))}

MANIFEST = {
 1: dict(start="sitting up on the wooden bed with both arms up, friends around him",
         beats=["he lowers his arms to his sides and gives a happy smile",
                "he sniffs the fresh morning air",
                "he swings both legs off the bed and plants his feet on the grass",
                "he stands up beside the bed",
                "he steps over and pats the brown-and-white dog, and it wags its tail",
                "he glances across at the pink pig and the small piglet"],
         dir="none",
         pop="Exactly one child — only the little boy — plus one brown-and-white dog, one pink pig and one small piglet. No other people or animals. Exactly two small distant bees.",
         static="the red barn with its weathervane, the wooden bed, the tall grass, the yellow flowers and the sky"),
 3: dict(start="crouched on the path stroking an orange tabby cat, tall flowers around",
         beats=["he strokes the cat's chin and it leans into his hand",
                "he touches a yellow flower beside him",
                "the two butterflies flutter past",
                "he straightens up and glances toward the mountain peak",
                "he walks away from the viewer along the path, the orange cat trotting along behind him"],
         dir="retreat",
         pop="Exactly one child — only the little boy — with exactly one orange tabby cat. No other people or animals. Exactly two butterflies.",
         static="the sunflowers, the red poppies, the lavender, the pine trees, the mountain ahead, the path and the sky"),
 4: dict(start="standing on the summit rock with both arms raised high, the cat beside him, the tire leaning behind",
         beats=["he lowers his arms and smiles at the sunrise",
                "he kneels down and gently strokes the orange cat",
                "he stands up with his hands on his hips looking out over the valley",
                "he sweeps one arm across the whole view"],
         dir="none",
         pop="Exactly one child — only the little boy — with exactly one orange tabby cat. No other people or animals.",
         static="the summit rock, the leaning black tire, the green hills, the coastline and the red barn far below, the sky and clouds"),
 5: dict(start="riding inside the black tire, mid-slope, arms up and laughing",
         beats=["the tire keeps rolling fast down the grassy slope, spinning, grass flying",
                "it rolls on past and away toward the bright beach at the horizon, getting smaller",
                "the boy laughs and holds onto the inside of the tire as it goes"],
         dir="retreat",
         pop="Exactly one child — only the little boy. No animals, no other people.",
         static="the grassy slope, the mountains behind, the distant barn and the sky"),
 6: dict(start="standing on the dry sand with one hand resting at his chin, watching the big wave break just offshore",
         beats=["the big wave breaks and rolls in, and the white foam runs up the sand toward him",
                "the two seagulls lift off and fly past him",
                "he lowers his hand from his chin and takes one small step back, still watching the water thoughtfully"],
         dir="none",
         pop="Exactly one child — only the little boy — plus two seagulls. No other people, no other animals.",
         static="the wooden board leaning on its stick, the rocks, the headland, the sea and the clouds"),
 7: dict(start="standing on the rock ledge looking out over the coast",
         beats=["he turns his head slowly, taking in the whole coastline",
                "he sits down on the ledge with his chin resting on his hand",
                "he picks a small flower and holds it up against the view, comparing them"],
         dir="none",
         pop="Exactly one child — only the little boy. No animals, no other people.",
         static="the rock ledge, the sea, the cliffs, the distant blue mountains and the sunlit clouds"),
 8: dict(start="standing on the rocks at the pool, looking up at the waterfall",
         beats=["the falls pour down with mist drifting across",
                "he crouches at the edge of the pool and dips one hand into the water",
                "he looks from the pool up to the falling water and around at the jungle",
                "he stands and wipes his hand on his jeans"],
         dir="none",
         pop="Exactly one child — only the little boy. No animals, no other people.",
         static="the waterfall, the pool, the jungle foliage and the rocks"),
 9: dict(start="sitting cross-legged on the sand with his chin resting on his fist",
         beats=["he tilts his head to one side as his thoughts whirl",
                "he draws a question mark in the sand with one finger",
                "he straightens up, lifts his chin and nods once, hopeful",
                "the waves lap gently and the two seagulls glide overhead"],
         dir="none",
         pop="Exactly one child — only the little boy — plus two seagulls. No other people.",
         static="the sand, the sea, the low sun and the distant hills"),
 10:dict(start="standing on the sand watching the single coconut fall just in front of him, mouth open in surprise, arms at his sides",
         beats=["the coconut thumps down into the sand with a small puff",
                "he leans in and inspects the coconut closely",
                "he looks up at the palm tree, puzzled"],
         dir="none",
         pop="Exactly one child — only the little boy. No other people, no other animals. Exactly one coconut.",
         static="the palm trees, the sand, the sea and the clouds"),
 11:dict(start="standing in the meadow with his hands in his pockets, looking up at the planet",
         beats=["he points up at the planet in the dusk sky",
                "the two bees drift and hover in the air above the meadow",
                "he follows the bees with his eyes and paces a few slow thoughtful steps"],
         dir="none",
         pop="Exactly one child — only the little boy. Exactly two bees. No other people or animals.",
         static="the meadow, the tall grass, the planet in the sky and the low warm sun"),
 12:dict(start="walking toward the viewer along the dune path, shoulders slumped, looking sad",
         beats=["he trudges on a few more steps, looking down",
                "he stops and cries out, his arms dropping to his sides",
                "his face softens and he lifts his head",
                "he smiles faintly and keeps walking toward the viewer"],
         dir="approach",
         pop="Exactly one child — only the little boy — plus one seagull. No other people, no other animals.",
         static="the dune path, the dune grass, the sea behind him and the sunset sky"),
 13:dict(start="standing at the wooden signpost on the dark path, wide-eyed",
         beats=["he reads the signpost, following it with his eyes",
                "the glowing eyes blink among the dark trees and the fireflies drift",
                "he takes a breath, turns and walks AWAY from the viewer up the path into the darkness, getting smaller"],
         dir="retreat",
         pop="Exactly one child — only the little boy. No animals, no other people, no glowing creatures coming forward.",
         static="the wooden signpost, the dark trees, the glowing eyes, the fireflies and the path"),
 14:dict(start="walking toward the viewer on the moonlit trail, eyes moving nervously",
         beats=["he takes another slow step toward the viewer",
                "the two owls' heads turn to follow him and the bat flutters past",
                "the snake slides across the path in front of him; he freezes",
                "he edges carefully around the snake and keeps walking slowly toward the viewer"],
         dir="approach",
         pop="Exactly one child — only the little boy — plus exactly two owls, one bat and one snake. No other people or animals.",
         static="the big moon, the dark trees, the fireflies and the trail"),
 15:dict(start="leaning in over the glowing book resting on the tree stump, one hand reaching",
         beats=["he touches the book and opens it with both hands",
                "warm light spills upward out of the book over his face",
                "he stares into it in wonder, his eyes wide"],
         dir="none",
         pop="Exactly one child — only the little boy. No animals, no other people.",
         static="the tree stump, the small sign, the dark trees and the night sky"),
 16:dict(start="standing in the middle of the wonderland, stacks of books on both sides",
         beats=["he steps forward through the shallow stream, looking around in awe",
                "the parrot flutters across to another stack of books",
                "the lion cub tilts its head at him",
                "he turns slowly on the spot, taking in the books, the painting and the globe",
                "he looks up as the stars twinkle above"],
         dir="none",
         pop="Exactly one child — only the little boy — plus exactly one parrot and one lion cub. No other people or animals.",
         static="the tall book stacks, the easel with its painting, the globe, the stream, the moon, the stars and the jungle foliage"),
 17:dict(start="standing at the open door with one hand on the handle, looking out",
         beats=["he pushes the door wide open",
                "he steps forward out over the threshold",
                "he stands on the threshold looking into the starfield as the nebula turns and his hair stirs"],
         dir="none",
         pop="Exactly one child — only the little boy. No animals, no other people.",
         static="the room walls, the light switch, the door frame and the starfield vista beyond"),
 18:dict(start="crouched in the sunflowers with the magnifying glass held up to his eye",
         beats=["he peers carefully through the magnifying glass and goes still",
                "the ladybug crawls onto his fingertip",
                "he lifts the ladybug up to eye level, smiling",
                "behind him a monarch butterfly lands on a sunflower and slowly opens its wings"],
         dir="none",
         pop="Exactly one child — only the little boy — plus exactly one ladybug and one monarch butterfly. No other people or animals.",
         static="the sunflowers, the garden path and the grass"),
 19:dict(start="standing in the sunflower field at dusk holding the brass spyglass up toward the sky with both hands, looking up",
         beats=["he slowly lowers the spyglass but keeps gazing up at the sky, wide-eyed",
                "he points up at Saturn with one hand, grinning",
                "the stars twinkle above the field"],
         dir="none",
         pop="Exactly one child — only the little boy. No animals, no other people.",
         static="the brass spyglass he is holding, the sunflower field, Saturn and the Milky Way"),
 20:dict(start="walking away from the viewer up the path toward the bed, back to camera",
         beats=["he walks on up the path toward the bed under the moon",
                "he reaches the bed and leaps in under the quilt with a bounce",
                "he settles with his hands behind his head, looking up at the moon",
                "the animals curl up on the grass beside the bed"],
         dir="retreat",
         pop="Exactly one child — only the little boy — plus exactly one puppy, one piglet and one small brown animal. No other people or animals.",
         static="the wooden bed, the red barn with its weathervane, the full moon, the stars and the grass"),
 21:dict(start="asleep in the wooden bed under the patchwork quilt, the rooster on the bedpost",
         beats=["his chest rises and falls slowly and the quilt shifts gently",
                "the puppies and the piglet breathe softly in their sleep",
                "the rooster ruffles its feathers and tucks its head down",
                "the fireflies drift and the stars turn slowly above"],
         dir="none",
         pop="Exactly one child — only the little boy, asleep — plus exactly one rooster on the bedpost, three puppies and one piglet asleep on the grass. No other people or animals.",
         static="the wooden bed, the patchwork quilt, the rooster, the full moon, the stars and the grass"),
}

WARDROBE = "The little boy wears his yellow-and-white horizontally striped short-sleeve shirt and blue jeans rolled at the cuff, and brown boots. "
# Per-scene wardrobe override — the BOOK'S OWN ART wins. Scene 6 shows him barefoot on the sand.
WARDROBE_BY_SCENE = {6: "The little boy wears his yellow-and-white horizontally striped short-sleeve shirt and blue jeans rolled at the cuff, and he is barefoot on the sand. "}
CAMERA = (" Camera completely static and locked: no zoom, no pan, no reframing. Preserve the illustration's exact painterly art style, "
          "colours, composition and proportions. His mouth stays relaxed; he does not speak and does not mouth words.")
STATIC_LEAD = "These stay exactly as they are and never appear, move or change: "
NOTHING_NEW = " Nothing new appears in the background at any moment — no new buildings, no new structures, no extra people."

def prompt(n):
    m = MANIFEST[n]
    beats = " ".join(b[0].upper() + b[1:].rstrip(".") + "." for b in m["beats"])
    w = WARDROBE_BY_SCENE.get(n, WARDROBE)
    return (f"{w}{m['pop']} {STATIC_LEAD}{m['static']}.{NOTHING_NEW} "
            f"Act in this order: {beats}{CAMERA}")

def duration(n):
    return max(5, min(15, int(math.ceil(T[n])) + 1))

if __name__ == "__main__":
    import sys
    scenes = [int(x) for x in sys.argv[1:]] or sorted(MANIFEST)
    for n in scenes:
        print(f"--- scene {n} | slot {T[n]}s | request {duration(n)}s | expect {MANIFEST[n]['dir']}")
        print(prompt(n)); print()
