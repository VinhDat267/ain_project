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
    # Must explain the abstention and list the covered topics (U3) ...
    assert any("Outside the indexed documents" in item.value for item in app.info)
    # ... and say which gate rejected it: the kayak query passes cosine but fails the intent gate.
    reason = next(item.value for item in app.info if "Why it was rejected" in item.value)
    assert "intent confidence" in reason and "failed" in reason
    # ... but must not route a rejected query to an office picked by the intent classifier.
    from starter.ui_helpers import OFFICE_REGISTRY

    shown = " ".join(item.value for item in list(app.info) + list(app.error))
    for office in OFFICE_REGISTRY.values():
        assert office["contact"] not in shown, f"Rejected query was routed to {office['contact']}"


def test_app_states_the_corpus_is_synthetic():
    """The UI must not present the synthetic corpus as an official university portal."""
    app = AppTest.from_file(str(Path(student_core.__file__).with_name("app.py")), default_timeout=30).run()
    page = " ".join(item.value for item in app.markdown)
    assert "not an official Hanoi University service" in page
    for claim in ("Official Regulation", "verified university documents", "Official Records", "Campus Offices"):
        assert claim not in page, claim


def test_feedback_button_writes_a_log_entry(tmp_path, monkeypatch):
    """'Helpful' must actually store the vote, not only show a toast."""
    import json

    from starter import ui_helpers

    log = tmp_path / "feedback.jsonl"
    monkeypatch.setattr(ui_helpers, "FEEDBACK_LOG", log)
    app = AppTest.from_file(str(Path(student_core.__file__).with_name("app.py")), default_timeout=30).run()
    app.text_input[0].set_value("When is tuition due for the semester?")
    app.button[1].click().run()
    next(b for b in app.button if b.label == "Helpful").click().run()

    assert not app.exception
    entries = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
    assert entries and entries[-1]["helpful"] is True
    assert entries[-1]["top_doc_id"] == "faq_tuition_01"


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


def test_manifest_and_business_metrics_consistency(tmp_path):
    """Verify that the manifest and business summary are quantitatively consistent with raw CSVs without mutating repo files."""
    import json

    manifest = build_manifest(output_path=tmp_path / "manifest.json")
    summary_df, per_intent_df, sensitivity_df = compute_business_metrics(output_dir=tmp_path)

    b_dict = dict(zip(summary_df["metric"], summary_df["value"]))

    assert manifest["metadata"]["total_documents"] == 112
    assert manifest["metadata"]["total_queries"] == 120
    assert manifest["metadata"]["total_faq"] == 84
    assert manifest["metadata"]["total_notices"] == 28

    assert b_dict["total_queries"] == 120
    assert b_dict["in_corpus_queries"] == 105
    assert b_dict["ooc_queries"] == 15
    assert b_dict["top3_rescue_rate"] == pytest.approx(0.9619, abs=1e-4)
    assert b_dict["raw_hit3_rate"] == pytest.approx(0.9810, abs=1e-4)
    assert b_dict["self_service_deflection_rate_overall"] == pytest.approx(0.7750, abs=1e-4)

    committed_manifest = json.loads(
        (PROJECT_ROOT / "experiments" / "results" / "report_verification_manifest.json").read_text(encoding="utf-8")
    )
    assert committed_manifest == manifest

    committed_summary = pd.read_csv(PROJECT_ROOT / "experiments" / "results" / "business" / "business_summary.csv")
    committed_dict = dict(zip(committed_summary["metric"], committed_summary["value"]))
    assert committed_dict == b_dict


def test_app_empty_state_renders_academic_directory():
    """Verify that the initial empty state presents the 7-domain directory and recent notices."""
    app = AppTest.from_file(str(Path(student_core.__file__).with_name("app.py")), default_timeout=30).run()
    assert not app.exception
    # When initial query is empty, it should render directory and recent notices
    assert any("Topic Directory & Contact Points" in item.value for item in app.markdown)
    assert any("Recent Campus Notices" in item.value for item in app.markdown)
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




def test_dashboard_tables_render_cleanly():
    """Dashboard tables: no leaked tag text, no NaN, and KPIs without green 'improvement' arrows."""
    app = AppTest.from_file(str(Path(student_core.__file__).with_name("app.py")), default_timeout=30).run()
    assert not app.exception

    tables = [item.value for item in app.markdown if "orca-table-wrap" in item.value]
    assert len(tables) >= 5, "expected the ablation, business, cost, CV and noise tables"
    for markup in tables:
        assert "</caption> border=" not in markup and "</caption>\nborder=" not in markup
        assert "NaN" not in markup

    assert len(app.metric) == 8
    assert all(not metric.delta for metric in app.metric)


def test_app_exposes_similarity_threshold_slider_by_default_and_abstains_when_raised():
    """Similarity threshold slider must be visible without toggling Inspector Mode and enforce abstention."""
    app = AppTest.from_file(str(Path(student_core.__file__).with_name("app.py")), default_timeout=30).run()
    assert not app.exception
    assert len(app.slider) >= 1, "Cosine similarity threshold slider should be directly visible in the sidebar"
    sim_slider = next((s for s in app.slider if "Cosine Similarity Threshold" in s.label), None)
    assert sim_slider is not None
    assert sim_slider.value == pytest.approx(student_core.RETRIEVAL_THRESHOLD, abs=1e-6)

    sim_slider.set_value(0.95)
    app.text_input[0].set_value("When is tuition due for the semester?")
    app.button[1].click().run()

    assert not app.exception
    assert len(app.success) == 0
    assert any("Information not found — please contact the administrative office." in item.value for item in app.error)


def test_app_result_cards_display_explicit_source_file_attribution():
    """Result cards must explicitly display source file provenance (faq.json vs. notices.json)."""
    app = AppTest.from_file(str(Path(student_core.__file__).with_name("app.py")), default_timeout=30).run()
    app.text_input[0].set_value("How do I reset my Student Portal password?")
    app.button[1].click().run()

    assert not app.exception
    cards = [item.value for item in app.markdown if "orca-card" in item.value]
    assert len(cards) >= 2
    assert any("faq.json" in card for card in cards), "Expected faq.json attribution on FAQ result card"
    assert any("notices.json" in card for card in cards), "Expected notices.json attribution on Notice result card"
