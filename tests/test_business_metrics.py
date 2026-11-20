"""Unit tests for business metrics computation and mathematical invariants."""
from pathlib import Path

import pytest

from experiments.business_metrics import compute_business_metrics

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_business_metrics_summary_values():
    summary_df, per_intent_df, sensitivity_df = compute_business_metrics()

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
    summary_df, per_intent_df, sensitivity_df = compute_business_metrics()
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


def test_cost_sensitivity_ratios():
    summary_df, per_intent_df, sensitivity_df = compute_business_metrics()

    assert len(sensitivity_df) == 4
    ratios = dict(zip(sensitivity_df["penalty_ratio"], sensitivity_df["expected_cost_per_query"]))

    # (w_wrong*10 + w_abstain*2) / 120
    assert ratios["1:1"] == pytest.approx(12.0 / 120.0, abs=1e-4)   # 0.1000
    assert ratios["3:1"] == pytest.approx(32.0 / 120.0, abs=1e-4)   # 0.2667
    assert ratios["5:1"] == pytest.approx(52.0 / 120.0, abs=1e-4)   # 0.4333
    assert ratios["10:1"] == pytest.approx(102.0 / 120.0, abs=1e-4) # 0.8500


def _tiny_per_query(tmp_path, ooc_abstained):
    """2 in-corpus (1 correct, 1 silent wrong) + 2 OOC, of which ``ooc_abstained`` are rejected."""
    import pandas as pd

    rows = [
        {"type": "normal", "expected_intent": "tuition", "abstained": 0, "hit1": 1, "hit3": 1},
        {"type": "paraphrase", "expected_intent": "exam", "abstained": 0, "hit1": 0, "hit3": 1},
        {"type": "out_of_corpus", "expected_intent": "", "abstained": int(ooc_abstained >= 1), "hit1": 0, "hit3": 0},
        {"type": "out_of_corpus", "expected_intent": "", "abstained": int(ooc_abstained >= 2), "hit1": 0, "hit3": 0},
    ]
    path = tmp_path / "per_query.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def test_answered_ooc_queries_cost_like_wrong_answers(tmp_path):
    safe = compute_business_metrics(_tiny_per_query(tmp_path, 2), output_dir=tmp_path / "a")
    leaky = compute_business_metrics(_tiny_per_query(tmp_path, 0), output_dir=tmp_path / "b")
    cost = {name: dict(zip(df[0]["metric"], df[0]["value"]))["expected_cost_per_query"]
            for name, df in (("safe", safe), ("leaky", leaky))}

    assert cost["safe"] == pytest.approx(5.0 * 1 / 4)            # one silent wrong answer
    assert cost["leaky"] == pytest.approx(5.0 * (1 + 2) / 4)     # plus two leaked OOC answers
    sens = dict(zip(leaky[2]["penalty_ratio"], leaky[2]["expected_cost_per_query"]))
    assert sens["1:1"] == pytest.approx(3 / 4) and sens["10:1"] == pytest.approx(30 / 4)


def test_summary_descriptions_follow_the_data(tmp_path):
    summary, _, _ = compute_business_metrics(
        _tiny_per_query(tmp_path, 1), output_dir=tmp_path, w_silent_wrong=3.0, w_false_abstain=2.0
    )
    desc = dict(zip(summary["metric"], summary["description"]))
    assert "(1/4)" in desc["self_service_deflection_rate_overall"]
    assert "(1/2)" in desc["unsafe_ooc_answer_rate"]
    assert "w_wrong=3" in desc["expected_cost_per_query"] and "w_abstain=2" in desc["expected_cost_per_query"]
