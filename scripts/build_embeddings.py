#!/usr/bin/env python3
"""
Build embeddings for chunks and persist them into a ChromaDB collection.
"""
import json
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

ROOT = Path(__file__).resolve().parents[1]
CHUNKS_FILE = ROOT / "data" / "chunks.jsonl"
PERSIST_DIR = ROOT / "data" / "chroma_db"

def load_chunks(path):
    chunks = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            chunks.append(json.loads(line))
    return chunks

def main():
    chunks = load_chunks(CHUNKS_FILE)
    print(f"Loaded {len(chunks)} chunks")

    client = chromadb.PersistentClient(path=str(PERSIST_DIR))

    # use sentence-transformers via local embedding function in chroma
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

    col_name = "washu_housing"
    # if collection exists, delete to ensure a clean rebuild
    existing = [c.name for c in client.list_collections()]
    if col_name in existing:
        try:
            client.delete_collection(col_name)
        except Exception:
            pass
    col = client.create_collection(name=col_name, embedding_function=ef)

    ids = []
    docs = []
    metadatas = []
    seen = set()

    # assign position index per source (group by source+url)
    groups = {}
    for c in chunks:
        key = (c.get("source"), c.get("url"))
        groups.setdefault(key, []).append(c)

    for key, group_chunks in groups.items():
        for pos, c in enumerate(group_chunks):
            base_id = c["id"]
            uid = base_id
            i = 1
            while uid in seen:
                uid = f"{base_id}-{i}"
                i += 1
            seen.add(uid)
            ids.append(uid)
            docs.append(c["text"])
            metadatas.append({
                "source": c.get("source"),
                "url": c.get("url"),
                "position": pos,
            })

    # add
    col.add(ids=ids, documents=docs, metadatas=metadatas)
    print(f"Added {len(ids)} vectors to collection '{col_name}' at {PERSIST_DIR}")

if __name__ == "__main__":
    main()
