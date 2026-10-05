# marketing/video/rig — layered character animation (the "characters move, backgrounds don't" rig)

Rev 2026-10-01. Supersedes Ken Burns / full-frame image-to-video as the BACKBONE
of a scene. Ken Burns and i2v are still used, but only as icing (see below).

## Why this exists
Evan's rule: "I don't want a still image slightly moved — I want the characters
themselves on the page to animate, and the background to stay consistent (the kid
slides down the hill, the hill doesn't move)."
Every hosted image-to-video model re-renders EVERY pixel, so the background
drifts/wobbles and the art gets reinterpreted. None of them can promise a locked
background. So the background is never generated: it is the original illustration,
pasted through pixel-for-pixel, and only the character sprite moves.

## The stack (per scene)
    L0 PLATE   = illustration with the character(s) removed (hole inpainted).
                 Pixels outside the hole are BIT-IDENTICAL to the original art.
    L1 SPRITE  = the character cut out as RGBA, FULL-FRAME (see below).
    L2 MOTION  = keyframed path + scale/rotate/squash, an affine about the
                 character's own anchor, with ease-in-out.
    L3 AMBIENT = optional, hero beats only: masked-region generation (see
                 ../MODEL-RESEARCH.md) — never a full-frame pass.

## Tools in this directory
    prep_scene.py    illustration -> sprite (full-frame RGBA) + QA sheet + plate
                     + a motion-spec skeleton whose t=0 IS the original position
    build_plate.py   illustration + FULL-FRAME cutout -> clean plate (LaMa inpaint)
    rig.py           plate + sprites + motion spec -> 1080p24 mp4 (ffmpeg encode)
    render_all.py    every scene spec in a book dir: render + BOTH proofs + filmstrip
    check_frame0.py  frame 0 vs the ORIGINAL ART (rig.py's --verify cannot see a
                     mis-placed sprite; this can)
    strip.py         QA filmstrip from a rendered clip
    sheet.py         contact sheet of scene illustrations / cutouts
    scene-05.json    worked example (scene 05, boy rolling downhill on a tire)
    .venv/           rembg + torch/LaMa + opencv + pillow + numpy (local, free)

Dependencies are all local and free: rembg (u2net, MIT) for the cutout,
big-lama for the hole fill, ffmpeg for the encode. No API, no cost per scene.

## Pipeline, per scene
    ./.venv/bin/python prep_scene.py <final-illustration.png> <book-dir> <scene-id> [dur]
        -> sprites/<scene>-cut-full.png  FULL-FRAME RGBA  (what rig.py uses)
        -> sprites/<scene>-cut.png       cropped to the character (QA / hand masks)
        -> sprites/qa-<scene>.png        original | captured-over-magenta | alpha
        -> plates/<scene>-plate.png      the clean plate
        -> plates/preview-<scene>-plate.png  same, hole outlined in magenta
        -> <scene>.json                  hold-only skeleton
    Then author the path in <scene>.json (see rig.py's docstring), and:
    ./.venv/bin/python render_all.py <book-dir>            # all scenes, both proofs
    ./.venv/bin/python render_all.py <book-dir> --only scene-05   # one scene

## Verification: two proofs, and both are needed
1. `rig.py --verify` — every frame, pixels NOT covered by a sprite must equal the
   plate. Guards the background. **Cannot** see a mis-placed or mis-scaled sprite:
   a shifted sprite just uncovers inpainted plate, so it passes while frame 0 no
   longer matches the art. This is not hypothetical — it passed in rev 2026-09-30
   with the sprite 296 px off and 5.5% too large.
2. `check_frame0.py` — frame 0 vs the original illustration. The ONLY place frame 0
   may differ is the reconstructed hole, dilated 4 px (LANCZOS support at the hole
   boundary). Everything else must be identical.

Verified 2026-10-01 on real art (Book 1):
| scene | sprite coverage | hole | bg delta / all frames | frame 0 outside hole |
|-------|-----------------|------|-----------------------|----------------------|
| 05 rolling tire | 20.4% | 24.8% | 0 | identical (0 px differ) |
| 02 spots mountain | 5.9% | 8.7% | 0 | identical (0 px differ) |
| 12 walking away | 10.5% | 13.7% | 0 | identical (0 px differ) |
| 20 walking home | 4.7% | 6.9% | 0 | identical (0 px differ) |
Render cost: 144 frames @1080p24 in ~25 s, $0. Re-render free on any timing change.

## Two bugs found and fixed 2026-10-01 (rev 2026-09-30 was wrong)
- **Sprite was never scaled with the plate.** rig.py resized the plate to the
  output frame and pasted sprites at their own size, so a 1024 sprite in a 1080
  frame was ~5.5% too big and ~296 px off its original spot. The scene-05 demo
  shipped with frame 0 differing from the original art over **30.9%** of the frame,
  while `--verify` reported "background pixel-identical". Fixed: `fit()` scales
  sprites by the plate's factor.
- **The sprite is now FULL-FRAME, not cropped to the character.** A cropped sprite
  is a separate image, so resizing it puts its pixels through a different
  resampling phase than the plate; every high-contrast edge (outlines, stripes,
  tire tread) landed a fraction of a pixel off — 6.4% of the frame differing, max
  channel delta 231, all along the character's silhouette. Full-frame sprite +
  identity-transform shortcut for held frames => frame 0 is exact.
- The pre-fix demo is kept for comparison: `out/scene-05-rig-demo-PREFIX-placement-bug.mp4`.

## Honest limitations
- The plate's hole is 8 px larger than the sprite (the dilate in build_plate.py),
  so where the character stood there is a faint grey ring once it walks away. That
  is the hole-fill quality knob, not a rig defect: fill the hole with a real image
  model that matches the art style (ComfyUI/SDXL inpaint, free/local, skill exists;
  or a cents-per-scene inpaint API) and the ring goes away. The rig does not care
  how the plate was made — it only needs a plate whose untouched pixels are original.
- rembg also grabs bright scenery sometimes: scene-20's moon came back as its own
  connected blob, 35% of the character's area. prep_scene.py keeps the LARGEST
  component only and prints what it dropped, because that blob is not cosmetic —
  it sets the character's anchor via the alpha bbox (scene-20's anchor was wrong by
  0.14 of the frame) and it puts a hole in the sky. Keeping a second blob (a cat, a
  prop that should move) is a deliberate per-scene edit, not a default.
- Sprites are rigid bodies: path/scale/rotate/squash. That reads great for sliding,
  rolling, hopping, leaning, walking away. It does NOT deform a character (no
  bending limbs). Where a limb must bend, use the AI hero-beat routes in
  ../MODEL-RESEARCH.md, or a second sprite per limb.
- Square illustrations into a 16:9 upload: framing is a separate decision
  (cover-crop = loses art; pillarbox = bars; blurred backfill = an L2 layer that
  uses the plate itself, free). Not solved here.

## Where the paid models still belong (3-6 clips per book, ~$3)
See ../MODEL-RESEARCH.md for the researched verdict. Short version: Luma Ray 3.2
multi-keyframe (drive motion with OUR OWN frames), Kling v1.0 motion brush via an
aggregator (the only region-locked brush over an API), ToonCrafter ($0.062/run,
built for illustrated input), LTX 2.3 inpaint (ambient life in a masked region
only). Runway Motion Brush and Kling's UI brush exist but are NOT reachable from
an API — they cannot be automated.
