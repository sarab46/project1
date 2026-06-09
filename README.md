# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

This project collects and exposes WashU undergraduate housing information (first‑year, sophomore, and upper‑division housing, on‑ and off‑campus options, and common student guidance).
This knowledge is valuable because students repeatedly ask the same operational questions (which dorms are first‑year, modern vs. traditional differences, moving timelines, amenities), and official pages are spread across multiple units (Residential Life, Admissions, OISS) while student discussion adds anecdotal detail; aggregating and grounding answers saves time and reduces misinformation.
---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Residential Life — First Year Housing | Official university page | https://reslife.wustl.edu/living-at-washu/for-students/first-year-housing/ |
| 2 | Residential Life — South 40 buildings | Official university page | https://reslife.wustl.edu/living-at-washu/for-students/south-40-buildings/ |
| 3 | Residential Life — Student housing overview | Official university page | https://reslife.wustl.edu/living-at-washu/for-students/ |
| 4 | Admissions — Residential communities | Official admissions guide | https://admissions.wustl.edu/life-at-washu/residential-communities/ |
| 5 | OISS — Housing resources and off‑campus guidance | Official international student housing page | https://oiss.wustl.edu/housing/ |
| 6 | Dis‑Orientation housing guide (student site) | Student-created guide / perspectives | https://sites.wustl.edu/diso2026-27/housing/ |
| 7 | Olin undergraduate housing | Department housing guidance | https://olinundergradglobal.wustl.edu/student-housing/ |
| 8 | Mail Services — living off campus | University help page | https://mailservices.wustl.edu/living-off-campus/ |
| 9 | Reddit — r/washu thread on on‑campus requirement | Community discussion | https://www.reddit.com/r/washu/comments/1oj10yd/oncampus_living_requirement/ |
| 10 | Reddit — dorm layouts and private bathroom reports | Community discussion | https://www.reddit.com/r/washu/comments/12qf4nn/washu_undergraduate_single_dorms_with_private/ |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** Approximately 500 tokens per chunk (≈ 3,000–3,500 characters) to keep semantic units coherent while fitting into common model context windows.

**Overlap:** 75 tokens overlap to avoid splitting sentences and lists across chunk boundaries and to increase the chance retrieved context contains the full fact.

**Why these choices fit your documents:** Pages are a mix of short lists (room amenities, dorm names) and longer prose (policies, descriptions); 500 tokens balances granularity and context so retrieval returns concise, answerable passages rather than long irrelevant blocks.

**Final chunk count:** 13 (see `data/chunks.jsonl`).

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** `sentence-transformers` all‑MiniLM‑L6‑v2 (local) — chosen for speed and low memory footprint during development.

**Production tradeoff reflection:** For a production service I'd consider higher‑dimensional API embeddings (e.g., OpenAI text‑embedding‑3‑large or similar) to increase retrieval precision; tradeoffs include higher cost and storage, potentially lower latency for a local model vs. more accuracy from larger models, and multilingual/domain‑specific needs that might justify fine‑tuning or using specialist embeddings.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**
"You are a helpful assistant that MUST answer using only the information in the provided documents. Use exact wording from the documents when possible. Do NOT use your own external knowledge. If the documents do not contain enough information to answer, respond exactly: 'I don't have enough information to answer that.'"

