"""UI Helper functions and formatters for the Campus FAQ Assistant.

Pure, deterministic functions with zero Streamlit runtime dependency,
ensuring 100% testability across UX formatting, intent-to-office routing,
source provenance labels, and accessibility tagging.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Vietnamese diacritics pattern for non-English query detection
VIETNAMESE_PATTERN = re.compile(
    r"[àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]",
    re.IGNORECASE,
)

# Common stopwords to exclude from visual keyword highlighting
HIGHLIGHT_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "of", "to", "in", "on",
    "for", "with", "at", "by", "from", "how", "what", "when", "where", "which",
    "who", "why", "can", "could", "would", "should", "is", "am", "are", "was",
    "were", "be", "been", "being", "have", "has", "had", "do", "does", "did",
    "i", "my", "me", "you", "your", "it", "its", "we", "our", "they", "their",
    "this", "that", "these", "those",
}

# Contact point per intent. "name" is quoted from, and "contact" paraphrases, the document named
# in "evidence" (data/faq.json or data/notices.json); tests/test_ui_helpers.py checks this.
# The corpus gives no buildings, room numbers or opening hours, so none are shown.
OFFICE_REGISTRY: dict[str, dict[str, str]] = {
    "course_registration": {
        "name": "Student Portal",
        "role": "Course registration, add/drop, waitlists, holds and override requests.",
        "contact": "Course Registration page of the HANU Student Portal",
        "evidence": "faq_course_registration_01",
    },
    "class_schedule": {
        "name": "My Schedule",
        "role": "Current class times, room numbers and printable weekly schedule.",
        "contact": "My Schedule page on the Student Portal",
        "evidence": "faq_class_schedule_01",
    },
    "exam": {
        "name": "Registrar's Office",
        "role": "Final exam calendar and exam conflict rescheduling.",
        "contact": "Conflict exam process (report at least two weeks before exam week)",
        "evidence": "faq_exam_02",
    },
    "tuition": {
        "name": "Bursar's Office",
        "role": "Payment calendar, installment plans, refunds and tuition statements.",
        "contact": "Student Portal billing tab, or the Bursar's Office in person",
        "evidence": "faq_tuition_11",
    },
    "student_services": {
        "name": "Advising Center",
        "role": "Academic advising appointments; other services are named in each answer.",
        "contact": "Advising tab on the Student Portal",
        "evidence": "faq_student_services_01",
    },
    "graduation": {
        "name": "Registrar",
        "role": "Graduation applications, honors cutoffs, transcripts and conferral dates.",
        "contact": "Registrar's transcript request service",
        "evidence": "faq_graduation_09",
    },
    "technical_support": {
        "name": "IT Help Desk",
        "role": "Course website errors, account lockouts and compromised accounts.",
        "contact": "Student Portal support ticket form",
        "evidence": "faq_technical_support_04",
    },
}

DEFAULT_OFFICE: dict[str, str] = {
    "name": "Student Portal",
    "role": "Student self-service.",
    "contact": "HANU Student Portal",
    "evidence": "faq_course_registration_01",
}

FEEDBACK_LOG = PROJECT_ROOT / "output" / "feedback" / "feedback.jsonl"

# 7-Domain Chromatic Palette aligned with authentic INTENTS in data/intents.csv
DOMAIN_PALETTE: dict[str, dict[str, str]] = {
    "course_registration": {
        "title": "Course Registration",
        "color": "#2563eb",  # Royal Blue
        "bg_badge": "#dbeafe",
        "text_badge": "#1e40af",
        "border": "#bfdbfe",
        "desc": "Add/drop deadlines, course prerequisites, credit overload limits, waitlists, and registration holds.",
    },
    "tuition": {
        "title": "Tuition & Fees",
        "color": "#059669",  # Emerald Teal
        "bg_badge": "#d1fae5",
        "text_badge": "#065f46",
        "border": "#a7f3d0",
        "desc": "Tuition payment deadlines, late penalties, installment plans, refund policies, and billing statements.",
    },
    "exam": {
        "title": "Examinations",
        "color": "#e11d48",  # Academic Crimson
        "bg_badge": "#ffe4e6",
        "text_badge": "#9f1239",
        "border": "#fecdd3",
        "desc": "Final exam schedules, conflict reporting, illness deferrals, makeup rules, and grade posting deadlines.",
    },
    "class_schedule": {
        "title": "Class Schedules & Rooms",
        "color": "#4f46e5",  # Indigo Violet
        "bg_badge": "#e0e7ff",
        "text_badge": "#3730a3",
        "border": "#c7d2fe",
        "desc": "Classroom assignments, lecture timetables, overlapping schedule resolutions, and section changes.",
    },
    "student_services": {
        "title": "Student Services & Advising",
        "color": "#d97706",  # Warm Amber
        "bg_badge": "#fef3c7",
        "text_badge": "#92400e",
        "border": "#fde68a",
        "desc": "Academic advising, tutoring centers, leaves of absence, counseling, and accessibility accommodations.",
    },
    "graduation": {
        "title": "Graduation & Degree Audit",
        "color": "#9333ea",  # Burgundy Plum
        "bg_badge": "#f3e8ff",
        "text_badge": "#6b21a8",
        "border": "#e9d5ff",
        "desc": "Degree audits, graduation filing, commencement dates, Latin honors cutoffs, and diploma distribution.",
    },
    "technical_support": {
        "title": "IT & Student Portal",
        "color": "#0284c7",  # Sky Cyan
        "bg_badge": "#e0f2fe",
        "text_badge": "#075985",
        "border": "#bae6fd",
        "desc": "Student Portal password resets, campus Wi-Fi configuration, email access, and multi-factor authentication.",
    },
}


def match_label(score: float) -> str:
    """Return calibrated match quality label based on empirical cosine distributions.

    - score >= 0.35: Strong match (contains 89.5% of Hit@1==1 queries).
    - 0.22 <= score < 0.35: Possible match (covers low-overlap paraphrases and boundary questions).
    - score < 0.22: Weak match (marginal confidence approaching abstention threshold).
    """
    if score >= 0.35:
        return "Strong match"
    if score >= 0.22:
        return "Possible match"
    return "Weak match"


def match_badge(score: float) -> str:
    """Return accessible badge with both geometric icon and textual label (WCAG 2.2 SC 1.4.1)."""
    label = match_label(score)
    if label == "Strong match":
        return f"🟢 {label}"
    if label == "Possible match":
        return f"🟡 {label}"
    return f"⚪ {label}"


def office_for_intent(intent: str) -> dict[str, str]:
    """Map an intent to the contact point named in the corpus for that topic."""
    return OFFICE_REGISTRY.get(intent, DEFAULT_OFFICE)


def is_non_english_query(query: str) -> bool:
    """Detect Vietnamese accented characters or high proportion of non-ASCII characters."""
    if not query or not query.strip():
        return False
    if VIETNAMESE_PATTERN.search(query):
        return True
    non_ascii_count = sum(1 for c in query if ord(c) > 127)
    return (non_ascii_count / len(query)) > 0.15


def load_notice_dates(notices_path: str | Path | None = None) -> dict[str, str]:
    """Load notice publication dates from data/notices.json into a dict {doc_id: date_str}."""
    path = Path(notices_path) if notices_path else (PROJECT_ROOT / "data" / "notices.json")
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return {item["id"]: item.get("date", "") for item in data if "id" in item}
    except Exception:
        return {}


def highlight_matched_terms(text: str, query: str) -> str:
    """Safely bold matched query terms within text using Markdown syntax without HTML injection."""
    if not text or not query:
        return text
    words = re.findall(r"\b[A-Za-z0-9_-]{3,}\b", query.lower())
    terms = {w for w in words if w not in HIGHLIGHT_STOPWORDS}
    if not terms:
        return text

    sorted_terms = sorted(terms, key=len, reverse=True)
    pattern = re.compile(r"\b(" + "|".join(re.escape(t) for t in sorted_terms) + r")\b", re.IGNORECASE)

    def replace_fn(match: re.Match[str]) -> str:
        return f"**{match.group(0)}**"

    return pattern.sub(replace_fn, text)


def clean_html(raw: str) -> str:
    """Strip leading/trailing whitespace and blank lines from multi-line HTML strings.

    Prevents CommonMark from interpreting 4+ space indented lines or blank-line-separated
    fragments inside st.markdown(..., unsafe_allow_html=True) as <pre><code> blocks.
    """
    if not raw:
        return ""
    return "\n".join(line.strip() for line in raw.splitlines() if line.strip())


def highlight_matched_terms_html(text: str, query: str) -> str:
    """Escape HTML and wrap matched query terms in <mark> tags.

    Terms are matched on the raw text and each piece is escaped afterwards, so a
    query word such as "amp" or "quot" can never match inside an HTML entity.
    """
    if not text:
        return ""
    if not query:
        return html.escape(text)

    words = re.findall(r"\b[A-Za-z0-9_-]{3,}\b", query.lower())
    terms = {w for w in words if w not in HIGHLIGHT_STOPWORDS}
    if not terms:
        return html.escape(text)

    sorted_terms = sorted(terms, key=len, reverse=True)
    pattern = re.compile(r"\b(" + "|".join(re.escape(t) for t in sorted_terms) + r")\b", re.IGNORECASE)

    parts: list[str] = []
    last = 0
    for match in pattern.finditer(text):
        parts.append(html.escape(text[last:match.start()]))
        parts.append(f'<mark class="orca-highlight">{html.escape(match.group(0))}</mark>')
        last = match.end()
    parts.append(html.escape(text[last:]))
    return "".join(parts)


def get_domain_catalog(documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build dynamic 7-domain catalog with accurate document counts and palette tokens (Fixes BE-2)."""
    # Group documents by intent
    intent_docs: dict[str, list[dict[str, Any]]] = {intent: [] for intent in DOMAIN_PALETTE}
    for doc in documents:
        intent = doc.get("intent", "")
        if intent in intent_docs:
            intent_docs[intent].append(doc)

    catalog: list[dict[str, Any]] = []
    for intent, meta in DOMAIN_PALETTE.items():
        docs = intent_docs.get(intent, [])
        faq_cnt = sum(1 for d in docs if d["id"].startswith("faq_") or d.get("source") == "faq.json")
        notice_cnt = sum(1 for d in docs if d["id"].startswith("notice_") or d.get("source") == "notices.json")
        office = office_for_intent(intent)

        catalog.append({
            "intent": intent,
            "title": meta["title"],
            "color": meta["color"],
            "bg_badge": meta["bg_badge"],
            "text_badge": meta["text_badge"],
            "border": meta["border"],
            "desc": meta["desc"],
            "office_name": office["name"],
            "office_contact": office["contact"],
            "total_count": len(docs),
            "faq_count": faq_cnt,
            "notice_count": notice_cnt,
        })
    return catalog


