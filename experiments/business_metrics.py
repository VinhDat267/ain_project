"""Compute operational and business metrics for campus FAQ assistant.

Evaluates self-service deflection rate, top-1 resolution, top-3 rescue,
safe escalation, silent failure rate, and expected cost per query.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def compute_business_metrics(
    per_query_path: Path | None = None,
    output_dir: Path | None = None,
    w_silent_wrong: float = 5.0,
    w_false_abstain: float = 1.0,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    pq_file = per_query_path or (PROJECT_ROOT / "experiments" / "results" / "midterm-sample" / "per_query.csv")
    out_dir = output_dir or (PROJECT_ROOT / "experiments" / "results" / "business")
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(pq_file)
    # Ensure boolean flags for safety
    is_abstained = df["abstained"].astype(bool)
    is_hit1 = df["hit1"].astype(bool)
    is_hit3 = df["hit3"].astype(bool)
    is_ooc = df["type"] == "out_of_corpus"
    is_in_corpus = ~is_ooc

    total_queries = len(df)
    n_in_corpus = int(is_in_corpus.sum())
    n_ooc = int(is_ooc.sum())

    # In-corpus metrics
    # Resolved at top-1 without abstaining
    answered_correct_top1_mask = is_in_corpus & (~is_abstained) & is_hit1
    n_answered_correct_top1 = int(answered_correct_top1_mask.sum())

    # Top-3 correct (includes rescued queries)
    top3_correct_mask = is_in_corpus & is_hit3
    n_top3_correct = int(top3_correct_mask.sum())

    # Abstentions
    false_abstentions_mask = is_in_corpus & is_abstained
    n_false_abstentions = int(false_abstentions_mask.sum())

    # OOC abstentions vs leaks
    ooc_abstained_mask = is_ooc & is_abstained
    n_ooc_abstained = int(ooc_abstained_mask.sum())
    n_ooc_leaked = n_ooc - n_ooc_abstained

    # Silent wrong answers (not abstained but top1 is wrong)
    silent_wrong_mask = is_in_corpus & (~is_abstained) & (~is_hit1)
    n_silent_wrong = int(silent_wrong_mask.sum())

    # Safe escalation: all safe handoffs to humans (15 OOC + false abstentions)
    total_escalations = int(is_abstained.sum())

    # Rates
    self_service_deflection_rate = n_answered_correct_top1 / total_queries
    in_corpus_resolution_rate_top1 = n_answered_correct_top1 / n_in_corpus
    top3_rescue_rate = n_top3_correct / n_in_corpus
    silent_wrong_answer_rate = n_silent_wrong / n_in_corpus
    safe_escalation_rate = total_escalations / total_queries
    false_abstention_rate = n_false_abstentions / n_in_corpus
    unsafe_ooc_answer_rate = n_ooc_leaked / n_ooc if n_ooc > 0 else 0.0

    # Expected penalty / cost per query
    expected_cost_per_query = (
        (w_silent_wrong * n_silent_wrong) + (w_false_abstain * n_false_abstentions)
    ) / total_queries

    summary_data = [
        {"metric": "total_queries", "value": float(total_queries), "description": "Total benchmark evaluation queries"},
        {"metric": "in_corpus_queries", "value": float(n_in_corpus), "description": "Queries with target document in corpus"},
        {"metric": "ooc_queries", "value": float(n_ooc), "description": "Out-of-corpus queries requiring abstention"},
        {"metric": "self_service_deflection_rate_overall", "value": round(self_service_deflection_rate, 4), "description": "Fraction of all queries resolved correctly at Top-1 (93/120)"},
        {"metric": "in_corpus_resolution_rate_top1", "value": round(in_corpus_resolution_rate_top1, 4), "description": "In-corpus queries resolved correctly at Top-1 (93/105)"},
        {"metric": "top3_rescue_rate", "value": round(top3_rescue_rate, 4), "description": "In-corpus queries with correct document in Top-3 cards (103/105)"},
        {"metric": "silent_wrong_answer_rate", "value": round(silent_wrong_answer_rate, 4), "description": "Queries answered incorrectly without abstaining (10/105)"},
        {"metric": "safe_escalation_rate", "value": round(safe_escalation_rate, 4), "description": "Queries safely routed to administrative office (17/120)"},
        {"metric": "false_abstention_rate", "value": round(false_abstention_rate, 4), "description": "Legitimate queries mistakenly abstained (2/105)"},
        {"metric": "unsafe_ooc_answer_rate", "value": round(unsafe_ooc_answer_rate, 4), "description": "Out-of-corpus queries mistakenly answered (0/15)"},
        {"metric": "expected_cost_per_query", "value": round(expected_cost_per_query, 4), "description": "Expected operational penalty per query (w_wrong=5.0, w_abstain=1.0)"},
    ]
    summary_df = pd.DataFrame(summary_data)
    summary_csv_path = out_dir / "business_summary.csv"
    summary_df.to_csv(summary_csv_path, index=False)

    # 2. Per-intent & Per-type Breakdown
    records: list[dict[str, Any]] = []

    # By intent
    in_corpus_df = df[is_in_corpus].copy()
    in_corpus_df["is_abstained"] = in_corpus_df["abstained"].astype(bool)
    in_corpus_df["is_hit1"] = in_corpus_df["hit1"].astype(bool)
    in_corpus_df["is_hit3"] = in_corpus_df["hit3"].astype(bool)

    for intent_name, group in in_corpus_df.groupby("expected_intent"):
        n_group = len(group)
        corr_top1 = int(((~group["is_abstained"]) & group["is_hit1"]).sum())
        corr_top3 = int(group["is_hit3"].sum())
        abstained = int(group["is_abstained"].sum())
        wrong_top1 = int(((~group["is_abstained"]) & (~group["is_hit1"])).sum())
        records.append({
            "segment_type": "intent",
            "segment_name": intent_name,
            "total_queries": n_group,
            "top1_correct": corr_top1,
            "top3_correct": corr_top3,
            "abstained": abstained,
            "silent_wrong": wrong_top1,
            "resolution_rate_top1": round(corr_top1 / n_group, 4) if n_group else 0.0,
            "top3_rescue_rate": round(corr_top3 / n_group, 4) if n_group else 0.0,
        })

    # By query type
    df_copy = df.copy()
    df_copy["is_abstained"] = df_copy["abstained"].astype(bool)
    df_copy["is_hit1"] = df_copy["hit1"].astype(bool)
    df_copy["is_hit3"] = df_copy["hit3"].astype(bool)

    for qtype, group in df_copy.groupby("type"):
        n_group = len(group)
        if qtype == "out_of_corpus":
            abstained = int(group["is_abstained"].sum())
            records.append({
                "segment_type": "query_type",
                "segment_name": qtype,
                "total_queries": n_group,
                "top1_correct": 0,
                "top3_correct": 0,
                "abstained": abstained,
                "silent_wrong": n_group - abstained,
                "resolution_rate_top1": 0.0,
                "top3_rescue_rate": 0.0,
            })
        else:
            corr_top1 = int(((~group["is_abstained"]) & group["is_hit1"]).sum())
            corr_top3 = int(group["is_hit3"].sum())
            abstained = int(group["is_abstained"].sum())
            wrong_top1 = int(((~group["is_abstained"]) & (~group["is_hit1"])).sum())
            records.append({
                "segment_type": "query_type",
                "segment_name": qtype,
                "total_queries": n_group,
                "top1_correct": corr_top1,
                "top3_correct": corr_top3,
                "abstained": abstained,
                "silent_wrong": wrong_top1,
                "resolution_rate_top1": round(corr_top1 / n_group, 4) if n_group else 0.0,
                "top3_rescue_rate": round(corr_top3 / n_group, 4) if n_group else 0.0,
            })

    per_intent_df = pd.DataFrame(records)
    per_intent_csv_path = out_dir / "per_intent_business.csv"
    per_intent_df.to_csv(per_intent_csv_path, index=False)

    return summary_df, per_intent_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute business and operational metrics")
    parser.add_argument("--w-silent-wrong", type=float, default=5.0)
    parser.add_argument("--w-false-abstain", type=float, default=1.0)
    args = parser.parse_args()

    s_df, pi_df = compute_business_metrics(
        w_silent_wrong=args.w_silent_wrong,
        w_false_abstain=args.w_false_abstain,
    )
    print("=== BUSINESS METRICS SUMMARY ===")
    print(s_df.to_string(index=False))
    print("\n=== SEGMENT BREAKDOWN ===")
    print(pi_df.to_string(index=False))
