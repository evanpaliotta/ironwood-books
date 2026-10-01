# Ironwood Books — AEO/SEO Metrics log

Monthly ritual (first Monday), run by the Ironwood AEO Check cron. Append a block per run, never overwrite.

Free measurement, no paid tools:
1. Search Console (https://search.google.com/search-console, property ironwoodbooks.com) — impressions/clicks trend, top queries. Requires Evan's browser session if API not connected; agent reports what it can and flags gaps.
2. AI citation check: run these 6 queries in ChatGPT, Perplexity, and Google (AI Overview) — is ironwoodbooks.com cited or mentioned, and which page?
   - best philosophy books for kids
   - books that teach kids to think
   - how to introduce philosophy to your child
   - aristotle golden mean for kids
   - books for teenage boys who don't read
   - lao tzu for kids / tao te ching for kids
3. Kit (ConvertKit) form signups count for the month (Evan's dashboard, or himalaya inbox check of the automation sends).

## Log

### 2026-09 (baseline)
- Baseline established; 5 guides live, llms.txt, schema, IndexNow deployed.
- GSC/AI-citation numbers: pending first check run.

### 2026-10
- Assets: ironwoodbooks.com, /llms.txt, /llms-full.txt, /sitemap-index.xml all HTTP 200. Pass.
- Guide audit (shipped since last check): philosophy-books-by-age (publishDate 2026-09-28). Live 200 + title present on https://ironwoodbooks.com/guides/philosophy-books-by-age/; "Last updated September 28, 2026" matches publishDate; registered in public/llms.txt (Guides summary) and public/llms-full.txt (full block, line 83). FAQPage JSON-LD (4 Q&A) live. Pass — only guide shipped this window, no drift.
- AI citations (6 queries): FIRST-PARTY BLOCKED THIS RUN. Google launched AI Overview for query 1 (best philosophy books for kids) then hard-rate-limited the headless IP (~89.x after one query); Perplexity behind Cloudflare bot wall with no saved session; ChatGPT no saved session. So no first-party ChatGPT/Perplexity citation read this cycle — flag for a manual check from Evan's browser.
- Organic SERP visibility (web_search proxy, all 6 clean queries): ironwoodbooks.com does NOT rank top-5 for any clean money query. Only surfaces when query contains site/brand terms (i.e., self-search). Competitors owning AI-answer space: Five Books, Doing Good Together, Kidopoly (Lao Tzu + Aristotle), School Reading List / UK Bookshop (teen boys), Britannica (golden mean).
- Indexed/QA surface is healthy: /guides/how-to-introduce-philosophy-to-your-child returns full FAQ-style copy and ranks #1 on its branded long-tail. Content is crawlable and quotable; the gap is authority/links, not on-page.
- Trend vs 2026-09: first real data. Baseline~flat: no citations gained, no losses (nothing to lose yet). No serverside errors observed.
- GSC data not available this run (no Search Console auth from cron).
- Next action (highest value): win one authority backlink/citation from a site already in AI-answer space (Five Books, Doing Good Together, School Reading List, Kidopoly) — pitch The Curious Kid meets Lao Tzu (new Book 3) so ironwoodbooks.com is the source AI answers cite for a philosophy-for-kids query. Guide-side follow-up (lower): Lao Tzu / opposites companion guide (queue #7) to own "lao tzu for kids" clean query.

