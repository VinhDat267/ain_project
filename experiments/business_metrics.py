"""Compute operational and business metrics for campus FAQ assistant.

Evaluates self-service deflection rate, top-1 resolution, top-3 rescue,
safe escalation, silent failure rate, cost sensitivity across penalty ratios,
and expected cost per query under operational assumptions.
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
    w_ooc_leak: float | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Write business_summary.csv, per_intent_business.csv and cost_sensitivity.csv.

    Cost per query = (w_silent_wrong * in-corpus wrong answers
    + w_ooc_leak * answered out-of-corpus queries
    + w_false_abstain * false abstentions) / total queries.
    An answered out-of-corpus query is a confident wrong answer, so
    ``w_ooc_leak`` defaults to ``w_silent_wrong``.
    """
    if w_ooc_leak is None:
        w_ooc_leak = w_silent_wrong
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

    # Top-3 delivered (non-abstained in-corpus queries whose target is in Top-3 cards)
    top3_delivered_mask = is_in_corpus & (~is_abstained) & is_hit3
    n_top3_delivered = int(top3_delivered_mask.sum())

    # Raw pre-gate Hit@3 (ranking only, includes abstained queries)
    raw_hit3_mask = is_in_corpus & is_hit3
    n_raw_hit3 = int(raw_hit3_mask.sum())

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
    top3_rescue_rate = n_top3_delivered / n_in_corpus
    raw_hit3_rate = n_raw_hit3 / n_in_corpus
    silent_wrong_answer_rate = n_silent_wrong / n_in_corpus
    safe_escalation_rate = total_escalations / total_queries
    false_abstention_rate = n_false_abstentions / n_in_corpus
    unsafe_ooc_answer_rate = n_ooc_leaked / n_ooc if n_ooc > 0 else 0.0

    def penalty(w_wrong: float, w_leak: float, w_abstain: float) -> float:
        return (w_wrong * n_silent_wrong) + (w_leak * n_ooc_leaked) + (w_abstain * n_false_abstentions)

    # Expected penalty / cost per query
    expected_cost_per_query = penalty(w_silent_wrong, w_ooc_leak, w_false_abstain) / total_queries

    summary_data = [
        {"metric": "total_queries", "value": float(total_queries), "description": "Total benchmark evaluation queries"},
        {"metric": "in_corpus_queries", "value": float(n_in_corpus), "description": "Queries with target document in corpus"},
        {"metric": "ooc_queries", "value": float(n_ooc), "description": "Out-of-corpus queries requiring abstention"},
        {"metric": "self_service_deflection_rate_overall", "value": round(self_service_deflection_rate, 4), "description": f"Fraction of all queries resolved correctly at Top-1 ({n_answered_correct_top1}/{total_queries})"},
        {"metric": "in_corpus_resolution_rate_top1", "value": round(in_corpus_resolution_rate_top1, 4), "description": f"In-corpus queries resolved correctly at Top-1 ({n_answered_correct_top1}/{n_in_corpus})"},
        {"metric": "top3_rescue_rate", "value": round(top3_rescue_rate, 4), "description": f"In-corpus queries answered with correct document in Top-3 cards ({n_top3_delivered}/{n_in_corpus})"},
        {"metric": "raw_hit3_rate", "value": round(raw_hit3_rate, 4), "description": f"In-corpus raw ranking Hit@3 before abstention gate ({n_raw_hit3}/{n_in_corpus})"},
        {"metric": "silent_wrong_answer_rate", "value": round(silent_wrong_answer_rate, 4), "description": f"In-corpus queries answered incorrectly without abstaining ({n_silent_wrong}/{n_in_corpus})"},
        {"metric": "safe_escalation_rate", "value": round(safe_escalation_rate, 4), "description": f"Queries where the assistant abstained and referred the student onward ({total_escalations}/{total_queries})"},
        {"metric": "false_abstention_rate", "value": round(false_abstention_rate, 4), "description": f"Legitimate queries mistakenly abstained ({n_false_abstentions}/{n_in_corpus})"},
        {"metric": "unsafe_ooc_answer_rate", "value": round(unsafe_ooc_answer_rate, 4), "description": f"Out-of-corpus queries mistakenly answered ({n_ooc_leaked}/{n_ooc})"},
        {"metric": "expected_cost_per_query", "value": round(expected_cost_per_query, 4), "description": f"Expected penalty per query (w_wrong={w_silent_wrong:g}, w_ooc_leak={w_ooc_leak:g}, w_abstain={w_false_abstain:g} assumption)"},
        {"metric": "w_silent_wrong", "value": float(w_silent_wrong), "description": "Penalty weight for an in-corpus wrong answer"},
        {"metric": "w_ooc_leak", "value": float(w_ooc_leak), "description": "Penalty weight for an answered out-of-corpus query"},
        {"metric": "w_false_abstain", "value": float(w_false_abstain), "description": "Penalty weight for a false abstention"},
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
        corr_top3 = int(((~group["is_abstained"]) & group["is_hit3"]).sum())
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
            corr_top3 = int(((~group["is_abstained"]) & group["is_hit3"]).sum())
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

    # 3. Cost Sensitivity Analysis across penalty ratios: 1:1, 3:1, 5:1, 10:1
    # Note: These weights are an operational research assumption, not empirical office labor telemetry.
    sensitivity_ratios = [(1.0, 1.0), (3.0, 1.0), (5.0, 1.0), (10.0, 1.0)]
    sensitivity_records: list[dict[str, Any]] = []
    # A leaked OOC answer is weighted like a silent wrong answer at every ratio.
    for w_wrong_val, w_abstain_val in sensitivity_ratios:
        total_penalty = penalty(w_wrong_val, w_wrong_val, w_abstain_val)
        cost_per_q = total_penalty / total_queries
        wrong_units = w_wrong_val * (n_silent_wrong + n_ooc_leaked)
        sensitivity_records.append({
            "penalty_ratio": f"{w_wrong_val:g}:{w_abstain_val:g}",
            "w_silent_wrong": w_wrong_val,
            "w_false_abstain": w_abstain_val,
            "n_silent_wrong": n_silent_wrong,
            "n_ooc_leaked": n_ooc_leaked,
            "n_false_abstentions": n_false_abstentions,
            "total_penalty_units": round(total_penalty, 4),
            "expected_cost_per_query": round(cost_per_q, 4),
            "cost_per_1000_queries": round(cost_per_q * 1000, 2),
            "silent_wrong_share_pct": round((wrong_units / total_penalty) * 100, 2) if total_penalty > 0 else 0.0,
        })
    sensitivity_df = pd.DataFrame(sensitivity_records)
    sensitivity_csv_path = out_dir / "cost_sensitivity.csv"
    sensitivity_df.to_csv(sensitivity_csv_path, index=False)

    return summary_df, per_intent_df, sensitivity_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute business and operational metrics")
    parser.add_argument("--w-silent-wrong", type=float, default=5.0)
    parser.add_argument("--w-false-abstain", type=float, default=1.0)
    parser.add_argument("--w-ooc-leak", type=float, default=None, help="defaults to --w-silent-wrong")
    args = parser.parse_args()

    s_df, pi_df, cs_df = compute_business_metrics(
        w_silent_wrong=args.w_silent_wrong,
        w_false_abstain=args.w_false_abstain,
        w_ooc_leak=args.w_ooc_leak,
    )
    print("=== BUSINESS METRICS SUMMARY ===")
    print(s_df.to_string(index=False))
    print("\n=== SEGMENT BREAKDOWN ===")
    print(pi_df.to_string(index=False))
    print("\n=== COST SENSITIVITY TABLE ===")
    print(cs_df.to_string(index=False))
