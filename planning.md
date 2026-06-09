# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

I picked housing for Washu STL as my domain. I wanted to answer housing questions for students looking for housing. It's valuable since one can save hours sifting through countless sources.
---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | https://reslife.wustl.edu/living-at-washu/for-students/first-year-housing/ | Covers freshman housing requirement, South 40 overview, Residential communities | https://reslife.washu.edu/living-at-washu/for-students/first-year-housing/ |
| 2 | https://reslife.wustl.edu/living-at-washu/for-students/south-40-buildings/ | South 40 Residential Communities — every freshman dorm, modern vs traditional, room types and amenities | https://reslife.washu.edu/living-at-washu/for-students/south-40-buildings/ |
| 3 | https://reslife.wustl.edu/living-at-washu/for-students/ | Residential Life — student housing overview for first-years, sophomores, and upper-division housing | https://reslife.wustl.edu/living-at-washu/for-students/ |
| 4 | https://admissions.wustl.edu/life-at-washu/residential-communities/ | Admissions housing guide — housing descriptions, room amenities, and community life | https://admissions.washu.edu/life-at-washu/residential-communities/ |
| 5 | https://oiss.wustl.edu/housing/ | Housing Options (OISS) — on-campus/off-campus options, requirements, and housing resources | https://oiss.wustl.edu/housing/ |
| 6 | https://sites.wustl.edu/diso2026-27/housing/ | Dis-Orientation Guide — student perspectives, apartment complexes, neighborhood overviews, housing stats | https://sites.wustl.edu/diso2026-27/housing/ |
| 7 | https://olinundergradglobal.wustl.edu/student-housing/ | Olin undergraduate housing resources — off-campus options, apartment info, meal-plan notes | https://olinundergradglobal.wustl.edu/student-housing/ |
| 8 | https://mailservices.wustl.edu/living-off-campus/ | Mail Services — living off campus guidance and university-supported off-campus housing information | https://mailservices.wustl.edu/living-off-campus/ |
| 9 | https://www.reddit.com/r/washu/comments/1oj10yd/oncampus_living_requirement/ | Reddit discussion on on-campus living requirement — student experiences, sophomore and Village housing | https://www.reddit.com/r/washu/comments/1oj10yd/oncampus_living_requirement/ |
| 10 | https://www.reddit.com/r/washu/comments/12qf4nn/washu_undergraduate_single_dorms_with_private/ | Reddit thread on dorm layouts and private bathrooms — student reports on single/double rooms and off-campus living | https://www.reddit.com/r/washu/comments/12qf4nn/washu_undergraduate_single_dorms_with_private/ |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**
For web pages and guides, use 500 tokens per chunk (≈3,000–3,500 characters).
**Overlap:**
Use 75 tokens overlap between consecutive chunks.
**Reasoning:**
Pages mix short FAQ sections, lists, and longer prose. A ~500‑token chunk keeps chunks small enough for accurate semantic embeddings while preserving local context; 75 tokens overlap prevents sentence/paragraph splits from losing meaning and helps retrieve contiguous facts (e.g., a dorm's amenities listed across lines). Use HTML-aware chunking (split on headings and list boundaries when present) so chunks align to semantic sections where possible.
---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**
Start with a moderate, fast model such as `all-MiniLM-L6-v2` (sentence-transformers) for development. For higher accuracy in production consider `text-embedding-3-large` (OpenAI) or equivalent high-dimension embeddings.
**Top-k:**
Retrieve top 5 chunks by default (`k=5`). Increase to 8–10 for longer queries or when the prompt benefits from more context.
**Production tradeoff reflection:**
If cost isn't a constraint use larger, higher-dimension embeddings to improve retrieval precision and reduce hallucination risk (longer context vectors, better semantic separation). Tradeoffs: higher accuracy vs higher cost and increased latency; larger models also require more storage and memory in the vector store. For multilingual or domain-specific tuning, consider fine‑tuned embeddings or adding domain‑specific signals (tf/idf weighting, publication date, source trust score).
---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | Which dorms can freshmen live in at WashU? | First‑year students are assigned to first‑year housing on the South 40 (see Residential Life first‑year housing). The system should return that freshmen are placed in South 40 residential communities and link to the per‑dorm listing on Residential Life. |
| 2 | What is the difference between modern and traditional dorms? | Modern halls have newer construction and often suite‑style layouts or more private bathrooms and updated amenities; traditional halls use older layouts with shared corridors and communal bathrooms (see South 40 buildings page for specific dorm comparisons). |
| 3 | Where do sophomores usually live? | Sophomores typically live in designated sophomore housing or upper‑division residence options described by Residential Life and Admissions; many remain on campus through sophomore year. The system should cite Residential Life/Admissions pages. |
| 4 | Can sophomores live off campus and when do students usually move off campus? | Policies vary by class and year, but many students move off campus after sophomore year (commonly junior year). The system should state that off‑campus options are available (see OISS/Mail Services/Dis‑Orientation guides) and note policy caveats. |
| 5 | What amenities are available in WashU dorms? | Amenities vary by hall and room type (examples: lounges, kitchenettes, wired/wireless networking, single/double rooms, and some halls with private or suite bathrooms). The answer should list common amenities and link to Admissions/Residential Life building pages for per‑hall details. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. Noisy or subjective sources: Reddit and student guides contain personal, sometimes contradictory opinions. Mitigation: prefer official pages for policy facts and surface student sources as anecdotal context with clear attribution and confidence scoring.
2. Fragmented or inconsistent page structure: HTML lists, tables, and PDFs may cause chunk splits that break facts across boundaries. Mitigation: implement HTML‑aware chunking (split on headings and list elements) and use overlap to capture context.
3. Stale or changing content: university pages and housing guides change annually. Mitigation: store source URLs and fetch timestamps; include last‑checked date in retrieval metadata and prefer recent official pages for policy answers.
4. Missing explicit lists: some answers require aggregating multiple pages (e.g., which dorms allow private baths). Mitigation: retrieve multiple chunks and use a conservative aggregator that cites sources for each claim.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->
```mermaid
flowchart LR
     A[Document Sources (web pages, Reddit, guides)] --> B[Ingestion: fetch HTML, normalize]
     B --> C[Chunking: HTML-aware, 500-token chunks, 75-token overlap]
     C --> D[Embeddings: sentence-transformers / OpenAI embeddings]
     D --> E[Vector store: FAISS or Chroma (store vectors + metadata + source URL + timestamp)]
     E --> F[Retriever: similarity search (top-k=5) + reranker/filters (source type, recency)]
     F --> G[Prompt Builder: synthesize retrieved chunks + instructions]
     G --> H[LLM: answer generation with source citations]
     H --> I[Post-process: add attributions, confidence score, source links]
```
---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**
Tool: Python scripts + BeautifulSoup, `requests`, `tiktoken` (or custom tokenizer).
Input: list of source URLs from Documents table and HTML content.
Output: normalized text chunks with metadata (URL, title, heading, chunk_id, char range, fetch timestamp).
Verify: run the ingestion on 2–3 pages and inspect chunk boundaries, overlap, and preserved headings.
**Milestone 4 — Embedding and retrieval:**
Tool: `sentence-transformers` (dev) or OpenAI embeddings (prod), vector DB `faiss` or `chromadb`.
Input: chunked documents from Milestone 3.
Output: persisted vector index with metadata and retrieval API (search by semantic similarity, filter by domain and recency).
Verify: run labelled queries from Evaluation Plan and ensure correct chunks appear in top‑k with expected source links.
**Milestone 5 — Generation and interface:**
Tool: LLM (OpenAI/GPT or chosen provider) for answer generation; minimal web UI or CLI wrapper for testing.
Input: user query + top‑k retrieved chunks + system prompt instructing citation style and conservative answering.
Output: final answer with inline citations and confidence score.
Verify: run the 5 evaluation questions and compare outputs to Expected answers; check that each factual claim is attributed to a specific source chunk.
