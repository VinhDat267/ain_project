"""Unit tests for ui_helpers module."""
import json
import re
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
        assert {"name", "role", "contact", "evidence"} <= set(office)
        assert len(office["name"]) > 0

    # Specific office assertions
    assert "Registrar" in office_for_intent("exam")["name"]
    assert "Bursar" in office_for_intent("tuition")["name"]
    assert "IT Help Desk" in office_for_intent("technical_support")["name"]


def _corpus_by_id():
    faq = json.loads((PROJECT_ROOT / "data" / "faq.json").read_text(encoding="utf-8"))
    notices = json.loads((PROJECT_ROOT / "data" / "notices.json").read_text(encoding="utf-8"))
    docs = {f["id"]: (f["intent"], f["question"] + " " + f["answer"]) for f in faq}
    docs.update({n["id"]: (n["intent"], n["title"] + " " + n["body"]) for n in notices})
    return docs


def test_all_offices_attested_in_corpus():
    """Each contact point must come from its evidence document, which must be on the same topic."""
    docs = _corpus_by_id()
    from starter.ui_helpers import DEFAULT_OFFICE, OFFICE_REGISTRY

    for intent, office in list(OFFICE_REGISTRY.items()) + [("course_registration", DEFAULT_OFFICE)]:
        assert office["evidence"] in docs, f"{intent}: unknown evidence doc {office['evidence']}"
        doc_intent, text = docs[office["evidence"]]
        assert doc_intent == intent, f"{intent}: evidence {office['evidence']} is about {doc_intent}"
        assert office["name"] in text, f"{intent}: '{office['name']}' not in {office['evidence']}"
        for word in re.findall(r"\b[A-Z][\w']+", office["contact"]):
            assert word.lower() in text.lower(), f"{intent}: contact word '{word}' not in {office['evidence']}"


def test_no_invented_locations_or_hours():
    """The corpus has no rooms, buildings or opening hours for offices, so the registry must not either."""
    from starter.ui_helpers import DEFAULT_OFFICE, OFFICE_REGISTRY

    for office in list(OFFICE_REGISTRY.values()) + [DEFAULT_OFFICE]:
        assert "location" not in office
        blob = " ".join(office.values())
        assert not re.search(r"\b(Room|Floor|Hall|Building|\d{1,2}:\d{2})\b", blob), blob


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


def test_highlight_never_matches_inside_html_entities():
    """Query words like 'amp' or 'quot' must not split the entities produced by escaping."""
    text = 'Tuition & Fees: the "late" fee is the student\'s amp charge.'
    highlighted = highlight_matched_terms_html(text, "amp quot x27 late")

    assert "&amp;" in highlighted and "&quot;" in highlighted and "&#x27;" in highlighted
    assert "&<mark" not in highlighted
    assert '<mark class="orca-highlight">late</mark>' in highlighted
    assert '<mark class="orca-highlight">amp</mark> charge' in highlighted
    # Matched text itself is escaped too
    assert highlight_matched_terms_html("<b>tuition</b>", "tuition") == (
        '&lt;b&gt;<mark class="orca-highlight">tuition</mark>&lt;/b&gt;'
    )


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
    assert kpis["in_corpus_queries"] == 105
    assert kpis["ooc_queries"] == 15
    assert kpis["mrr"] == pytest.approx(0.943, abs=0.01)
    assert kpis["intent_accuracy"] == pytest.approx(0.9714, abs=0.01)
    assert kpis["intent_correct"] == 102
    assert kpis["top3_rescue_rate"] == pytest.approx(0.9619, abs=0.01)
    assert kpis["raw_hit3"] == pytest.approx(0.9810, abs=0.01)
    assert kpis["w_silent_wrong"] == 5.0


def test_load_dashboard_kpis_reads_the_files(tmp_path):
    """KPIs must come from the CSVs, not from built-in numbers (the old loader silently fell back)."""
    (tmp_path / "midterm-sample").mkdir()
    (tmp_path / "business").mkdir()
    (tmp_path / "midterm-sample" / "summary.csv").write_text(
        "type,n,hit3,intent_acc,ooc_rejection,mrr\n"
        "out_of_corpus,10,,,,\n"
        "in_corpus,40,0.5,0.75,,0.6\n"
        "all,50,0.5,0.75,0.8,0.6\n",
        encoding="utf-8",
    )
    (tmp_path / "business" / "business_summary.csv").write_text(
        "metric,value,description\ntop3_rescue_rate,0.45,x\nexpected_cost_per_query,0.25,x\nw_silent_wrong,3.0,x\n",
        encoding="utf-8",
    )
    kpis = load_dashboard_kpis(tmp_path)
    assert kpis["mrr"] == 0.6
    assert kpis["intent_accuracy"] == 0.75 and kpis["intent_correct"] == 30
    assert kpis["raw_hit3"] == 0.5 and kpis["top3_rescue_rate"] == 0.45
    assert kpis["ooc_rejection_rate"] == 0.8
    assert (kpis["total_queries"], kpis["in_corpus_queries"], kpis["ooc_queries"]) == (50, 40, 10)
    assert kpis["expected_cost"] == 0.25 and kpis["w_silent_wrong"] == 3.0
    assert kpis["deflection_rate"] is None  # missing metric stays None, no stale default


def test_load_dashboard_kpis_without_files(tmp_path):
    assert all(value is None for value in load_dashboard_kpis(tmp_path).values())


def test_record_feedback_appends_json_lines(tmp_path):
    from starter.ui_helpers import record_feedback

    log = tmp_path / "fb" / "feedback.jsonl"
    record_feedback("When is tuition due?", "faq_tuition_01", helpful=True, log_path=log)
    record_feedback("When is tuition due?", "faq_tuition_01", helpful=False, log_path=log)
    entries = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
    assert [e["helpful"] for e in entries] == [True, False]
    assert entries[0]["top_doc_id"] == "faq_tuition_01" and entries[0]["query"] == "When is tuition due?"



def _text_outside_cells(markup):
    """Text nodes that are not inside <td>, <th> or <caption> (i.e. visible stray text)."""
    from html.parser import HTMLParser

    class Collector(HTMLParser):
        def __init__(self):
            super().__init__()
            self.stack, self.stray = [], []

        def handle_starttag(self, tag, attrs):
            self.stack.append(tag)

        def handle_endtag(self, tag):
            if tag in self.stack:
                del self.stack[len(self.stack) - 1 - self.stack[::-1].index(tag):]

        def handle_data(self, data):
            if data.strip() and not {"td", "th", "caption"} & set(self.stack):
                self.stray.append(data.strip())

    collector = Collector()
    collector.feed(markup)
    return collector.stray


def test_table_html_has_no_stray_attribute_text_and_formats_cells():
    import pandas as pd
    from starter.ui_helpers import table_html

    df = pd.DataFrame({"rule": ["no_gate", "dual <b>"], "cosine": [float("nan"), 0.15], "rate": [0.8666666, 10.0]})
    markup = table_html(df, caption="Ablation & gates")

    assert _text_outside_cells(markup) == []  # old code leaked 'border="0" class="dataframe orca-table">'
    assert re.search(r'<table [^>]*><caption class="orca-table-caption">Ablation &amp; gates</caption>', markup)
    assert markup.count("<table") == 1 and markup.startswith('<div class="orca-table-wrap">')
    assert "NaN" not in markup and "—" in markup
    assert ">0.8667<" in markup and ">10<" in markup and ">0.15<" in markup
    assert "<b>" not in markup and "dual &lt;b&gt;" in markup
