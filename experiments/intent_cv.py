"""E5b: stratified 5-fold cross-validation of the intent classifiers on the 112 documents.

Owner: Nguyen Anh Duong (D08). Contract: INTERFACE.md section 7.10.
Folds: StratifiedKFold(n_splits=5, shuffle=True, random_state=42), labels = intent.
Models: IntentClassifier (nb / logreg / svm, bow / tfidf); k-NN via a Retriever
built on the training fold only + knn_intent (k = 1, 5); majority_intent floor.

Usage:
    python experiments/intent_cv.py
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold

from experiments.baselines import knn_intent, majority_intent
from starter.intent import IntentClassifier, IntentConfig
from starter.retrieval import RetrievalConfig, Retriever
from starter.student_core import load_documents

N_SPLITS = 5
RANDOM_STATE = 42

MODEL_CONFIGS: dict[str, tuple[str, Optional[IntentConfig]]] = {
    "majority": ("majority", None),
    "knn1": ("knn1", None),
    "knn5": ("knn5", None),
    "nb_bow": ("intent", IntentConfig(model="nb", features="bow")),
    "nb_tfidf": ("intent", IntentConfig(model="nb", features="tfidf")),
    "logreg_bow": ("intent", IntentConfig(model="logreg", features="bow")),
    "logreg_tfidf": ("intent", IntentConfig(model="logreg", features="tfidf")),
    "svm_bow": ("intent", IntentConfig(model="svm", features="bow")),
    "svm_tfidf": ("intent", IntentConfig(model="svm", features="tfidf")),
}


def cross_validate(
    documents: Optional[list[dict]] = None,
    n_splits: int = N_SPLITS,
    random_state: int = RANDOM_STATE,
) -> pd.DataFrame:
    """One row per method: accuracy and macro-F1, mean and std over the 5 folds."""
    docs = load_documents() if documents is None else documents
    labels = np.array([doc["intent"] for doc in docs])
    texts = np.array([doc["text"] for doc in docs])

    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)

    results: list[dict] = []

    for name, (kind, config) in MODEL_CONFIGS.items():
        fold_accs: list[float] = []
        fold_f1s: list[float] = []

        for train_idx, test_idx in skf.split(texts, labels):
            train_docs = [docs[i] for i in train_idx]
            test_docs = [docs[i] for i in test_idx]
            y_test = labels[test_idx]

            if kind == "majority":
                pred_label = majority_intent(train_docs)
                y_pred = [pred_label] * len(test_docs)

            elif kind in ("knn1", "knn5"):
                k = 1 if kind == "knn1" else 5
                retriever = Retriever(train_docs, RetrievalConfig(analyzer="word"))
                y_pred = []
                for test_doc in test_docs:
                    ranked = retriever.rank(test_doc["text"])
                    pred_intent, _ = knn_intent(ranked, k=k)
                    y_pred.append(pred_intent)

            elif kind == "intent" and config is not None:
                train_texts = [d["text"] for d in train_docs]
                train_labels = [d["intent"] for d in train_docs]
                clf = IntentClassifier(config).fit(train_texts, train_labels)
                y_pred = [clf.predict(d["text"])[0] for d in test_docs]

            else:
                raise ValueError(f"Unknown model kind: {kind}")

            fold_accs.append(accuracy_score(y_test, y_pred))
            fold_f1s.append(f1_score(y_test, y_pred, average="macro", zero_division=0))

        results.append({
            "model": name,
            "acc_mean": float(np.mean(fold_accs)),
            "acc_std": float(np.std(fold_accs)),
            "f1_mean": float(np.mean(fold_f1s)),
            "f1_std": float(np.std(fold_f1s)),
        })

    return pd.DataFrame(results)


def main(argv: Optional[list[str]] = None) -> int:
    """Write experiments/results/dev/intent_cv.csv."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print(f"Running {N_SPLITS}-fold stratified cross-validation on 112 corpus documents...")
    df = cross_validate()

    out_csv = PROJECT_ROOT / "experiments" / "results" / "dev" / "intent_cv.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)

    print("Intent Cross-Validation Results (mean ± std):")
    fmt = {
        "acc_mean": lambda v: f"{v:.3f}",
        "acc_std": lambda v: f"{v:.3f}",
        "f1_mean": lambda v: f"{v:.3f}",
        "f1_std": lambda v: f"{v:.3f}",
    }
    print(df.to_string(index=False, formatters=fmt))
    print(f"\nWrote results to: {out_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
