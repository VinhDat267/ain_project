"""Regression checks against the supplied, already measured midterm sample."""
from pathlib import Path

import pytest
from sklearn.feature_extraction.text import TfidfVectorizer

from starter import student_core
from starter.retrieval import RetrievalConfig, Retriever


def test_handwritten_char_wb_scores_match_sklearn_with_word_boundaries():
    texts = ["I can't connect to Wi-Fi!", "connect  a\tstudent portal", "tuition fees"]
    docs = [{"id": str(i), "text": text} for i, text in enumerate(texts)]
    retriever = Retriever(docs, RetrievalConfig(analyzer="char_wb", sublinear_tf=True))
    vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
    matrix = vectorizer.fit_transform(texts)
    for query in ["I conncet to Wi-Fi!", "a student", "portal\nconnect", "unknown"]:
        expected = (matrix @ vectorizer.transform([query]).T).toarray().ravel()
        actual = {doc["id"]: score for doc, score in retriever.rank(query)}
        assert [actual[str(i)] for i in range(len(docs))] == pytest.approx(expected)


def test_public_classifier_returns_the_sample_logistic_regression_confidence():
    label, confidence = student_core.classify_intent("How do I reset my Student Portal password?")
    assert label == "technical_support"
    assert confidence == pytest.approx(0.8774289247, abs=1e-5)


def test_dual_gate_rejects_high_cosine_out_of_corpus_query():
    query = "Can I rent a kayak from the campus recreation center?"
    assert student_core.retrieve(query) == []
    raw = student_core.retrieve(query, threshold=-1, intent_threshold=None)
    assert raw[0][0]["id"] == "faq_student_services_02"
    assert raw[0][1] == pytest.approx(0.3938667388, abs=1e-6)


def test_raw_ranking_can_be_measured_separately_from_abstention():
    ranked = student_core.retrieve(
        "Two of my finals overlap on the same day - who do I tell?",
        top_k=112, threshold=-1, intent_threshold=None,
    )
    ids = [doc["id"] for doc, _ in ranked]
    assert ids[0] == "faq_class_schedule_02"
    assert ids.index("faq_exam_02") == 1
    assert len(ids) == 112


def test_demo_displays_intent_and_retrieved_answer():
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(str(Path(student_core.__file__).with_name("app.py")), default_timeout=30).run()
    app.text_input[0].set_value("How do I reset my Student Portal password?")
    app.button[1].click().run()
    assert not app.exception
    assert any("technical_support" in item.value for item in app.success)
    assert any("faq_technical_support_01" in item.value for item in app.markdown)


def test_demo_displays_the_abstention_banner():
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(str(Path(student_core.__file__).with_name("app.py")), default_timeout=30).run()
    app.text_input[0].set_value("Can I rent a kayak from the campus recreation center?")
    app.button[1].click().run()
    assert not app.exception
    assert any("Information not found" in item.value for item in app.error)
