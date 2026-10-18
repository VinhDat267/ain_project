"""Evaluate retrieval + intent classification on the dev queries.

Owner: Vinh (V08). Contract: INTERFACE.md sections 7.2-7.4 and 7.7.
The test split is never run from here: it runs once, as a batch, through
``run_ablation.py --split test --final`` (INTERFACE.md 7.4, 7.8).

Usage:
    python experiments/evaluate.py --split dev --run-name baseline --retriever jaccard --intent majority
    python experiments/evaluate.py --split dev --run-name word_v1 --intent knn1
    python experiments/evaluate.py --split dev --run-name nb_lodo --intent-mode lodo
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import time
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Literal, Optional, Union

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd  # noqa: E402

from experiments.baselines import JaccardRetriever, knn_intent, majority_intent  # noqa: E402
from experiments.metrics import hit_at_k, precision_at_k, reciprocal_rank  # noqa: E402
from starter.intent import IntentConfig  # noqa: E402
from starter.retrieval import RetrievalConfig, Retriever  # noqa: E402

DEV_DIR = PROJECT_ROOT / "experiments" / "dev"
TEST_FILE = PROJECT_ROOT / "data" / "queries_test.csv"
RESULTS_DIR = PROJECT_ROOT / "experiments" / "results"

QUERY_COLUMNS = ["id", "query", "type", "expected_intent", "expected_doc_id", "notes"]
TYPES = ("normal", "paraphrase", "typo", "out_of_corpus")
OOC = "out_of_corpus"
TOP_IDS_K = 10

PER_QUERY_COLUMNS = [
    "query_id", "type", "query", "expected_doc_id", "expected_intent",
    "top_ids", "top1_score", "top2_score", "rank", "rr", "hit1", "hit3", "p1", "p3",
    "abstained", "pred_intent", "intent_conf", "intent_correct", "latency_ms",
]
SUMMARY_COLUMNS = [
    "type", "n", "mrr10", "hit1", "hit1_count", "hit3", "p1", "p3", "intent_acc",
    "abstain_rate", "e2e_acc1", "e2e_count", "balanced_e2e", "ooc_rejection",
    "false_abstention", "latency_ms",
]

RetrieverSpec = Union[RetrievalConfig, str]          # RetrievalConfig, "jaccard" or "bm25"
IntentSpec = Union[IntentConfig, str]                # IntentConfig, "majority", "knn1" or "knn5"
IntentPredictor = Callable[[str, list, str], tuple[str, float]]


class IntentNotReady(RuntimeError):
    """Raised when an IntentConfig run is requested before intent.py is implemented."""


# ----------------------------------------------------------------------------- loading

def _read_query_file(path: Path) -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        missing = [c for c in QUERY_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"{path.name} is missing columns {missing}")
        return [{c: (row.get(c) or "").strip() for c in QUERY_COLUMNS} for row in reader if (row.get("query") or "").strip()]


def dev_query_files(dev_dir: Path = DEV_DIR) -> list[Path]:
    return sorted(dev_dir.glob("queries_dev_*.csv"))


def load_queries(split: Literal["dev", "test"], dev_dir: Path = DEV_DIR, test_file: Path = TEST_FILE) -> list[dict[str, str]]:
    """Read ``data/queries_test.csv`` or concatenate ``experiments/dev/queries_dev_*.csv``.

    The test split is only loaded by ``run_ablation.py`` behind the test lock.
    """
    if split == "test":
        rows = _read_query_file(test_file)
    elif split == "dev":
        rows = [row for path in dev_query_files(dev_dir) for row in _read_query_file(path)]
    else:
        raise ValueError(f"Unknown split {split!r}")
    ids = [row["id"] for row in rows]
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        raise ValueError(f"Duplicate query ids: {duplicates[:5]}")
    return rows


# ----------------------------------------------------------------------------- building

def build_retriever(spec: RetrieverSpec, documents: list[dict[str, Any]]):
    """Instantiate the retriever described by ``spec``."""
    if isinstance(spec, RetrievalConfig):
        return Retriever(documents, spec)
    if spec == "jaccard":
        return JaccardRetriever(documents)
    if spec == "bm25":
        from starter.bm25 import BM25Retriever
        return BM25Retriever(documents)
    raise ValueError(f"Unknown retriever spec {spec!r}")


def describe(spec: Any) -> Any:
    """JSON-friendly description of a retriever or intent spec."""
    if is_dataclass(spec):
        kind = "tfidf" if isinstance(spec, RetrievalConfig) else "model"
        return {"kind": kind, **asdict(spec)}
    return {"kind": str(spec)}


def make_intent_predictor(intent: IntentSpec, documents: list[dict[str, Any]], intent_mode: str) -> IntentPredictor:
    """Return ``predict(query, ranked, expected_doc_id) -> (intent, confidence)``."""
    lodo = intent_mode == "lodo"
    if intent == "majority":
        label = majority_intent(documents)
        share = sum(doc["intent"] == label for doc in documents) / max(len(documents), 1)
        return lambda query, ranked, expected: (label, share)
    if intent in ("knn1", "knn5"):
        k = int(intent[3:])
        return lambda query, ranked, expected: knn_intent(ranked, k, exclude_id=expected if lodo and expected else None)
    if isinstance(intent, IntentConfig):
        from starter.intent import IntentClassifier, build_training_data

        def fit(exclude: tuple[str, ...]):
            try:
                texts, labels = build_training_data(documents, exclude_ids=exclude, include_descriptions=intent.include_descriptions)
                return IntentClassifier(intent).fit(texts, labels)
            except NotImplementedError as exc:
                raise IntentNotReady("starter/intent.py is not implemented yet (D04); use --intent knn1") from exc

        cache: dict[tuple[str, ...], Any] = {}

        def predict(query: str, ranked: list, expected: str) -> tuple[str, float]:
            key = (expected,) if lodo and expected else ()
            if key not in cache:
                cache[key] = fit(key)
            return cache[key].predict(query)
        return predict
    raise ValueError(f"Unknown intent spec {intent!r}")


# ----------------------------------------------------------------------------- evaluation

def evaluate_run(
    queries: list[dict[str, str]],
    documents: list[dict[str, Any]],
    retriever: Any,
    intent: IntentSpec,
    intent_mode: Literal["full", "lodo"] = "full",
) -> pd.DataFrame:
    """Return one row per query with exactly ``PER_QUERY_COLUMNS``.

    ``retriever`` is any object with ``rank()``/``search()`` (``Retriever``,
    ``JaccardRetriever`` or ``BM25Retriever``). ``"majority"`` is the chance
    baseline; ``"knn1"`` / ``"knn5"`` vote over the retriever ranking
    (``knn1`` == top1_doc). ``intent_mode="lodo"`` refits the classifier
    without ``expected_doc_id``, or excludes it from the k-NN neighbours.
    """
    if intent_mode not in ("full", "lodo"):
        raise ValueError(f"Unknown intent_mode {intent_mode!r}")
    predict_intent = make_intent_predictor(intent, documents, intent_mode)
    rows = []
    for q in queries:
        started = time.perf_counter()
        ranked = retriever.rank(q["query"])
        abstained = int(retriever.search(q["query"], 3) == [])
        pred_intent, intent_conf = predict_intent(q["query"], ranked, q["expected_doc_id"])
        latency_ms = (time.perf_counter() - started) * 1000.0

        ids = [doc["id"] for doc, _ in ranked]
        scores = [score for _, score in ranked]
        row = {
            "query_id": q["id"],
            "type": q["type"],
            "query": q["query"],
            "expected_doc_id": q["expected_doc_id"],
            "expected_intent": q["expected_intent"],
            "top_ids": "|".join(ids[:TOP_IDS_K]),
            "top1_score": scores[0] if scores else 0.0,
            "top2_score": scores[1] if len(scores) > 1 else 0.0,
            "rank": None, "rr": None, "hit1": None, "hit3": None, "p1": None, "p3": None,
            "abstained": abstained,
            "pred_intent": pred_intent,
            "intent_conf": float(intent_conf),
            "intent_correct": None,
            "latency_ms": latency_ms,
        }
        expected = q["expected_doc_id"]
        if q["type"] != OOC and expected:
            row.update({
                "rank": ids.index(expected) + 1 if expected in ids else None,
                "rr": reciprocal_rank(ids, expected, k=10),
                "hit1": hit_at_k(ids, expected, 1),
                "hit3": hit_at_k(ids, expected, 3),
                "p1": precision_at_k(ids, expected, 1),
                "p3": precision_at_k(ids, expected, 3),
                "intent_correct": int(pred_intent == q["expected_intent"]),
            })
        rows.append(row)
    return pd.DataFrame(rows, columns=PER_QUERY_COLUMNS)


def _e2e_correct(frame: pd.DataFrame) -> pd.Series:
    """Per-row end-to-end correctness (INTERFACE.md 7.2)."""
    is_ooc = frame["type"] == OOC
    in_corpus_ok = (frame["hit1"] == 1) & (frame["abstained"] == 0)
    return (is_ooc & (frame["abstained"] == 1)) | (~is_ooc & in_corpus_ok)


def _summary_row(label: str, frame: pd.DataFrame) -> dict[str, Any]:
    e2e = _e2e_correct(frame)
    row: dict[str, Any] = {col: float("nan") for col in SUMMARY_COLUMNS}
    row.update({
        "type": label,
        "n": len(frame),
        "abstain_rate": frame["abstained"].mean(),
        "e2e_acc1": e2e.mean(),
        "e2e_count": int(e2e.sum()),
        "latency_ms": frame["latency_ms"].mean(),
    })
    in_corpus = frame[frame["type"] != OOC]
    if len(in_corpus):
        row.update({
            "mrr10": in_corpus["rr"].astype(float).mean(),
            "hit1": in_corpus["hit1"].astype(float).mean(),
            "hit1_count": int(in_corpus["hit1"].astype(float).sum()),
            "hit3": in_corpus["hit3"].astype(float).mean(),
            "p1": in_corpus["p1"].astype(float).mean(),
            "p3": in_corpus["p3"].astype(float).mean(),
            "intent_acc": in_corpus["intent_correct"].astype(float).mean(),
        })
    return row


def summarize(per_query: pd.DataFrame) -> pd.DataFrame:
    """One row per query type plus an overall row; one column per metric in 7.2.

    Balanced E2E is the mean of the four per-type E2E Acc@1 values.
    """
    present = [t for t in TYPES if (per_query["type"] == t).any()]
    others = sorted(set(per_query["type"]) - set(TYPES))
    rows = [_summary_row(t, per_query[per_query["type"] == t]) for t in present + others]

    in_corpus = per_query[per_query["type"] != OOC]
    ooc = per_query[per_query["type"] == OOC]
    if len(in_corpus):
        rows.append(_summary_row("in_corpus", in_corpus))
    overall = _summary_row("all", per_query)
    per_type_e2e = [r["e2e_acc1"] for r in rows if r["type"] in TYPES]
    overall["balanced_e2e"] = sum(per_type_e2e) / len(per_type_e2e) if per_type_e2e else float("nan")
    overall["ooc_rejection"] = ooc["abstained"].mean() if len(ooc) else float("nan")
    overall["false_abstention"] = in_corpus["abstained"].mean() if len(in_corpus) else float("nan")
    rows.append(overall)
    return pd.DataFrame(rows, columns=SUMMARY_COLUMNS)


# ----------------------------------------------------------------------------- output

def git_commit() -> str:
    """Current commit hash, suffixed with ``+dirty`` when tracked code has local changes.

    Experiment outputs under ``experiments/results`` are ignored, so writing
    results does not mark the next run as dirty.
    """
    try:
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, capture_output=True, text=True, check=True).stdout.strip()
        dirty = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no", "--", ".", ":(exclude)experiments/results"],
            cwd=PROJECT_ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip()
        return sha + ("+dirty" if dirty else "")
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def write_run(out_dir: Path, per_query: pd.DataFrame, summary: pd.DataFrame, config: dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    per_query.to_csv(out_dir / "per_query.csv", index=False)
    summary.to_csv(out_dir / "summary.csv", index=False)
    (out_dir / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")


def run_config(split: str, run_name: str, retriever: RetrieverSpec, intent: IntentSpec, intent_mode: str, n_queries: int, query_files: list[str]) -> dict[str, Any]:
    return {
        "split": split,
        "run_name": run_name,
        "retriever": describe(retriever),
        "intent": describe(intent),
        "intent_mode": intent_mode,
        "n_queries": n_queries,
        "query_files": query_files,
        "commit": git_commit(),
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def format_summary(summary: pd.DataFrame) -> str:
    cols = ["type", "n", "mrr10", "hit1", "hit3", "p3", "intent_acc", "abstain_rate", "e2e_acc1", "balanced_e2e"]
    return summary[cols].to_string(index=False, float_format=lambda v: f"{v:.3f}", na_rep="")


# ----------------------------------------------------------------------------- CLI

def main(argv: Optional[list[str]] = None) -> int:
    """Parse CLI args (dev split only; refuse ``--split test``), write results."""
    parser = argparse.ArgumentParser(description="Evaluate retrieval + intent on the dev queries.")
    parser.add_argument("--split", choices=["dev", "test"], default="dev")
    parser.add_argument("--run-name", required=True)
    parser.add_argument("--retriever", choices=["tfidf", "jaccard", "bm25"], default="tfidf")
    parser.add_argument("--intent", choices=["model", "majority", "knn1", "knn5"], default="model")
    parser.add_argument("--intent-mode", choices=["full", "lodo"], default="full")
    args = parser.parse_args(argv)

    if args.split == "test":
        print("The test split runs only once, as a batch: python experiments/run_ablation.py --split test --final", file=sys.stderr)
        return 2

    from starter import student_core
    documents = student_core.load_documents()
    retriever_spec: RetrieverSpec = args.retriever
    if args.retriever == "tfidf":
        retriever_spec = getattr(student_core, "DEFAULT_RETRIEVAL_CONFIG", None) or RetrievalConfig()
    intent_spec: IntentSpec = args.intent
    if args.intent == "model":
        intent_spec = getattr(student_core, "DEFAULT_INTENT_CONFIG", None) or IntentConfig()

    queries = load_queries("dev")
    try:
        retriever = build_retriever(retriever_spec, documents)
        per_query = evaluate_run(queries, documents, retriever, intent_spec, args.intent_mode)
    except (IntentNotReady, NotImplementedError) as exc:
        print(f"Cannot run: {exc}", file=sys.stderr)
        return 1
    summary = summarize(per_query)
    out_dir = RESULTS_DIR / "dev" / args.run_name
    files = [p.name for p in dev_query_files()]
    write_run(out_dir, per_query, summary, run_config("dev", args.run_name, retriever_spec, intent_spec, args.intent_mode, len(queries), files))
    print(format_summary(summary))
    print(f"\nWrote {out_dir.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
