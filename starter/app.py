"""Interactive Streamlit application for Project 12 — Campus Notice and FAQ Assistant.

Redesigned with Oxford Navy & Claude Daylight Chromatic design tokens, student-centric academic directory,
staggered card animations, accessible WCAG 2.2 AA contrast, visual score meters, and research inspector mode.
"""
from __future__ import annotations

import html
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from starter.bm25 import BM25Retriever  # noqa: E402
from starter.retrieval import RetrievalConfig, Retriever  # noqa: E402
from starter.student_core import (  # noqa: E402
    INTENT_THRESHOLD,
    RETRIEVAL_THRESHOLD,
    _get_retriever,
    classify_intent,
    load_documents,
    retrieve,
)
from starter.theme import apply_theme  # noqa: E402
from starter.ui_helpers import (  # noqa: E402
    DOMAIN_PALETTE,
    clean_html,
    get_domain_catalog,
    get_intent_ranking,
    highlight_matched_terms_html,
    is_non_english_query,
    load_dashboard_kpis,
    load_notice_dates,
    match_badge,
    match_label,
    office_for_intent,
    record_feedback,
)

DISCLAIMER = (
    "Course project demo (AIN, Project 12). Answers come only from a synthetic, educational "
    "HANU corpus; this is not an official Hanoi University service."
)


def fmt_rate(value: float | None, spec: str = ".1%") -> str:
    """Format a KPI, or "n/a" when its result file was missing."""
    return "n/a" if value is None else format(value, spec)


def fmt_count(rate: float | None, total: int | None) -> str:
    """Format ``round(rate * total)/total``, or "n/a"."""
    if rate is None or total is None:
        return "n/a"
    return f"{round(rate * total)}/{total}"


def render_html(raw_html: str) -> None:
    """Render multi-line HTML safely without triggering CommonMark 4-space code blocks."""
    st.markdown(clean_html(raw_html), unsafe_allow_html=True)


def show_table(df: pd.DataFrame, caption: str = "Data Table") -> None:
    """Render dataframe as an accessible HTML table without pyarrow dependency (WCAG 2.2 SC 1.3.1)."""
    html_table = df.to_html(index=False, classes="orca-table", border=0)
    if "<caption" not in html_table:
        html_table = html_table.replace(
            "<table",
            f'<table role="table" class="orca-table"><caption style="font-weight:600;text-align:left;padding:6px 0;font-size:0.9rem;color:#5e5d59;">{caption}</caption>',
            1,
        )
    render_html(html_table)


@st.cache_resource
def _get_comparison_retrievers() -> tuple[Retriever, BM25Retriever]:
    """Cache auxiliary Word TF-IDF and BM25 retrievers to prevent re-indexing latency (Fixes BE-3)."""
    docs = load_documents()
    word_ret = Retriever(docs, RetrievalConfig(analyzer="word", sublinear_tf=True))
    bm25_ret = BM25Retriever(docs)
    return word_ret, bm25_ret


