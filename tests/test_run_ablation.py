"""Tests for the test-split lock in experiments/run_ablation.py (V11).

These tests never touch data/queries_test.csv: they pass synthetic queries and
a temporary results directory.
"""
from __future__ import annotations

import json

import pytest

from experiments.run_ablation import EXPERIMENTS, SplitLocked, frozen_hash, run_frozen_on_test

QUERIES = [
    {"id": "s1", "query": "When is tuition due for the semester?", "type": "normal",
     "expected_intent": "tuition", "expected_doc_id": "faq_tuition_01", "notes": ""},
    {"id": "s2", "query": "best pizza in town", "type": "out_of_corpus",
     "expected_intent": "", "expected_doc_id": "", "notes": ""},
]
RUNS = {"final": ("jaccard", "majority", "full")}


def test_first_run_writes_the_lock_only_after_success(tmp_path):
    run_frozen_on_test(runs=RUNS, queries=QUERIES, results_dir=tmp_path)
    lock = json.loads((tmp_path / "test" / "LOCK").read_text(encoding="utf-8"))
    assert lock["frozen_hash"] == frozen_hash(RUNS) and lock["runs"] == ["final"]
    assert (tmp_path / "test" / "final" / "summary.csv").exists()


def test_second_run_is_refused_without_a_reason(tmp_path):
    run_frozen_on_test(runs=RUNS, queries=QUERIES, results_dir=tmp_path)
    with pytest.raises(SplitLocked):
        run_frozen_on_test(runs=RUNS, queries=QUERIES, results_dir=tmp_path)


def test_rerun_with_reason_is_logged_and_keeps_the_original_lock(tmp_path):
    run_frozen_on_test(runs=RUNS, queries=QUERIES, results_dir=tmp_path)
    original = (tmp_path / "test" / "LOCK").read_text(encoding="utf-8")
    run_frozen_on_test("fix MRR off-by-one", runs=RUNS, queries=QUERIES, results_dir=tmp_path)
    assert (tmp_path / "test" / "LOCK").read_text(encoding="utf-8") == original
    assert "fix MRR off-by-one" in (tmp_path / "test" / "RERUN_LOG.md").read_text(encoding="utf-8")


def test_rerun_with_changed_parameters_is_refused(tmp_path):
    run_frozen_on_test(runs=RUNS, queries=QUERIES, results_dir=tmp_path)
    changed = {"final": ("jaccard", "knn1", "full")}
    with pytest.raises(SplitLocked):
        run_frozen_on_test("try another intent", runs=changed, queries=QUERIES, results_dir=tmp_path)


def test_a_failing_batch_leaves_no_lock(tmp_path):
    broken = {"final": ("jaccard", "majority", "full"), "broken": ("no_such_retriever", "majority", "full")}
    with pytest.raises(ValueError):
        run_frozen_on_test(runs=broken, queries=QUERIES, results_dir=tmp_path)
    assert not (tmp_path / "test" / "LOCK").exists()


def test_a_final_run_is_required(tmp_path):
    with pytest.raises(ValueError):
        run_frozen_on_test(runs={"other": RUNS["final"]}, queries=QUERIES, results_dir=tmp_path)


def test_experiment_groups_are_well_formed():
    for group, runs in EXPERIMENTS.items():
        for name, run in runs.items():
            assert len(run) == 3 and run[2] in ("full", "lodo"), (group, name)
