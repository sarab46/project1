#!/usr/bin/env python3
"""
End-to-end generation helper.

Provides `ask(question)` which:
 - retrieves top-k chunks using the existing query pipeline
 - builds a grounded prompt that instructs the model to answer only from retrieved context
 - calls Groq LLM if `GROQ_API_KEY` is set in `.env`, otherwise falls back to a conservative synthesizer

Returns: dict {"answer": str, "sources": [metadata entries]}
"""
import os
from dotenv import load_dotenv
from pathlib import Path
from typing import List, Dict

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
from scripts.query import query_collection, synthesize_answer


def _build_prompt(question: str, chunks: List[Dict]) -> str:
    # include chunk texts and metadata as context with clear separators
    ctx_parts = []
    for i, c in enumerate(chunks, 1):
        src = c.get("metadata", {})
        header = f"[DOC {i}] source={src.get('source')} url={src.get('url')} position={src.get('position')}"
        body = c.get("document", "").strip()
        ctx_parts.append(header + "\n" + body)

    context = "\n\n---\n\n".join(ctx_parts)

    system = (
        "You are a helpful assistant that MUST answer using only the information in the provided documents. "
        "Use exact wording from the documents when possible. Do NOT use your own external knowledge. "
        "If the documents do not contain enough information to answer, respond exactly: 'I don't have enough information to answer that.'"
    )

    prompt = f"{system}\n\nCONTEXT:\n{context}\n\nQUESTION: {question}\n\nAnswer:" 
    return prompt


def _call_groq(prompt: str) -> str:
    try:
        from groq import Groq
    except Exception:
        raise RuntimeError("groq package not installed or unavailable")

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set in environment")

    client = Groq(api_key=api_key)
    # use a small completion; for real use tune model/params
    resp = client.generate(model="llama-3.3-70b-versatile", prompt=prompt, max_tokens=512)
    # groq client returns a dict-like object; convert safely
    if isinstance(resp, dict):
        return resp.get("text", "").strip()
    return str(resp).strip()


def ask(question: str, k: int = 5) -> Dict:
    # retrieve
    chunks = query_collection(question, k=k)

    # if no chunks return safe message
    if not chunks:
        return {"answer": "I don't have enough information to answer that.", "sources": []}

    # prefer Groq if configured, otherwise use conservative synthesizer
    prompt = _build_prompt(question, chunks)
    try:
        if os.environ.get("GROQ_API_KEY"):
            ans = _call_groq(prompt)
            # best-effort: return ans and the sources we passed
            sources = [c.get("metadata") for c in chunks]
            return {"answer": ans, "sources": sources}
    except Exception:
        # fall back to conservative local synthesizer
        pass

    # fallback: synthesize_answer (already conservative) and return sources
    ans, srcs = synthesize_answer(question, chunks)
    return {"answer": ans, "sources": srcs}


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: generate.py \"your question\"")
    else:
        res = ask(sys.argv[1])
        print("Answer:\n", res["answer"])
        print("\nSources:\n", res["sources"])
