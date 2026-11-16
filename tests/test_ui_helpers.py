"""Unit tests for ui_helpers module."""
import json
from pathlib import Path

import pytest

from starter.ui_helpers import (
    get_domain_catalog,
    get_intent_ranking,
    highlight_matched_terms,
    highlight_matched_terms_html,
    is_non_english_query,
    load_dashboard_kpis,
    load_notice_dates,
    match_badge,
    match_label,
    office_for_intent,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_match_label_calibration():
    # Strong match >= 0.35
    assert match_label(0.77) == "Strong match"
    assert match_label(0.35) == "Strong match"

    # Possible match 0.22 - 0.35
    assert match_label(0.3499) == "Possible match"
    assert match_label(0.25) == "Possible match"
    assert match_label(0.22) == "Possible match"

    # Weak match < 0.22
    assert match_label(0.2199) == "Weak match"
    assert match_label(0.15) == "Weak match"
    assert match_label(0.0) == "Weak match"


def test_match_badge_has_icon_and_label():
    assert "🟢" in match_badge(0.40) and "Strong match" in match_badge(0.40)
    assert "🟡" in match_badge(0.28) and "Possible match" in match_badge(0.28)
    assert "⚪" in match_badge(0.18) and "Weak match" in match_badge(0.18)


def test_office_for_all_seven_intents():
    intents = [
        "course_registration",
        "class_schedule",
        "exam",
        "tuition",
        "student_services",
        "graduation",
        "technical_support",
    ]
    for intent in intents:
        office = office_for_intent(intent)
        assert isinstance(office, dict)
        assert "name" in office
        assert "role" in office
        assert "location" in office
        assert len(office["name"]) > 0

    # Specific office assertions
    assert "Registrar" in office_for_intent("course_registration")["name"]
    assert "Bursar" in office_for_intent("tuition")["name"]
    assert "IT Help Desk" in office_for_intent("technical_support")["name"]


def test_all_offices_attested_in_corpus():
    """Verify that every office returned by office_for_intent is attested in data/faq.json or notices.json."""
    faq = json.loads((PROJECT_ROOT / "data" / "faq.json").read_text(encoding="utf-8"))
    notices = json.loads((PROJECT_ROOT / "data" / "notices.json").read_text(encoding="utf-8"))
    corpus_text = " ".join(
        [f["question"] + " " + f["answer"] for f in faq]
        + [n["title"] + " " + n["body"] for n in notices]
    )

    intents = [
        "course_registration",
        "class_schedule",
        "exam",
        "tuition",
        "student_services",
        "graduation",
        "technical_support",
    ]
    for intent in intents:
        office = office_for_intent(intent)
        office_name = office["name"]
        assert office_name in corpus_text, f"Office '{office_name}' for intent '{intent}' is not attested in data/!"


def test_is_non_english_query():
    # English queries
    assert not is_non_english_query("When is tuition due for the semester?")
    assert not is_non_english_query("How do I register for classes at HANU?")
    assert not is_non_english_query("tution dedline paymnt")
    assert not is_non_english_query("")

    # Vietnamese accented queries
    assert is_non_english_query("Hạn nộp học phí là khi nào?")
    assert is_non_english_query("Làm sao để đăng ký môn học?")
    assert is_non_english_query("quy chế tốt nghiệp")
    assert is_non_english_query("thi lại điểm F")


def test_load_notice_dates_from_real_file():
    dates = load_notice_dates()
    assert len(dates) == 28
    assert "notice_course_registration_01" in dates
    assert dates["notice_course_registration_01"] == "2026-11-03"


def test_highlight_matched_terms():
    text = "The deadline to pay tuition for Fall semester is Friday."
    query = "When is the tuition deadline?"
    highlighted = highlight_matched_terms(text, query)

    # Keywords "deadline" and "tuition" should be bolded
    assert "**deadline**" in highlighted
    assert "**tuition**" in highlighted
    # Stopwords like "is" or "the" should not be bolded
    assert "**is**" not in highlighted
    assert "**the**" not in highlighted


def test_highlight_matched_terms_html():
    text = "The deadline to pay tuition for Fall semester is Friday. <script>alert(1)</script>"
    query = "When is the tuition deadline?"
    highlighted = highlight_matched_terms_html(text, query)

    # Must escape raw HTML
    assert "<script>" not in highlighted
    assert "&lt;script&gt;" in highlighted
    # Keywords wrapped in <mark> tag
    assert '<mark class="orca-highlight">deadline</mark>' in highlighted
    assert '<mark class="orca-highlight">tuition</mark>' in highlighted
    # No markdown ** leaks
    assert "**" not in highlighted


def test_get_domain_catalog():
    from starter.student_core import load_documents
    docs = load_documents()
    catalog = get_domain_catalog(docs)

    assert len(catalog) == 7
    total_docs = sum(c["total_count"] for c in catalog)
    total_faqs = sum(c["faq_count"] for c in catalog)
    total_notices = sum(c["notice_count"] for c in catalog)

    assert total_docs == 112
    assert total_faqs == 84
    assert total_notices == 28

    intents = {c["intent"] for c in catalog}
    assert "course_registration" in intents
    assert "tuition" in intents
    assert "exam" in intents
    assert "class_schedule" in intents
    assert "student_services" in intents
    assert "graduation" in intents
    assert "technical_support" in intents

    for item in catalog:
        assert item["color"].startswith("#")
        assert len(item["office_name"]) > 0


def test_get_intent_ranking():
    ranking = get_intent_ranking("When is tuition due for the semester?", top_n=3)
    assert len(ranking) == 3
    # Top intent should be tuition
    assert ranking[0][0] == "tuition"
    assert ranking[0][1] > 0.5
    # Probabilities sorted descending
    assert ranking[0][1] >= ranking[1][1] >= ranking[2][1]


def test_load_dashboard_kpis():
    kpis = load_dashboard_kpis()
    assert isinstance(kpis, dict)
    assert "mrr" in kpis
    assert "intent_accuracy" in kpis
    assert "deflection_rate" in kpis
    assert "top3_rescue_rate" in kpis
    assert kpis["total_queries"] == 120
    assert kpis["mrr"] == pytest.approx(0.943, abs=0.01)
    assert kpis["intent_accuracy"] == pytest.approx(0.9714, abs=0.01)
    assert kpis["top3_rescue_rate"] == pytest.approx(0.9810, abs=0.01)

