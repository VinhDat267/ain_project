"""Tests for experiments/evaluate.py (V08), on synthetic documents and queries."""
from __future__ import annotations

import math

import pandas as pd
import pytest

from experiments.baselines import JaccardRetriever
from experiments.evaluate import (
    PER_QUERY_COLUMNS,
    SUMMARY_COLUMNS,
    evaluate_run,
    load_queries,
    main,
    summarize,
)


def _doc(doc_id, intent, text):
    return {"id": doc_id, "intent": intent, "question": text, "answer": "", "text": text, "source": "faq.json"}


DOCS = [
    _doc("d1", "tuition", "tuition payment deadline semester"),
    _doc("d2", "exam", "final exam schedule room"),
    _doc("d3", "tuition", "tuition refund policy"),
]


def _q(qid, query, qtype, intent="", doc=""):
    return {"id": qid, "query": query, "type": qtype, "expected_intent": intent, "expected_doc_id": doc, "notes": ""}


QUERIES = [
    _q("n1", "tuition payment deadline", "normal", "tuition", "d1"),
    _q("p1", "refund of tuition", "paraphrase", "tuition", "d3"),       # d3 is top-1 (2 shared tokens)
    _q("t1", "fnial exam scheduel", "typo", "exam", "d2"),              # only "exam" survives
    _q("o1", "weather forecast tomorrow", "out_of_corpus"),            # no shared token -> abstain
]


def test_per_query_columns_and_metrics():
    df = evaluate_run(QUERIES, DOCS, JaccardRetriever(DOCS), "knn1")
    assert list(df.columns) == PER_QUERY_COLUMNS
    rows = df.set_index("query_id")
    assert rows.loc["n1", "rank"] == 1 and rows.loc["n1", "rr"] == 1.0 and rows.loc["n1", "p3"] == pytest.approx(1 / 3)
    assert rows.loc["n1", "top_ids"].split("|")[0] == "d1"
    assert rows.loc["o1", "abstained"] == 1 and pd.isna(rows.loc["o1", "rr"]) and pd.isna(rows.loc["o1", "intent_correct"])
    assert rows.loc["n1", "abstained"] == 0
    assert rows.loc["t1", "pred_intent"] == "exam"


def test_summary_balanced_e2e_is_mean_over_types():
    df = evaluate_run(QUERIES, DOCS, JaccardRetriever(DOCS), "knn1")
    summary = summarize(df).set_index("type")
    assert list(summarize(df).columns) == SUMMARY_COLUMNS
    per_type = [summary.loc[t, "e2e_acc1"] for t in ("normal", "paraphrase", "typo", "out_of_corpus")]
    assert summary.loc["all", "balanced_e2e"] == pytest.approx(sum(per_type) / 4)
    assert summary.loc["all", "ooc_rejection"] == 1.0
    assert summary.loc["all", "false_abstention"] == 0.0
    assert summary.loc["in_corpus", "n"] == 3
    assert math.isnan(summary.loc["out_of_corpus", "mrr10"])


def test_threshold_makes_in_corpus_queries_abstain():
    df = evaluate_run(QUERIES, DOCS, JaccardRetriever(DOCS, threshold=0.99), "majority")
    summary = summarize(df).set_index("type")
    assert summary.loc["all", "false_abstention"] == 1.0
    # ranking metrics ignore the threshold
    assert summary.loc["normal", "hit1"] == 1.0


def test_lodo_excludes_the_expected_document_from_knn():
    full = evaluate_run(QUERIES[:1], DOCS, JaccardRetriever(DOCS), "knn1", "full").iloc[0]
    lodo = evaluate_run(QUERIES[:1], DOCS, JaccardRetriever(DOCS), "knn1", "lodo").iloc[0]
    assert full["pred_intent"] == "tuition"
    assert lodo["intent_conf"] <= full["intent_conf"]


def test_load_queries_concatenates_dev_files_and_rejects_duplicates(tmp_path):
    header = "id,query,type,expected_intent,expected_doc_id,notes\n"
    (tmp_path / "queries_dev_a.csv").write_text(header + "a1,hello,normal,exam,d2,\n", encoding="utf-8")
    (tmp_path / "queries_dev_b.csv").write_text(header + "b1,bye,out_of_corpus,,,\n", encoding="utf-8")
    assert [q["id"] for q in load_queries("dev", dev_dir=tmp_path)] == ["a1", "b1"]
    (tmp_path / "queries_dev_c.csv").write_text(header + "a1,again,normal,exam,d2,\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_queries("dev", dev_dir=tmp_path)


def test_cli_refuses_the_test_split():
    assert main(["--split", "test", "--run-name", "x"]) == 2
