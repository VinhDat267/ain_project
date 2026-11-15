"""Tests for experiments/intent_cv.py (E5b)."""
from __future__ import annotations

import pandas as pd
import pytest

from experiments.intent_cv import cross_validate


def test_cross_validate_structure():
    df = cross_validate(n_splits=2)  # fast 2-fold test
    assert isinstance(df, pd.DataFrame)
    expected_cols = {"model", "acc_mean", "acc_std", "f1_mean", "f1_std"}
    assert set(df.columns) == expected_cols
    assert "logreg_tfidf" in df["model"].values
    assert "nb_bow" in df["model"].values
    assert "majority" in df["model"].values
    # Check probabilities in [0, 1]
    assert (df["acc_mean"] >= 0.0).all() and (df["acc_mean"] <= 1.0).all()
