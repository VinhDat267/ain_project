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

# Section 12 of Project12_Nghien_cuu_thuat_toan.md, integrated as supplied.
# These defaults reproduce that sample, rather than a new dev-set selection.
RETRIEVAL_THRESHOLD = 0.15
INTENT_THRESHOLD = 0.34


def _sample_retrieval_config():
    from starter.retrieval import RetrievalConfig

    return RetrievalConfig(
        analyzer="char_wb", char_ngram_range=(3, 5), remove_stopwords=False,
        sublinear_tf=True, threshold=RETRIEVAL_THRESHOLD,
    )


def _sample_intent_config():
    from starter.intent import IntentConfig

    return IntentConfig(
        model="logreg", features="tfidf", lr_C=10,
        include_descriptions=True, include_questions=True, sublinear_tf=True,
    )


# Infrastructure-only loading must work without ML dependencies, including when
# the lecturer loads this file by path alongside another project's starter.
try:
    DEFAULT_RETRIEVAL_CONFIG = _sample_retrieval_config()
    DEFAULT_INTENT_CONFIG = _sample_intent_config()
except ImportError:
    DEFAULT_RETRIEVAL_CONFIG = None
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
        from starter.retrieval import Retriever
        docs = load_documents()
        config = DEFAULT_RETRIEVAL_CONFIG or _sample_retrieval_config()
        _RETRIEVER = Retriever(docs, config)
    return _RETRIEVER


def _get_classifier():
    """Lazily instantiate and fit the shared IntentClassifier instance."""
    global _CLASSIFIER
    if _CLASSIFIER is None:
        from starter.intent import IntentClassifier, build_training_data
        config = DEFAULT_INTENT_CONFIG or _sample_intent_config()
        texts, labels = build_training_data(
            load_documents(), include_descriptions=config.include_descriptions,
            include_questions=config.include_questions,
        )
        _CLASSIFIER = IntentClassifier(config).fit(texts, labels)
    return _CLASSIFIER


def classify_intent(query: str) -> tuple[str, float]:
    """Return ``(intent_label, confidence)`` for ``query``.

    Trained on ``data/intents.csv`` and the labeled documents from
    :func:`load_documents`. Confidence comes from Logistic Regression.
    """
    if not isinstance(query, str):
        query = ""
    return _get_classifier().predict(query)


def retrieve(
    query: str, top_k: int = 3, threshold: float | None = None,
    intent_threshold: float | None = INTENT_THRESHOLD,
) -> list[tuple[dict[str, Any], float]]:
    """Return up to ``top_k`` ``(document, score)`` pairs ranked by relevance.

    Uses classical IR (TF-IDF + cosine similarity over :func:`load_documents`).
    Applies the sample's cosine floor and intent-confidence gate. For ranking
    evaluation, use ``threshold=-1, intent_threshold=None`` to disable both.
    """
    if not isinstance(query, str):
        query = ""
    if top_k <= 0:
        return []
    retriever = _get_retriever()
    ranked = retriever.rank(query)
    cutoff = retriever.config.threshold if threshold is None else threshold
    if not ranked or ranked[0][1] < cutoff:
        return []
    if intent_threshold is not None and classify_intent(query)[1] < intent_threshold:
        return []
    return ranked[:top_k]
