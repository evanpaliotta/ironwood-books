# YOUTUBE.md — Ironwood Books YouTube Channel (source of truth)

Start date: 2026-09-29. One-person press; agent produces drafts/assets, Evan
records voice and pushes. Everything here must obey BRAND_TASTE.md (read it
before producing): plain dad voice, timeless, no hedging, book is never the
pitch.

## 1. Strategic verdict

The channel exists to SELL BOOKS and build the parent/homeschool trust that
the site guides already capture. Two engines, one brand:

- Discovery = thematically-keyed, parent-facing long-form ("philosophy for
  kids", "Socratic questions at bedtime") that mirrors the existing AEO guide
  queue. Repurpose guide topic -> video. Search + Suggested grow the channel.
- Demand = READ-ALOUDS of the Curious Kid books. Parents literally search
  "<title> read aloud". Evergreen, high CTR, drives Amazon. Uses existing book
  art, near-zero new assets.

Order of launch: read-aloud of Book 1 (search demand now) -> 2 parent explainer
videos (repurposed guides #2 and #7) -> Shorts cut from everything to feed the
funnel. Cadence: 1 long-form / month, 2-3 Shorts / week. Do not chase news.

## 2. Formats (the menu)

| Format | Ages | Purpose | Assets needed |
|--------|------|---------|---------------|
| Read-aloud (Curious Kid) | 4-8 + parents | Sell book, evergreen search | Book art + Evan voice |
| Parent explainer ("Socratic qs for bedtime", "opposites for kids") | parents | Discovery/SEO, matches guides | Script + motion stills + TTS or voice |
| Channel trailer ("why I write philosophy books for kids") | parents | Identity | 60-90s, Evan voice |
| Shorts: couplet / illustration reveal / 2-line idea | all | Feed funnel | Cut from above, vertical |

## 3. PRODUCTION MODEL (rev 2026-10-01) — full-frame image-to-video

REV 2026-10-01: Evan watched the bake-off and the rig demos. VERDICT: the
bake-off look is exactly what he wants; he "does not like the rigs at all".
The rig/plate/sprite approach is SHELVED (its README and bugs are documented for
whoever picks it up). Ken Burns is also out. Every scene is a full-frame
image-to-video generation from the final illustration.

Budget (Evan, 2026-10-01): up to ~$0.50 per scene, clip length ~5s (max 10s).
Iterate-cheap matters more than latest-and-greatest: he'd rather pay per second
on a good model than $1/scene on a flat model he might re-roll. The bake-off
models (Wan fast, Seedance 2.0, Kling v2.5 Turbo) all looked good to him; Wan
fast's choppiness is its 624x624 low-res tier, not the model family.

Per-scene process (one scene at a time, his review before the next):
1. Read the scene's illustration + narration line + SCENE_NOTES entry.
2. Write the MOTION BRIEF from the scene itself: what the character does
   relative to the setting (e.g. "glances up the mountain, turns, starts up the
   path"), what ambient motion fits (clouds, water, leaves), what must NOT
   change (style, colors, composition).
3. Generate ONE clip (first scene = Kling v2.5 Turbo Pro, ~$0.45/5s). Optional
   last-frame image for a discrete action.
4. Evan reviews. Learn preferences. Then the next scene.
Cost per book at 21 scenes x ~$0.50 ≈ $10, well under any subscription.

The 2026-09-30 rig plan below is historical:

Evan's rule (2026-09-30): a drifting still is not the goal. The CHARACTERS must
animate while the background stays CONSISTENT (the kid slides down the hill; the
hill does not move, wobble, or get reimagined). That rules out full-frame
image-to-video as the backbone: those models re-render every pixel, so the art
drifts. Verified, with sources: marketing/video/MODEL-RESEARCH.md.

Layer stack per scene (the rig — marketing/video/rig/README.md):
0. PLATE: the illustration with the character(s) removed (the hole is inpainted).
   Every pixel outside the hole is BIT-IDENTICAL to the original artwork.
1. SPRITE: the character cut out as RGBA (rembg, free/local) — same pixels.
2. MOTION: keyframed path + scale/rotate/squash, ease-in-out, timed to the
   narration. Frame 0 == the original illustration, so nothing ever "pops".
3. AMBIENT (3-6 hero beats per book, optional): masked-region generation only —
   never a full-frame pass.
Cost: $0 per scene, deterministic, re-rendering is free. Proven on real art:
video/rig/out/scene-05-rig-demo.mp4 (boy rolls downhill; background verified
pixel-identical on all 144 frames — rig.py --verify exits non-zero otherwise).

Ken Burns (free zoompan) and full-frame AI i2v stay in the kit as icing on top
of the rig, never as the moving picture itself.

Where the paid models still belong (full verdict + sources in MODEL-RESEARCH.md):
- Luma Ray 3.2 (Replicate `luma/ray-3.2`, $0.30 / 5s 720p): multi-keyframe i2v
  pins 1-64 guide frames at exact output-frame indexes (5s = frames 0-120 @24fps).
  Feed it frames the RIG generated (character at successive positions) and it
  interpolates between OUR frames — the strongest "direct the motion" lever, and
  the best first-frame preservation of the bunch. Replicate exposes start/end
  image only; the multi-keyframe surface is Luma's own API.
- Kling v1.0 motion brush via an aggregator (PiAPI / GoAPI): the ONLY real
  region-locked brush reachable over an API — mask_url (transparent PNG, same
  size as the image) + static_masks (max 1) + dynamic_masks (max 6, each with a
  bezier point path). v1.0 only, image-to-video only, no end frame. Old model:
  hero beats only.
- ToonCrafter (`fofr/tooncrafter`, Replicate, $0.062/run): built for ILLUSTRATED
  input, 2-10 keyframe images. Composite the plate twice — character at start,
  character at end — and it invents only the in-between; both ends are our art.
  Max 512-768px, upscale after. Cheapest real fit for a discrete action.
- LTX 2.3 (`replicate/ltxvideo-2.3-lora`, ~$0.16/run): Inpaint/Outpaint with a
  white mask (black preserved) + a "Cinemagraph" task -> ambient life in a
  masked region only (curtain, water, trees) without touching the character.
- Kling 3.0 (fal, ~$0.112/s): keep for pure AMBIENT beats — best ambient motion
  in our own bake-off. Its API has no brush; Motion Control transfers motion
  from a reference VIDEO and re-renders the whole frame, so backgrounds drift.
- Runway Gen-4 Turbo / Gen-4.5: Motion Brush exists in the WEB APP ONLY. The
  API (`/v1/image_to_video`) takes image + prompt + ratio/duration/seed — no
  mask, no brush. Automation impossible; the $15/mo plan is a subscription
  (banned). Hand-brushing is a one-off manual job, Evan's call — not a pipeline.
- Pika (subscription, no region control) and Kaiber (style transfer that DRIFTS
  from the source art): both skipped.

## 3b. VOICE (LOCKED 2026-09-29) and models
- VOICE: Evan records everything — read-alouds, trailer, explainers. No TTS
  anywhere in the pipeline. Writing model = none needed; manuscripts exist.
- VIDEO (answered 2026-09-30): character motion no longer relies on a
  full-frame image-to-video model. The rig (marketing/video/rig/, §3) does the
  moving picture for free and keeps the background locked. AI i2v is reduced to
  3-6 hero beats per book, chosen by the bake-off results below and the model
  roles in §3 (verdicts + sources: video/MODEL-RESEARCH.md).

## 3c. HARNESS DECISION (locked 2026-09-29): Replicate API, pay-per-second

Evan clarified: paid OK if pay-as-you-go (no subscriptions). Replicate is
already in his stack and is the harness: it carries Veo 3.1, Kling v3,
Seedance 2.0, Wan 2.6, LTX-2.3, Hailuo — billed per output second.
OpenRouter is TEXT-ONLY; no video models there.

Verified prices (Sep 2026, approx):
- Wan 2.2 i2v FAST (Replicate): **flat ~$0.05 per video** (480p fast tier; the
  bake-off clip rendered 624x624). Wan 2.2 i2v **a14b** is the per-video one:
  $0.40 (480p) / $1.00 (720p). Do not quote "$0.40/clip" for the fast tier — the
  fast tier is a flat per-VIDEO price, not per second.
- Seedance 2.0: from ~$0.067/s (480p) upward; 720p 5s lands ~$0.35-0.75. Exact
  720p rate unverified — check the model page before budgeting.
- Kling: published Kling API list pricing ≈ $0.14 per unit/second at 720p
  (Kling 3.0 Turbo w/ audio $0.112/s, no audio $0.084/s). Kling v2.5 Turbo Pro's
  own Replicate rate is UNVERIFIED.
- Veo 3.1: $0.20/s (no audio needed — we have Evan's VO, never pay for audio)
- Evan's own Replicate billing page is the authority on what was actually spent;
  published list rates are for estimating only.

Cost reality for Book 1: 6 accent clips x 5s x 720p on Wan ≈ $2.40. A whole
book's accents ≈ $3-5. Bake-off across 4 models ≈ $2. Trivial.

## 3d. CANONICAL WORKFLOW (rev 2026-09-30) — audio file to published video

1. Evan records the narration (one file) -> marketing/audio/raw/. Human gate.
2. AUDIO: cleanup + slicing -> narration master + scene-timings.json (§3e).
3. RIG per scene: cutout -> plate -> motion spec -> rig.py --verify (free, local).
   All 21 scenes. Re-render any scene for free when the timing or motion changes.
4. HERO BEATS (3-6 per book): one AI clip each, only where the rig cannot read
   (see the model roles above). ~$3 per book. Bake-off already done 2026-09-29.
5. STITCH: scenes in narration order, continuous VO, ducked music bed, optional
   per-scene captions, 1080p H.264 export.
6. SHORTS: 3 verticals cut from the same material (opening couplet, the
   "why up so slow / down so fast" scene, outro).
7. Evan reviews the cut -> changes are re-stitches, nearly free.
8. UPLOAD: yt-dlp with SEO title/description/tags, ASIN dp link, Made-for-Kids
   designation per video (§7b).
API keys: REPLICATE_API_TOKEN (exists, ~/.zshenv chmod 600) / FAL_KEY if needed.
Never inline a key in chat.

## 3e. AUDIO PIPELINE (added 2026-09-30) — raw phone memo -> narration master

Evan records Voice Memos on the phone; the mic is fine, the ROOM matters more.
Runs entirely local except the optional step 3b. Commands verified on this Mac.

0. RECORDING SPEC (give this to Evan): quiet soft room (bed/couch/closet);
   phone 6-12 in. from the mouth, slightly off-axis; slow, kid-paced; leave 3 s
   of room tone at the START (the denoiser learns the noise floor from it) and
   pause 2-3 s between scenes (that gap is what the slicer cuts on); if a scene
   flubs, re-read only that scene and say "scene NN pickup" — never re-record
   the whole file.
1. INGEST + QC (raw is never edited): ffprobe for codec/rate/channels/duration;
   ffmpeg `astats`/`ebur128` for peaks. True peak at 0 dBFS = clipped =
   unfixable -> ask for that scene again. Peak target while recording: -12 to
   -6 dBFS.
2. CUT (before cleanup, so cleanup runs once over final content): splice takes,
   drop flubs and dead air, 0.15 s pad either side. Working copy = WAV 48k/24-bit.
3. CLEAN — pick one, A/B it on the same scene, keep the pre-cleanup file:
   a. LOCAL/FREE/NO UPLOAD (default — the voice never leaves the Mac):
      `-af "highpass=f=80,afftdn=nf=-25,anlmdn=s=0.00002"` + manual clicks and
      plosives. Verified chain; measured -43.6 -> -16.0 LUFS in one pass.
   b. CLOUD AI (free tier): Adobe Podcast Enhance Speech at 50-70 strength
      (free = 1 enhanced hour/day, <= 30 min/file, audio only, one at a time;
      >30 min -> split the file). Best at fan/AC/room. Above ~70 it sounds
      reconstructed. Auphonic free tier stamps a jingle on free productions —
      never on a published file.
   Neither fixes clipping or a big echoey room.
4. LEVEL + MASTER (local, deterministic): two-pass `loudnorm`
   I=-16 LUFS, TP=-1.5 dBTP, LRA=11 -> YouTube target (use I=-14 if the file
   also serves as a podcast/music-forward master). Gate below -45 dB. Verify
   with `ebur128`: measured I within +/-1 LUFS, TP < -1.0 dBTP.
5. ALIGN (free, local): whisper.cpp forced alignment against the manuscript we
   already have -> word-level timestamps, so scene boundaries are EXACT, not
   guessed. Sanity check: every script line must be present; a >1.5 s gap
   inside a scene means a missed line. NOTE: whisper-cli is not installed yet.
6. SLICE + TIMING TABLE: cut scene segments on the aligned boundaries; emit
   marketing/video/book01/scene-timings.json — per scene: id, t_start, t_end,
   dur, narration text, illustration path, sprite path, plate path, motion spec.
   Every visual step downstream reads that file; it is the single source of
   timing truth.
7. MUSIC BED: one licensed/CC0 bed per video (a copyright claim on a kids
   channel is not worth it), bed -24 to -28 LUFS under the voice, ducked
   automatically (`sidechaincompress threshold=0.02:ratio=8:attack=20:release=400`),
   1 s fade in, 2-3 s fade out under the outro. Verified: voice stays at
   -16.0 LUFS with the bed ducked underneath.
8. FINAL MIX + VERIFY: voice + ducked bed -> master; print measured I/TP into the
   video's row in the metrics log. Never claim "clean" without the numbers.
9. ARCHIVE: raw + cleaned + master + timings JSON. Never overwrite the raw.

- YouTube channel on the existing Google account (allow time to verify).
- Google Cloud project + YouTube Data API v3, OAuth client. This is the one
  real "service" setup for programmatic title/description/thumbnail/upload.
- yt-dlp (free) for the same upload path without a full API app — simplest
  first upload route; can use it to verify metadata too.
- ffmpeg via Homebrew (FREE, core renderer: Ken Burns pan/zoom over stills,
  burn-in captions, concat, resize to 1080/vertical). NOT installed yet.
- Whisper.cpp OR YouTube auto-captions for subtitles (free).
- No transcription/editing SaaS needed. No paid AI video gen (Runway/Sora/Veo)
  — Ken Burns over existing book art is more on-brand and cheaper.

Setup todo (do once, in order):
  1. Create channel + set up Google Cloud project, enable YouTube Data API,
     create OAuth client (help via hermes gateway / Evan walks credentialed
     portals together — memory).
  2. brew install ffmpeg; pip/uv install yt-dlp.
  3. Confirm upload path (yt-dlp) and test-upload a 5s draft to unlisted.

## 5. Models (ideal per job)

- Scripts / long-form writing: heavy model (user rule: Kimi K3-class for
  complex writing). Score output against BRAND 4-criteria grid, >=7 to ship.
- Titles + descriptions + tags: same heavy model; keyword-check via Amazon
  autocomplete + YouTube suggest. No paid SEO tools.
- Narration: Evan's voice (read-alouds, trailer). Built-in text_to_speech
  (edge == free crisp default) for explainers/Shorts.
- Thumbnails / motion frames: existing book illustration finals first; new
  frames via ComfyUI / diffusion pipeline (free, skills exist). Thumbnails =
  a strong illustration + 3-4 word title case, no clickbait.
- Video assembly: clips + ffmpeg (concat, captions, audio mix). Scene animation =
  full-frame image-to-video per scene (§3, rev 2026-10-01).

## 6. Video build recipe (read-aloud, per video)

1. Script = manuscript text + hook (10s) + outro CTA (book link, "stay
   curious"). Identify scene -> illustration pairing (21 scenes = 21 stills).
2. Stills from book art (already high-res finals, 21 of them).
3. ANIMATION (per scene, paid, one at a time): full-frame image-to-video from the
   final illustration with a motion brief written from the scene (§3). ~$0.25-0.45
   per 5s clip. Review each clip before the next scene.
4. Audio: narration master from §3e (48k WAV, -16 LUFS, TP < -1.5) + ducked
   music bed, 0.5s gap after each scene.
5. Burn optional bottom caption for scene-one line (parent reads along).
6. Export .mp4 (H.264, 24fps, yuv420p). Thumbnail from cover final + title
   overlay.
7. Upload via yt-dlp with SEO title/desc/tags from the heavy model + ASIN dp
   Amazon link, transcript, and end screen to subscribe.
8. Cut 3 Shorts (~20-45s vertical) from the same audio/art: opening couplet,
   "why so slow up, fast down" scene, outro.

## 7. Metrics (append, don't overwrite — mirrors METRICS.md style)

Track monthly: views/CTR/avg-view by video, which topic captured search, subs,
Amazon click-through from the description (use a UTM/ASIN link). Log under
"## YYYY-MM" blocks in a YOUTUBE-METRICS.md. Watch: read-alouds tend to spike
then hold (evergreen); parent explainers are the growth/discovery lever.

## 7b. COPPA / "Made for Kids" (researched 2026-09-29 — structural, read first)

- A read-aloud of an ages 4-8 picture book is almost certainly classified
  Made-for-Kids (animated characters + child-directed language + story format).
  That is a LEGAL designation (COPPA), not a preference. FTC fined Disney $10M
  (2025) for mislabeling; mislabeling to keep features is real legal risk.
- MFK disables: comments, notification bell, end screens, cards, playlists,
  autoplay-on-home, personalized ads (RPM ~$1-3 vs $5-15 — irrelevant here,
  we monetize via Amazon sales, not ads). It also kills the retention layer,
  so read-alouds grow by SEARCH + thumbnails only. Plan CTA in the spoken
  outro + description, never rely on end screens.
- CRITICAL: never set a channel-level MFK default. Channel stays general
  audience; designate PER VIDEO. Read-alouds/Shorts from them = MFK.
  Parent-facing explainers = NOT MFK (audience is parents) and keep comments,
  bell, end screens — that is where community and growth machinery lives.
  This mixed-channel structure is deliberate; protect it.
- Packaging check before upload: if a thumbnail/title looks child-directed
  (cartoon-flooded frame, bubble lettering, child-cadence title), YouTube's
  classifier can force MFK on a video you designated general audience. Keep
  explainer packaging parent-coded.
- YouTube "quality principles" for kids content reward learning and
  curiosity — the brand IS that. Keep read-alouds non-promotional (book link
  in description, gentle spoken outro); heavy-commercial kids content gets
  limited ads/exclusion from the Kids app.
- AI-generated kids content is under active FTC/advocacy pressure (bans
  proposed for YouTube Kids). Accent-animation on OUR OWN copyrighted
  illustrations is low-risk, but keep disclosures honest and avoid AI voice
  on MFK-designated kids videos.

## 9. CHANNEL LAUNCH + SEO PLAN (drafted 2026-10-01 — needs Evan's decisions)

Goal: a channel that compounds search demand for the books, not a video hobby.
Two engines (§1): parent-facing discoverable long-form + read-alouds that capture
"<title> read aloud" demand. Everything below is free tooling; no paid SEO tools.

A. IDENTITY (decided 2026-10-01 — no channel exists yet, starting from scratch)
   - CHANNEL NAME = **Ironwood Kids** (Evan's pick). Handle @ironwoodkids was
     FREE when checked 2026-10-01 (youtube.com/@ironwoodkids returned 404).
     Known tradeoff, stated once and accepted: "Ironwood Kids" is also a
     children's-ministry name at Ironwood Church (Mesa, AZ), so search results
     have some collision; the handle itself is unclaimed and the category
     (storytime/read-alouds) will differentiate. Do not relitigate per session.
   - AUTHOR NAME = **Evan Paliotta**, his real name, already the published author
     name on the KDP listing ("By Evan Paliotta | Ironwood Books"). NOT a pen name
     — the earlier note about "by Jean Lane" was from the old manuscript draft and
     is wrong. Use Evan Paliotta everywhere.
   - NAMING structure: name the channel Ironwood Kids (brand-level so later
     Ironwood series and non-book kids videos fit), one playlist per series.
   - Art: avatar = the boy's face from the cover; banner = a 3-panel spread of
     finals with the wordmark. All existing art, $0.
   - About text: 2 lines on what the channel is + link to the site + the book.
     Include the word parents actually type ("read aloud bedtime stories").

B. SETUP CHECKLIST (once, in order)
   1. Create the channel on the existing Google account; complete verification.
   2. Google Cloud project -> enable YouTube Data API v3 -> OAuth client (needed
      only for programmatic upload/metadata; yt-dlp is the simpler first route).
   3. yt-dlp installed (2026-10-01); ffmpeg already installed.
   4. Upload ONE unlisted test (5s clip) to prove the path, then delete it.
   5. Channel-level settings: NOT made-for-kids (mixed channel — MFK is per video,
      §7b), no channel-level defaults that a classifier can misread.
   6. Sections/playlists: one playlist per book + "Bedtime Stories" + "Philosophy
      for Kids". Playlists are the free retention layer on non-MFK videos and
      harmless on MFK ones.

C. SEO / PACKAGING (per video)
   - TITLE formula: [Series/Character] + [action, plain words] + (Read Aloud
     Bedtime Story for Kids). Front-load the search phrase parents type; keep the
     character name in every title so the channel builds one entity.
   - KEYWORDS: harvest free from YouTube autocomplete + Amazon autocomplete +
     the site's own search-console data (the guides already rank). No tools.
   - DESCRIPTION: 2-line hook, then per-scene timestamps (chapters), then the
     Amazon dp link (ASIN, tagged), then the site link. MFK read-alouds: the CTA
     lives here + in the spoken outro because end screens are disabled.
   - THUMBNAIL: one strong illustration + 3-4 words of title case. Test 2 per
     video if the first month's CTR is under ~4%.
   - CAPTIONS: whisper.cpp forced alignment from the manuscript -> burned-in
     optional, uploaded .srt always (accessibility + keyword surface).
   - SHORTS: 3 verticals per video, cut from the SAME clips (open couplet, the
     hook scene, the outro line). Vertical crop from square art = center crop;
     keep the character in the middle third.
   - CADENCE: 1 long-form + 2-3 Shorts per month to start (sustainable solo).
   - CROSS-LINK: each video's description links the matching site guide, and each
     guide page can embed the video — that is the AEO citation loop that already
     works for the text guides.

D. MEASURE (monthly, YOUTUBE-METRICS.md)
   - Views, CTR, avg view duration per video; which search terms surfaced.
   - Amazon click-through from the description link.
   - The honest early signal is CTR + retention, not subs. If a read-aloud holds
     >50% avg view on a 6-8 min video, the format works; if retention falls off a
     cliff at the first slow scene, tighten the pacing before making more.

## 10. NARRATION VOICE + SCENE TRANSITIONS (rev 2026-10-01)

VOICE — DECIDED DIRECTION: Evan reads the whole book himself; the recording is
then ENHANCED, not replaced. He does not want a clone of his voice. He is open to
a voice-changer pass that keeps his timing/delivery but swaps the timbre for a
more pleasant narrator voice. Plan: 1) clean + master his recording (the §3e
chain: denoise, EQ, de-ess, gentle compression, loudness to -16 LUFS). 2) If he
wants more: A/B test ElevenLabs VOICE CHANGER (speech-to-speech — preserves his
tone and delivery, converts to another voice; ~$0.12/min via API, 5 min max per
conversion = per-scene chunks) on ONE scene, his voice-cleaned vs
voice-changed, and he picks. Cloning a third-party voice for kids content is the
one area with real FTC/advocacy pressure — his explicit call before any of it is
published. His own voice enhanced has no disclosure requirement; YouTube's own
help page lists "voice or audio repair" and "cloning one's own voice" as
no-disclosure items.
Recording booked by Evan for 2026-10-02 (Book 1, one file, per the §3e spec).

TRANSITIONS — Evan rejected dissolve/page-slide/3D-flip mockups (2026-10-01).
New direction: a real EDITOR with a proper page-turn animation. Verdict after
research: **DaVinci Resolve (free version)** — professional editor, its Fusion
page does genuine page-turn/flip effects, and it is scriptable (Python API +
community CLIs `dvr` / `resolve-cli`: import media, build timelines, render
from the command line), so it can be driven as well as ffmpeg. Plan: install
Resolve on the mini, build the page-turn ONCE as a reusable Fusion macro,
render transition files, ffmpeg stays as fallback for dumb assembly only.
iMovie has no built-in page turn; FCP's is a paid plugin + $299 app;
Filmora/PowerDirector have page turns but are subscriptions (banned).

## 11. TOOLCHAIN (installed + verified on the mini, 2026-10-01/02)
Done, all free:
- ffmpeg + ffprobe (Homebrew). Verified the filters the pipeline needs are
  present: xfade, loudnorm, ebur128, sidechaincompress, afftdn, anlmdn,
  highpass, acompressor, silencedetect, astats, adeclick, adeclip.
- whisper.cpp (brew whisper-cpp) + models ggml-base.en.bin and ggml-small.en.bin
  in ~/.cache/whisper (small.en is the one to use for scene alignment).
- yt-dlp (upload path), sox, mas (Mac App Store CLI).
- Python 3.9 system + the rig venv (rembg, torch/LaMa, opencv, pillow, numpy).
- Review server: ~/video-preview served on :8000 (bind 0.0.0.0) with the clip
  page and teleprompter.html.

DaVinci Resolve — INSTALLED 2026-10-02 (App Store build, free/"Lite", 21.1,
2.9GB, /Applications/DaVinci Resolve.app). Launches, writes prefs, creates its
Fusion tree. ONE STRUCTURAL FINDING: the free build cannot accept scripts from an
outside process — Blackmagic's scripting README scopes the "External scripting:
None/Local/Network" preference to STUDIO, and it is absent from Lite's config.
Measured: Python using Resolve's bundled module gets `scriptapp('Resolve') -> None`.
What works on free: scripts run FROM INSIDE Resolve (Workspace > Scripts > ...),
and Fusion macros/templates dropped into its container paths. So the working split
is "I author the file, Evan clicks it in the menu". Driving Resolve directly
(build timelines, apply transitions, render) needs Studio — $295 ONE-TIME, not a
subscription — decision pending with Evan.
Paths that matter (App Store build is sandboxed, so the container is the real one):
- Scripts: ~/Library/Containers/com.blackmagic-design.DaVinciResolveLite/Data/Library/Application Support/Fusion/Scripts/{Utility,Comp,Edit,Color,Tool,Deliver}
- Templates / Macros / Settings: .../Fusion/{Templates,Macros,Settings}
- Bundle: scripting devkit at .../Contents/Resources/Developer/Scripting (README.md
  there is the authority); fusionscript.so at .../Contents/Libraries/Fusion/
- Env exports (for Studio later) appended to ~/.zshenv.
- Smoke test written for him: Scripts/Utility/resolve_hello.py + a README in that
  folder. Page-turn is still TO BUILD (as a Fusion macro/template, reused for
  every scene change).

## 8. Rules (hard)

- FULL-FRAME IMAGE-TO-VIDEO PER SCENE (Evan, 2026-10-01, supersedes the
  "characters move, backgrounds don't" rule). He watched both and prefers the
  bake-off look; the rig is shelved. One scene at a time, his review before the
  next; ~$0.25-0.45 per 5s clip. The rig README and its two proof scripts stay in
  the repo for anyone who needs exact background lock later.
- NEVER SPEND WITHOUT AN EXPLICIT GO. An example Evan gives ("the boy should turn
  and head up the mountain") is PROMPT MATERIAL, not an instruction to generate.
  Ask first; he corrected exactly this on 2026-10-01 after one $0.45 clip.
- QA every generated clip before accepting it: extract first/mid/last frames and
  check the art style, the character, and that no elements were added or lost. A
  clip can render "successfully" and still be wrong. Report the model, the
  duration and the estimated cost with every clip.
- Audio: the RAW recording is never edited; cleanup runs once, after the cut;
  keep the pre-cleanup copy. AI cannot fix clipping or a big echoey room — say
  so and ask for a re-read instead of pretending. No music bed on free tiers
  that stamp a jingle (Auphonic). No TTS anywhere.
- Before calling audio "clean" or "mastered", print the measured numbers
  (ebur128: I in LUFS, TP in dBTP). Numbers or it didn't happen.
- Region-lock facts (2026-09-30): Runway Motion Brush and Kling's Motion Brush
  exist in the WEB UIs only and are NOT reachable from their APIs — they cannot
  be automated, and their web plans are subscriptions (banned). The only
  region-locked brush over an API is Kling v1.0 via an aggregator (PiAPI/GoAPI).
  Don't plan around a brush a pipeline can't call.
- Bake-off DONE 2026-09-29 (scene-15, silent 5s clips, real Replicate runs):
  Wan 2.2 / Seedance 2.0 / Kling v2.5-turbo all PASSED style preservation.
  Best ambient motion: Kling. Best value: Wan. <$2.50 total. Clips + Ken Burns
  demo in marketing/video/bakeoff/. Token stored in ~/.zshenv (chmod 600).

- Obey BRAND_TASTE.md voice & the 4-criteria grid on every script.
- Paid rules per Evan 2026-09-29: no ad buys / no subscriptions. Pay-per-use
  API (Replicate/fal) for video accents IS authorized. Ad buys stay banned.
- Do not fabricate product facts (age ranges, dates, titles beyond confirmed:
  1 & 2 published, Book 3 = Lao Tzu in progress). TBD stays TBD.
- Evergreen only; never date-stamp or chase trends.
- Read-alouds: Evan's voice only; get his nod before publishing any full-book
  read (whole-book-on-YouTube is a deliberate call).
- Do not claim "published" without a live check.