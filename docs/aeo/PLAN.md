# AEO Execution Plan — ironwoodbooks.com

Goal: when someone asks ChatGPT, Claude, Perplexity, or Google AI "what are good picture books that teach kids values / philosophy / how to think," Ironwood Books gets mentioned, cited, or linked.

This plan is written for mechanical execution by a coding agent (Sonnet-class). Each task has concrete steps and acceptance criteria. Tasks marked **[EVAN]** need the human (account signups, dashboard toggles, judgment on outreach). Everything else is executable from this repo. Full research behind these decisions: `docs/aeo/RESEARCH.md`. Content briefs: `docs/aeo/BRIEFS.md`. Measurement protocol: `docs/aeo/MEASUREMENT.md`.

Ground rules for all work in this plan:
- Voice: plain sentences, first person where natural, no em dashes anywhere, no marketing fragments ("Timeless. Focused. Memorable."), no invented quotes or fake reviews. Match the tone of `src/pages/about.astro`.
- Never fabricate facts, statistics, or book details. Every third-party book named in a listicle must be a real book, verified against its Amazon or publisher page before inclusion.
- Our own books are always disclosed as ours in any list that includes them ("this is our book").
- After every task that changes the site: `npm run build` must pass, then commit and push to `main` (deploys via GitHub Actions to Cloudflare Pages).

---

## Phase 0: Unblock AI crawlers (do first, everything else is pointless until this is done)

### T0.1 [EVAN] Turn off Cloudflare's AI crawler blocking — ✅ DONE 2026-08-12
Toggled off in Security → AI Crawl Control → Signals → "Managed robots.txt". Verified `https://ironwoodbooks.com/robots.txt` no longer shows the Cloudflare-injected block. (Note: the toggle path in the current dashboard is AI Crawl Control → Signals, not Security → Bots as originally guessed — updating the steps below for the record.)
As of 2026-08-12, Cloudflare injects a managed robots.txt that DISALLOWS GPTBot, ClaudeBot, CCBot, Google-Extended, Amazonbot, Applebot-Extended, Bytespider, and meta-externalagent, and publishes `Content-Signal: ai-train=no`. The site is invisible to AI systems on purpose right now.

Steps (Cloudflare dashboard, zone ironwoodbooks.com, zone ID e3c1ec9d97fb86112ccff475380ce004):
1. Security → Bots (or "Bot Management" / "AI Audit" depending on dashboard version): set "Block AI bots" / "AI Scrapers and Crawlers" to **off** (or "Allow").
2. Find the "Content Signals" / managed robots.txt setting (surfaced under Bots or under the robots.txt management page) and **disable managed robots.txt injection** so the repo's own robots.txt (T0.2) is served as-is.
3. Verify: `curl -s https://ironwoodbooks.com/robots.txt` shows ONLY the repo file, no "BEGIN Cloudflare Managed content" block.

Decision + rationale (so nobody re-litigates it): we ALLOW all AI crawlers including training crawlers. The research default is "block training, allow search," which is an IP-protection posture. Our posture is reach: the ebooks are deliberately free, and being inside future models' training data means models natively know the brand. There is no revenue lost to AI reading these books; there is reach lost by hiding them.

### T0.2 Ship our own robots.txt — ✅ DONE 2026-08-12
Create `public/robots.txt` exactly:

```
# ironwoodbooks.com — all readers welcome, human or machine.

User-agent: *
Allow: /

Sitemap: https://ironwoodbooks.com/sitemap-index.xml
```

Acceptance: after deploy AND T0.1, `https://ironwoodbooks.com/robots.txt` serves this content with no Cloudflare-injected block. If the managed block still appears, stop and flag for Evan; do not proceed to Phase 2 until resolved.

---

## Phase 1: Technical foundation (one working session)

