"""Automated end-to-end UX, AppTest and data consistency test suite."""
from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from experiments.business_metrics import compute_business_metrics
from scripts.build_report_tables import build_manifest
from starter import student_core
from starter.student_core import _get_retriever, retrieve
from starter.ui_helpers import load_notice_dates

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_app_in_corpus_query_displays_intent_and_markdown_doc_id():
    """Verify in-corpus query renders success banner with intent and markdown card with doc id."""
    app = AppTest.from_file(str(Path(student_core.__file__).with_name("app.py")), default_timeout=30).run()
    app.text_input[0].set_value("When is tuition due for the semester?")
    app.button[1].click().run()

    assert not app.exception
    # Must show success banner with intent name
    assert any("tuition" in item.value for item in app.success)
    # Must show target document id in markdown card
    assert any("faq_tuition_01" in item.value for item in app.markdown)


def test_app_ooc_query_abstains_without_conflicting_success():
    """Verify out-of-corpus query triggers error banner and SUPPRESSES any green success banner (U2)."""
    app = AppTest.from_file(str(Path(student_core.__file__).with_name("app.py")), default_timeout=30).run()
    app.text_input[0].set_value("Can I rent a kayak from the campus recreation center?")
    app.button[1].click().run()

    assert not app.exception
    # Must NOT have any green success banner
    assert len(app.success) == 0, f"Conflicting success banner displayed: {[s.value for s in app.success]}"
    # Must have the exact required abstention error string
    assert any("Information not found — please contact the administrative office." in item.value for item in app.error)
    # Must provide administrative routing escalation guidance (U3)
    assert any("Suggested Administrative Routing" in item.value for item in app.info)


def test_notice_dates_provenance_integrity():
    """Verify that all 28 notices have valid YYYY-MM-DD dates loaded from notices.json."""
    dates = load_notice_dates()
    assert len(dates) == 28
    for doc_id, date_str in dates.items():
        assert doc_id.startswith("notice_")
        assert len(date_str) == 10  # YYYY-MM-DD
        assert date_str.startswith("2026-")


def test_explain_mathematical_invariant_sums_to_cosine():
    """Verify linear feature attribution invariant: sum of explain() weights == cosine score."""
    retriever = _get_retriever()
    query = "How do I reset my Student Portal password?"
    ranked = retrieve(query, top_k=1)
    assert ranked, "Expected retrieval results for valid query"

    doc, cosine_score = ranked[0]
    # Request all feature contributions
    all_contribs = retriever.explain(query, doc["id"], top_n=5000)
    sum_contributions = sum(score for _, score in all_contribs)

    assert sum_contributions == pytest.approx(cosine_score, abs=1e-5)


def test_manifest_and_business_metrics_consistency():
    """Verify that the manifest and business summary are quantitatively consistent with raw CSVs."""
    manifest = build_manifest()
    summary_df, per_intent_df, sensitivity_df = compute_business_metrics()

    b_dict = dict(zip(summary_df["metric"], summary_df["value"]))

    assert manifest["metadata"]["total_documents"] == 112
    assert manifest["metadata"]["total_queries"] == 120
    assert manifest["metadata"]["total_faq"] == 84
    assert manifest["metadata"]["total_notices"] == 28

    assert b_dict["total_queries"] == 120
    assert b_dict["in_corpus_queries"] == 105
    assert b_dict["ooc_queries"] == 15
    assert b_dict["top3_rescue_rate"] == pytest.approx(0.9810, abs=1e-4)
    assert b_dict["self_service_deflection_rate_overall"] == pytest.approx(0.7750, abs=1e-4)


def test_app_empty_state_renders_academic_directory():
    """Verify that the initial empty state presents the 7-domain directory and recent notices."""
    app = AppTest.from_file(str(Path(student_core.__file__).with_name("app.py")), default_timeout=30).run()
    assert not app.exception
    # When initial query is empty, it should render directory and recent notices
    assert any("Official Academic Domains & Student Services Directory" in item.value for item in app.markdown)
    assert any("Recent Official Campus Notices" in item.value for item in app.markdown)
    assert any("Bursar's Office" in item.value for item in app.markdown)


def test_no_indented_html_code_blocks_in_app():
    """Verify no HTML block in app.markdown contains 4-space indented lines or blank lines that trigger CommonMark <pre><code> blocks."""
    app = AppTest.from_file(str(Path(student_core.__file__).with_name("app.py")), default_timeout=30).run()
    for item in app.markdown:
        val = item.value
        if val.startswith("<div"):
            for line in val.splitlines():
                assert line != "", f"Blank line inside HTML block would break CommonMark HTML parsing: {val[:120]}"
                assert not line.startswith("    "), f"4-space indented line inside HTML block: {line}"

    # Also verify after running a query
    app.text_input[0].set_value("When is tuition due for the semester?")
    app.button[1].click().run()
    for item in app.markdown:
        val = item.value
        if val.startswith("<div"):
            for line in val.splitlines():
                assert line != "", f"Blank line inside HTML block would break CommonMark HTML parsing: {val[:120]}"
                assert not line.startswith("    "), f"4-space indented line inside HTML block: {line}"


