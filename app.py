#!/usr/bin/env python3
"""Minimal Gradio app wiring retrieval -> generation.

Usage: python app.py
Open http://localhost:7860
"""
import gradio as gr
from scripts.generate import ask


def handle_query(question: str):
    res = ask(question)
    sources = res.get("sources") or []
    sources_text = "\n".join(f"• {s.get('source')} — {s.get('url')}" for s in sources if s)
    return res.get("answer"), sources_text


with gr.Blocks() as demo:
    inp = gr.Textbox(label="Your question")
    btn = gr.Button("Ask")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=6)
    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

if __name__ == "__main__":
    demo.launch()
