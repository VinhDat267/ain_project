"""Tests for experiments/baselines.py (V09)."""
from __future__ import annotations

import pytest

from experiments.baselines import JaccardRetriever, knn_intent, majority_intent
from starter.intent import INTENTS


def _doc(doc_id: str, intent: str, text: str) -> dict:
    return {"id": doc_id, "intent": intent, "question": text, "answer": "", "text": text, "source": "faq.json"}


DOCS = [
    _doc("d1", "tuition", "tuition payment deadline semester"),
    _doc("d2", "exam", "final exam schedule room"),
    _doc("d3", "tuition", "tuition refund policy"),
]


def test_jaccard_scores_token_set_overlap():
    ranked = JaccardRetriever(DOCS).rank("tuition deadline")
    scores = {doc["id"]: score for doc, score in ranked}
    assert scores["d1"] == pytest.approx(2 / 4)   # {tuition, deadline} vs 4 tokens
    assert scores["d3"] == pytest.approx(1 / 4)   # {tuition} vs {tuition, refund, policy, deadline}
    assert scores["d2"] == 0.0
    assert [doc["id"] for doc, _ in ranked] == ["d1", "d3", "d2"]


def test_jaccard_ties_break_by_id_and_empty_query_abstains():
    retriever = JaccardRetriever(DOCS)
    assert [doc["id"] for doc, _ in retriever.rank("")] == ["d1", "d2", "d3"]
    assert retriever.search("") == []
    assert retriever.search("tuition", top_k=0) == []


def test_jaccard_threshold_abstains():
    assert JaccardRetriever(DOCS, threshold=0.9).search("tuition deadline") == []
    assert len(JaccardRetriever(DOCS, threshold=0.1).search("tuition deadline", top_k=2)) == 2


def test_majority_intent_breaks_ties_by_intent_order():
    assert majority_intent(DOCS) == "tuition"
    balanced = [_doc(f"x{i}", intent, "t") for i, intent in enumerate(reversed(INTENTS))]
    assert majority_intent(balanced) == INTENTS[0]


def test_knn_intent_weighted_vote_and_confidence():
    ranked = [(DOCS[1], 0.6), (DOCS[0], 0.5), (DOCS[2], 0.3)]
    assert knn_intent(ranked, 1) == ("exam", pytest.approx(1.0))
    intent, conf = knn_intent(ranked, 3)
    assert intent == "tuition"                     # 0.5 + 0.3 > 0.6
    assert conf == pytest.approx(0.8 / 1.4)


def test_knn_intent_excludes_the_expected_document_for_lodo():
    ranked = [(DOCS[1], 0.6), (DOCS[0], 0.5), (DOCS[2], 0.3)]
    assert knn_intent(ranked, 1, exclude_id="d2")[0] == "tuition"


def test_knn_intent_falls_back_to_majority_when_all_scores_are_zero():
    ranked = [(doc, 0.0) for doc in DOCS]
    assert knn_intent(ranked, 5) == ("tuition", 0.0)
