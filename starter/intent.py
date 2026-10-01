"""Intent classification module (BoW/TF-IDF + Naive Bayes / Logistic Regression).

Owner: Nguyen Anh Duong. Contract: INTERFACE.md section 6.
scikit-learn is allowed here, but import it *inside* functions/methods, never
at module top level: the offline sanity tests must run without it.
"""
from __future__ import annotations

from collections.abc import Collection
from dataclasses import dataclass
from typing import Any, Literal

Document = dict[str, Any]

# Same order as data/intents.csv.
INTENTS: tuple[str, ...] = (
    "course_registration",
    "exam",
    "tuition",
    "class_schedule",
    "student_services",
    "graduation",
    "technical_support",
)


@dataclass(frozen=True)
class IntentConfig:
    """Every knob the experiments are allowed to turn (INTERFACE.md 6)."""

    model: Literal["nb", "logreg", "svm"] = "nb"
    features: Literal["bow", "tfidf"] = "bow"
    ngram_range: tuple[int, int] = (1, 1)
    nb_alpha: float = 1.0
    lr_C: float = 1.0
    svm_C: float = 1.0
    include_descriptions: bool = False


def build_training_data(
    documents: list[Document],
    exclude_ids: Collection[str] = (),
    include_descriptions: bool = False,
) -> tuple[list[str], list[str]]:
    """Return ``(texts, labels)`` from ``doc["text"]`` and ``doc["intent"]``.

    Skip every document whose ``id`` is in ``exclude_ids`` (used by the
    leave-one-document-out evaluation). When ``include_descriptions`` is True,
    also add the 7 ``(description, intent)`` rows of ``data/intents.csv``.
    """
    raise NotImplementedError("Implement build_training_data() in intent.py")


class IntentClassifier:
    """Supervised intent classifier configured by ``IntentConfig``."""

    def __init__(self, config: IntentConfig = IntentConfig()) -> None:
        self.config = config

    def fit(self, texts: list[str], labels: list[str]) -> "IntentClassifier":
        """Train on ``texts``/``labels`` and return ``self``."""
        raise NotImplementedError("Implement IntentClassifier.fit()")

    def predict_proba(self, query: str) -> dict[str, float]:
        """Return a probability for each of the 7 ``INTENTS``, summing to 1.

        For ``model="svm"`` this is the softmax of ``decision_function`` (a
        normalised score, not a calibrated probability), so SVM is for
        comparison only and never the product model.

        Raise ``RuntimeError`` if called before ``fit``. Never raise on an
        empty query.
        """
        raise NotImplementedError("Implement IntentClassifier.predict_proba()")

    def predict(self, query: str) -> tuple[str, float]:
        """Return ``(most_likely_intent, its_probability)``."""
        raise NotImplementedError("Implement IntentClassifier.predict()")
