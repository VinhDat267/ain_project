"""Plot the 7x7 intent confusion matrix from midterm-sample/per_query.csv."""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix

from starter.intent import INTENTS

DISPLAY_LABELS = [
    "Course Reg",
    "Exam",
    "Tuition",
    "Schedule",
    "Services",
    "Graduation",
    "Tech Support",
]


def plot_confusion_matrix(
    per_query_path: Path | None = None,
    output_path: Path | None = None,
) -> Path:
    pq_file = per_query_path or (PROJECT_ROOT / "experiments" / "results" / "midterm-sample" / "per_query.csv")
    out_file = output_path or (PROJECT_ROOT / "experiments" / "results" / "figures" / "intent_confusion.png")

    df = pd.read_csv(pq_file)
    in_corpus = df[df["type"] != "out_of_corpus"].copy()

    y_true = in_corpus["expected_intent"].tolist()
    y_pred = in_corpus["pred_intent"].tolist()
    correct = int(sum(t == p for t, p in zip(y_true, y_pred)))
    total = len(in_corpus)
    acc = correct / total if total else 0.0

    cm = confusion_matrix(y_true, y_pred, labels=list(INTENTS))

    fig, ax = plt.subplots(figsize=(8.0, 6.4))
    im = ax.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    ticks = np.arange(len(INTENTS))
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)
    ax.set_xticklabels(DISPLAY_LABELS, rotation=30, ha="right", fontsize=10, fontweight="bold")
    ax.set_yticklabels(DISPLAY_LABELS, fontsize=10, fontweight="bold")

    thresh = cm.max() / 2.0 if cm.size else 0.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            val = int(cm[i, j])
            ax.text(
                j,
                i,
                str(val),
                ha="center",
                va="center",
                fontsize=11,
                fontweight="bold",
                color="white" if val > thresh else "#141413",
            )

    ax.set_xlabel("Predicted Intent", fontsize=11, fontweight="bold", labelpad=10)
    ax.set_ylabel("Ground Truth Intent", fontsize=11, fontweight="bold", labelpad=10)
    ax.set_title(
        f"7x7 Intent Confusion Matrix ({correct}/{total} In-Corpus Correct, {acc:.1%})",
        fontsize=12.5,
        fontweight="bold",
        pad=16,
    )

    out_file.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_file, dpi=200, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    return out_file


def main() -> int:
    out_file = plot_confusion_matrix()
    print(f"Wrote {out_file.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