def get_intent_ranking(query: str, top_n: int = 3) -> list[tuple[str, float]]:
    """Extract top_n intent probability rankings for multi-topic visibility (Fixes BE-4)."""
    if not query or not query.strip():
        return []
    try:
        from starter.student_core import _get_classifier
        classifier = _get_classifier()
        probs = classifier.predict_proba(query)
        sorted_probs = sorted(probs.items(), key=lambda item: (-item[1], item[0]))
        return sorted_probs[:top_n]
    except Exception:
        return []


KPI_KEYS = (
    "mrr", "intent_accuracy", "intent_correct", "top3_rescue_rate", "raw_hit3", "ooc_rejection_rate",
    "total_queries", "in_corpus_queries", "ooc_queries",
    "deflection_rate", "safe_escalation_rate", "false_abstention_rate", "expected_cost",
    "w_silent_wrong", "w_false_abstain", "w_ooc_leak",
)

# business_summary.csv metric name -> KPI key
_BUSINESS_KPIS = {
    "self_service_deflection_rate_overall": "deflection_rate",
    "top3_rescue_rate": "top3_rescue_rate",
    "safe_escalation_rate": "safe_escalation_rate",
    "false_abstention_rate": "false_abstention_rate",
    "expected_cost_per_query": "expected_cost",
    "w_silent_wrong": "w_silent_wrong",
    "w_false_abstain": "w_false_abstain",
    "w_ooc_leak": "w_ooc_leak",
}


