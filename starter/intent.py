"""Intent classification module (BoW/TF-IDF + Naive Bayes / Logistic Regression).

Owner: Nguyen Anh Duong. Contract: INTERFACE.md section 6.
scikit-learn is allowed here, but import it *inside* functions/methods, never
at module top level: the offline sanity tests must run without it.
"""
from __future__ import annotations

from collections.abc import Collection
from dataclasses import dataclass
from pathlib import Path
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
    include_questions: bool = False
    sublinear_tf: bool = False


def build_training_data(
    documents: list[Document],
    exclude_ids: Collection[str] = (),
    include_descriptions: bool = False,
    include_questions: bool = False,
) -> tuple[list[str], list[str]]:
    """Return ``(texts, labels)`` from ``doc["text"]`` and ``doc["intent"]``.

    Skip every document whose ``id`` is in ``exclude_ids`` (used by the
    leave-one-document-out evaluation). When ``include_descriptions`` is True,
    also add the 7 ``(description, intent)`` rows of ``data/intents.csv``.
    """
    import csv

    excluded = set(exclude_ids)
    retained = [doc for doc in documents if doc["id"] not in excluded]
    texts = [doc["text"] for doc in retained]
    labels = [doc["intent"] for doc in retained]
    if include_questions:
        texts.extend(doc["question"] for doc in retained)
        labels.extend(doc["intent"] for doc in retained)
    if include_descriptions:
        path = Path(__file__).resolve().parent.parent / "data" / "intents.csv"
        with path.open(newline="", encoding="utf-8") as source:
            for row in csv.DictReader(source):
                texts.append(row["description"])
                labels.append(row["intent"])
    return texts, labels


class IntentClassifier:
    """Supervised intent classifier configured by ``IntentConfig``."""

    def __init__(self, config: IntentConfig = IntentConfig()) -> None:
        self.config = config
        self._model = None

    def fit(self, texts: list[str], labels: list[str]) -> "IntentClassifier":
        """Train on ``texts``/``labels`` and return ``self``."""
        from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.naive_bayes import MultinomialNB
        from sklearn.pipeline import make_pipeline
        from sklearn.svm import LinearSVC

        if self.config.features == "bow":
            vectorizer = CountVectorizer(ngram_range=self.config.ngram_range)
        elif self.config.features == "tfidf":
            vectorizer = TfidfVectorizer(
                ngram_range=self.config.ngram_range, sublinear_tf=self.config.sublinear_tf
            )
        else:
            raise ValueError(f"Unknown intent features: {self.config.features}")
        if self.config.model == "nb":
            classifier = MultinomialNB(alpha=self.config.nb_alpha)
        elif self.config.model == "logreg":
            classifier = LogisticRegression(C=self.config.lr_C, max_iter=2000)
        elif self.config.model == "svm":
            classifier = LinearSVC(C=self.config.svm_C, random_state=42)
        else:
            raise ValueError(f"Unknown intent model: {self.config.model}")
        self._model = make_pipeline(vectorizer, classifier)
        self._model.fit(texts, labels)
        return self

    def predict_proba(self, query: str) -> dict[str, float]:
        """Return a probability for each of the 7 ``INTENTS``, summing to 1.

        For ``model="svm"`` this is the softmax of ``decision_function`` (a
        normalised score, not a calibrated probability), so SVM is for
        comparison only and never the product model.

        Raise ``RuntimeError`` if called before ``fit``. Never raise on an
        empty query.
        """
        if self._model is None:
            raise RuntimeError("Call fit() before predicting an intent")
        query = query if isinstance(query, str) else ""
        if self.config.model == "svm":
            import numpy as np

            scores = np.atleast_1d(self._model.decision_function([query])[0])
            if scores.size == 1:
                scores = np.array([-scores[0], scores[0]])
            weights = np.exp(scores - scores.max())
            values = weights / weights.sum()
        else:
            values = self._model.predict_proba([query])[0]
        probabilities = dict.fromkeys(INTENTS, 0.0)
        probabilities.update(
            (str(label), float(value)) for label, value in zip(self._model.classes_, values)
        )
        return probabilities

    def predict(self, query: str) -> tuple[str, float]:
        """Return ``(most_likely_intent, its_probability)``."""
        probabilities = self.predict_proba(query)
        label = max(probabilities, key=probabilities.get)
        return label, probabilities[label]