### T1.1 Sitemap — ✅ DONE 2026-08-12
1. `npx astro add sitemap` (adds `@astrojs/sitemap` and updates `astro.config.mjs`; `site` is already set).
2. Build and confirm `dist/sitemap-index.xml` exists.
Acceptance: `https://ironwoodbooks.com/sitemap-index.xml` returns XML listing all pages.

### T1.2 Structured data (JSON-LD) — ✅ DONE 2026-08-12
`src/components/Schema.astro` renders any JSON-LD object. Organization+Person+WebSite graph added to `MainLayout.astro` (renders on every page via a new `extraSchema` prop). Book schema added to all three book pages with real ISBNs (Ways of the World: 9798250261326, 124 pages, pulled from its live Amazon listing since it wasn't in memory). All JSON-LD validated as parseable JSON post-build.
Add a `<slot name="head" />`-free approach: create `src/components/Schema.astro` that takes a `schema` prop (object) and renders `<script type="application/ld+json" set:html={JSON.stringify(schema)} />`. Use it as follows.

1. **Organization + WebSite** on every page (add to `MainLayout.astro` head):
```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://ironwoodbooks.com/#org",
      "name": "Ironwood Books",
      "url": "https://ironwoodbooks.com",
      "logo": "https://ironwoodbooks.com/images/og-default.png",
      "founder": { "@id": "https://ironwoodbooks.com/#evan" }
    },
    {
      "@type": "Person",
      "@id": "https://ironwoodbooks.com/#evan",
      "name": "Evan Paliotta",
      "url": "https://ironwoodbooks.com/about",
      "jobTitle": "Author",
      "worksFor": { "@id": "https://ironwoodbooks.com/#org" }
    },
    {
      "@type": "WebSite",
      "url": "https://ironwoodbooks.com",
      "name": "Ironwood Books",
      "publisher": { "@id": "https://ironwoodbooks.com/#org" }
    }
  ]
}
```

2. **Book schema** on each of the three book pages. Template (fill per book from the table below):
```json
{
  "@context": "https://schema.org",
  "@type": "Book",
  "name": "<TITLE>",
  "author": { "@id": "https://ironwoodbooks.com/#evan" },
  "publisher": { "@id": "https://ironwoodbooks.com/#org" },
  "inLanguage": "en",
  "typicalAgeRange": "<AGE RANGE>",
  "genre": "<GENRE>",
  "image": "https://ironwoodbooks.com<COVER PATH>",
  "url": "https://ironwoodbooks.com/books/<SLUG>",
  "numberOfPages": <PAGES>,
  "isbn": "<ISBN, omit field if unknown>",
  "workExample": [
    {
      "@type": "Book",
      "bookFormat": "https://schema.org/EBook",
      "potentialAction": {
        "@type": "ReadAction",
        "target": "https://ironwoodbooks.com/books/<SLUG>#download",
        "expectsAcceptanceOf": { "@type": "Offer", "price": "0", "priceCurrency": "USD" }
      }
    },
    {
      "@type": "Book",
      "bookFormat": "https://schema.org/Paperback",
      "isbn": "<ISBN>",
      "offers": { "@type": "Offer", "price": "9.99", "priceCurrency": "USD", "url": "<AMAZON URL>" }
    }
  ]
}
```

| Book | Slug | ISBN | Amazon | Pages | Ages | Genre |
|---|---|---|---|---|---|---|
| The Adventures of the Curious Kid | the-adventures-of-the-curious-kid | 9798252325590 | https://www.amazon.com/dp/B0GSZ9MJL6 | 24 | 4-8 | Children's picture book |
| The Curious Kid Meets Aristotle | the-curious-kid-meets-aristotle | 9798181939677 | https://www.amazon.com/dp/B0H6PGDD98 | 24 | 4-8 | Children's picture book |
| The Ways of the World | the-ways-of-the-world | (check KDP bookshelf; omit if not found) | https://www.amazon.com/dp/B0GQXRLDBZ | (from KDP) | 14-18 | Young adult nonfiction, philosophy |

Acceptance: each page validates clean at https://validator.schema.org (paste rendered HTML), and `npm run build` passes.

3. **FAQPage schema** goes on book pages only when T2.4 adds visible FAQ sections. Schema must mirror the visible text exactly, never schema-only FAQs.

### T1.3 llms.txt — ✅ DONE 2026-08-12 (partial: no Guides link yet, add when Phase 2 ships)
Cheap, speculative value, do it anyway. Create `public/llms.txt`: one H1 (`# Ironwood Books`), one-paragraph description (site purpose, who it's for), then a bulleted link list: the three book pages with one-line descriptions, /about, /guides/ index (once it exists), and the free ebook policy sentence. Keep under 60 lines. Acceptance: served at `https://ironwoodbooks.com/llms.txt`.

### T1.4 [EVAN] Bing Webmaster Tools + Google Search Console
ChatGPT Search runs on Bing's index; this is why Bing matters more than habit suggests.
1. Bing: sign in at bing.com/webmasters with the Google account, use "Import from Google Search Console" if GSC exists, else verify by DNS TXT (add via Cloudflare dashboard or ask the agent to prep the record). Submit the sitemap.
2. Google Search Console: verify domain property via DNS TXT, submit sitemap.
Agent may do the in-browser clicking if Evan is signed in (same CDP browser flow used for KDP), but account choices are Evan's.

### T1.5 IndexNow (instant Bing indexing on deploy) — ✅ DONE 2026-08-12
Key file: `public/43af4e6d497dd7653af217c5ac327304.txt`. Ping step added to `.github/workflows/deploy.yml` after the Cloudflare Pages deploy step.
1. Generate a 32-char hex key, save as `public/<key>.txt` containing the key itself.
2. Add a deploy-time ping to `.github/workflows/deploy.yml` after the Pages deploy step:
```yaml
- name: Ping IndexNow
  run: |
    curl -s "https://api.indexnow.org/indexnow?url=https://ironwoodbooks.com/&key=<KEY>"
```
(Simple single-URL ping is enough at this site size; per-URL submission is overkill.)
Acceptance: workflow green, Bing Webmaster shows IndexNow submissions within a few days.

---

## Phase 2: Citable content (the actual strategy)

The research is unambiguous: listicles are the #1 cited format (about 22% of AI citations), direct-answer pages get pulled into answers, and pages need a named author and visible updated date. We are building the resource that AI engines cite for "philosophy books for kids," and it happens to be ours.

### T2.1 Guides infrastructure — ✅ DONE 2026-08-13
1. Create `src/layouts/GuideLayout.astro`: extends MainLayout; props: title, description, publishDate, updatedDate, plus Article JSON-LD (author = Evan Person @id, dates, headline). Visible byline block under the H1: "By Evan Paliotta · Updated <Month DD, YYYY>". Body slot styled like the About page (max-width ~720px prose, Fraunces headings).
2. Create `src/pages/guides/index.astro`: plain list of guides with one-line descriptions.
3. Add "Guides" to header nav and footer nav in MainLayout.
Acceptance: /guides/ renders, nav links work, Article schema validates.

### T2.2 Write the five guides — ✅ DONE 2026-08-13
All five shipped. Every third-party book in the listicles (guides 1, 2, 5) was verified real/in-print via web search before inclusion — see the verification pass in the session that wrote them. Guide 1 ended up with 8 verified third-party titles + our 2 (10 total) rather than the brief's "10-12," because padding with unverified titles would violate the no-fabrication rule. Guide 5 similarly has 5 verified third-party titles + ours (6) rather than "8-10" for the same reason. This is a real constraint going forward: don't pad lists to hit a round number.
Full briefs with target queries, outlines, and format rules are in `docs/aeo/BRIEFS.md`. Order of execution (highest leverage first):
1. `/guides/best-philosophy-books-for-kids` (the flagship listicle)
2. `/guides/books-that-teach-kids-how-to-think`
3. `/guides/how-to-introduce-philosophy-to-your-child` (how-to, no book list)
4. `/guides/aristotle-golden-mean-explained-for-kids`
5. `/guides/best-books-for-teenage-boys-who-dont-read` (Ways of the World's audience)

Non-negotiable format rules (they come straight from citation research):
- First 2 sentences of the page directly answer the title's implied question. No throat-clearing.
- H2s phrased as questions where natural; each H2 section answers itself in the first 50-150 words.
- One comparison table per listicle (title, ages, one-line "teaches", format/price).
- Named author + visible updated date (GuideLayout provides).
- Internal links to our book pages; external links to every third-party book's publisher or Amazon page.
- 1200-2000 words. Longer is not better.

### T2.3 One guide = one commit
Ship each guide as its own commit with build passing, so review and rollback stay clean. After each deploy, ping IndexNow (automatic via T1.5).

### T2.4 FAQ sections on the three book pages — ✅ DONE 2026-08-13
Built as a shared `BookFAQ.astro` component instead of copy-pasted per page: takes a `questions` array, renders the visible Q&A and the FAQPage JSON-LD from the same data, so the two can never drift apart.
Add a visible "Questions parents ask" section to each book page: 4-5 real questions with 2-4 sentence answers (see BRIEFS.md section 6 for the exact Q&A sets). Then add matching FAQPage JSON-LD. Acceptance: text visible on page, schema mirrors it exactly, validates.

---

## Phase 3: Earned media (where AI actually finds small brands)

Research finding: AI engines cite third-party surfaces (education blogs, Reddit, library lists) far more than small brand domains. On-site work makes us citable; this phase makes us cited. Most of this is [EVAN] judgment work; the agent preps materials.

### T3.1 Prep the outreach kit (agent) — ✅ DONE 2026-08-19
`docs/aeo/OUTREACH.md`. Includes a live, confirmed target (fivebooks.com — caught it being cited by Perplexity for the flagship query during the 2026-08-19 measurement check) plus categories still needing research before pitching.

### T3.2 [EVAN] Blog outreach
Pitch 15-20 parenting/homeschool/philosophy-education blogs for review or inclusion in their book lists (Philosophy Foundation, Prindle Institute's kids resources, homeschool curriculum bloggers, "books for kids" roundup authors found by searching the target queries in BRIEFS.md and noting who ranks). Reviews on those blogs are exactly what AI engines cite. Track pitches in OUTREACH.md.

### T3.3 [EVAN] Reddit, honestly
30-60 min/week in r/ChildrensBooks, r/homeschool, r/Parenting, r/booksuggestions: answer real questions well; mention our books only when they genuinely fit and always with the free-PDF link and a disclosure ("I wrote this one"). Reddit is the single most-cited domain in AI answers; astroturfing gets deleted and worse. No agent automation here, ever.

### T3.4 [EVAN] Library/institutional lists
Submit to ALSC/ALA reading list consideration, local library acquisition request forms, and Goodreads (claim author profile; add all three books). Low acceptance rates, high payoff, once per cycle.

---

## Phase 4: Measure monthly

See `docs/aeo/MEASUREMENT.md`: a 20-minute monthly protocol (ask the 12 target queries across ChatGPT/Claude/Perplexity/Google AI, log mentions in the table there; check Cloudflare analytics for chatgpt.com / perplexity.ai / claude.ai referrers and AI crawler hits; check Bing Webmaster citation data). The log lives in that file; append, never overwrite.

Honest expectations: Phase 0-1 effects (being indexable) within 2-4 weeks. Guide citations possible within 4-8 weeks on long-tail queries. Earned-media-driven mentions 3-6 months. If nothing has moved in the logs by month 3, the bottleneck is almost certainly Phase 3, not more on-site tuning.
