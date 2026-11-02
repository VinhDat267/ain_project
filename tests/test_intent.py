"""Behavior required when integrating the supplied midterm code sample."""
import math

import pytest

from starter.intent import INTENTS, IntentClassifier, IntentConfig, build_training_data
from starter.student_core import load_documents


def test_training_data_matches_the_sample_and_excludes_all_versions_in_lodo():
    docs = load_documents()
    texts, labels = build_training_data(docs, include_questions=True, include_descriptions=True)
    assert len(texts) == len(labels) == 231
    target = docs[0]
    held_out, held_labels = build_training_data(
        docs, exclude_ids=[target["id"]], include_questions=True, include_descriptions=True
    )
    assert len(held_out) == len(held_labels) == 229
    assert target["text"] not in held_out
    assert target["question"] not in held_out


@pytest.mark.parametrize("model,features", [("nb", "bow"), ("logreg", "tfidf"), ("svm", "tfidf")])
def test_classifiers_predict_a_real_intent_and_handle_an_empty_query(model, features):
    texts, labels = build_training_data(load_documents())
    classifier = IntentClassifier(IntentConfig(model=model, features=features)).fit(texts, labels)
    label, confidence = classifier.predict("tuition fees payment")
    assert label == "tuition"
    assert 0 < confidence <= 1
    probabilities = classifier.predict_proba("")
    assert set(probabilities) == set(INTENTS)
    assert math.isclose(sum(probabilities.values()), 1.0)
    assert all(0 <= value <= 1 for value in probabilities.values())


def test_predict_before_fit_has_a_clear_error():
    with pytest.raises(RuntimeError, match="fit"):
        IntentClassifier().predict("tuition")
