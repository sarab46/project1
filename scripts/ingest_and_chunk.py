#!/usr/bin/env python3
"""
Ingest documents (local files or web URLs) and chunk them according to planning.md.

Outputs:
 - data/raw/<slug>.txt for raw text
 - data/chunks.jsonl with one JSON object per chunk: {id, source, url, chunk_text}

This script is defensive: if `requests` or `bs4` are not installed it will only process local files.
"""
import os
import re
import json
import hashlib
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "documents"
RAW_DIR = ROOT / "data" / "raw"
CHUNKS_FILE = ROOT / "data" / "chunks.jsonl"

# Chunking parameters (match planning.md)
CHUNK_SIZE_CHARS = 3000  # approx ~500 tokens
OVERLAP_CHARS = 450      # approx ~75 tokens


def slugify(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s.lower()).strip("-")
    return s[:120]


def extract_sources_from_planning(planning_path: Path):
    txt = planning_path.read_text(encoding="utf-8")
    # extract URLs from Documents table lines
    urls = []
    for line in txt.splitlines():
        if line.strip().startswith("|") and "http" in line:
            # find all http(s) URLs in the line
            found = re.findall(r"https?://[^|\s)]+", line)
            for u in found:
                urls.append(u.strip())
    return list(dict.fromkeys(urls))


def clean_html_text(html: str):
    try:
        from bs4 import BeautifulSoup
    except Exception:
        # fallback: remove tags naively
        text = re.sub(r"<script.*?>.*?</script>", "", html, flags=re.S)
        text = re.sub(r"<style.*?>.*?</style>", "", text, flags=re.S)
        text = re.sub(r"<[^>]+>", "\n", text)
        text = re.sub(r"\n{2,}", "\n\n", text)
        return html_unescape(text)

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "form"]):
        tag.decompose()

    # prefer article or main
    main = soup.find("article") or soup.find("main")
    if main:
        text = main.get_text(separator="\n")
    else:
        # fallback to body
        body = soup.find("body")
        text = body.get_text(separator="\n") if body else soup.get_text(separator="\n")

    return html_unescape(re.sub(r"\n{2,}", "\n\n", text)).strip()


def html_unescape(s: str) -> str:
    import html

    return html.unescape(s)


def fetch_url(url: str):
    try:
        import requests
    except Exception:
        print("requests not available; skipping web fetch for", url)
        return None
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print("Failed to fetch", url, "->", e)
        return None


def split_into_sentences(text: str):
    # naive sentence splitter
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if s.strip()]


def chunk_text(text: str, chunk_size=CHUNK_SIZE_CHARS, overlap=OVERLAP_CHARS):
    sentences = split_into_sentences(text)
    chunks = []
    cur = []
    cur_len = 0
    for sent in sentences:
        cur.append(sent)
        cur_len += len(sent) + 1
        if cur_len >= chunk_size:
            chunk = " ".join(cur).strip()
            chunks.append(chunk)
            # prepare overlap: keep last overlap chars worth of text
            overlap_text = " ".join(cur)
            if len(overlap_text) > overlap:
                # find split point from the end at word boundary
                keep = overlap_text[-overlap:]
                cur = [keep]
                cur_len = len(keep)
            else:
                cur = []
                cur_len = 0
    if cur:
        chunk = " ".join(cur).strip()
        if chunk:
            chunks.append(chunk)
    # filter empties
    return [c for c in chunks if len(c) > 0]


def ensure_dirs():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    CHUNKS_FILE.parent.mkdir(parents=True, exist_ok=True)


def process_local_files():
    results = []
    for p in DOCS_DIR.iterdir():
        if p.is_file() and p.suffix.lower() in {".txt", ".md"}:
            text = p.read_text(encoding="utf-8")
            src = str(p.name)
            results.append({"source": src, "url": None, "text": text})
    return results


def main():
    ensure_dirs()
    planning = ROOT / "planning.md"
    urls = extract_sources_from_planning(planning)
    print(f"Found {len(urls)} URLs in planning.md")

    docs = process_local_files()
    print(f"Found {len(docs)} local files in documents/")

    # fetch remote pages if requests available
    for url in urls:
        html = fetch_url(url)
        if html:
            text = clean_html_text(html)
            docs.append({"source": url.split("/")[2], "url": url, "text": text})

    # save raw
    for d in docs:
        src = d.get("source") or d.get("url")[:80]
        slug = slugify(src + "-" + (d.get("url") or "local"))
        path = RAW_DIR / f"{slug}.txt"
        path.write_text(d["text"], encoding="utf-8")

    # chunk all docs
    all_chunks = []
    for d in docs:
        text = d["text"]
        if not text or len(text.strip()) == 0:
            continue
        chunks = chunk_text(text)
        for i, c in enumerate(chunks):
            uid = hashlib.sha1((d.get("url") or d.get("source", "local") + str(i)).encode()).hexdigest()[:12]
            all_chunks.append({"id": uid, "source": d.get("source"), "url": d.get("url"), "text": c})

    # write chunks
    with open(CHUNKS_FILE, "w", encoding="utf-8") as fh:
        for ch in all_chunks:
            fh.write(json.dumps(ch, ensure_ascii=False) + "\n")

    print(f"Wrote {len(all_chunks)} chunks to {CHUNKS_FILE}")

    # print 5 random chunks
    if len(all_chunks) == 0:
        print("No chunks generated. Check that documents exist or that web fetch succeeded and bs4/requests are available.")
        return

    sample = random.sample(all_chunks, min(5, len(all_chunks)))
    print("\nSample chunks:\n")
    for s in sample:
        print("---")
        print("Source:", s.get("source"), s.get("url"))
        print(s["text"][:1000].replace('\n', ' '))
        print("\n")


if __name__ == "__main__":
    main()
