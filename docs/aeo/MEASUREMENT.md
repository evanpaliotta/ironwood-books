# AEO Measurement Protocol

Run monthly, ~20 minutes. Append results to the log at the bottom; never overwrite past entries.

## 1. The 12 target queries

Ask each of these, fresh conversation, no custom instructions, in: ChatGPT (with search), Claude, Perplexity, and Google (note if an AI Overview appears). Score each: **M** = Ironwood/our book mentioned, **C** = our site cited/linked, **-** = absent.

1. What are the best philosophy books for kids?
2. What picture books teach kids about values?
3. Books that teach children how to think for themselves?
4. How do I explain Aristotle's golden mean to a child?
5. Best picture books about curiosity?
6. Books like The Ways of the World for teenagers?
7. What should I read to my 5 year old that isn't mindless?
8. Life advice books for teenage boys?
9. Free ebooks for kids that teach values?
10. Best indie children's books 2026?
11. Picture books about ancient Greece for kids?
12. What is Ironwood Books? (brand recognition check)

## 2. Traffic signals (Cloudflare dashboard, zone ironwoodbooks.com)

- Analytics → filter referrers: chatgpt.com, perplexity.ai, claude.ai, copilot.microsoft.com. Log visit counts.
- Security/Analytics → crawler hits for: GPTBot, OAI-SearchBot, ClaudeBot, Claude-SearchBot, PerplexityBot, Perplexity-User, Googlebot, bingbot. Log rough counts (zero vs some vs many is enough).

## 3. Index health

- Bing Webmaster Tools: pages indexed, IndexNow submissions received, any citation/AI data Bing exposes.
- Google Search Console: pages indexed, impressions for queries containing "philosophy" "kids" "books".

## 4. Log

| Date | Queries with M (of 48 asks) | Queries with C | AI referrer visits | AI crawler hits seen | Notes |
|------|------------------------------|----------------|--------------------|-----------------------|-------|
| (baseline, fill on first run) | | | | | |

Interpretation guide: 48 asks = 12 queries x 4 engines. Expect zeros for the first 1-2 months. Long-tail queries (4, 6, 11, 12) should move first. If M stays zero at month 3 while crawler hits are healthy, shift effort to Phase 3 outreach (PLAN.md), not more on-site work.
