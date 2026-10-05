# Ironwood Books — Marketing Ops (source of truth)

One-person press. Agent runs the cadence; Evan approves manuscripts/covers and pushes to deploy.
Deploy = `git push origin main` from ~/Projects/ironwood-books (Evan does this; agent commits locally only).

## Cadence
- 1 guide/week. Agent drafts Monday, commits, Telegram note: "Guide drafted + committed — push to deploy."
- 80% evergreen / 20% reactive. Every guide: 2 internal links (guide↔book, guide↔guide), FAQ block, comparison table when the topic fits, "Last updated" date.
- Every new book spawns 2 companion guides at publish time.
- Monthly (first Monday): AEO check job — see METRICS.md.

## Guide queue (draft in this order; mark DONE + date when committed)
| # | Brief | Status |
|---|-------|--------|
| 1 | Philosophy books by age: comparison table, 4-6 vs 7-9 vs 10-12, incl. series + 3rd-party titles | DONE 2026-09-28 |
| 2 | Socratic questions to ask your kid at bedtime (10 questions, FAQ format) | DONE 2026-10-05 |
| 3 | Plato for kids — philosopher deep-dive #1 (sets up Book 4) | TODO |
| 4 | Critical thinking books for 5-year-olds (long-tail) | TODO |
| 5 | How to read aloud so kids ask questions (companion to series spine) | TODO |
| 6 | Stoicism for kids: Marcus Aurelius / Epictetus explainers | TODO |
| 7 | Books about opposites/contrast for kids (companion to Book 3, Lao Tzu) | TODO |
| 8 | Golden Mean worked examples for everyday parenting (refresh of existing guide + last-updated stamp) | TODO |

## One-time fixes (Week-1 list)
- [x] llms-full.txt generated from site content (2026-09-28; full text of all 6 guides, linked from llms.txt)
- [ ] guides/index.astro → Astro.glob auto-discovery (kills hand-maintained array) — BLOCKED: `import: 'frontmatter'` glob is not supported for .astro pages in the current Astro version; reverted to the manual array. Frontmatter added to all guides so the swap is trivial once supported.
- [x] JSON-LD: add lastReviewed/lastUpdated to GuideLayout schema (2026-09-28)
- [x] "Last updated" visible on all 6 existing guides (2026-09-28; byline now reads "Last updated <date>")

## Rules
- Never invent KDP/Amazon facts; ASIN dp URLs only (skill: ironwood-book-factory).
- Voice: Evan's plain first-person dad voice — read ~/Projects/ironwood-series-archive/Ironwood Books/BRAND_TASTE.md before drafting.
- No em-dashes in book copy; guides follow the same house voice.
- Keyword method: Amazon autocomplete endpoint (see ironwood-book-factory KDP section) + manual AI-answer checks. No paid tools.
