"""Tests for experiments/noise_curve.py (E3b)."""
from __future__ import annotations

import pandas as pd
import pytest

from experiments.noise_curve import (
    LEVELS,
    evaluate_noise_curve,
    load_normal_dev_queries,
    noisy_query,
)
from starter.student_core import load_documents


def test_noisy_query_determinism_and_levels():
    text = "When is tuition due for the semester?"
    q0 = noisy_query(text, 0, 0)
    assert q0 == text

    q1 = noisy_query(text, 1, 0)
    assert q1 != text
    # Deterministic
    assert noisy_query(text, 1, 0) == q1


def test_evaluate_noise_curve_structure():
    queries = load_normal_dev_queries()[:5]  # run on 5 queries for fast test
    docs = load_documents()
    df = evaluate_noise_curve(queries, docs)

    assert isinstance(df, pd.DataFrame)
    assert set(df.columns) == {"k", "method", "hit1", "mrr10"}
    assert set(df["method"].unique()) == {"jaccard", "word", "char", "hybrid"}
    assert len(df) == len(LEVELS) * 4