def load_dashboard_kpis(results_dir: str | Path | None = None) -> dict[str, Any]:
    """Read the dashboard KPIs from the result CSVs; there are no built-in fallback numbers.

    ``midterm-sample/summary.csv`` is a per-type table (rows ``in_corpus``,
    ``out_of_corpus``, ``all``); ``business/business_summary.csv`` is a
    ``metric,value`` table. A KPI whose file or row is missing stays ``None``
    and the app shows "n/a", so a stale number is never presented as current.
    """
    import pandas as pd

    base = Path(results_dir) if results_dir else PROJECT_ROOT / "experiments" / "results"
    kpis: dict[str, Any] = dict.fromkeys(KPI_KEYS)

    summary_file = base / "midterm-sample" / "summary.csv"
    if summary_file.exists():
        try:
            rows = pd.read_csv(summary_file).set_index("type")
            in_corpus, ooc, all_rows = rows.loc["in_corpus"], rows.loc["out_of_corpus"], rows.loc["all"]
            kpis["mrr"] = float(in_corpus["mrr"])
            kpis["intent_accuracy"] = float(in_corpus["intent_acc"])
            kpis["raw_hit3"] = float(in_corpus["hit3"])
            kpis["ooc_rejection_rate"] = float(all_rows["ooc_rejection"])
            kpis["in_corpus_queries"] = int(in_corpus["n"])
            kpis["ooc_queries"] = int(ooc["n"])
            kpis["total_queries"] = int(all_rows["n"])
            kpis["intent_correct"] = round(kpis["intent_accuracy"] * kpis["in_corpus_queries"])
        except (OSError, KeyError, ValueError):
            pass

    business_file = base / "business" / "business_summary.csv"
    if business_file.exists():
        try:
            frame = pd.read_csv(business_file)
            values = dict(zip(frame["metric"], frame["value"]))
            for metric, key in _BUSINESS_KPIS.items():
                if metric in values:
                    kpis[key] = float(values[metric])
        except (OSError, KeyError, ValueError):
            pass

    return kpis


def record_feedback(query: str, doc_id: str, helpful: bool, log_path: str | Path | None = None) -> Path:
    """Append one feedback vote as a JSON line and return the log path.

    The log lives in ``output/feedback/`` (git-ignored) so the team can read the
    votes during error analysis.
    """
    from datetime import datetime, timezone

    path = Path(log_path) if log_path else FEEDBACK_LOG
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "query": query,
        "top_doc_id": doc_id,
        "helpful": bool(helpful),
    }
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return path
