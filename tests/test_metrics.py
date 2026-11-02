"""Tests for experiments/metrics.py (V07)."""
from __future__ import annotations

import pytest

from experiments.metrics import hit_at_k, precision_at_k, reciprocal_rank

RANKED = ["d3", "d1", "d7", "d2", "d9"]


def test_reciprocal_rank_uses_the_position_of_the_expected_document():
    assert reciprocal_rank(RANKED, "d3") == 1.0
    assert reciprocal_rank(RANKED, "d7") == pytest.approx(1 / 3)


def test_reciprocal_rank_is_zero_outside_the_cutoff_or_when_missing():
    assert reciprocal_rank(RANKED, "d9", k=4) == 0.0
    assert reciprocal_rank(RANKED, "absent") == 0.0


def test_hit_at_k():
    assert hit_at_k(RANKED, "d1", 1) == 0
    assert hit_at_k(RANKED, "d1", 2) == 1
    assert hit_at_k(RANKED, "absent", 5) == 0


def test_precision_at_k_is_capped_at_one_over_k_with_one_relevant_document():
    assert precision_at_k(RANKED, "d3", 1) == 1.0
    assert precision_at_k(RANKED, "d3", 3) == pytest.approx(1 / 3)
    assert precision_at_k(RANKED, "d2", 3) == 0.0


def test_empty_ranking_scores_zero():
    assert reciprocal_rank([], "d1") == 0.0
    assert hit_at_k([], "d1", 3) == 0
    assert precision_at_k([], "d1", 3) == 0.0


@pytest.mark.parametrize("func", [hit_at_k, precision_at_k])
def test_non_positive_k_is_rejected(func):
    with pytest.raises(ValueError):
        func(RANKED, "d1", 0)
