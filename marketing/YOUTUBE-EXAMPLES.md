# YOUTUBE-EXAMPLES.md — real-world animated read-aloud examples (researched 2026-09-29)

## The benchmark channel
LolliPop Animated Book (youtube.com/@LolliPopBook). 2D cutout animation over
book art, music bed, Amazon affiliate book link in description. EXACTLY our
monetization model (books, not ad revenue).
- "Pete the Cat I Love My White Shoes | Animated Book | Read aloud" — 3:56, 41.8M views
- "Where's Spot?" — 2:11, 4.6M views
- "Pete the Cat Saves Christmas" — 4:15, 3.8M views
What to steal: subtle puppet-style character motion only; full-screen art;
length 2-4 min (not 10); book link first line of description; music bed under
narration; evergreen keywords stacked in description.

## Publisher / interactive style
- "Where's Spot? | Interactive Read Aloud | Penguin Storytime" — publisher-run,
  flap-lift interactive pauses ("Where could Spot be?"). Steal: the pause-and-
  question beat fits our Kid asking questions.

## Author DIY (closest to our production reality)
- Heather Cash — "How to Create a Read-Aloud Video of Your Children's Book"
  (Canva-based, author-made).
- Mike Donohue's "$9" book-trailer workflow: static frames -> Runway/Kling
  free credits for hero motion -> Canva assembly -> human voiceover. Proves
  the free-tier + assemble-in-free-editor path works for indie authors.
- ReadKidz — commercial all-in-one (paid) AI picture book + animated video;
  shows the demand, we assemble equivalent pipeline from free pieces.

## AI video model landscape (for accent clips), distilled
- The hard truth from practitioners: all of these are MOTION engines, not
  story engines. They struggle when asked to keep identity + scene + motion at
  once. Our case is the EASIEST version: our illustrations already have a
  consistent character; we need only subtle motion. Image-to-video with our
  art as the reference is the documented strength of every tool below.
- Kling 3.0: best motion physics/consistency per clip; free tier limited.
- Runway Gen-4.5: best per-shot control (motion brush = animate ONE region,
  e.g. just the Kid's arm — ideal for "small animations"); 125 free credits.
- PixVerse V6: best speed, cheapest per clip; daily free credits.
- Pika: weakest quality, best free tier (80/mo, no watermark, commercial OK).
- Seedance 2.x: best multi-reference consistency (multi-angle character).
- Veo 3.1: best native audio (we don't need it — we have Evan's voice).
- Higgsfield: aggregator for all of the above in one workspace + Soul Cast
  character consistency + MCP integration. Best-fit paid option; blocked only
  by the no-paid-tools rule pending Evan's sign-off.

## Verdict for our bake-off
Test the SAME Kid illustration with: Runway motion brush (free credits),
Kling free tier, PixVerse free tier, and Higgsfield free playground. Pick by
eye. If none pass, local Wan in ComfyUI is the fallback, and Higgsfield paid
is the escalation.
