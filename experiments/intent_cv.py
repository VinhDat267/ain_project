"""E5b: stratified 5-fold cross-validation of the intent classifiers on the 112 documents.

Owner: Nguyen Anh Duong (D08). Contract: INTERFACE.md section 7.10.
Folds: StratifiedKFold(n_splits=5, shuffle=True, random_state=42), labels = intent.
Models: IntentClassifier (nb / logreg / svm, bow / tfidf); k-NN via a Retriever
built on the training fold only + knn_intent (k = 1, 5); majority_intent floor.

Usage:
    python experiments/intent_cv.py
"""
from __future__ import annotations

from typing import Optional

N_SPLITS = 5
RANDOM_STATE = 42


def cross_validate() -> "pandas.DataFrame":  # noqa: F821
    """One row per method: accuracy and macro-F1, mean and std over the 5 folds."""
    raise NotImplementedError("Implement cross_validate()")


def main(argv: Optional[list[str]] = None) -> int:
    """Write experiments/results/dev/intent_cv.csv."""
    raise NotImplementedError("Implement main()")


if __name__ == "__main__":
    raise SystemExit(main())
