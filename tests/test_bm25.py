"""Tests for starter/bm25.py (V13).

The expected scores in test_scores_match_a_hand_calculation are worked out
step by step in the test itself, independently of the implementation.
"""
from __future__ import annotations

import math

import pytest

from starter.bm25 import BM25Retriever
from starter.student_core import load_documents


def _doc(doc_id: str, text: str) -> dict:
    return {"id": doc_id, "intent": "x", "question": text, "answer": "", "text": text, "source": "faq.json"}


DOCS = [
    _doc("d1", "tuition payment deadline"),       # 3 tokens
    _doc("d2", "tuition tuition refund"),         # 3 tokens, "tuition" twice
    _doc("d3", "exam schedule room posted"),      # 4 tokens
]


def test_scores_match_a_hand_calculation():
    k1, b = 1.5, 0.75
    n, avgdl = 3, (3 + 3 + 4) / 3
    idf_tuition = math.log((n - 2 + 0.5) / (2 + 0.5) + 1)     # "tuition" is in 2 of 3 docs
    idf_rare = math.log((n - 1 + 0.5) / (1 + 0.5) + 1)        # "deadline" is in 1 doc
    norm_len3 = k1 * (1 - b + b * 3 / avgdl)

    def term(idf, f):
        return idf * f * (k1 + 1) / (f + norm_len3)

    expected = {
        "d1": term(idf_tuition, 1) + term(idf_rare, 1),
        "d2": term(idf_tuition, 2),
        "d3": 0.0,
    }
    scores = {doc["id"]: s for doc, s in BM25Retriever(DOCS).rank("tuition deadline")}
    for doc_id, value in expected.items():
        assert scores[doc_id] == pytest.approx(value, abs=1e-12)
    assert scores["d1"] == pytest.approx(1.5192, abs=1e-4)


def test_ranking_order_and_tie_break_by_id():
    ranked = BM25Retriever(DOCS).rank("tuition deadline")
    assert [doc["id"] for doc, _ in ranked] == ["d1", "d2", "d3"]
    assert [doc["id"] for doc, _ in BM25Retriever(DOCS).rank("")] == ["d1", "d2", "d3"]


def test_term_frequency_saturates():
    one = BM25Retriever([_doc("a", "exam room"), _doc("b", "other words")]).score("exam")[0]
    many = BM25Retriever([_doc("a", "exam exam exam exam exam exam exam exam room"), _doc("b", "other words")]).score("exam")[0]
    idf = math.log((2 - 1 + 0.5) / (1 + 0.5) + 1)
    assert one < many < idf * (1.5 + 1)          # grows with tf but never passes idf * (k1 + 1)


def test_b_controls_length_normalisation():
    docs = [_doc("short", "exam room"), _doc("long", "exam room schedule posted building floor")]
    with_norm = BM25Retriever(docs, b=0.75).score("exam")
    no_norm = BM25Retriever(docs, b=0.0).score("exam")
    assert with_norm[0] > with_norm[1]           # the longer document is penalised
    assert no_norm[0] == pytest.approx(no_norm[1])


def test_idf_stays_positive_for_a_term_in_every_document():
    docs = [_doc("a", "exam room"), _doc("b", "exam hall")]
    assert BM25Retriever(docs).score("exam")[0] > 0.0


def test_search_abstain_rules():
    retriever = BM25Retriever(DOCS)
    assert retriever.search("") == []
    assert retriever.search("pizza weather") == []
    assert retriever.search("tuition", top_k=0) == []
    assert BM25Retriever(DOCS, threshold=5.0).search("tuition deadline") == []
    assert [doc["id"] for doc, _ in retriever.search("tuition deadline", top_k=2)] == ["d1", "d2"]


def test_runs_on_the_real_corpus_and_is_deterministic():
    retriever = BM25Retriever(load_documents())
    first = retriever.rank("When is tuition due for the semester?")
    second = retriever.rank("When is tuition due for the semester?")
    assert len(first) == 112
    assert [(d["id"], s) for d, s in first] == [(d["id"], s) for d, s in second]
    assert first[0][0]["intent"] == "tuition"
