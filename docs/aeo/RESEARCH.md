# AI Engine Optimization (AEO/GEO) Research Report — August 2026
## For ironwoodbooks.com: Indie Children's Book Publisher

---

## EXECUTIVE SUMMARY

AI search engines (ChatGPT, Claude, Perplexity, Google AI Overviews, Copilot) now handle **12–18% of English informational queries** as of Q1 2026, up from under 2% a year prior. For a small indie children's book site, this represents a genuine discovery opportunity—but only if you understand how these engines *source* answers, which differs fundamentally from Google's traditional search model.

**Key Insight:** AI engines show a **strong bias toward earned media (84% of citations)** and third-party authority over brand-owned content (5–10%). For a tiny domain like ironwoodbooks.com, this means: skip chasing backlinks to your site; instead, focus on appearing in third-party curated lists, reviews, and recommendations that AI engines actively cite.

**Honest Timeline:** 
- Structural/technical fixes: **2–4 weeks** visible (crawler access, schema)
- Content optimization + direct-answer pages: **4–8 weeks**
- Third-party earned media impact: **2–6 months** (requires real outreach, not automation)
- Meaningful traffic volume: **3–12 months** (depends on category competition and authority)

---

## 1. HOW AI ENGINES SOURCE ANSWERS (August 2026)

### The Dual Architecture: Training Data vs. RAG Retrieval

All major AI engines use **two distinct information pathways**:

1. **Training Data (Pre-cutoff, baked into model weights)**
   - Content published before the model's training cutoff is embedded inside the model itself
   - These models cannot be updated without retraining
   - You have *no direct control* over this layer; it's historical

2. **RAG (Retrieval-Augmented Generation) — Live web search at inference time**
   - When a user asks a current question, the engine fetches live web results
   - Only about **15% of retrieved pages get cited** (most are just context)
   - This is where **current visibility happens**

**Critical Practical Difference:**
- Training data → shapes how the model *describes your category* (useful for authority framing)
- RAG retrieval → determines whether you *get cited today* (determines traffic)

For a small site, **RAG retrieval matters far more** than training data, because you'll never have significant training-data presence until you build authority over months/years. Focus on being *in live indices* and *retrievable* for queries about your content.

---

### Which Index/Crawler Each Engine Uses

| Engine | Training Crawler | Search/Retrieval Index | Crawler User-Agent (Search) |
|--------|-----------------|----------------------|----------------------------|
| **ChatGPT Search** | GPTBot | Bing (licensed) | OAI-SearchBot |
| **Claude** | ClaudeBot | Proprietary Anthropic index | Claude-SearchBot |
| **Perplexity** | PerplexityBot (training) | Proprietary + public web | PerplexityBot |
| **Google AI Overviews** | Google-Extended | Google Index (existing) | Googlebot |
| **Copilot/Gemini** | Various | Bing/Microsoft Graph | Not separately branded |

**Key Finding:** ChatGPT Search's visibility is **directly tied to Bing's index**. If Bing hasn't indexed your content, ChatGPT can't cite it. This makes **Bing Webmaster Tools + IndexNow** unexpectedly critical for multi-engine coverage (strong evidence).

---

## 2. TECHNICAL CHECKLIST: What Measurably Helps

### Priority 1: Crawler Access (robots.txt) — Implement Immediately

**Status: STRONG EVIDENCE** — Blocking crawlers literally prevents visibility.

**Recommended robots.txt configuration** (for most publishers, including indie):

```
# Block training crawlers (protects content from model ingestion)
User-agent: GPTBot
Disallow: /

User-agent: ClaudeBot
Disallow: /

# Allow search/retrieval crawlers (maintains citation visibility)
User-agent: OAI-SearchBot
Allow: /

User-agent: Claude-SearchBot
Allow: /

User-agent: PerplexityBot
Allow: /

# Perplexity user agent (real-time user fetches)
User-agent: Perplexity-User
Allow: /

# Standard crawlers
User-agent: Googlebot
Allow: /

# Google training signal (opt-out only; comment out to block AI training use)
# User-agent: Google-Extended
# Disallow: /
```

**Rationale:**
- Training crawlers (GPTBot, ClaudeBot) → protect your IP from model training without attribution
- Search crawlers → keep you visible in live AI answers
- Review quarterly; new crawlers emerge (e.g., AppleBot-Extended in 2026)

**For ironwoodbooks.com:** Add this configuration to `/robots.txt` on Cloudflare Pages. Verify crawlers can access your site via Bing Webmaster Tools and Claude/Perplexity documentation logs.

---

### Priority 2: Bing Indexing & IndexNow — Critical for ChatGPT