**How source attribution is surfaced in the response:**
The prompt builder injects each retrieved chunk with a header containing `source`, `url`, and `position`; the generator is instructed to answer only from those chunks. The UI and API return the answer plus the list of source metadata (source and URL) so callers can verify claims; the conservative fallback synthesizer also attaches the source chunk text for each claim.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Which dorms can freshmen live in at WashU? | First‑year students are assigned to South 40 residential communities (list of first‑year halls). | Returned South 40 overview and list of first‑year residence halls with source links to Residential Life pages. | Relevant | Accurate |
| 2 | What is the difference between modern and traditional dorms? | Modern buildings: newer, often suite‑style and have elevators; Traditional: older layouts, communal bathrooms on floors. | Answer described modern vs traditional but missed a few nuance examples; top chunk had higher similarity distance. | Partially relevant | Partially accurate |
| 3 | Where do sophomores usually live? | Many sophomores remain on the South 40; some move to the Northside or special interest housing. | Returned that most sophomores live on South 40 and described Northside/Village options with sources. | Relevant | Accurate |
| 4 | Can sophomores live off campus and when do students usually move off campus? | Off‑campus options exist; many students move off campus after sophomore year, but policies and timing vary. | Mentioned off‑campus options (OISS, Quadrangle) and cautioned about timing; linked to OISS guidance. | Relevant | Partially accurate |
| 5 | What amenities are available in WashU dorms? | Amenities vary by hall and room type (lounges, dining, fitness, mail center, Wi‑Fi, laundry). | Listed common amenities from Residential Life and Admissions pages and included per‑hall examples. | Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off‑target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** Which dorms are explicitly listed as having private bathrooms?  

**What the system returned:** The answer mixed examples and student anecdotes and did not confidently list which halls have private bathrooms.  

**Root cause (tied to a specific pipeline stage):** The per‑hall bathroom information was split across multiple small HTML sections and across two chunks; retrieval returned only one fragment (retrieval stage) and the generator had insufficient contiguous context to state the full list.  

**What you would change to fix it:** Increase chunk size or improve HTML‑aware chunking to keep full per‑hall amenity lists together; add a reranker that prefers chunks containing hall names when the question mentions a specific hall.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**
The `planning.md` chunking and retrieval sections forced explicit choices (500‑token target, 75‑token overlap, top‑k=5) which made it straightforward to implement and test `scripts/ingest_and_chunk.py`, `scripts/build_embeddings.py`, and `scripts/query.py` consistently; having these concrete values also helped prompt the AI when generating implementation code so outputs matched the desired behavior.  

**One way your implementation diverged from the spec, and why:**
I initially used the local `sentence-transformers` `all-MiniLM-L6-v2` model instead of an API‑hosted high‑dimensional embedding (the spec indicated this as a development choice), because latency and ease of offline testing were prioritized for development and reproducibility in the classroom environment; production deployment would trade cost for higher‑quality embeddings.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* The `Chunking Strategy` section from `planning.md` plus several example HTML pages and asked: "Implement `chunk_text()` that is HTML‑aware, uses ~500 token chunks with 75 token overlap, and preserves headings as boundaries."  
- *What it produced:* A Python function that split text naively by characters and tried to preserve headings.  
- *What I changed or overrode:* I refactored the generated code to use sentence‑based splitting, added explicit overlap handling, and fixed edge cases for list items and HTML tables so per‑hall lists were preserved.  

**Instance 2**

- *What I gave the AI:* A prompt describing the retrieval + generation flow and the desired grounding instruction and asked it to scaffold `scripts/generate.py` with a conservative system prompt and a Groq‑backed call path.  
- *What it produced:* A working `generate.py` scaffold that built a prompt from retrieved chunks and attempted a Groq call if `GROQ_API_KEY` existed.  
- *What I changed or overrode:* I edited the prompt to require the exact fallback sentence when documents are insufficient, added safer error handling around the Groq call, and ensured the function returns both answer text and the list of source metadata for UI display.

## Demo video guidance

Record a 3–5 minute demo showing: (1) three different queries with the returned answer and visible source citations in the UI, (2) one query where retrieval+generation works well (e.g., "Which dorms can freshmen live in?"), (3) one query where the system struggles (e.g., "Which dorms have private bathrooms?" — narrate that the data was split across chunks and retrieval returned fragments), and (4) a quick walkthrough of the evaluation table in this README.  

Note: some WashU pages are behind portal logins or require an active WashU account; these pages were not crawled during ingestion — document this limitation in the video and show how the UI returns a conservative "I don't have enough information to answer that." response when the sources are missing.

---

If you want, I can also generate a short recording script (lines to say during the video) and a set of three example queries to paste into the UI.
