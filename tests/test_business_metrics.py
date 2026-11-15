"""Unit tests for business metrics computation and mathematical invariants."""
from pathlib import Path

import pytest

from experiments.business_metrics import compute_business_metrics

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_business_metrics_summary_values():
    summary_df, per_intent_df = compute_business_metrics()

    metrics = dict(zip(summary_df["metric"], summary_df["value"]))

    assert metrics["total_queries"] == 120
    assert metrics["in_corpus_queries"] == 105
    assert metrics["ooc_queries"] == 15

    # Core rates
    assert metrics["self_service_deflection_rate_overall"] == pytest.approx(0.7750, abs=1e-4)
    assert metrics["in_corpus_resolution_rate_top1"] == pytest.approx(0.8857, abs=1e-4)
    assert metrics["top3_rescue_rate"] == pytest.approx(0.9810, abs=1e-4)
    assert metrics["silent_wrong_answer_rate"] == pytest.approx(0.0952, abs=1e-4)
    assert metrics["safe_escalation_rate"] == pytest.approx(0.1417, abs=1e-4)
    assert metrics["false_abstention_rate"] == pytest.approx(0.0190, abs=1e-4)
    assert metrics["unsafe_ooc_answer_rate"] == pytest.approx(0.0000, abs=1e-4)
    assert metrics["expected_cost_per_query"] == pytest.approx(0.4333, abs=1e-4)


def test_business_metrics_invariants():
    summary_df, per_intent_df = compute_business_metrics()
    metrics = dict(zip(summary_df["metric"], summary_df["value"]))

    # In-corpus partition invariant: resolution + silent_wrong + false_abstain = 1.0
    res_rate = metrics["in_corpus_resolution_rate_top1"]
    wrong_rate = metrics["silent_wrong_answer_rate"]
    abstain_rate = metrics["false_abstention_rate"]
    assert res_rate + wrong_rate + abstain_rate == pytest.approx(1.0, abs=1e-4)

    # All OOC queries must be rejected (15/15)
    ooc_rows = per_intent_df[per_intent_df["segment_name"] == "out_of_corpus"]
    assert len(ooc_rows) == 1
    assert ooc_rows.iloc[0]["abstained"] == 15
    assert ooc_rows.iloc[0]["silent_wrong"] == 0

    # Normal and Typo queries have 100% resolution
    for qtype in ["normal", "typo"]:
        row = per_intent_df[per_intent_df["segment_name"] == qtype].iloc[0]
        assert row["resolution_rate_top1"] == 1.0
        assert row["top3_rescue_rate"] == 1.0
        assert row["abstained"] == 0