**Status: STRONG EVIDENCE** — ChatGPT Search runs on Bing's index. If Bing hasn't crawled your page, ChatGPT can't cite it.

**Implementation:**
1. Verify your site is indexed in Bing Webmaster Tools (submit sitemap)
2. Implement **IndexNow** — Bing crawls pages typically within 24 hours of submission
3. Set up IndexNow on your site (details in Bing Webmaster Tools)

**Timeline:** 24–48 hours for initial indexing; 1–2 weeks for stable presence.

**Why this matters:** Bing is owned by Microsoft, which owns ~49% of OpenAI. Bing's crawl feeds OpenAI's retrieval index.

---

### Priority 3: Google Search Console & Sitemap

**Status: STANDARD PRACTICE** — Ensures Google crawls your content. While Google AI Overviews are less dominant than ChatGPT/Claude/Perplexity today, they still represent ~5–7% of conversational queries.

**Action:** Verify ironwoodbooks.com in Google Search Console, submit sitemap, monitor crawl errors.

---

### llms.txt (The Controversial File)

**Status: SPECULATIVE / LOW CONFIDENCE** 

**What it is:** `/llms.txt` — a human-readable file you place at your site root describing your brand, permissions, and preferred citation format.

**Adoption Reality (as of August 2026):**
- ~10% adoption across major domains (up from 2.13% in 2025)
- **Anthropic & Perplexity** have publicly confirmed support; they do use it
- **OpenAI** (ChatGPT) has never explicitly confirmed consuming llms.txt; Google explicitly does not
- Measured effectiveness: **8 out of 9 sites saw no measurable change** in traffic after implementing it

**Evidence Assessment:** Modest, incremental benefit if you implement it well. It does **NOT** unlock visibility on its own. Most value is in **brand governance** (reducing AI hallucinations about your products) rather than citation boost.

**Recommendation for ironwoodbooks.com:** **Optional.** If you implement it, use it to:
1. Declare your books and their correct descriptions
2. Point to your official website
3. Request accurate author/publisher attribution

**Example template:**
```
About: Ironwood Books publishes children's books teaching philosophy and values
Creator: Evan Paliotta (author/publisher)
Books: 
  - The Ways of the World (ages 14+)
  - The Adventures of the Curious Kid (ages 4-8)
  - Philosophy books for children focused on Aristotle's Golden Mean
Website: https://ironwoodbooks.com
Contact: hello@ironwoodbooks.com
```

**Skip if time-constrained.** Not a blocker.

---

### Structured Data (Schema.org) — Moderate Evidence

**Status: MIXED EVIDENCE** — Helps but isn't required. FAQ schema is no longer a Google SERP feature (Google dropped it in May 2026), but FAQ *content* (actual question-answer pairs on the page) still helps.

**Recommended Schema Types for ironwoodbooks.com:**

1. **Article Schema** (on blog posts, author pages)
   - Title, author, publication date, content description
   - Helps Claude & Perplexity understand your content structure

2. **Book Schema** (on product/landing pages for each book)
   - ISBN, author, description, image, publisher info, reviews
   - Increases likelihood of citation in book-recommendation contexts
   - Example: `"The Ways of the World - ages 14+" + schema data`

3. **FAQPage Schema** (if you create dedicated FAQ pages)
   - Helps LLMs parse Q&A structure
   - Not required, but correlates with ~40% higher citation likelihood

4. **Organization Schema** (homepage)
   - Name, logo, contact, founder (Evan), social profiles
   - Establishes brand identity for AI systems

**Implementation:** Use JSON-LD in `<script type="application/ld+json">` tags. Tools: Schema.org validator, Yoast SEO (if you migrate to WordPress), or hand-code in Astro templates.

**Realistic Impact:** 5–15% citation improvement if well-implemented; not a game-changer on its own.

---

### Page Speed, Mobile Friendliness, Rendering

**Status: STANDARD PRACTICE** — Not unique to GEO, but matters.

AI crawlers can index static HTML and do parse JavaScript-rendered content, but:
- **Static HTML (Astro default)** → crawlers see content immediately ✓
- **JS-heavy rendering** → delays crawler understanding, may miss content

**For ironwoodbooks.com (Astro + Cloudflare Pages):** You're already doing this well. No changes needed.

---

## 3. CONTENT PATTERNS AI ENGINES CITE

### Research Finding: What Gets Cited

Data from 17,551+ analyzed AI citations (BrightEdge, HubSpot, Ritner Digital) shows:

