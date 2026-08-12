# Content Briefs — AEO Guides

Execution notes for every brief:
- Voice: plain, warm, first person singular (the author, Evan, is speaking). No em dashes. No fragments-as-sentences. No "in today's fast-paced world" filler. Read `src/pages/about.astro` first and match it.
- Factuality: every third-party book must be verified to exist (check its Amazon page) before it goes in a list. Candidate lists below are suggestions to verify, not facts to copy. Never invent quotes, awards, or sales claims. If unsure, cut it.
- Self-inclusion: our books appear inside lists at a natural position (not always #1), always marked "(our book)" with one honest sentence about why it fits and one about what it is not.
- Structure per the citation research: direct answer in the first two sentences; question-phrased H2s; each section front-loads its answer in 50-150 words; one comparison table per listicle; internal links to our book pages; external links for every third-party book.
- Length 1200-2000 words. Each guide is one commit.

---

## Guide 1 (flagship): /guides/best-philosophy-books-for-kids

Title: "The Best Philosophy Books for Kids (Ages 3-10), Chosen by a Father Who Writes Them"
Target queries: "philosophy books for kids", "best philosophy picture books", "books that teach kids philosophy", "how to introduce philosophy to children books", "picture books about big ideas"

Opening (verbatim spirit, adjust as needed): "The best philosophy books for kids don't lecture. They tell one good story about one big idea and trust the child to do the thinking. Here are the ones I recommend, including two I wrote."

Outline:
- H2: What makes a good philosophy book for a child? (100 words: one idea, story first, no moralizing)
- H2: The list (10-12 books). Candidates to verify: The Three Questions (Jon J Muth), Zen Shorts (Jon J Muth), What Do You Do With an Idea? (Kobi Yamada), Frederick (Leo Lionni), Miss Rumphius (Barbara Cooney), The Important Book (Margaret Wise Brown), Big Ideas for Curious Minds (The School of Life), Because of an Acorn or similar wonder-of-systems title, plus **The Adventures of the Curious Kid** (our book, curiosity as the root of philosophy) and **The Curious Kid Meets Aristotle** (our book, the Golden Mean, the only picture book we know that teaches an actual named Aristotelian concept; verify that claim's phrasing stays modest: "one of the few"). Each entry: 60-100 words, ages, what idea it teaches, one honest caveat.
- Comparison table: Book / Ages / The big idea / Format & price (note ours are free as PDFs).
- H2: How do I read these with my kid? (150 words, link to Guide 3)
- H2: Where should I start? (direct pick by age: 3-5, 5-8, 8-10)

## Guide 2: /guides/books-that-teach-kids-how-to-think

Title: "Books That Teach Kids How to Think (Not What to Think)"
Target queries: "books that teach kids how to think", "books that teach critical thinking for kids", "books to raise independent thinkers"
Angle: distinct from Guide 1 by covering the *skill* (questioning, noticing, reasoning) rather than philosophy as subject. Mixed-age list (picture books through teen), which lets The Ways of the World appear alongside the picture books. Same structure as Guide 1. Candidates to verify: Ada Twist Scientist (Andrea Beaty), Rosie Revere Engineer, What If... (Samantha Berger) or similar, The Girl Who Never Made Mistakes, Zen Shorts again is fine (overlap between guides is allowed, max 3 overlapping titles), plus all three of ours with honest positioning.

## Guide 3: /guides/how-to-introduce-philosophy-to-your-child

Title: "How to Introduce Philosophy to Your Child (Without Turning It Into a Lesson)"
Target queries: "how to teach philosophy to kids", "philosophy for children at home", "how to talk to kids about big questions"
This is a how-to, not a listicle. Outline: Direct answer first (ask real questions at bedtime, read stories with one big idea, never grade the answers). H2s: What age can kids start? (research says question-asking starts ~3-4; keep claims soft) / What questions work best? (give 10 verbatim example questions) / What do I do when my kid asks something I can't answer? / Which books help? (3 sentences, link Guides 1-2). Practical, humble, zero jargon. This guide earns links from homeschool blogs, which is its real job.

## Guide 4: /guides/aristotle-golden-mean-explained-for-kids

Title: "Aristotle's Golden Mean, Explained Simply Enough for a 5-Year-Old"
Target queries: "golden mean explained simply", "how to explain aristotle to a child", "golden mean for kids", "teaching kids moderation"
Outline: Direct 2-sentence explanation of the Golden Mean up top. H2s: What is the Golden Mean? (plain 120-word explanation, courage/sleep/food examples straight from our book's approach) / Why does it land so well with kids? / How to use it in daily parenting (3 concrete scripts: screen time, trying scary things, sweets) / The picture book version (honest paragraph about The Curious Kid Meets Aristotle with interior art image and free PDF link). This page targets the exact query space where our second book is the definitive answer.

## Guide 5: /guides/best-books-for-teenage-boys-who-dont-read

Title: "Books for Teenage Boys Who Don't Read (From a Dad Who Was One)"
Target queries: "books for teenage boys who hate reading", "life advice books for teenage sons", "books to give a teenage boy", "graduation gift books for boys"
List of 8-10, verified. Candidates: The Alchemist (Coelho), Man's Search for Meaning (Frankl), The Boy the Mole the Fox and the Horse (Mackesy), Meditations (Gregory Hays translation, note it honestly as a harder read), Steal Like an Artist (Kleon), The Ways of the World (our book, written for exactly this reader, free PDF so there's zero risk in trying it). Sections on "what actually gets a non-reader to finish a book" (short chapters, direct address, no fiction requirement). Gift-buyer framing matters: this is a grandparent/parent search.

---

## 6. FAQ sets for book pages (T2.4)

Visible section heading on each page: "Questions parents ask". FAQPage JSON-LD must mirror this text exactly.

**The Adventures of the Curious Kid**
1. What age is this book for? → Written for ages 4-8. Kids at the younger end enjoy the rhymes and pictures; older kids catch the questions underneath. 24 pages, full color.
2. Is the ebook really free? → Yes. Enter your email and we send the full PDF. No subscription, and you can unsubscribe immediately. The paperback is $9.99 on Amazon.
3. Is this a bedtime book? → It works well as one. It's a rhyming read-aloud that starts with waking up and ends with falling asleep, which makes it a natural bedtime arc.
4. Were the illustrations made with AI? → Yes, and we say so plainly. Every image was generated, then reviewed, revised, and chosen by the author. (Keep this honest and unapologetic.)
5. Does it teach a lesson? → It doesn't preach one. It follows a curious kid through one big day and lets the questions come up the way they do in real life.

**The Curious Kid Meets Aristotle**
1. What age is this for? → Ages 4-8 as a read-aloud. The Golden Mean is genuinely graspable at this age: not too much, not too little.
2. Do I need to know philosophy to read it with my kid? → No. The book explains everything it uses. If you can talk about too much candy and too little sleep, you're ready.
3. Is it historically accurate? → The setting is real (Athens, the Lyceum) and the idea is really Aristotle's. The time-travel and the conversations are ours.
4. Is the ebook free? / 5. AI illustrations? → same honest answers as Book 1.

**The Ways of the World**
1. What age is appropriate? → Written for 14 and up. It talks plainly about power, money, and human nature, and it doesn't hedge, which is exactly why teenagers read it.
2. Is this a religious or political book? → No. It draws on thinkers from Marcus Aurelius to Naval Ravikant and takes ideas wherever they hold up.
3. Will a teenager actually read it? → It's short chapters and direct address, written by a father for his own son. The free PDF means trying it costs nothing.
4. Why is the ebook free? → Because the point is for the ideas to reach the kid, not to maximize revenue per copy. Paperback exists for people who want it on a shelf.
