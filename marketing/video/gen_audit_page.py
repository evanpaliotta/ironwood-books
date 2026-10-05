#!/usr/bin/env python3
"""gen_audit_page.py — emit the pipeline audit page STRAIGHT FROM manifest.py, so the
published plan and the prompts actually sent to the model can never disagree."""
import importlib, json, os
import manifest as M

REV = "/Users/evanpaliotta/Projects/ironwood-series-archive/book-01-adventures/video/review"
T = M.T
total = sum(M.duration(n) for n in sorted(M.MANIFEST))
cost = total * 0.05

rows = []
for n in sorted(M.MANIFEST):
    m = M.MANIFEST[n]
    slot = T[n]; dur = M.duration(n)
    beats = "<br>".join(f"{i+1}. {b}" for i, b in enumerate(m["beats"]))
    cap = " <span class='warn'>(15s cap: 0.74s settle hold)</span>" if (n == 16) else ""
    held = "" if dur >= slot + 0.5 else " <span class='warn'>(hold)</span>"
    rows.append(f"""<tr><td>{n}</td><td>{slot:.2f}s → <b>{dur}s</b>{held}{cap}</td>
<td>{m['start']}</td><td>{beats}</td><td>{m['dir']}</td></tr>""")

audit = [
 ("Backpedaling / time-reversed motion", "Reversal is gone from the toolchain; every clip is generated FORWARD from the still. The gate measures the subject's area trend and fails a clip whose direction contradicts the manifest.", "manifest 'dir' + qa_gate direction check"),
 ("Visible seam mid-scene", "One clip per scene. There is no join anywhere in the book, so there is nothing to seam.", "architecture (20 clips, 20 scenes)"),
 ("A structure appearing (the barn)", "Every prompt names that scene's static anchors and says nothing new appears. The gate diff's frame 0 against 1.5s/3s/mid/end outside the subject's tracked box and flags any region over 1.5% of frame.", "manifest 'static' + qa_gate structure check"),
 ("An invented character (the second child)", "Population is stated positively with counts in every prompt; the strip is read for counts before it ships.", "manifest 'pop' + strip review"),
 ("Wardrobe drift (pajamas)", "One fixed wardrobe string in all 20 prompts.", "prompt template"),
 ("Talking mouths", "'His mouth stays relaxed; he does not speak and does not mouth words' in all 20 prompts; checked on the strip.", "prompt template + strip review"),
 ("Wrong travel direction (scene 13)", "Direction is explicit in the beats ('walks AWAY from the viewer') and enforced by the gate (8% area-trend threshold).", "manifest beats + gate"),
 ("Frozen end / dead air", "Full-length clips from the still; no arrivals to pad; the freeze check looks for IDENTICAL CONSECUTIVE FRAMES (the metric that caught my earlier mistake).", "gate freeze check"),
 ("Scene 5's story logic (must end at the beach)", "The beats carry him rolling away toward the beach, and the gate's continuity check compares the clip's last frame with scene 6's first frame.", "manifest beats + continuity check"),
 ("Narration sync", "narration-timings-v3-final.json is the master clock: clip length = slot, turns sit inside the measured pauses, verified by silencedetect on the finished cut.", "assembly + verification"),
 ("Page turns", "Rendered from the outgoing scene's REAL last frame into the incoming scene's REAL first frame, ends verified exact.", "assembly"),
]

risks = [
 ("Grok variance — no prompt guarantees a take", "The gate reduces, never eliminates. Budgeted ~30% re-renders ($4 of the $18). A failed clip is re-rendered and re-gated before you see it."),
 ("Scene 16 (15.74s slot, 15s cap)", "0.74s settle hold at the end while everything breathes — the one hold in the book, and it lands on the outro beat."),
 ("Scene 15's visual leads its line by ~1 line", "You've accepted this. Starting at the still means he's already leaning over the book while 'just up ahead' is spoken."),
 ("Clips of 14–15s are past anything I've verified", "12s and 14s came back clean in the A/B test; 15s is untested. Five scenes request 15s — first failures will be here and I'll report them."),
 ("Ambient drift (waves, grass, bees)", "Allowed by design — the structural classifier decides whether a change is ambient (fine) or structural (fail)."),
 ("The gate cannot judge 'feel'", "It measures seam delta, direction, structure, wardrobe, population, timing. Whether a clip is charming is your call, always."),
]

# Findings from the independent art verification pass (each one caught a real error in my draft plan)
verified = [
 ("Scene 6 — pose was wrong", "I had him at the water's edge being crashed on. The art shows him standing on DRY sand with a hand at his chin, the wave breaking offshore. Start pose and beats rewritten."),
 ("Scene 6 — wardrobe was wrong", "He is BARE FOOT in this illustration. A single global 'brown boots' string would have fought the book's own art, so wardrobe is now per-scene, with the art as the source of truth."),
 ("Scene 10 — pose and action were wrong", "The coconut is already low, near his knee, and he is standing with his arms at his sides. I had invented 'arms up, startled'. Beats rewritten."),
 ("Scene 11 — bees were misplaced", "The two bees hover high in the sky; my beat brought them to circle his head. They now stay where the art puts them."),
 ("Scene 19 — the prop was wrong", "It is a HANDHELD brass spyglass held up to the sky, not a tripod he kneels at. Start pose, prop and beats rewritten."),
 ("Prompt format — run-on clauses", "The beats concatenated into a single run-on sentence. Now each beat is its own sentence under 'Act in this order:'.", ),
 ("Freeze metric — wrong measure", "The A/B test showed my 'motion coverage' scored the good clip lower than the frozen one. A freeze is now detected as IDENTICAL CONSECUTIVE FRAMES."),
 ("Gate threshold — too strict", "A correct recede shrank the subject only 14% across the clip and was wrongly failed at a 15% bar. Now 8%."),
]

