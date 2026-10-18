"""Project 12 AI core — campus notice/FAQ assistant.

Owner: Viet Anh (wiring A05). Contract: INTERFACE.md section 4.
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
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Default configs — frozen at V16 (INTERFACE.md section 4)
try:
    from starter.retrieval import RetrievalConfig
    DEFAULT_RETRIEVAL_CONFIG = RetrievalConfig()
except Exception:
    DEFAULT_RETRIEVAL_CONFIG = None

try:
    from starter.intent import IntentConfig
    DEFAULT_INTENT_CONFIG = IntentConfig()
except Exception:
    DEFAULT_INTENT_CONFIG = None

_RETRIEVER = None
_CLASSIFIER = None


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


def _get_retriever():
    """Lazily instantiate the shared Retriever instance."""
    global _RETRIEVER
    if _RETRIEVER is None:
        from starter.retrieval import RetrievalConfig, Retriever
        docs = load_documents()
        config = DEFAULT_RETRIEVAL_CONFIG if DEFAULT_RETRIEVAL_CONFIG is not None else RetrievalConfig()
        _RETRIEVER = Retriever(docs, config)
    return _RETRIEVER


def _get_classifier():
    """Lazily instantiate and fit the shared IntentClassifier instance."""
    global _CLASSIFIER
    if _CLASSIFIER is None:
        try:
            from starter.intent import IntentClassifier, IntentConfig, build_training_data
            docs = load_documents()
            texts, labels = build_training_data(docs)
            config = DEFAULT_INTENT_CONFIG if DEFAULT_INTENT_CONFIG is not None else IntentConfig()
            clf = IntentClassifier(config)
            clf.fit(texts, labels)
            _CLASSIFIER = clf
        except Exception:
            _CLASSIFIER = "fallback"
    return _CLASSIFIER


def _classify_intent_fallback(query: str) -> tuple[str, float]:
    """Fallback classifier: use top-1 document intent and score."""
    retriever = _get_retriever()
    ranked = retriever.rank(query)
    if ranked:
        top_doc, top_score = ranked[0]
        return str(top_doc["intent"]), float(top_score)
    return "course_registration", 0.0


def classify_intent(query: str) -> tuple[str, float]:
    """Return ``(intent_label, confidence)`` for ``query``.

    Trained on ``data/intents.csv`` and the labeled documents from
    :func:`load_documents`. Fallback to top-1 retrieved document intent
    when ``starter/intent.py`` is not yet implemented (INTERFACE.md 4).
    """
    if not isinstance(query, str):
        query = ""
    clf = _get_classifier()
    if clf != "fallback" and hasattr(clf, "predict"):
        try:
            return clf.predict(query)
        except Exception:
            pass
    return _classify_intent_fallback(query)


def retrieve(query: str, top_k: int = 3) -> list[tuple[dict[str, Any], float]]:
    """Return up to ``top_k`` ``(document, score)`` pairs ranked by relevance.

    Uses classical IR (TF-IDF + cosine similarity over :func:`load_documents`).
    Returns an empty list when query is out-of-corpus or score is below threshold.
    """
    if not isinstance(query, str):
        query = ""
    return _get_retriever().search(query, top_k)
