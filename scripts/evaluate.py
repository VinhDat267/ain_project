"""Reproduce section 12 of the team's midterm document from the integrated code.

The supplied benchmark has already been inspected. This reports a fixed sample
configuration, not an untouched test estimate or a cross-validation result.
Existing dev experiments and their frozen-test lock are left intact.
"""
from __future__ import annotations

import argparse
import hashlib
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from experiments.evaluate import evaluate_run, load_queries, run_config, summarize, write_run
from starter import student_core as core
from starter.intent import build_training_data
from starter.retrieval import Retriever


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "experiments/results/midterm-sample")
    args = parser.parse_args(argv)

    import numpy
    import sklearn

    queries = load_queries("test")
    documents = core.load_documents()
    training_texts, _ = build_training_data(
        documents, include_questions=core.DEFAULT_INTENT_CONFIG.include_questions,
        include_descriptions=core.DEFAULT_INTENT_CONFIG.include_descriptions,
    )
    per_query = evaluate_run(
        queries, documents, Retriever(documents, core.DEFAULT_RETRIEVAL_CONFIG),
        core.DEFAULT_INTENT_CONFIG, intent_threshold=core.INTENT_THRESHOLD,
    )
    # The old experiment protocol uses MRR@10. The supplied slides use full MRR;
    # preserve both labels so rank 11 is not silently scored as zero in the latter.
    per_query["rr_full"] = 1.0 / per_query["rank"]
    summary = summarize(per_query)
    for index, row in summary.iterrows():
        selected = per_query
        if row["type"] == "in_corpus":
            selected = selected[selected["type"] != "out_of_corpus"]
        elif row["type"] != "all":
            selected = selected[selected["type"] == row["type"]]
        summary.loc[index, "mrr"] = selected["rr_full"].mean()

    config = run_config(
        "reused_benchmark", "midterm-sample", core.DEFAULT_RETRIEVAL_CONFIG,
        core.DEFAULT_INTENT_CONFIG, "full", len(queries), ["data/queries_test.csv"],
    )
    config.update({
        "evaluation": "fixed sample reproduction; benchmark previously inspected; not cross-validation",
        "intent_threshold": core.INTENT_THRESHOLD,
        "training_samples": len(training_texts),
        "normal_queries_overlap_training_questions": sum(
            query["type"] == "normal" and query["query"] in training_texts for query in queries
        ),
        "versions": {"python": platform.python_version(), "numpy": numpy.__version__, "scikit-learn": sklearn.__version__},
        "source_sha256": {
            name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            for name in ["starter/student_core.py", "starter/retrieval.py", "starter/intent.py",
                         "experiments/evaluate.py", "scripts/evaluate.py"]
        },
    })
    write_run(args.output_dir, per_query, summary, config)
    ablation = []
    is_ooc = per_query["type"] == "out_of_corpus"
    for name, cosine, intent in [
        ("no_gate", None, None), ("cosine_only", core.RETRIEVAL_THRESHOLD, None),
        ("intent_only", None, core.INTENT_THRESHOLD),
        ("dual", core.RETRIEVAL_THRESHOLD, core.INTENT_THRESHOLD),
    ]:
        rejected = per_query["top1_score"] < (cosine if cosine is not None else -1)
        if intent is not None:
            rejected = rejected | (per_query["intent_conf"] < intent)
        correct = (is_ooc & rejected) | (~is_ooc & ~rejected & (per_query["hit1"] == 1))
        ablation.append({
            "rule": name, "cosine_threshold": cosine, "intent_threshold": intent,
            "correct": int(correct.sum()), "total": len(per_query),
            "ooc_rejected": int((is_ooc & rejected).sum()), "ooc_total": int(is_ooc.sum()),
        })
    import pandas as pd

    pd.DataFrame(ablation).to_csv(args.output_dir / "ablation.csv", index=False)
    for query_type in ("normal", "paraphrase", "typo"):
        row = summary[summary["type"] == query_type].iloc[0]
        print(f"{query_type:11s} MRR {row.mrr:.3f}  P@1 {row.p1:.3f}  "
              f"Hit@3 {row.hit3:.3f}  P@3 {row.p3:.3f}  Intent {row.intent_acc:.1%}")
    overall = summary[summary["type"] == "all"].iloc[0]
    ooc = per_query[per_query["type"] == "out_of_corpus"]
    print(f"Overall MRR: {overall.mrr:.3f} (full ranking); MRR@10: {overall.mrr10:.3f}")
    print(f"End-to-end: {int(overall.e2e_count)}/{int(overall.n)}")
    print(f"OOC rejected: {int(ooc.abstained.sum())}/{len(ooc)}")
    print("Fixed configuration on the reused benchmark; not a CV estimate.")
    print(f"Wrote {args.output_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