| Format | Citation Share | Best For |
|--------|----------------|----------|
| **Listicles** ("Best X for Y") | 21.9% | Commercial intent (product discovery) |
| **Articles** (how-to, explainers) | 16.7% | Informational intent |
| **Product pages** | 13.7% | E-commerce, tangible items |
| **Comparison tables** | Variable | ChatGPT specifically (95% citation rate) |
| **FAQ sections** (with schema) | Variable | Reduces hallucinations, boosts clarity |

---

### Content Structure That Works

**Universal winning pattern:**

1. **Open with a direct 1–2 sentence answer** (44.2% of LLM citations come from the first 30% of a page)
2. **Use H2 subheadings** as questions (mirrors conversational input)
3. **Provide 50–150 word answers** under each heading (digestible for LLM context windows)
4. **Include stats, original research, author credentials** (E-E-A-T signals)
5. **Update visible date** at the top/bottom (shows freshness to LLMs)
6. **Name the author with a bio** (vastly increases citation likelihood; 67% higher inclusion with named authorship)

---

### For ironwoodbooks.com Specifically: Book Description Strategy

**Current structure:** Product pages for each book (good).

**Optimization:**
- Add a **"Who should read this?"** FAQ section
  - Question: "What age is The Ways of the World for?"
  - Answer: "Ages 14 and up. It covers timeless ideas about how the world works, including stories on leadership, ethics, and thinking for yourself."

- Add a **"What makes Ironwood Books different?"** comparison table
  - Compare to: traditional school textbooks, other indie publishers, mainstream self-help for teens
  - Highlight: philosophy-focused, parent-written, not AI-generic

- Add **author credibility signals** to each book page
  - Evan's background (father, what makes him qualified to write for children)
  - Where books are available (Amazon, direct download)
  - Reviews/testimonials (if any; can add as you collect)

- Create a **"Best philosophy books for children"** listicle/comparison page
  - Include your two books alongside 3–5 other respected titles
  - Cite real reviews or curricula that use them
  - Make it comparative, not just promotional

---

### E-E-A-T: Experience, Expertise, Authoritativeness, Trustworthiness

**Status: STRONG EVIDENCE** — Drives both Google and AI citations.

**What AI systems specifically reward:**
- **Experience:** Real-world use case (Evan writing for his son counts; tie it to the content)
- **Expertise:** Domain knowledge (philosophy/education background helps; if Evan has any formal training, mention it)
- **Authoritativeness:** Verifiable credentials and third-party mentions (book reviews, teacher recommendations, etc.)
- **Trustworthiness:** Transparent author bio, correct information, updated content

**Data:** Sites with strong E-E-A-T signals see **67% higher inclusion rates** in AI answers and **3.2x more frequently cited** than sites lacking these signals.

