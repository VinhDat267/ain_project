"""E3b: retrieval quality as the number of typos per query grows (k = 0..3).

Owner: Viet Anh (A09). Contract: INTERFACE.md section 7.9.
Input: the 49 ``normal`` queries of experiments/dev/queries_dev_auto.csv.
For level k, apply the lecturer's ``_make_typo`` k times; the j-th call on the
i-th query uses ``random.Random(1000 * k + 100 * j + i)``.

Usage:
    python experiments/noise_curve.py
"""
from __future__ import annotations

import csv
import random
import sys
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import matplotlib.pyplot as plt
import pandas as pd

from experiments.baselines import JaccardRetriever
from experiments.metrics import hit_at_k, reciprocal_rank
from scripts.generate_corpus import _make_typo
from starter.retrieval import RetrievalConfig, Retriever
from starter.student_core import load_documents

LEVELS = (0, 1, 2, 3)


def noisy_query(text: str, k: int, i: int) -> str:
    """Return ``text`` with ``k`` adjacent-letter-swap typos (seeded as above)."""
    current = text
    for j in range(k):
        rng = random.Random(1000 * k + 100 * j + i)
        current = _make_typo(current, rng)
    return current


def load_normal_dev_queries() -> list[dict[str, str]]:
    """Load the 49 normal queries from experiments/dev/queries_dev_auto.csv."""
    path = PROJECT_ROOT / "experiments" / "dev" / "queries_dev_auto.csv"
    queries: list[dict[str, str]] = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("type") == "normal":
                queries.append(row)
    return queries


def evaluate_noise_curve(
    queries: list[dict[str, str]],
    documents: list[dict],
) -> pd.DataFrame:
    """Evaluate Hit@1 and MRR@10 across noise levels for 4 retrieval strategies."""
    retrievers = {
        "jaccard": JaccardRetriever(documents),
        "word": Retriever(documents, RetrievalConfig(analyzer="word")),
        "char": Retriever(documents, RetrievalConfig(analyzer="char_wb", char_ngram_range=(3, 5))),
        "hybrid": Retriever(documents, RetrievalConfig(analyzer="hybrid", hybrid_alpha=0.5, char_ngram_range=(3, 5))),
    }

    records: list[dict] = []

    for k in LEVELS:
        for method_name, retriever in retrievers.items():
            rrs: list[float] = []
            hits: list[int] = []
            for i, q in enumerate(queries):
                query_text = noisy_query(q["query"], k, i)
                ranked = retriever.rank(query_text)
                ranked_ids = [doc["id"] for doc, _ in ranked[:10]]
                expected_id = q["expected_doc_id"]
                rrs.append(reciprocal_rank(ranked_ids, expected_id, k=10))
                hits.append(hit_at_k(ranked_ids, expected_id, k=1))

            records.append({
                "k": k,
                "method": method_name,
                "hit1": float(sum(hits) / len(hits)),
                "mrr10": float(sum(rrs) / len(rrs)),
            })

    return pd.DataFrame(records)


def plot_noise_curve(df: pd.DataFrame, output_path: Path) -> None:
    """Plot Hit@1 and MRR@10 vs typo noise level k (0..3)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=300)

    colors = {
        "jaccard": "#888888",
        "word": "#1f77b4",
        "char": "#ff7f0e",
        "hybrid": "#2ca02c",
    }
    markers = {
        "jaccard": "s",
        "word": "o",
        "char": "^",
        "hybrid": "D",
    }

    for method in ["jaccard", "word", "char", "hybrid"]:
        sub = df[df["method"] == method].sort_values("k")
        ax1.plot(
            sub["k"], sub["hit1"],
            label=method.capitalize(),
            color=colors.get(method, "blue"),
            marker=markers.get(method, "o"),
            linewidth=2,
        )
        ax2.plot(
            sub["k"], sub["mrr10"],
            label=method.capitalize(),
            color=colors.get(method, "blue"),
            marker=markers.get(method, "o"),
            linewidth=2,
        )

    ax1.set_title("Hit@1 vs. Injected Typos (k = 0..3)")
    ax1.set_xlabel("Number of Injected Typos (k)")
    ax1.set_ylabel("Hit@1")
    ax1.set_xticks(LEVELS)
    ax1.set_ylim(-0.05, 1.05)
    ax1.grid(True, linestyle="--", alpha=0.6)
    ax1.legend(loc="lower left")

    ax2.set_title("MRR@10 vs. Injected Typos (k = 0..3)")
    ax2.set_xlabel("Number of Injected Typos (k)")
    ax2.set_ylabel("MRR@10")
    ax2.set_xticks(LEVELS)
    ax2.set_ylim(-0.05, 1.05)
    ax2.grid(True, linestyle="--", alpha=0.6)
    ax2.legend(loc="lower left")

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def main(argv: Optional[list[str]] = None) -> int:
    """Hit@1 and MRR@10 per level for Jaccard, word, char and hybrid retrieval.

    Write experiments/results/dev/noise_curve.csv and figures/noise_curve.png.
    """
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    queries = load_normal_dev_queries()
    documents = load_documents()

    print(f"Loaded {len(queries)} normal dev queries and {len(documents)} documents.")
    df = evaluate_noise_curve(queries, documents)

    out_csv = PROJECT_ROOT / "experiments" / "results" / "dev" / "noise_curve.csv"
    out_png = PROJECT_ROOT / "experiments" / "results" / "figures" / "noise_curve.png"

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    plot_noise_curve(df, out_png)

    print("Noise curve summary:")
    print(df.to_string(index=False, float_format=lambda v: f"{v:.3f}"))
    print(f"Saved: {out_csv}")
    print(f"Saved: {out_png}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
