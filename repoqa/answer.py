import os

import anthropic

from .indexer import search

MODEL = os.environ.get("REPOQA_MODEL", "claude-sonnet-5-5")
SYSTEM = (
    "You answer questions about a codebase using ONLY the provided snippets. "
    "Cite every claim as [path:start-end]. If the snippets don't contain the answer, say so."
)


def ask(question: str) -> dict:
    hits = search(question)
    context = "\n\n".join(f"[{p}:{s}-{e}]\n{body}" for p, s, e, body in hits)
    msg = anthropic.Anthropic().messages.create(
        model=MODEL,
        max_tokens=1000,
        system=SYSTEM,
        messages=[{"role": "user", "content": f"Snippets:\n{context}\n\nQuestion: {question}"}],
    )
    return {
        "answer": msg.content[0].text,
        "sources": [{"path": p, "start": s, "end": e} for p, s, e, _ in hits],
    }
