"""Run named experiment groups on the dev split, or the frozen batch on the test split.

Owner: Vinh (V11); Viet Anh adds the E3/E4 groups. Contract: INTERFACE.md 7.4 and 7.8.

Usage:
    python experiments/run_ablation.py --split dev --group E1
    python experiments/run_ablation.py --split test --final                       # ONCE, 15/10 21:00
    python experiments/run_ablation.py --split test --final --rerun-reason "..."  # evaluation-bug fix only
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Union

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd  # noqa: E402

from experiments.evaluate import (  # noqa: E402
    IntentNotReady,
    RESULTS_DIR,
    build_retriever,
    describe,
    evaluate_run,
    git_commit,
    load_queries,
    run_config,
    summarize,
    write_run,
)
from starter.intent import IntentConfig  # noqa: E402
from starter.retrieval import RetrievalConfig  # noqa: E402

# (retrieval, intent, intent_mode); retrieval may be "jaccard" or "bm25",
# intent may be "majority", "knn1" or "knn5", intent_mode is "full" or "lodo".
Run = tuple[Union[RetrievalConfig, str], Union[IntentConfig, str], str]

WORD = RetrievalConfig()  # word TF-IDF, index_field="text", stopwords removed

# Group name -> run name -> Run. Each owner adds their group by PR.
EXPERIMENTS: dict[str, dict[str, Run]] = {
    # E0: baselines vs the default word TF-IDF.
    "E0": {
        "baseline_jaccard_majority": ("jaccard", "majority", "full"),
        "word_default_knn1": (WORD, "knn1", "full"),
    },
    # E1: index only the question, or question + answer.
    "E1": {
        "word_text": (WORD, "knn1", "full"),
        "word_question": (RetrievalConfig(index_field="question"), "knn1", "full"),
    },
    # E2: word options, one change at a time from word_text.
    "E2": {
        "word_text": (WORD, "knn1", "full"),
        "keep_stopwords": (RetrievalConfig(remove_stopwords=False), "knn1", "full"),
        "bigram": (RetrievalConfig(word_ngram_range=(1, 2)), "knn1", "full"),
        "sublinear_tf": (RetrievalConfig(sublinear_tf=True), "knn1", "full"),
    },
    # E3, E4: char n-grams and hybrid — Viet Anh adds them (A08).
    # E7: BM25 (outside the course) vs word TF-IDF + cosine (V13).
    "E7": {
        "bm25": ("bm25", "knn1", "full"),
        "word_text": (WORD, "knn1", "full"),
        "sublinear_tf": (RetrievalConfig(sublinear_tf=True), "knn1", "full"),
    },
    # E5: five ways to classify intent, full training and leave-one-document-out.
    "E5": {
        f"{name}_{mode}": (WORD, intent, mode)
        for name, intent in [
            ("majority", "majority"),
            ("knn1", "knn1"),
            ("knn5", "knn5"),
            ("nb_bow", IntentConfig(model="nb", features="bow")),
            ("logreg_tfidf", IntentConfig(model="logreg", features="tfidf")),
            ("svm_tfidf", IntentConfig(model="svm", features="tfidf")),
        ]
        for mode in ("full", "lodo")
    },
}

# Frozen at V17 (14/10). Must contain a run named "final" (the DEFAULT configs).
FROZEN_COMPARISONS: dict[str, Run] = {}

TEST_LOCK = RESULTS_DIR / "test" / "LOCK"
RERUN_LOG = RESULTS_DIR / "test" / "RERUN_LOG.md"
KEY_METRICS = ["mrr10", "hit1", "intent_acc", "e2e_acc1"]


class SplitLocked(RuntimeError):
    """The test split already ran, or the frozen comparisons changed since then."""


def frozen_hash(runs: dict[str, Run]) -> str:
    """Stable hash of a set of runs, stored in LOCK to detect parameter changes."""
    payload = {name: [describe(r), describe(i), mode] for name, (r, i, mode) in sorted(runs.items())}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def compare_runs(long_summary: pd.DataFrame) -> pd.DataFrame:
    """One row per run: key metrics per query type, plus Balanced E2E."""
    rows = []
    for run, frame in long_summary.groupby("run", sort=False):
        by_type = frame.set_index("type")
        row: dict[str, Any] = {"run": run}
        for t in ("normal", "paraphrase", "typo"):
            if t in by_type.index:
                row[f"mrr_{t}"] = by_type.loc[t, "mrr10"]
                row[f"hit1_{t}"] = by_type.loc[t, "hit1"]
        if "in_corpus" in by_type.index:
            row["intent_acc"] = by_type.loc["in_corpus", "intent_acc"]
        row["ooc_rejection"] = by_type.loc["all", "ooc_rejection"]
        row["balanced_e2e"] = by_type.loc["all", "balanced_e2e"]
        rows.append(row)
    return pd.DataFrame(rows)


def _evaluate_runs(runs: dict[str, Run], split: str, queries: list[dict], results_dir: Path, skip_unready: bool) -> pd.DataFrame:
    from starter.student_core import load_documents

    documents = load_documents()
    summaries = []
    for name, (retrieval, intent, mode) in runs.items():
        try:
            retriever = build_retriever(retrieval, documents)
            per_query = evaluate_run(queries, documents, retriever, intent, mode)
        except (IntentNotReady, NotImplementedError) as exc:
            if not skip_unready:
                raise
            print(f"  skip {name}: {exc}")
            continue
        summary = summarize(per_query)
        write_run(results_dir / split / name, per_query, summary,
                  run_config(split, name, retrieval, intent, mode, len(queries), []))
        summaries.append(summary.assign(run=name))
        print(f"  done {name}")
    if not summaries:
        return pd.DataFrame()
    long = pd.concat(summaries, ignore_index=True)
    return long[["run"] + [c for c in long.columns if c != "run"]]


def run_group(group: str, results_dir: Path = RESULTS_DIR, queries: Optional[list[dict]] = None) -> pd.DataFrame:
    """Evaluate every run of ``EXPERIMENTS[group]`` on dev; write ablation_<group>.csv."""
    if group not in EXPERIMENTS:
        raise KeyError(f"Unknown group {group!r}; known: {sorted(EXPERIMENTS)}")
    queries = queries if queries is not None else load_queries("dev")
    long = _evaluate_runs(EXPERIMENTS[group], f"dev/{group}", queries, results_dir, skip_unready=True)
    if long.empty:
        return long
    comparison = compare_runs(long)
    (results_dir / "dev").mkdir(parents=True, exist_ok=True)
    long.to_csv(results_dir / "dev" / f"ablation_{group}.csv", index=False)
    comparison.to_csv(results_dir / "dev" / f"ablation_{group}_compare.csv", index=False)
    return comparison


def run_frozen_on_test(rerun_reason: Optional[str] = None, *, runs: Optional[dict[str, Run]] = None,
                       queries: Optional[list[dict]] = None, results_dir: Path = RESULTS_DIR) -> pd.DataFrame:
    """Evaluate ``FROZEN_COMPARISONS`` on the test split in one batch.

    Write the lock only after the whole batch succeeds. If the lock exists,
    refuse unless ``rerun_reason`` is given and the hash of the frozen runs
    matches the one stored in the lock; then append to the rerun log.
    """
    runs = FROZEN_COMPARISONS if runs is None else runs
    if "final" not in runs:
        raise ValueError("FROZEN_COMPARISONS must be filled at the freeze (V17) and contain a run named 'final'")
    lock, rerun_log = results_dir / "test" / "LOCK", results_dir / "test" / "RERUN_LOG.md"
    digest = frozen_hash(runs)
    if lock.exists():
        info = json.loads(lock.read_text(encoding="utf-8"))
        if not rerun_reason:
            raise SplitLocked(f"The test split already ran at {info.get('created_at')}. Rerun only to fix an "
                             "evaluation bug, with --rerun-reason.")
        if info.get("frozen_hash") != digest:
            raise SplitLocked("FROZEN_COMPARISONS changed since the locked run; parameters cannot change after the freeze.")

    queries = queries if queries is not None else load_queries("test")
    long = _evaluate_runs(runs, "test", queries, results_dir, skip_unready=False)
    comparison = compare_runs(long)
    long.to_csv(results_dir / "test" / "frozen_summary.csv", index=False)
    comparison.to_csv(results_dir / "test" / "frozen_compare.csv", index=False)

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if lock.exists():
        if not rerun_log.exists():
            rerun_log.write_text("# Test-split reruns (evaluation-bug fixes only)\n\n", encoding="utf-8")
        with open(rerun_log, "a", encoding="utf-8") as fh:
            fh.write(f"- {now} | commit {git_commit()} | {rerun_reason}\n")
    else:
        lock.write_text(json.dumps({"created_at": now, "commit": git_commit(), "frozen_hash": digest,
                                    "runs": sorted(runs)}, indent=2), encoding="utf-8")
    return comparison


def main(argv: Optional[list[str]] = None) -> int:
    """Parse ``--split``, ``--group``, ``--final`` and ``--rerun-reason``."""
    parser = argparse.ArgumentParser(description="Run experiment groups (dev) or the frozen batch (test).")
    parser.add_argument("--split", choices=["dev", "test"], default="dev")
    parser.add_argument("--group", help=f"dev only; one of {sorted(EXPERIMENTS)}")
    parser.add_argument("--final", action="store_true", help="required for --split test")
    parser.add_argument("--rerun-reason", help="test only: why the locked test run must be repeated")
    args = parser.parse_args(argv)

    fmt = {"float_format": lambda v: f"{v:.3f}", "na_rep": "", "index": False}
    if args.split == "dev":
        if not args.group:
            parser.error("--group is required for --split dev")
        print(run_group(args.group).to_string(**fmt))
        return 0
    if not args.final:
        parser.error("--split test requires --final")
    try:
        print(run_frozen_on_test(args.rerun_reason).to_string(**fmt))
    except (SplitLocked, ValueError) as exc:
        print(f"Refused: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