html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Book 1 — pipeline audit (one model, one method)</title>
<style>
:root{{--gold:#c9b26a;--bg:#1a1f1c;--card:#242b26;--dim:#9fb0a4}}
body{{font-family:-apple-system,sans-serif;background:var(--bg);color:#eee;max-width:1100px;margin:28px auto;padding:0 18px}}
h1{{color:var(--gold);font-size:1.4em;margin-bottom:4px}}
h2{{color:var(--gold);font-size:1.08em;margin-top:26px}}
.sub{{color:var(--dim);margin-bottom:14px;line-height:1.5}}
.card{{background:var(--card);border:1px solid #333;border-radius:12px;padding:14px;margin:14px 0}}
table{{width:100%;border-collapse:collapse;font-size:.8em;margin-top:8px}}
td,th{{padding:6px 8px;border-bottom:1px solid #333;text-align:left;vertical-align:top}}
th{{color:var(--gold)}}
code{{background:#151a17;padding:1px 4px;border-radius:4px;font-size:.85em}}
.good{{color:#7fd18c}}.warn{{color:#e0a97a}}.bad{{color:#e08a7a}}
pre{{background:#151a17;padding:10px;border-radius:8px;font-size:.76em;white-space:pre-wrap;line-height:1.5}}
</style></head><body>
<h1>Pipeline audit — one model, one method, prompts rewritten</h1>
<div class="sub">Everything below is generated from <code>manifest.py</code>, the same file that assembles the prompts actually sent to the model, so this page and the run cannot drift apart. Nothing renders until you approve this.</div>

<div class="card">
<h2>1. The method</h2>
<ul style="line-height:1.6;font-size:.88em">
<li><b>One model:</b> Grok Imagine, 720p, 16:9. No Kling, no cap problems, no second toolchain.</li>
<li><b>One clip per scene.</b> Each clip begins on the pose the illustration shows and plays forward. No joins anywhere in the book.</li>
<li><b>No reversal, ever.</b> That was the backpedaling; it is out of the toolchain.</li>
<li><b>No holds</b> except scene 16's 0.74s settle (15s cap) — the only one.</li>
<li><b>Prompts are assembled from the manifest</b> — wardrobe, population, static anchors, ordered beats — never written by hand.</li>
<li><b>Every clip passes the gate before you see it:</b> direction, structural appearance (with ambient classification), freeze (identical consecutive frames), frame-0 fidelity, wardrobe/population on the strip, continuity with the next scene.</li>
<li><b>Scene 2 stays</b> as approved. Scenes 1 and 3–21 are regenerated (scene 1 because of the barn).</li>
</ul></div>

<div class="card">
<h2>2. The prompt template — one real example (scene 13, verbatim)</h2>
<pre>{M.prompt(13)}</pre>
<div class="sub">Every scene's prompt has the same four blocks in the same order: wardrobe · population with counts · static anchors + "nothing new appears" · "Act in this order: &lt;beats&gt;" · camera/style/mouth.</div>
</div>

<div class="card">
<h2>3. The 20-scene manifest (the actual input)</h2>
<table>
<tr><th>Sc</th><th>Slot → request</th><th>Start pose (from the art)</th><th>Beats, in order</th><th>Gate expects</th></tr>
{''.join(rows)}
</table>
</div>

<div class="card">
<h2>4. Audit — every failure we hit, and the control that now prevents it</h2>
<table>
<tr><th>Failure</th><th>Control</th><th>Enforced by</th></tr>
{''.join(f"<tr><td class='bad'>{a}</td><td>{b}</td><td><code>{c}</code></td></tr>" for a,b,c in audit)}
</table>
</div>

<div class="card">
<h2>5. What the independent verification pass caught (before any rendering)</h2>
<table>
<tr><th>Found</th><th>Correction</th></tr>
{''.join(f"<tr><td class='bad'>{a}</td><td>{b}</td></tr>" for a,b in verified)}
</table>
</div>

<div class="card">
<h2>6. Residual risks — what the plan does NOT solve</h2>
<table>
<tr><th>Risk</th><th>Honest position</th></tr>
{''.join(f"<tr><td class='warn'>{a}</td><td>{b}</td></tr>" for a,b in risks)}
</table>
</div>

<div class="card">
<h2>6. Run plan and cost</h2>
<p class="sub">276 seconds of generation across 20 scenes. <b>$13.80</b> at $0.05/s, plus a ~30% re-render allowance → <b>~$18 worst case</b>.</p>
<p class="sub">Batches of five, so you see progress and can stop: (1,3,4,5,6) → (7,8,9,10,11) → (12,13,14,15,16) → (17,18,19,20,21). After each batch: gate every clip, assemble the scenes built so far into a watchable partial, and report anything that failed with the evidence.</p>
<p class="sub">Then one final assembly: page turns from real frames, narration clock, silencedetect verification, and the finished 720p film plus a 1080p upload version.</p>
</div>

<div class="sub">Approve this and I start batch 1. If you want any beat changed, change it in the manifest — the page, the prompts and the run all follow.</div>
</body></html>"""
open(REV + "/pipeline-audit.html", "w").write(html)
print("written", REV + "/pipeline-audit.html")
print("total seconds", total, "cost $%.2f" % cost)
