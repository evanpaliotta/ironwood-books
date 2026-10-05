# MODEL-RESEARCH.md — image/animation models for the read-aloud pipeline
Researched 2026-09-30 (supersedes the 2026-09-29 model notes in YOUTUBE.md §3).
Question: which models can animate a CHARACTER inside our illustration while the
BACKGROUND stays consistent — and can we drive it from an API, pay-per-use?

## Verdict in one line
No hosted model guarantees a locked background. Region lock comes from either
(a) a real motion-brush/mask API, or (b) our own compositing rig
(plate + character sprite). Use (b) as the backbone, (a) for 1-2 hero beats.

## 1. What the candidates actually expose

| Model | Character/region control | In an API? | Price | Use for us |
|---|---|---|---|---|
| Luma Ray 3.2 (Ray 3 family) | Multi-keyframe i2v: 1-64 guide frames pinned at exact output-frame indexes (5s = frames 0-120 at 24fps). "Direct any frame." Strongest at holding the look of the anchor stills. No mask. | Yes. Replicate `luma/ray-3.2` exposes start_image/end_image (5s only); the full multi-keyframe surface is Luma's own API (docs.agents.lumalabs.ai) | Replicate: $0.30 per 5s 720p; $0.90 per 10s 720p; $1.20 per 5s 1080p | BEST motion-directing lever: feed it frames WE generated (character at successive positions) so the motion is ours, not invented. 1-2 hero beats. |
| Runway Gen-4 Turbo / Gen-4.5 | Motion Brush (paint a region, give it a direction) exists in the WEB APP ONLY. The API `/v1/image_to_video` surface accepts image + promptText + ratio/duration/seed (+ last_image_url on gen3a_turbo) — no mask, no brush. | API = pay-per-use credits (Turbo 5 credits/s = $0.05/s ≈ $0.25 per 5s; Gen-4.5 12 credits/s = $0.12/s ≈ $0.60 per 5s). The $15/mo plan is a subscription (banned by our rules) | Motion Brush can NOT be automated. Hand-brushing is a manual UI job — Evan's call, one-off, not a pipeline. |
| Kling 3.0 (official v3 API + fal/Replicate) | Official v3 API schema is contents/settings (prompt, first_frame, last_frame, element, duration, resolution, audio, multi_shot) — NO motion brush. Motion Brush is a web-UI feature. Motion Control (API) transfers motion from a REFERENCE VIDEO and re-renders the whole frame | Yes, per-second, no subscription (fal v3 Pro ~$0.112/s audio-off) | Not for character motion (background not locked). Keep Kling for pure AMBIENT beats — best ambient motion in our own bake-off. |
| Kling v1.0 motion brush via aggregators (PiAPI, GoAPI) | The ONLY real region-locked brush over an API: `motion_brush{mask_url, static_masks[≤1], dynamic_masks[≤6]}` — transparent-PNG mask same size as image, each dynamic mask gets a bezier point path (≥2 points, 10+ recommended); origin top-left | Yes, pay-per-use | Kling v1.0 only, image-to-video only, image_tail_url forbidden. Old model. Hero beats only, verify by eye. |
| Kling Motion Control (v3, fal) | Motion transfer from reference video onto one character image; character_orientation image|video; needs a clear person/animal subject | Yes, ~$0.126-0.168/s | Re-renders the full frame → background drifts. Not our path. |
| Pika | No motion brush, no region control over an API; simplest UI, least precise | $8/mo subscription | Skip (subscription + no region lock). |
| Kaiber | Style-first transformation — it DRIFTS from the source art; audio-reactive style transfer | Subscription | Skip: it would change our illustrations. |
| ToonCrafter (`fofr/tooncrafter`, Replicate) | Purpose-built for ILLUSTRATED input: 2-10 keyframe images, interpolates between them. Composite the plate with the character at the start position AND at the end position → it invents only the in-between; both ends are pixel-identical to our art | Yes, Replicate | $0.062 per run, max 512-768px (upscale after) | Cheapest real fit for discrete character actions (slide, hop, turn). |
| LTX 2.3 Creative Lab (`replicate/ltxvideo-2.3-lora`) | Inpaint/Outpaint task: white mask area regenerated, black preserved (mask can be a still or a per-frame video). Plus a "Cinemagraph" task (one still → selected natural motion) | Yes, Replicate | ~$0.16 per run | Ambient life on a masked region only (curtain, water, trees) without touching the character. |
| Wan 2.2 / 2.7, Seedance 2.x | Full-frame i2v only (Wan 2.7 adds first+last frame, clip continuation) | Yes, Replicate/fal, cheap | Wan ~$0.04-0.08/s | Ambient/background beats only. Already bake-off tested (2026-09-29). |

## 2. Where our own bake-off already stands (2026-09-29, real Replicate runs)
Scene-15, silent 5s clips: Wan 2.2 (cheap), Seedance 2.0, Kling v2.5-turbo all
PASSED style preservation. Best ambient motion = Kling; best value = Wan.
Clips: marketing/video/bakeoff/out/. It answered "which model moves our art
without ruining it" — it did NOT answer "can one character move while the rest
of the frame holds." None of them can: they all re-render every pixel.

## 3. Sources (fetched 2026-09-30)
- Luma multi-keyframe i2v (keyframes + keyframe_indexes, 1-64 anchors, 5s→0-120): https://docs.agents.lumalabs.ai/guides/videos/generation
- Luma Ray 3.2 model page + pricing: https://replicate.com/luma/ray-3.2
- Runway API surface (no brush param): https://docs.dev.runwayml.com/api , wrapper param list: https://github.com/reiarthur/easy-ai-clients/blob/main/docs/video/image_to_video/runway.md
- Runway Motion Brush is a web feature; plans from $15/mo
- Kling official v3 image-to-video schema (no motion brush): https://kling.ai/document-api/api/video/3-0-omni/image-to-video
- Kling motion_brush parameter spec (v1.0 only, mask + bezier paths): https://piapi.ai/docs/kling-api/motion-brush-examples , https://goapi.ai/docs/kling-api/create-task
- Kling Motion Control vs Motion Brush (different tools): https://ugccopilot.ai/blog/kling-motion-control-complete-guide
- fal Kling v3 Pro i2v input schema: https://fal.ai/models/fal-ai/kling-video/v3/pro/image-to-video/api
- ToonCrafter (illustrated input, 2-10 keyframes, $0.062/run): https://replicate.com/fofr/tooncrafter
- LTX 2.3 Creative Lab tasks incl. Inpaint/Outpaint + Cinemagraph: https://replicate.com/replicate/ltxvideo-2.3-lora
- Wan 2.7 i2v first/last-frame + continuation: https://replicate.com/wan-video/wan-2.7-i2v
- Audio cleanup free tiers: Adobe Podcast Enhance (1 hr/day, ≤30 min/file, 50-70 strength) https://tooltrim.com/en/guide/adobe-podcast-ai-free-limits-alternatives-2026 ; Auphonic free = 2 hr/mo WITH a jingle
