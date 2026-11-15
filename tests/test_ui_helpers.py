"""Unit tests for ui_helpers module."""
from pathlib import Path

import pytest

from starter.ui_helpers import (
    highlight_matched_terms,
    is_non_english_query,
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
    assert "IT Helpdesk" in office_for_intent("technical_support")["name"]

    # Unknown intent returns fallback office
    fallback = office_for_intent("astronomy_club")
    assert "University Administrative Office" in fallback["name"]


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