st.set_page_config(
    page_title="HANU Student Knowledge Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply centralized high-craft design tokens & CSS
apply_theme()

documents = load_documents()
notice_dates = load_notice_dates()
kpis = load_dashboard_kpis()
n_faqs = sum(1 for d in documents if d["source"] == "faq.json" or d["id"].startswith("faq_"))
n_notices = sum(1 for d in documents if d["source"] == "notices.json" or d["id"].startswith("notice_"))

# ----------------- SIDEBAR: CONTROLS & CORPUS EXPLORER -----------------
# NOTE: To guarantee 100% compatibility with automated AppTest suites (tests/test_midterm_sample.py),
# DO NOT declare any st.text_input or st.button inside the sidebar prior to the main search inputs!
with st.sidebar:
    st.markdown("### HANU Assistant")
    st.markdown(
        "<p style='font-size:0.875rem;color:#5e5d59;line-height:1.45;margin-bottom:0.75rem;'>"
        f"{DISCLAIMER}"
        "</p>",
        unsafe_allow_html=True,
    )

    inspector_param = st.query_params.get("inspector", "0") == "1"
    inspector_mode = st.toggle(
        "Research & Inspector Mode",
        value=inspector_param,
        help="Enable technical inspectability: dual-gate parameter sliders, explain() feature attributions, and 3-way retrieval comparisons.",
    )

    if inspector_mode:
        st.markdown(
            "<div style='padding:0.6rem 0.75rem;background:#faf9f5;border-radius:6px;border:1px solid #d6d3c4;margin-bottom:0.75rem;font-size:0.8rem;color:#b45309;'>"
            "<strong>Inspector Mode Active</strong>: Threshold sliders override production defaults."
            "</div>",
            unsafe_allow_html=True,
        )
        similarity_thresh = st.slider(
            "Cosine Similarity Threshold (θ_sim)",
            min_value=0.0,
            max_value=1.0,
            value=float(RETRIEVAL_THRESHOLD),
            step=0.01,
            help="Minimum cosine similarity required before returning results. Sub-threshold queries trigger safe abstention.",
        )
        intent_thresh = st.slider(
            "Intent Confidence Gate (θ_intent)",
            min_value=0.0,
            max_value=1.0,
            value=float(INTENT_THRESHOLD),
            step=0.01,
            help="Minimum posterior confidence required from the calibrated intent classifier.",
        )
        top_k_val = st.slider(
            "Top-K Cards",
            min_value=1,
            max_value=10,
            value=3,
            step=1,
            help="Number of document cards to present to the user.",
        )
    else:
        similarity_thresh = float(RETRIEVAL_THRESHOLD)
        intent_thresh = float(INTENT_THRESHOLD)
        top_k_val = 3

    st.markdown("---")
    st.markdown("#### Sample Inquiries")
    presets = {
        "(Type your own question or select)": "",
        "1. Tuition payment deadline": "When is tuition due for the semester?",
        "2. Student Portal login & password": "How do I reset my Student Portal password?",
        "3. Timetable schedule conflict [q_056]": "How can I tell if my class times conflict with each other?",
        "4. Registration account hold [q_111]": "My account has a registration hold - what does that mean and how do I remove it?",
        "5. Checking class times [q_064]": "Where do I go to see my current classes and times?",
        "6. Noisy query with typos": "tution dedline paymnt for upcomng semster",
        "7. Wi-Fi connection issue": "I conncet to Wi-Fi!",
        "8. Out-of-scope query (Recreation kayak)": "Can I rent a kayak from the campus recreation center?",
        "9. Out-of-scope query (Campus dining)": "What's the best restaurant near campus for vegan food?",
    }
    selected_preset = st.selectbox("Quick-load sample questions:", list(presets.keys()))

    st.markdown("---")
    st.markdown("#### Document Archive")
    st.markdown(
        f"<p style='font-size:0.8rem;color:#5e5d59;margin-bottom:0.5rem;'>"
        f"Archive contains <strong>{len(documents)}</strong> synthetic corpus documents ({n_faqs} FAQs, {n_notices} Notices)."
        f"</p>",
        unsafe_allow_html=True,
    )

    intents = sorted({doc["intent"] for doc in documents})
    chosen_intent = st.selectbox("Browse archive by topic:", ["(all)"] + intents)
    filtered_docs = documents if chosen_intent == "(all)" else [d for d in documents if d["intent"] == chosen_intent]
    with st.expander(f"View archive documents ({len(filtered_docs)})", expanded=False):
        for doc in filtered_docs[:30]:
            doc_date = notice_dates.get(doc["id"], "")
            date_label = f" · Published {doc_date}" if doc_date else ""
            st.markdown(f"**`{doc['id']}`**{date_label} — {doc['question']}")
            st.caption(f"Source: {doc['source']} | Topic: `{doc['intent']}`")

# ----------------- MAIN TABS -----------------
tab_search, tab_eval = st.tabs(["Student Assistant", "Operational & Research Dashboard"])

# ----------------- TAB 1: ASSISTANT -----------------
with tab_search:
    # Oxford Navy Hero Masthead Banner
    render_html(
        f"""
        <div class="orca-hero-banner">
            <div class="orca-hero-overline">AIN Course Project · Synthetic HANU Corpus</div>
            <div class="orca-hero-title">HANU Student Knowledge Assistant</div>
            <div class="orca-hero-subtitle">
                Retrieval-only answers on course registration, tuition, exams, schedules, graduation,
                student services and IT support. {DISCLAIMER}
            </div>
            <div class="orca-stat-strip">
                <span class="orca-stat-pill"><strong>{len(documents)}</strong> Documents</span>
                <span class="orca-stat-pill"><strong>{n_faqs}</strong> FAQs</span>
                <span class="orca-stat-pill"><strong>{n_notices}</strong> Notices</span>
                <span class="orca-stat-pill"><strong>{len(DOMAIN_PALETTE)}</strong> Topics</span>
                <span class="orca-stat-pill"><strong>{fmt_rate(kpis['top3_rescue_rate'])}</strong> Top-3 Rescue</span>
                <span class="orca-stat-pill"><strong>Dual-Gate</strong> Rejection</span>
            </div>
        </div>
        """
    )

    query_param_q = st.query_params.get("q", "")
    auto_retrieve = st.query_params.get("auto_retrieve", "0") == "1"
    default_text = query_param_q if query_param_q else (presets[selected_preset] if selected_preset and presets[selected_preset] else "")
    # CRITICAL: app.text_input[0] MUST be the search query input!
    query = st.text_input(
        "Ask a question about university regulations",
        value=default_text,
        placeholder="e.g., When is tuition due for the semester?",
    )

    # CRITICAL: app.button[0] = "Classify intent", app.button[1] = "Retrieve documents"
    col1, col2 = st.columns(2)
    with col1:
        classify_clicked = st.button("Classify intent")
    with col2:
        retrieve_clicked = st.button("Retrieve documents")

    # If user pressed enter, clicked retrieve, auto_retrieved, or picked a preset
    should_retrieve = retrieve_clicked or auto_retrieve or bool(query.strip() and not classify_clicked)

    if classify_clicked and query.strip():
        intent, confidence = classify_intent(query)
        office = office_for_intent(intent)
        st.success(f"Intent: {intent} · confidence {confidence:.0%}")

        # Structured Two-Column Office Ticket with Intent Probability Ranking (Fixes BE-4)
        top_intents = get_intent_ranking(query, top_n=3)
        ranking_items = "".join([
            f"<div style='display:flex; justify-content:space-between; margin-bottom:0.25rem; font-size:0.8125rem;'>"
            f"<span><strong>#{idx}</strong> <code>{int_name}</code></span>"
            f"<span style='color:#2563eb; font-weight:600;'>{prob:.1%}</span>"
            f"</div>"
            for idx, (int_name, prob) in enumerate(top_intents, start=1)
        ])

        ticket_html = f"""
        <div class="orca-office-ticket domain-{intent}">
            <div class="orca-ticket-grid">
                <div>
                    <div style="font-size:0.75rem; font-weight:700; letter-spacing:0.06em; text-transform:uppercase; color:#2563eb; margin-bottom:0.25rem;">
                        Suggested Contact (named in the corpus)
                    </div>
                    <div style="font-family:Georgia, serif; font-size:1.15rem; font-weight:600; color:#141413; margin-bottom:0.35rem;">
                        {office['name']}
                    </div>
                    <div style="font-size:0.875rem; color:#5e5d59; line-height:1.45; margin-bottom:0.75rem;">
                        {office['role']}
                    </div>
                    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:0.65rem 0.85rem;">
                        <div style="font-size:0.75rem; font-weight:600; color:#64748b; margin-bottom:0.35rem;">
                            Calibrated Intent Probability Breakdown
                        </div>
                        {ranking_items}
                    </div>
                </div>
                <div>
                    <div style="font-size:0.75rem; font-weight:700; letter-spacing:0.06em; text-transform:uppercase; color:#64748b; margin-bottom:0.25rem;">
                        Self-Service Channel
                    </div>
                    <div style="font-size:0.95rem; font-weight:600; color:#141413; margin-bottom:0.35rem;">
                        {office['contact']}
                    </div>
                    <div style="font-size:0.8125rem; color:#87867f; border-top:1px solid #e8e6dc; padding-top:0.5rem;">
                        Source: <code>{office['evidence']}</code>. The corpus lists no buildings, rooms or opening hours.
                    </div>
                </div>
            </div>
        </div>
        """
        render_html(ticket_html)

    elif should_retrieve and query.strip():
        # Retrieve candidate documents using calibrated dual-gate
        results = retrieve(
            query,
            top_k=top_k_val,
            threshold=similarity_thresh,
            intent_threshold=intent_thresh,
        )
        intent, confidence = classify_intent(query)
        office = office_for_intent(intent)

        # Non-English detection warning
        if is_non_english_query(query):
            st.warning(
                "**Language Advisory**: The HANU regulatory knowledge base is indexed in English. "
                "Questions in Vietnamese or other languages may experience lower retrieval recall. "
                "(Quý sinh viên vui lòng đặt câu hỏi bằng tiếng Anh để nhận câu trả lời chính xác nhất)."
            )

        if not results:
            # Abstention: show the required error string and no success banner. Do not name
            # an office here: the intent label of a rejected query is the classifier's forced
            # guess, so routing on it would present a confident answer the system just declined.
            st.error("Information not found — please contact the administrative office.")

            topic_list = ", ".join(meta["title"] for meta in DOMAIN_PALETTE.values())
            st.info(
                f"**Outside the indexed documents.** This assistant answers only from its {len(documents)} "
                f"FAQ and notice documents and found none that matches well enough.\n\n"
                f"**Topics it covers:** {topic_list}.\n\n"
                f"**Tips:**\n"
                f"1. If your question is about one of these topics, rephrase it with campus terms "
                f"(e.g. *'tuition payment'*, *'course add/drop'*, *'final exam'*).\n"
                f"2. Check spelling and expand abbreviations.\n"
                f"3. Otherwise, ask the university directly: the corpus has no information on this question."
            )
        else:
            # Successful retrieval: Render green success banner with intent, confidence, and office routing
            st.success(f"Intent: {intent} · confidence {confidence:.0%} · Routed to {office['name']}")
            st.markdown(f"### Found {len(results)} relevant documents:")

            retriever = _get_retriever()
            for rank_idx, (doc, score) in enumerate(results, start=1):
                label_text = match_label(score)
                badge_str = match_badge(score)
                badge_class = "orca-badge-strong" if label_text == "Strong match" else ("orca-badge-possible" if label_text == "Possible match" else "orca-badge-weak")

                doc_date = notice_dates.get(doc["id"], "")
                if doc["id"].startswith("notice_") or doc.get("source") == "notices.json":
                    src_tag = f"Notice · Published {doc_date}" if doc_date else "Notice"
                    src_class = "orca-badge-notice"
                else:
                    src_tag = "FAQ Entry"
                    src_class = "orca-badge-faq"

                # HTML-safe highlighting using <mark> (Fixes BE-1)
                highlighted_answer = highlight_matched_terms_html(doc["answer"], query)
                is_featured = (rank_idx == 1)
                card_class = f"orca-card-featured domain-{doc['intent']}" if is_featured else f"orca-card domain-{doc['intent']}"
                featured_badge_html = '<div class="orca-featured-badge">★ TOP RECOMMENDED ANSWER</div>' if is_featured else ''

                meter_pct = min(max(int(score * 100), 5), 100)
                meter_color = "#166534" if score >= 0.35 else ("#b45309" if score >= 0.22 else "#64748b")

                card_html = f"""
                <div class="{card_class}">
                    {featured_badge_html}
                    <div class="orca-meta-row">
                        <span class="orca-badge {src_class}">{src_tag}</span>
                        <span class="orca-badge {badge_class}">{badge_str}</span>
                        <span style="font-size:0.75rem; color:#87867f; margin-left:auto;">
                            Domain: <strong>{doc['intent']}</strong>
                        </span>
                    </div>
                    <div class="orca-question">#{rank_idx} · {html.escape(doc['question'])}</div>
                    <div class="orca-meter-container">
                        <span>Relevance Match: <strong>{score:.3f}</strong></span>
                        <div class="orca-meter-track">
                            <div class="orca-meter-fill" style="width:{meter_pct}%; background:{meter_color};"></div>
                        </div>
                        <span>({label_text})</span>
                    </div>
                    <div class="orca-answer">{highlighted_answer}</div>
                    <details>
                        <summary>Technical Details & Document Provenance</summary>
                        <p style="font-size:0.8rem;color:#5e5d59;margin:0.35rem 0 0 0;">
                            Document ID: <code>{doc['id']}</code> | Relevance Cosine: <strong>{score:.4f}</strong> | Topic Intent: <code>{doc['intent']}</code>
                        </p>
                    </details>
                </div>
                """
                render_html(card_html)

                # Ensure doc['id'] is present in markdown stream for AppTest inspection compatibility
                st.markdown(f"<!-- doc_id:{doc['id']} -->", unsafe_allow_html=True)

                # Feature attribution explain() (Inspector Mode)
                if inspector_mode:
                    with st.expander(f"Feature Attribution (`explain()`) for `{doc['id']}`", expanded=False):
                        contribs = retriever.explain(query, doc["id"], top_n=6)
                        if contribs:
                            df_contrib = pd.DataFrame(
                                contribs,
                                columns=["Feature (Word / Sub-word n-gram)", "Cosine Contribution Score"],
                            )
                            show_table(df_contrib, caption=f"Top Overlapping Features Attributed to {doc['id']}")
                        else:
                            st.caption("No overlapping subword features found.")

                st.markdown("---")

            # Feedback mechanism
            render_html(
                "<p style='font-size:0.85rem;color:#5e5d59;margin-bottom:0.5rem;'>Was this answer helpful for your inquiry?</p>"
            )
            fb_col1, fb_col2, _ = st.columns([1, 1, 6])
            with fb_col1:
                vote_yes = st.button("Helpful", key="fb_yes")
            with fb_col2:
                vote_no = st.button("Needs Clarification", key="fb_no")
            if vote_yes or vote_no:
                try:
                    log_path = record_feedback(query, results[0][0]["id"], helpful=vote_yes)
                    shown = log_path.relative_to(PROJECT_ROOT) if log_path.is_relative_to(PROJECT_ROOT) else log_path
                    st.toast(f"Thank you. Feedback saved to {shown.as_posix()}.")
                except OSError as exc:
                    st.toast(f"Feedback could not be saved: {exc}")

        # In Inspector Mode: Display 3-way retrieval method comparison using cached retrievers (Fixes BE-3)
        if inspector_mode and query.strip():
            with st.expander("3-Way Retrieval Method Comparison (Word TF-IDF vs Char_wb vs BM25)", expanded=False):
                try:
                    word_retriever, bm25_retriever = _get_comparison_retrievers()

                    word_top3 = word_retriever.rank(query)[:3]
                    char_top3 = results[:3] if results else _get_retriever().rank(query)[:3]
                    bm25_top3 = bm25_retriever.rank(query)[:3]

                    comp_rows = []
                    for i in range(3):
                        w_doc, w_sc = word_top3[i] if i < len(word_top3) else ({"id": "-"}, 0.0)
                        c_doc, c_sc = char_top3[i] if i < len(char_top3) else ({"id": "-"}, 0.0)
                        b_doc, b_sc = bm25_top3[i] if i < len(bm25_top3) else ({"id": "-"}, 0.0)
                        comp_rows.append({
                            "Rank": f"#{i+1}",
                            "Char_wb (Production)": f"{c_doc['id']} (cos: {c_sc:.3f})",
                            "Word TF-IDF": f"{w_doc['id']} (cos: {w_sc:.3f})",
                            "Okapi BM25": f"{b_doc['id']} (score: {b_sc:.2f})",
                        })
                    show_table(pd.DataFrame(comp_rows), caption="Top-3 Retrieval Comparison across Distinct Vector Spaces")
                except Exception as e:
                    st.caption(f"Comparison view unavailable: {e}")

    else:
        # FIRST-USE EMPTY STATE: Dynamic 7-Domain Bento Grid with Chromatic Cards (Fixes BE-2)
        render_html(
            f"""
            <div style="margin: 1.5rem 0 0.5rem 0;">
                <div style="font-family: Georgia, 'Times New Roman', serif; font-size: 1.3rem; font-weight: 600; color: #141413; margin-bottom: 0.35rem;">
                    Topic Directory & Contact Points
                </div>
                <p style="font-size: 0.925rem; color: #5e5d59; margin-bottom: 1.25rem;">
                    The corpus indexes {len(documents)} synthetic documents across {len(DOMAIN_PALETTE)} topics. Each card names the contact point the corpus gives for that topic:
                </p>
            </div>
            """
        )

        domain_catalog = get_domain_catalog(documents)
        cards_html = []
        for item in domain_catalog:
            c_html = f"""
            <div class="orca-directory-card domain-{item['intent']}">
                <div>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
                        <span class="orca-directory-office" style="color:{item['color']};">
                            {item['office_name']}
                        </span>
                        <span style="font-size:0.75rem; background:{item['bg_badge']}; color:{item['text_badge']}; border:1px solid {item['border']}; padding:0.1rem 0.45rem; border-radius:4px; font-weight:600;">
                            {item['total_count']} docs
                        </span>
                    </div>
                    <div class="orca-directory-title">{item['title']}</div>
                    <div class="orca-directory-desc">{item['desc']}</div>
                </div>
                <div class="orca-directory-footer">
                    <span>{item['faq_count']} FAQs · {item['notice_count']} Notices</span>
                </div>
            </div>
            """
            cards_html.append(clean_html(c_html))

        grid_container = f'<div class="orca-directory-grid">{"".join(cards_html)}</div>'
        render_html(grid_container)

        render_html(
            """
            <div style="margin: 2rem 0 0.75rem 0; border-top: 1px solid #e8e6dc; padding-top: 1.25rem;">
                <div style="font-family: Georgia, 'Times New Roman', serif; font-size: 1.15rem; font-weight: 600; color: #141413; margin-bottom: 0.25rem;">
                    Recent Campus Notices
                </div>
                <p style="font-size: 0.875rem; color: #5e5d59; margin-bottom: 1rem;">
                    The three most recent notices in the corpus, by publication date:
                </p>
            </div>
            """
        )

        # Render 3 recent notices from dataset
        recent_notices = [
            d for d in documents if d["id"].startswith("notice_") or d.get("source") == "notices.json"
        ]
        recent_notices.sort(key=lambda d: notice_dates.get(d["id"], ""), reverse=True)
        for notice in recent_notices[:3]:
            d_date = notice_dates.get(notice["id"], "")
            date_part = f" · Published {d_date}" if d_date else ""
            excerpt = notice["answer"][:170] + ("..." if len(notice["answer"]) > 170 else "")
            render_html(
                f"""
                <div class="orca-notice-card domain-{notice['intent']}">
                    <div class="orca-meta-row" style="margin-bottom:0.25rem;">
                        <span class="orca-badge orca-badge-notice">Notice{date_part}</span>
                        <span style="font-size:0.75rem; color:#87867f;">Record ID: <code>{notice['id']}</code></span>
                        <span style="font-size:0.75rem; color:#87867f; margin-left:auto;">Domain: <code>{notice['intent']}</code></span>
                    </div>
                    <div style="font-family:Georgia, serif; font-weight:600; font-size:0.95rem; color:#141413; margin-bottom:0.25rem;">
                        {html.escape(notice['question'])}
                    </div>
                    <div style="font-size:0.875rem; color:#5e5d59; line-height:1.5;">
                        {html.escape(excerpt)}
                    </div>
                </div>
                """
            )

# ----------------- TAB 2: EVALUATION DASHBOARD -----------------
with tab_eval:
    n_bench = kpis["total_queries"] if kpis["total_queries"] is not None else "n/a"
    render_html(
        f"""
        <div style="margin-bottom:1.25rem; border-bottom:1px solid #e8e6dc; padding-bottom:1rem;">
            <h2 style="font-family:Georgia, serif; font-size:1.6rem; font-weight:600; color:#141413; margin-bottom:0.25rem;">
                Benchmark Evaluation & Operational Business Dashboard
            </h2>
            <p style="font-size:0.95rem; color:#5e5d59; margin-bottom:0;">
                Measured on the course's {n_bench} benchmark queries and {len(documents)} corpus documents
                (read from <code>experiments/results/midterm-sample/</code> and <code>experiments/results/business/</code>).
            </p>
        </div>
        """
    )

    if all(kpis[k] is None for k in ("mrr", "deflection_rate")):
        st.info("Result files not found. Run `python scripts/evaluate.py` and `python experiments/business_metrics.py`.")

    weights = (
        "n/a" if kpis["w_silent_wrong"] is None
        else f"Penalty w_wrong={kpis['w_silent_wrong']:g}, w_ooc_leak={kpis['w_ooc_leak']:g}, "
             f"w_abstain={kpis['w_false_abstain']:g}"
    )
    intent_detail = (
        "n/a" if kpis["intent_correct"] is None
        else f"{kpis['intent_correct']}/{kpis['in_corpus_queries']} in-corpus correct"
    )

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Overall Full MRR", fmt_rate(kpis["mrr"], ".3f"),
                  help=f"Mean Reciprocal Rank on the {kpis['in_corpus_queries'] or 'n/a'} in-corpus benchmark queries")
    col_m2.metric("Intent Accuracy", fmt_rate(kpis["intent_accuracy"]), intent_detail)
    col_m3.metric(
        "Self-Service Deflection",
        fmt_rate(kpis["deflection_rate"]),
        f"{fmt_count(kpis['deflection_rate'], kpis['total_queries'])} queries resolved at Top-1",
    )
    col_m4.metric(
        "Top-3 Rescue Rate",
        fmt_rate(kpis["top3_rescue_rate"]),
        f"{fmt_count(kpis['top3_rescue_rate'], kpis['in_corpus_queries'])} in-corpus captured in Top-3",
    )

    col_m5, col_m6, col_m7, col_m8 = st.columns(4)
    col_m5.metric(
        "OOC Rejection",
        fmt_rate(kpis["ooc_rejection_rate"]),
        f"{fmt_count(kpis['ooc_rejection_rate'], kpis['ooc_queries'])} out-of-corpus blocked",
    )
    col_m6.metric(
        "Safe Escalation",
        fmt_rate(kpis["safe_escalation_rate"]),
        f"{fmt_count(kpis['safe_escalation_rate'], kpis['total_queries'])} abstained and referred onward",
    )
    col_m7.metric(
        "False Abstention",
        fmt_rate(kpis["false_abstention_rate"]),
        f"{fmt_count(kpis['false_abstention_rate'], kpis['in_corpus_queries'])} in-corpus queries rejected",
    )
    col_m8.metric("Expected Cost / Query", fmt_rate(kpis["expected_cost"], ".4f"), weights)

    st.markdown("---")
    dash_col1, dash_col2 = st.columns(2)

    with dash_col1:
        st.markdown("#### Operational Business Metrics & Segment Breakdown")
        per_intent_file = PROJECT_ROOT / "experiments" / "results" / "business" / "per_intent_business.csv"
        if per_intent_file.exists():
            df_pi = pd.read_csv(per_intent_file)
            show_table(df_pi, caption="Operational Performance Breakdown by Intent & Query Type")
        else:
            st.info("Run `python experiments/business_metrics.py` to generate segment metrics.")

        st.markdown("#### Cost Sensitivity Analysis across Penalty Ratios")
        sensitivity_file = PROJECT_ROOT / "experiments" / "results" / "business" / "cost_sensitivity.csv"
        if sensitivity_file.exists():
            df_sens = pd.read_csv(sensitivity_file)
            show_table(df_sens, caption="Cost Sensitivity under 1:1, 3:1, 5:1, and 10:1 Penalty Ratios")
        else:
            st.info("Run `python experiments/business_metrics.py` to generate sensitivity table.")

        st.markdown("#### Dual-Gate Ablation Study")
        ablation_file = PROJECT_ROOT / "experiments" / "results" / "midterm-sample" / "ablation.csv"
        if not ablation_file.exists():
            ablation_file = PROJECT_ROOT / "experiments" / "results" / "dev" / "ablation.csv"
        if ablation_file.exists():
            df_ab = pd.read_csv(ablation_file)
            show_table(df_ab, caption=f"Empirical Ablation Across {n_bench} Benchmark Queries")
        else:
            st.info("Ablation file not found.")

        st.markdown("#### 5-Fold Stratified Intent Cross-Validation (E5b)")
        cv_file = PROJECT_ROOT / "experiments" / "results" / "dev" / "intent_cv.csv"
        if cv_file.exists():
            df_cv = pd.read_csv(cv_file)
            show_table(df_cv, caption="Stratified 5-Fold Intent Cross-Validation on 112 Documents")
        else:
            st.info("Intent CV results pending.")

    with dash_col2:
        st.markdown("#### Intent Confusion Matrix (7x7)")
        cm_img = PROJECT_ROOT / "experiments" / "results" / "figures" / "intent_confusion.png"
        if cm_img.exists():
            st.image(
                str(cm_img),
                caption=f"7x7 Intent Confusion Matrix ({intent_detail}, {fmt_rate(kpis['intent_accuracy'])})",
                use_column_width=True,
            )

        st.markdown("#### Noise Degradation Curve (E3b: 0..3 Typo Swaps)")
        noise_img = PROJECT_ROOT / "experiments" / "results" / "figures" / "noise_curve.png"
        if noise_img.exists():
            st.image(str(noise_img), caption="Hit@1 & MRR@10 vs. Number of Typo Injections", use_column_width=True)
        else:
            st.info("Noise curve figure pending.")

        # This figure is the preliminary E6 sweep (18/10): cosine gate only, word TF-IDF +
        # sublinear TF, dev split. The shipped dual-gate char_wb config is evidenced by the
        # "Dual-Gate Ablation Study" table, not by this curve.
        st.markdown("#### Preliminary Threshold Sweep (E6, word TF-IDF)")
        sweep_img = PROJECT_ROOT / "experiments" / "results" / "figures" / "threshold_sweep_sublinear_tf.png"
        if sweep_img.exists():
            st.image(
                str(sweep_img),
                caption=(
                    "Cosine-only threshold sweep for word TF-IDF + sublinear TF on the dev split (18/10). "
                    "Not the production config: see the Dual-Gate Ablation table for char_wb 3-5 "
                    f"with cosine ≥ {RETRIEVAL_THRESHOLD} and intent ≥ {INTENT_THRESHOLD}."
                ),
                use_column_width=True,
            )
        else:
            st.info("Threshold sweep figure pending.")

        noise_curve_file = PROJECT_ROOT / "experiments" / "results" / "dev" / "noise_curve.csv"
        if noise_curve_file.exists():
            st.markdown("#### Noise Curve Raw Data (E3b)")
            df_noise = pd.read_csv(noise_curve_file)
            show_table(df_noise, caption="Noise Degradation Under Typographic Perturbations")
