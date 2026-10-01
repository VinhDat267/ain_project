"""Project 12 AI core — campus notice/FAQ assistant.

Fill in ``classify_intent`` and ``retrieve`` yourself using **classical**
information retrieval / text classification techniques from CS50 AI's
Language topic: tokenization, n-grams, Bag-of-Words, TF-IDF, Naive Bayes,
cosine similarity, or similar. Attention/Transformer architectures may be
studied as optional background, but they are not required, and a hosted
LLM (ChatGPT API, Claude API, Hugging Face Inference, or similar) must
**not** replace this core — see the course AI policy and grading guidelines.

Heavy imports (scikit-learn, etc.) belong *inside* these functions, not at
module import time, so that ``load_documents`` and the offline sanity
tests keep working even before you install a classical-ML library.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def load_documents() -> list[dict[str, Any]]:
    """Load every FAQ and notice entry as a flat list of documents.

    This is infrastructure, not the graded core: it only reads the
    provided JSON files. Each returned dict has at least ``id``,
    ``intent``, ``question`` (or notice title), ``answer`` (or notice
    body), ``text`` (question/title + answer/body concatenated, handy for
    Bag-of-Words features), and ``source``.
    """
    documents: list[dict[str, Any]] = []

    faq = json.loads((DATA_DIR / "faq.json").read_text(encoding="utf-8"))
    for entry in faq:
        documents.append(
            {
                "id": entry["id"],
                "intent": entry["intent"],
                "question": entry["question"],
                "answer": entry["answer"],
                "text": f"{entry['question']} {entry['answer']}",
                "source": "faq.json",
            }
        )

    notices = json.loads((DATA_DIR / "notices.json").read_text(encoding="utf-8"))
    for entry in notices:
        documents.append(
            {
                "id": entry["id"],
                "intent": entry["intent"],
                "question": entry["title"],
                "answer": entry["body"],
                "text": f"{entry['title']} {entry['body']}",
                "source": "notices.json",
            }
        )

    return documents


def classify_intent(query: str) -> tuple[str, float]:
    """Return ``(intent_label, confidence)`` for ``query``.

    Implement this with a classical classifier (Bag-of-Words + Naive
    Bayes, TF-IDF + logistic regression, etc.) trained on
    ``data/intents.csv`` and the labeled documents from
    :func:`load_documents`. Do not call a hosted LLM.
    """
    raise NotImplementedError("Implement classify_intent() with your own classifier.")


def retrieve(query: str, top_k: int = 3) -> list[tuple[dict[str, Any], float]]:
    """Return up to ``top_k`` ``(document, score)`` pairs ranked by relevance.

    Implement this with classical IR (TF-IDF + cosine similarity, BM25,
    Bag-of-Words overlap, etc.) over :func:`load_documents`. If nothing is
    relevant enough, return an **empty list** instead of fabricating a
    match: the product must abstain (no document / low confidence) rather
    than invent an answer for an out-of-corpus question.
    """
    raise NotImplementedError("Implement retrieve() with your own IR method.")
