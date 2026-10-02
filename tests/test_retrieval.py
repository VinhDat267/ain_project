"""Unit tests for starter.retrieval (tasks A04, A06, A07, A12)."""
from __future__ import annotations

import math
import numpy as np
import pytest
from sklearn.feature_extraction.text import TfidfVectorizer

from starter.preprocess import tokenize
from starter.retrieval import RetrievalConfig, Retriever
from starter.student_core import load_documents


@pytest.fixture
def sample_documents() -> list[dict]:
    return [
        {
            "id": "doc_01",
            "intent": "tuition",
            "question": "When is tuition due for the semester?",
            "answer": "Tuition fees must be paid before the second week of classes.",
            "text": "When is tuition due for the semester? Tuition fees must be paid before the second week of classes.",
            "source": "faq.json",
        },
        {
            "id": "doc_02",
            "intent": "exam",
            "question": "How can I check my final exam schedule?",
            "answer": "Final exam schedules are posted on the student portal two weeks prior.",
            "text": "How can I check my final exam schedule? Final exam schedules are posted on the student portal two weeks prior.",
            "source": "faq.json",
        },
        {
            "id": "doc_03",
            "intent": "student_services",
            "question": "What are the student health center hours?",
            "answer": "The health center is open Monday through Friday from 8 AM to 5 PM.",
            "text": "What are the student health center hours? The health center is open Monday through Friday from 8 AM to 5 PM.",
            "source": "faq.json",
        },
    ]


def test_retriever_word_matches_sklearn(sample_documents):
    config = RetrievalConfig(analyzer="word", remove_stopwords=False, sublinear_tf=False, index_field="text")
    retriever = Retriever(sample_documents, config)

    # Build sklearn vectorizer on same corpus
    corpus = [doc["text"] for doc in sample_documents]
    vec = TfidfVectorizer(
        tokenizer=tokenize,
        lowercase=False,
        token_pattern=None,
        smooth_idf=True,
        norm="l2",
        sublinear_tf=False,
    )
    X = vec.fit_transform(corpus).toarray()

    queries = [
        "tuition fees semester",
        "final exam schedule",
        "student health center hours",
        "random unseen words xyz",
    ]

    for q in queries:
        ranked = retriever.rank(q)
        q_vec = vec.transform([q]).toarray()[0]
        sk_scores = X @ q_vec

        # Check score of each doc matches sklearn within 1e-6
        for doc, score in ranked:
            doc_idx = next(i for i, d in enumerate(sample_documents) if d["id"] == doc["id"])
            expected_score = float(sk_scores[doc_idx])
            assert math.isclose(score, expected_score, abs_tol=1e-6), (
                f"Query '{q}' for doc '{doc['id']}': got {score}, expected {expected_score}"
            )


def test_retriever_sublinear_tf_matches_sklearn(sample_documents):
    config = RetrievalConfig(analyzer="word", remove_stopwords=False, sublinear_tf=True, index_field="text")
    retriever = Retriever(sample_documents, config)

    corpus = [doc["text"] for doc in sample_documents]
    vec = TfidfVectorizer(
        tokenizer=tokenize,
        lowercase=False,
        token_pattern=None,
        smooth_idf=True,
        norm="l2",
        sublinear_tf=True,
    )
    X = vec.fit_transform(corpus).toarray()

    query = "exam exam exam schedule"
    ranked = retriever.rank(query)
    q_vec = vec.transform([query]).toarray()[0]
    sk_scores = X @ q_vec

    for doc, score in ranked:
        doc_idx = next(i for i, d in enumerate(sample_documents) if d["id"] == doc["id"])
        expected_score = float(sk_scores[doc_idx])
        assert math.isclose(score, expected_score, abs_tol=1e-6)


def test_rank_ordering_and_tie_breaking(sample_documents):
    config = RetrievalConfig(analyzer="word")
    retriever = Retriever(sample_documents, config)

    # Empty query will yield score 0 for all docs; tie-break should be by id ascending
    ranked = retriever.rank("")
    assert len(ranked) == len(sample_documents)
    scores = [score for _, score in ranked]
    assert all(s == 0.0 for s in scores)
    ids = [doc["id"] for doc, _ in ranked]
    assert ids == sorted(ids), "Ties must be broken by document id ascending"


def test_search_abstains_correctly(sample_documents):
    config = RetrievalConfig(analyzer="word", threshold=0.3)
    retriever = Retriever(sample_documents, config)

    # 1. top_k <= 0 -> []
    assert retriever.search("tuition", top_k=0) == []
    assert retriever.search("tuition", top_k=-1) == []

    # 2. Empty query / no known words (score 0.0) -> []
    assert retriever.search("") == []
    assert retriever.search("xyzzy qwerty nonexistingword") == []

    # 3. Score below threshold -> []
    # If query matches weakly below 0.3
    low_match = retriever.rank("classes")[0][1]
    retriever_strict = Retriever(sample_documents, RetrievalConfig(threshold=low_match + 0.1))
    assert retriever_strict.search("classes") == []

    # 4. Valid query above threshold -> returns top_k
    res = retriever.search("When is tuition due?", top_k=2)
    assert len(res) <= 2
    assert len(res) > 0
    assert res[0][0]["id"] == "doc_01"


def test_explain_contributions_sum_to_score(sample_documents):
    config = RetrievalConfig(analyzer="word", remove_stopwords=False)
    retriever = Retriever(sample_documents, config)

    query = "tuition fees semester"
    doc_id = "doc_01"
    ranked_scores = {doc["id"]: score for doc, score in retriever.rank(query)}
    score = ranked_scores[doc_id]

    # Explain top 100 features
    explanations = retriever.explain(query, doc_id, top_n=100)
    total_contrib = sum(contrib for _, contrib in explanations)
    assert math.isclose(total_contrib, score, abs_tol=1e-6)


def test_char_and_hybrid_analyzers(sample_documents):
    char_retriever = Retriever(sample_documents, RetrievalConfig(analyzer="char"))
    ranked_char = char_retriever.rank("tuiton")  # typo: tuiton
    assert len(ranked_char) == len(sample_documents)
    # Char n-grams should still match 'tuition'
    assert ranked_char[0][0]["id"] == "doc_01"
    assert ranked_char[0][1] > 0.0

    hybrid_retriever = Retriever(sample_documents, RetrievalConfig(analyzer="hybrid", hybrid_alpha=0.5))
    ranked_hybrid = hybrid_retriever.rank("tuition")
    assert len(ranked_hybrid) == len(sample_documents)
    assert ranked_hybrid[0][0]["id"] == "doc_01"


def test_determinism(sample_documents):
    retriever1 = Retriever(sample_documents)
    retriever2 = Retriever(sample_documents)

    query = "How to register and pay tuition for exam?"
    res1 = [(d["id"], s) for d, s in retriever1.rank(query)]
    res2 = [(d["id"], s) for d, s in retriever2.rank(query)]
    assert res1 == res2


def test_real_corpus_retrieval():
    docs = load_documents()
    assert len(docs) == 112
    retriever = Retriever(docs, RetrievalConfig(analyzer="word"))
    query = "When is tuition due for the semester?"
    results = retriever.search(query, top_k=3)
    assert len(results) > 0
    top_doc, top_score = results[0]
    assert "tuition" in top_doc["intent"]
    assert top_score > 0.3
