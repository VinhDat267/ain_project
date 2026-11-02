"""Tests for experiments/sweep_threshold.py (V15)."""
from __future__ import annotations

import pandas as pd
import pytest

from experiments.sweep_threshold import best_threshold, main, sweep

PER_QUERY = pd.DataFrame({
    "type": ["normal", "paraphrase", "typo", "out_of_corpus", "out_of_corpus"],
    "top1_score": [0.80, 0.30, 0.60, 0.25, 0.00],
    "hit1": [1, 1, 1, None, None],
})


def test_sweep_counts_abstentions_and_balanced_e2e():
    table = sweep(PER_QUERY, thresholds=[0.0, 0.28, 0.5]).set_index("threshold")
    # th = 0: only the zero-score OOC query abstains
    assert table.loc[0.0, "ooc_rejection"] == 0.5 and table.loc[0.0, "false_abstention"] == 0.0
    # th = 0.28: both OOC rejected, every in-corpus query kept -> perfect
    assert table.loc[0.28, "balanced_e2e"] == pytest.approx(1.0)
    # th = 0.5: the paraphrase query (0.30) is wrongly rejected
    assert table.loc[0.5, "false_abstention"] == pytest.approx(1 / 3)
    assert table.loc[0.5, "e2e_paraphrase"] == 0.0


def test_best_threshold_prefers_the_smallest_among_ties():
    table = sweep(PER_QUERY, thresholds=[0.26, 0.28, 0.29])
    assert best_threshold(table)["threshold"] == 0.26


def test_cli_refuses_test_split_results(tmp_path):
    path = tmp_path / "test" / "final" / "per_query.csv"
    path.parent.mkdir(parents=True)
    PER_QUERY.to_csv(path, index=False)
    assert main([str(path)]) == 2
