"""Evaluate retrieval + intent classification on the dev queries.

Owner: Vinh. Contract: INTERFACE.md sections 7.2-7.4 and 7.7.
The test split is never run from here: it runs once, as a batch, through
``run_ablation.py --split test --final`` (INTERFACE.md 7.4, 7.8).

Usage:
    python experiments/evaluate.py --split dev --run-name baseline --retriever jaccard --intent majority
    python experiments/evaluate.py --split dev --run-name word_v1
    python experiments/evaluate.py --split dev --run-name nb_lodo --intent-mode lodo
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Literal, Optional, Union

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from starter.intent import IntentConfig  # noqa: E402

DEV_DIR = PROJECT_ROOT / "experiments" / "dev"
TEST_FILE = PROJECT_ROOT / "data" / "queries_test.csv"
RESULTS_DIR = PROJECT_ROOT / "experiments" / "results"

PER_QUERY_COLUMNS = [
    "query_id", "type", "query", "expected_doc_id", "expected_intent",
    "top_ids", "top1_score", "top2_score", "rank", "rr", "hit1", "hit3", "p1", "p3",
    "abstained", "pred_intent", "intent_conf", "intent_correct", "latency_ms",
]


def load_queries(split: Literal["dev", "test"]) -> list[dict[str, str]]:
    """Read ``data/queries_test.csv`` or concatenate ``experiments/dev/queries_dev_*.csv``.

    The test split is only loaded by ``run_ablation.py`` behind the test lock.
    """
    raise NotImplementedError("Implement load_queries()")


def evaluate_run(
    queries: list[dict[str, str]],
    documents: list[dict[str, Any]],
    retriever: Any,
    intent: Union[IntentConfig, Literal["majority", "knn1", "knn5"]],
    intent_mode: Literal["full", "lodo"] = "full",
) -> "pandas.DataFrame":  # noqa: F821
    """Return one row per query with exactly ``PER_QUERY_COLUMNS``.

    ``retriever`` is any object with ``rank()``/``search()`` (``Retriever`` or
    ``JaccardRetriever``). ``"majority"`` is the chance baseline; ``"knn1"``
    / ``"knn5"`` vote over the retriever ranking (``knn1`` == top1_doc).
    ``intent_mode="lodo"`` refits the classifier without ``expected_doc_id``,
    or excludes it from the k-NN neighbours.
    """
    raise NotImplementedError("Implement evaluate_run()")


def summarize(per_query: "pandas.DataFrame") -> "pandas.DataFrame":  # noqa: F821
    """One row per query type plus an overall row; one column per metric in 7.2.

    Balanced E2E is the mean of the four per-type E2E Acc@1 values.
    """
    raise NotImplementedError("Implement summarize()")


def main(argv: Optional[list[str]] = None) -> int:
    """Parse CLI args (dev split only; refuse ``--split test``), write results."""
    raise NotImplementedError("Implement main()")


if __name__ == "__main__":
    raise SystemExit(main())
