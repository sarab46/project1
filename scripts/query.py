#!/usr/bin/env python3
"""
Simple retrieval and QA helper that queries the ChromaDB collection and
prints top-k chunks and a conservative synthesized answer with citations.
"""
import sys
from pathlib import Path
from chromadb.config import Settings
import chromadb
import textwrap

ROOT = Path(__file__).resolve().parents[1]
PERSIST_DIR = ROOT / "data" / "chroma_db"

def load_collection(name="washu_housing"):
    client = chromadb.PersistentClient(path=str(PERSIST_DIR))
    return client.get_collection(name)

def synthesize_answer(query, docs):
    # conservative: return sentences from top docs that match keywords
    keywords = [w.lower() for w in query.split() if len(w) > 3]
    excerpts = []
    for d in docs:
        text = d["document"]
        # find first sentence containing any keyword
        for sent in text.split('. '):
            s = sent.strip()
            if len(s) < 20:
                continue
            if any(k in s.lower() for k in keywords[:6]):
                excerpts.append((s, d.get("metadata")))
                break
    if not excerpts:
        # fallback: return first 2 docs bodies truncated
        out = "\n\n".join([d["document"][:800] for d in docs[:2]])
        return out, [d.get("metadata") for d in docs[:2]]

    # join excerpts and list citations
    answer = " \n\n ".join([e[0] for e in excerpts[:4]])
    sources = [e[1] for e in excerpts[:4]]
    return answer, sources

def query_collection(q, k=5):
    col = load_collection()
    results = col.query(query_texts=[q], n_results=k, include=["documents", "metadatas", "distances"]) 
    docs = []
    # chroma returns dicts of lists
    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    for doc_id, doc_text, meta, dist in zip(ids, documents, metadatas, distances):
        docs.append({"id": doc_id, "document": doc_text, "metadata": meta, "distance": dist})
    return docs

def main():
    if len(sys.argv) < 2:
        print("Usage: query.py \"your question\"")
        return
    q = sys.argv[1]
    docs = query_collection(q)
    print(f"Top {len(docs)} retrieved chunks:\n")
    for i, d in enumerate(docs, 1):
        dist = d.get('distance')
        print(f"[{i}] source={d['metadata'].get('source')} url={d['metadata'].get('url')} distance={dist:.4f}")
        print(textwrap.shorten(d['document'].replace('\n', ' '), width=800))
        print('\n')

    ans, sources = synthesize_answer(q, docs)
    print("====Synthesized answer====")
    print(ans)
    print("\nSources:")
    for s in sources:
        print(s)

if __name__ == "__main__":
    main()