**Action for ironwoodbooks.com:**
1. Expand the "About Evan" page with real credentials and motivation
2. Add author bio to every book description
3. Collect and display testimonials (teachers, parents who've read the books)
4. Link to external authority (philosophy education organizations, curriculum listings)

---

## 4. OFF-SITE CITATION SOURCES — Where AI Engines Pull From

### The Citation Cartel (August 2026)

Research from Everything-PR and 5W PR found that **Wikipedia, Reddit, and YouTube account for >60% of all AI citations** across engines. This creates a "citation cartel" where small sites struggle to surface unless they're also mentioned in these dominant sources.

**Citation frequency by source type:**

| Source | Multi-Engine Freq. | Notes |
|--------|-------------------|-------|
| **Reddit** | 40–46% | #1 source across every major AI engine |
| **Wikipedia** | 26–48% (ChatGPT: 48%) | Foundational training + RAG source |
| **YouTube** | ~19% (Google Overviews) | Dominant video source |
| **LinkedIn** | Top 5 (B2B dominant) | Blogs, articles, professional content |
| **Forbes** | Top 5 | Doubled in ChatGPT citations post-Sept 2025 |
| **Goodreads** | Not in top 50 | **Surprisingly low for books** |
| **Amazon reviews** | Not prominently cited | **Below expectation** |
| **Book blogs** | Not measured | **No major data on indie book blogs** |

---

### What This Means for ironwoodbooks.com

**Bad news:** Book discovery via AI is **NOT** primarily routed through Goodreads or Amazon, despite those being major book platforms. This means:
- Being a top-rated book on Goodreads doesn't directly translate to AI citations (though it adds credibility)
- Amazon's "Customers also bought" won't trigger AI recommendations

**Good news:** There are proven off-site channels that DO get cited:

1. **Reddit** (40% multi-engine frequency)
   - Communities: r/Parenting, r/Teachers, r/Philosophy, r/ChildrensBooks
   - Strategy: Genuine participation, answering questions about values/parenting/education
   - Do NOT spam with links; Redditors detect this instantly
   - **Effectiveness:** High (Reddit citations volatile but high-volume)
   - **Timeline:** 4–12 weeks to build credibility; long-term payoff

2. **Wikipedia** (26–48% frequency depending on engine)
   - Limited upside for indie publishers (Wikipedia has strict notability rules)
   - *Could* create: "Philosophy in Children's Literature" mention if you gather enough press coverage
   - **Not a quick-win channel**

3. **Education/Parenting blogs & listicles** (unmeasured but observable)
   - Parent blogs, education blogs, philosophy blogs that curate "best books for X"
   - These get cited by AI when they're comprehensive/authoritative
   - Strategy: Reach out to 20–30 education bloggers, offer review copies
   - **Effectiveness:** Moderate-to-high if blog is well-known
   - **Timeline:** 2–4 weeks per relationship; 3–6 months to see cumulative impact

4. **Book review platforms for indie authors**
   - IndieReader, Indie Book Awards (both get some AI citations)
   - Submit your books for review/awards (costs ~$50–300 per submission)
   - **Effectiveness:** Low-to-moderate (niche audience)
   - **Timeline:** 2–3 months for results

5. **Curriculum/education resource sites**
   - ALA Recommended Reading Lists (ALSC has summer reading lists, teacher favorites)
   - Teachers Pay Teachers, Common Sense Media
   - Philosophy for Children resources (The Philosophy Foundation, Prindle Institute)
   - **Strategy:** Reach out to curators, offer your books as recommended resources
   - **Effectiveness:** Moderate (curriculum integration takes time but is stable)
   - **Timeline:** 3–12 months

---

### Third-Party Strategy (The Real GEO Lever for Small Sites)

**Key Finding:** Distributing content to a wide range of publications can increase AI citations by **up to 325%** compared to publishing only on your own site.

**Specific actions for ironwoodbooks.com:**
1. Create 3–5 shareable, permission-focused articles:
   - "Philosophy at Home: 5 Aristotle Ideas for Dinner Table Conversations"
   - "Why Picture Books About Values Matter More Than You Think"
   - "Curious Kids Ask the Deepest Questions — Here's How to Answer Them"

2. Pitch these to:
   - Parent blogs (MomJoy, Modern Parents Messy Kids, etc.)
   - Education blogs (Edutopia, TeachingChannel, etc.)
   - Philosophy blogs (Philosophy Foundation, Brains On, etc.)
   - Medium (large audience, gets AI-cited when well-written)

3. Each placement should link back to ironwoodbooks.com or mention your books by name

4. Stack multiple mentions across platforms → AI engines notice pattern → higher citation likelihood

**Realistic conversion:** 1–3 successful placements per 20 outreach attempts (3–15% success rate for cold pitches).

---

## 5. MEASUREMENT: How to Track AI-Driven Visibility & Traffic

### Referrer Tracking (GA4 / Cloudflare Analytics)

**Direct indicators of AI traffic:**

| AI Engine | Referrer String | Crawler User-Agent |
|-----------|-----------------|-------------------|
| ChatGPT Search | chatgpt.com | OAI-SearchBot |
| Claude | claude.ai | Claude-SearchBot, Claude-User |
| Perplexity | perplexity.ai | PerplexityBot, Perplexity-User |
| Google AI Overviews | google.com | Googlebot (in referrer) |
| Copilot | copilot.microsoft.com | Bingbot |

**In Cloudflare Analytics for ironwoodbooks.com:**
1. Go to Analytics > Requests by Referrer
2. Look for traffic from `chatgpt.com`, `perplexity.ai`, `claude.ai`
3. Filter by these referrers to isolate AI traffic
4. Note: Some AI crawlers don't send referrer (especially Claude-User), so this undercounts

**In GA4:**
1. Create a custom channel group with regex for AI referrers: `(chatgpt|perplexity|claude\.ai|copilot\.microsoft)`
2. Track these as "AI Search" channel separate from "Organic"
3. Monitor weekly; track conversion rate separately (AI visitors convert 3–27x better than organic)

---

### Crawler Activity (Server/CDN Logs)

**Monitor for these crawlers in your Cloudflare logs:**
- `OAI-SearchBot` → ChatGPT Search indexing
- `Claude-SearchBot`, `Claude-User` → Claude retrieval
- `PerplexityBot`, `Perplexity-User` → Perplexity indexing
- `GPTBot`, `ClaudeBot` → Training crawls (you blocked these, so expect minimal/zero traffic)

**What to look for:** Consistent crawl activity (weekly or more frequent) = the bot is actively indexing your site.

---

### AI Visibility Measurement Tools

**For a small budget (free or <$100/month):**

1. **Profound (free tier with limited features)**
   - Tracks how often your site is mentioned in AI-generated answers
   - Pricing: Free tier tracks 10 queries, paid tiers from $200/month
   - **Best for:** Tracking specific product/brand mentions
   - **Effort:** Low; set up once, check weekly

2. **Otterly AI** ($29/month for SMBs)
   - Monitors AI citations and brand mentions across ChatGPT, Claude, Perplexity, Google Overviews
   - Tracks share of voice in AI answers
   - **Best for:** Indie/small publishers on a tight budget
   - **Effort:** Low maintenance

3. **Ahrefs Brand Radar** (with paid Ahrefs plan, $129+/month)
   - AI visibility is bolted on to Ahrefs's SEO suite
   - Tracks mentions and citations
   - **Best for:** If you already use Ahrefs for SEO
   - **Effort:** Moderate; requires SEO knowledge

4. **Manual Testing Protocol (FREE)**
   - Run monthly tests with your target queries
   - Log mentions in a spreadsheet
   - **Example queries for ironwoodbooks.com:**
     - "Philosophy books for teenagers"
     - "Best books teaching kids values"
     - "Picture books about curiosity for kids"
     - "How to teach ethics to children"
   - Try each query in ChatGPT Search, Claude, Perplexity, Google AI Overviews
   - Screenshot/note if Ironwood Books is mentioned
   - **Timeline:** 15 minutes per month
   - **Cost:** Free
   - **Accuracy:** Manual but reliable; catches things automated tools miss

---

### Bing Webmaster Tools (New in 2026)

**Breaking feature:** Microsoft added **Citation Share** reporting in Bing Webmaster Tools (April 2026).

**What it shows:**
- Percentage of AI citations your site captures for specific queries
- Tracked over time (weekly/monthly trends)
- Early access only; rolling out through 2026

**Action for ironwoodbooks.com:**
1. Set up Bing Webmaster Tools (if not already)
2. Watch for Citation Share feature availability in your region
3. Track citation share for key queries once available

---

## 6. BOOK DISCOVERY SPECIFICS (Children's Books & Philosophy)

### Where Books Actually Get Discovered in 2026

**Research Finding:** For children's books specifically, AI citation patterns differ from general merchandise:

| Discovery Channel | Evidence | Notes |
|-------------------|----------|-------|
| **Goodreads** | Low-to-moderate | Primarily an internal recommendation engine, not cited by AI engines |
| **Amazon** | Low | Reviews cited occasionally, but not as primary discovery source |
| **Educational blogs** | High | Teacher blogs, parenting blogs, curriculum sites heavily cited |
| **ALA lists** (ALSC) | High | Association for Library Service to Children lists are authoritative & cited |
| **School reading lists** | High | Curriculum integration + school adoption = authority signal |
| **Wikipedia** | Moderate | Lists of "Children's literature" or "Philosophy books" if notability met |
| **Reddit** | Moderate | r/Parenting, r/Teachers communities discuss book recommendations |
| **YouTube** | Moderate | Book reviewers (BookTube); if a video becomes popular, cited in Overviews |

---

### The "Philosophy + Children" Niche Opportunity

**Key finding:** Philosophy education is a growing niche in K–12, but resources are scattered:

**High-authority sources for philosophy education:**
- The Philosophy Foundation (UK-based, but globally recognized)
- Prindle Institute for Ethics (Indiana University)
- ALSC Book Lists (American Library Association, children's division)
- Common Sense Media (parental guide, often cited)
- University education departments (curriculum research)

**Realistic path to visibility:**
1. **Get listed on Philosophy Foundation's resource page** (if they accept indie publishers)
   - Contact: Do research on their submission process
   - Value: Trusted, AI-cited source

2. **Submit to ALSC Summer Reading List / Teacher Favorites**
   - Typically curated once yearly
   - Acceptance: Low (hundreds of submissions), but high payoff if accepted
   - Contacts in research results

3. **Get reviews from education-focused publications**
   - Common Sense Media book reviews
   - Education Week (smaller children's books section)
   - Scholastic's Teacher Magazine (for educator-facing reviews)

4. **Create a "Books for Teaching Philosophy to Children" list on your site**
   - Include your books + 5–10 other well-known philosophy children's books
   - Make it authoritative with citations
   - AI engines will cite this comparison when people ask "best philosophy books for kids"

---

### Goodreads Strategy (Complement, Not Primary)

**Why Goodreads is lower-priority for AI discovery:**
- Goodreads is a closed ecosystem; its content isn't heavily crawled by AI engines
- However, Goodreads reviews and ratings *do* matter for SEO/brand signals (Google uses them)
- Goodreads readers are humans (your real customers), not AI engines

**Action for ironwoodbooks.com:**
- Claim your books on Goodreads (both published titles)
- Encourage readers to review (offer review copies)
- Goodreads is useful for human discovery + credibility, not AI discovery

---

## 7. REALISTIC TIMELINE & EFFORT

### What Pays Off When

| Tactic | Timeline | Effort | Confidence | Cost |
|--------|----------|--------|------------|------|
| **robots.txt + crawler access** | 1–4 weeks | Low (1–2 hrs) | STRONG | Free |
| **Bing indexing + IndexNow** | 1–2 weeks | Low (2–4 hrs) | STRONG | Free |
| **Schema markup (Book + Article)** | 2–4 weeks | Moderate (4–8 hrs) | MIXED | Free |
| **Direct-answer FAQ pages** | 4–8 weeks | Moderate (8–16 hrs) | STRONG | Free |
| **One well-placed guest article** | 2–4 weeks (to write & pitch) + 3–6 weeks (for traction) | Moderate (4–6 hrs) | STRONG | Free (or review copy) |
| **Third-party review campaign (10 pitches)** | 6–12 weeks | High (20–30 hrs) | STRONG | $0–300 (optional review fees) |
| **Build Reddit presence** | 8–16 weeks | High (ongoing) | STRONG | Free |
| **Goodreads/Amazon reviews** | Ongoing | Low | MIXED | Free |
| **Paid tool (Otterly, Profound)** | Immediate | Low (setup) | MIXED | $30–200/mo |
| **llms.txt file** | 1–2 hours | Low | SPECULATIVE | Free |

---

### Case Study Timelines (Real Data from August 2026)

**Short-term wins (published by multiple sources):**
- **Beauty brand:** 3.3x increase in AI mentions in **60 days** (structured content + schema)
- **Fintech platform:** +22% AI discoverability in **4 weeks** (direct-answer pages)
- **SaaS company:** 0 → 70% relevant AI answers in **6 weeks** (combined technical + content)

**Medium-term results (3–6 months):**
- **B2B software:** 3x growth in AI-attributed traffic after **90 days** (earned media + content)
- **Fintech:** 4,900% revenue increase, 2,622% traffic growth in **14 months** (full program)

**Key insight:** Most dramatic results come from **third-party earned media** (blogs, reviews, listicles), not on-site optimization alone. Technical + content = 4–8 week visible impact; earned media = 2–6 month compounding impact.

---

## 8. COMMON MISTAKES (Avoid These)

1. **Blocking all training crawlers AND search crawlers** → Makes you invisible to all AI engines
   - Mistake: `Disallow: /` for all AI bots
   - Fix: Block training bots (GPTBot, ClaudeBot), allow search bots (OAI-SearchBot, Claude-SearchBot)

2. **Waiting for llms.txt to be a game-changer** → It isn't, not yet
   - Mistake: Spending weeks perfecting llms.txt instead of creating content
   - Fix: Implement only if easy; prioritize content

3. **Assuming Goodreads + Amazon = AI visibility** → Wrong
   - Mistake: Focusing 100% effort on book platform reviews
   - Fix: 50% on Goodreads (for humans), 50% on education blogs/Reddit (for AI)

4. **Building backlinks for authority** → Slow and low ROI for GEO
   - Mistake: Buying backlinks, seeking high-DA link exchanges
   - Fix: Invest in earned media placements instead (higher citation ROI)

5. **Publishing only on your own site** → 5× fewer AI citations than distributed content
   - Mistake: Keeping exclusive content only on ironwoodbooks.com
   - Fix: Repurpose articles into guest posts, Medium posts, Substack, etc.

6. **Ignoring Reddit** → 40% of AI citations come from Reddit
   - Mistake: Dismissing Reddit as "not credible"
   - Fix: Build authentic presence in parenting/teaching communities; answer genuine questions

7. **One-off outreach** → Relationships > one-time emails
   - Mistake: Spamming 100 bloggers with templated "review my book" emails
   - Fix: Pick 20–30 education/parenting bloggers, follow them, engage with their content, *then* ask

---

## 9. PRIORITIZED ACTION LIST FOR IRONWOODBOOKS.COM (Top 10)

### Phase 1: Foundation (Weeks 1–4) — Get Listed & Indexable

1. **Implement robots.txt for AI crawlers**
   - Add block rules for GPTBot/ClaudeBot; allow rules for OAI-SearchBot/Claude-SearchBot/PerplexityBot
   - Estimated time: 30 minutes
   - Cost: Free
   - Expected impact: Enables all downstream GEO tactics

2. **Set up Bing Webmaster Tools + IndexNow**
   - Claim ironwoodbooks.com in Bing Webmaster Tools
   - Submit sitemap
   - Enable IndexNow (auto-notifies Bing when you update pages)
   - Estimated time: 1–2 hours
   - Cost: Free
   - Expected impact: 24–48 hour indexing; enables ChatGPT Search visibility

3. **Add schema markup to Book product pages**
   - Book schema for "The Ways of the World" and "The Adventures of the Curious Kid"
   - Include: title, author (Evan), publication date, ISBN, description, image, publisher
   - Estimated time: 2–4 hours
   - Cost: Free
   - Expected impact: 5–10% citation improvement on book-specific queries

4. **Verify Google Search Console**
   - Ensure ironwoodbooks.com is verified
   - Monitor indexing status
   - Estimated time: 30 minutes
   - Cost: Free
   - Expected impact: Maintains Google AI Overviews visibility

---

### Phase 2: Content Optimization (Weeks 4–8) — Make Pages AI-Citable

5. **Create a "Best Philosophy Books for Children" comparison page**
   - Include your two books + 5–10 well-known titles
   - Structure: Listicle format, comparison table, E-E-A-T signals (author bio)
   - Estimated time: 4–6 hours
   - Cost: Free
   - Expected impact: STRONG — listicles are 21.9% of all AI citations; you become the source

6. **Add FAQ sections to each book product page**
   - "Who should read this book?" "What makes this book different?" "How can teachers use it?"
   - Estimated time: 2–3 hours
   - Cost: Free
   - Expected impact: MODERATE — FAQ content boosts clarity for AI systems; not a huge traffic driver but helps precision

7. **Write a "How to Teach Philosophy at Home" guide**
   - 2,500–3,500 word article
   - Structure: Direct answer in first 200 words, H2 subheadings as questions, stats/credibility signals
   - Pitch to 3–5 parenting blogs as guest article
   - Estimated time: 6–8 hours (including pitching)
   - Cost: Free (or $50 review copy to influential parent bloggers)
   - Expected impact: STRONG — earned media placements compound over months

---

### Phase 3: Earned Media & Community (Weeks 8–16) — Build Third-Party Citations

8. **Launch Reddit community participation**
   - r/Parenting: Answer questions about raising thoughtful kids
   - r/Teachers: Discuss resources for teaching values/philosophy
   - r/ChildrensBooks: Review your books authentically
   - Do NOT spam; focus on genuine value (Answer 10 genuine questions before mentioning your books)
   - Estimated time: 30–60 minutes/week (ongoing)
   - Cost: Free
   - Expected impact: STRONG (40% multi-engine frequency); slow burn but compounding

9. **Pitch review copies to 20 education/parenting blogs**
   - Build a list of 20–30 relevant blogs (philosophy-focused, parenting, education)
   - Personalize pitches; mention why their audience would love your books
   - Offer free review copy
   - Estimated time: 8–12 hours (one-time)
   - Cost: $0–40 (2 review copies if needed)
   - Expected impact: STRONG — 10–30% conversion = 2–9 placements; each placement = 1–3 month visibility boost

10. **Submit books to ALSC (American Library Association) Teacher Favorites & Summer Reading Lists**
    - Research annual submission process for ALSC recommendations
    - Submit "The Adventures of the Curious Kid" (picture book, perfect for ALSC audience)
    - Estimated time: 4–6 hours
    - Cost: Free (may require ISBN/publication proof)
    - Expected impact: VERY HIGH IF ACCEPTED — ALA lists are foundational to education discovery; but acceptance rate is low (1–3%)

---

### Bonus: Quick Wins (If Time Permits)

11. **Create an llms.txt file** (Optional, quick)
    - Add to `/llms.txt` at site root
    - No huge impact, but low effort
    - Estimated time: 30 minutes
    - Cost: Free

12. **Set up Otterly AI monitoring** (Optional, nice-to-have)
    - Get weekly digest of AI mentions of "Ironwood Books" and your book titles
    - Estimated time: 30 minutes setup + 5 min/week review
    - Cost: $29/month
    - Value: Visibility into what's working; helps you prioritize effort

---

## SUMMARY: What Actually Works (Evidence Assessment)

### STRONG EVIDENCE (Do These)
✅ Allow AI search crawlers, block training crawlers  
✅ Index with Bing + use IndexNow  
✅ Create listicle/comparison pages (highest citation format)  
✅ Add direct-answer content with E-E-A-T signals  
✅ Pitch to education blogs & Reddit (earned media dominates citations)  
✅ Schema markup (modest but real boost)  

### MIXED EVIDENCE (Helpful But Not Essential)
⚠️ llms.txt (nice for brand control, low citation impact)  
⚠️ FAQ schema markup (content matters more than schema)  
⚠️ Goodreads/Amazon reviews (helps humans, not AI engines)  
⚠️ Paid AI visibility tools for small publishers (nice to track, but not required)  

### SPECULATIVE / HYPE (Skip)
❌ Backlink building for GEO (slow, low ROI)  
❌ Targeting mega-authority domains only  
❌ Expecting domain authority to substitute for content quality  

---

## SOURCES

### Core Research & Case Studies
- [Mastering generative engine optimization in 2026 — Search Engine Land](https://searchengineland.com/mastering-generative-engine-optimization-in-2026-full-guide-469142)
- [Answer Engine Optimization Statistics 2026 — OmniBound AI](https://www.omnibound.ai/blog/answer-engine-optimization-aeo-statistics)
- [How ChatGPT, Google AI Overviews, and Perplexity Source Information in 2026 — Leapd](https://www.leapd.ai/blog/ai-visibility/how-chatgpt-google-ai-overviews-and-perplexity-source-information-in-2026)
- [GEO 2026 Case Studies — Averi](https://www.averi.ai/learn/the-definitive-guide-to-geo-get-cited-by-ai-in-2026)
- [The 50 Most Cited Websites in AI Search — Everything-PR](https://everything-pr.com/the-50-most-cited-websites-in-ai-reddit-wikipedia-youtube-lead-2026-index)

### Crawlers & Technical
- [AI Crawler User Agents Reference 2026 — Honey B AI](https://www.honeyb.ai/blog/ai-crawler-user-agents-reference-2026)
- [GPTBot, ClaudeBot, PerplexityBot Configuration Guide 2026 — Best SEO SG](https://www.bestseo.sg/blog/ai-crawlers-gptbot-claudebot-perplexitybot/)
- [State of llms.txt 2026 — Presenc AI](https://presenc.ai/research/state-of-llms-txt-2026)
- [Bing Webmaster Tools: Secret Weapon for AI Search Visibility 2026 — BlogSEO](https://www.blogseo.io/blog/bing-webmaster-tools-ai-search-visibility-2025)

### Content Formats & Structure
- [Content Formats AI Engines Actually Cite — HubSpot Marketing Blog](https://blog.hubspot.com/marketing/content-format-types-that-earn-citations)
- [The Content Formats AI Search Actually Cites 2026 — Ritner Digital](https://www.ritnerdigital.com/blog/the-content-formats-ai-search-actually-cites-based-on-what-were-seeing-across-clients)
- [FAQ Schema for AI Overviews 2026 — StackMatix](https://www.stackmatix.com/blog/optimizing-faq-schema-google-ai-overviews)

### Measurement & Tools
- [How to Track AI Traffic (ChatGPT, Claude, Perplexity) 2026 — Humblytics](https://humblytics.com/blog/how-to-track-ai-traffic-chatgpt-claude-perplexity)
- [AI Visibility Tools Comparison 2026 — Nick Lafferty](https://nicklafferty.com/blog/best-ai-visibility-optimization-platforms/)
- [Tracking AI User Bots in Cloudflare 2026 — Two Octobers](https://twooctobers.com/blog/tracking-ai-user-bots-in-cloudflare-to-measure-ai-visibility/)

### Book Discovery & Publishing
- [Where Indie Authors Can Get Reviews 2026 — Indie Book Beacon](https://indiebookbeacon.com/2026/06/02/where-indie-authors-can-get-honest-book-reviews-2026/)
- [How Indie Book Marketing Works 2026 — Indie Lit Lounge](https://indielitlounge.substack.com/p/how-to-get-more-book-reviews-in-2026)
- [ALSC Book Lists & Teacher Favorites 2026 — American Library Association](https://www.ala.org/alsc/book-lists)
- [Philosophy for Children Resources — The Philosophy Foundation](https://www.philosophy-foundation.org)

### E-E-A-T & Authority
- [How AI Search Engines Interpret Expertise & Trust 2026 — Medium](https://medium.com/@ianbann/how-ai-search-engines-interpret-expertise-and-trust-in-2026-7c4db3e0510b)
- [E-E-A-T in 2026 — Contently](https://contently.com/2026/05/11/eeat-and-ai-search-author-credentials/)

---

**Report Generated:** August 2026  
**Target Audience:** Small indie children's book publisher  
**Confidence Levels Applied:** Evidence-backed claims prioritized; speculative tactics flagged
