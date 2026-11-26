"""Interactive Streamlit application for Project 12 — Campus Notice and FAQ Assistant.

Achromatic-ledger style (starter/theme.py): the answer comes first, set in ink on white cards, with the
cosine bar as the one coloured data element; a topic directory when nothing has been asked yet; and a
research inspector mode with the intent gate, top-k, explain() and a 3-way retrieval comparison.
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
    load_dev_split_summary,
    load_notice_dates,
    match_badge,
    match_label,
    office_for_intent,
    record_feedback,
    table_html,
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
    render_html(table_html(df, caption))


def kpi(col, label: str, value: str, detail: str, help_text: str | None = None) -> None:
    """KPI value with its detail as a caption.

    st.metric's delta slot draws a green up-arrow, which reads as "improved" and
    is wrong for counts such as false abstentions; it also truncates long text.
    """
    col.metric(label, value, help=help_text)
    col.caption(detail)


@st.cache_resource
def _get_comparison_retrievers() -> tuple[Retriever, BM25Retriever]:
    """Cache auxiliary Word TF-IDF and BM25 retrievers to prevent re-indexing latency (Fixes BE-3)."""
    docs = load_documents()
    word_ret = Retriever(docs, RetrievalConfig(analyzer="word", sublinear_tf=True))
    bm25_ret = BM25Retriever(docs)
    return word_ret, bm25_ret


st.set_page_config(
    page_title="HANU Student Knowledge Assistant",
    layout="wide",
    # "auto" keeps the sidebar open on desktop and folded on a phone, where it would cover the question box.
    initial_sidebar_state="auto",
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

    similarity_thresh = st.slider(
        "Cosine Similarity Threshold (θ_sim)",
        min_value=0.0,
        max_value=1.0,
        value=float(RETRIEVAL_THRESHOLD),
        step=0.01,
        help="Minimum cosine similarity required before returning results. Sub-threshold queries trigger safe abstention.",
    )

    inspector_param = st.query_params.get("inspector", "0") == "1"
    inspector_mode = st.toggle(
        "Research & Inspector Mode",
        value=inspector_param,
        help="Enable technical inspectability: intent confidence gate and top-k sliders, explain() feature attributions, and 3-way retrieval comparisons.",
    )

    if inspector_mode:
        st.markdown(
            "<p class='orca-inspector-note'>Intent gate, top-k, explain() and the 3-way comparison are shown.</p>",
            unsafe_allow_html=True,
        )
        intent_thresh = st.slider(
            "Intent Confidence Gate (θ_intent)",
            min_value=0.0,
            max_value=1.0,
            value=float(INTENT_THRESHOLD),
            step=0.01,
            help="Minimum Logistic Regression posterior (uncalibrated) required before results are shown.",
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
        intent_thresh = float(INTENT_THRESHOLD)
        top_k_val = 3

    st.markdown("---")
    presets = {
        "Choose a sample question": "",
        "Tuition payment deadline": "When is tuition due for the semester?",
        "Student Portal password": "How do I reset my Student Portal password?",
        "Timetable conflict (q_056)": "How can I tell if my class times conflict with each other?",
        "Registration hold (q_111)": "My account has a registration hold - what does that mean and how do I remove it?",
        "Checking class times (q_064)": "Where do I go to see my current classes and times?",
        "Typo-heavy question": "tution dedline paymnt for upcomng semster",
        "Wi-Fi connection issue": "I conncet to Wi-Fi!",
        "Out of scope: kayak rental": "Can I rent a kayak from the campus recreation center?",
        "Out of scope: campus dining": "What's the best restaurant near campus for vegan food?",
    }
    selected_preset = st.selectbox("Sample questions", list(presets.keys()))

    st.markdown("---")
    st.markdown("#### Document Archive")
    st.markdown(
        f"<p class='orca-section-note'>{len(documents)} synthetic documents: {n_faqs} FAQs, {n_notices} notices.</p>",
        unsafe_allow_html=True,
    )

    intents = sorted({doc["intent"] for doc in documents})
    chosen_intent = st.selectbox("Browse by topic", ["(all)"] + intents)
    filtered_docs = documents if chosen_intent == "(all)" else [d for d in documents if d["intent"] == chosen_intent]
    with st.expander(f"View archive documents ({len(filtered_docs)})", expanded=False):
        for doc in filtered_docs[:30]:
            doc_date = notice_dates.get(doc["id"], "")
            date_label = f" · Published {doc_date}" if doc_date else ""
            st.markdown(f"**`{doc['id']}`**{date_label} — {doc['question']}")
            st.caption(f"Source: {doc['source']} | Topic: `{doc['intent']}`")

# ----------------- MAIN TABS -----------------
tab_search, tab_eval = st.tabs(["Student Assistant", "Dashboard"])

# ----------------- TAB 1: ASSISTANT -----------------
with tab_search:
    # Title row: a noun title and one line, so the question box and the answer stay on the first screen.
    render_html(
        f"""
        <div class="orca-title-row">
            <h1 class="orca-title">HANU Student Knowledge Assistant</h1>
            <p class="orca-subtitle">Answers from {n_faqs} FAQs and {n_notices} notices, with source file and cosine;
            other questions are refused. {DISCLAIMER}</p>
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
    # Both buttons on one left edge; Retrieve is the screen's main job, so it is the one primary.
    col1, col2, _ = st.columns([1.5, 2, 4.5], gap="small")
    with col1:
        classify_clicked = st.button("Classify intent", use_container_width=True)
    with col2:
        retrieve_clicked = st.button("Retrieve documents", type="primary", use_container_width=True)

    # If user pressed enter, clicked retrieve, auto_retrieved, or picked a preset
    should_retrieve = retrieve_clicked or auto_retrieve or bool(query.strip() and not classify_clicked)

    if classify_clicked and query.strip():
        intent, confidence = classify_intent(query)
        office = office_for_intent(intent)
        st.success(f"Intent: {intent} · confidence {confidence:.0%}")

        # Structured Two-Column Office Ticket with Intent Probability Ranking (Fixes BE-4)
        top_intents = get_intent_ranking(query, top_n=3)
        ranking_items = "".join([
            f"<div class='orca-ticket-row'><span>{idx}. <code>{int_name}</code></span><span>{prob:.1%}</span></div>"
            for idx, (int_name, prob) in enumerate(top_intents, start=1)
        ])

        ticket_html = f"""
        <div class="orca-office-ticket">
            <div class="orca-ticket-grid">
                <div>
                    <div class="orca-ticket-label">Contact named in the corpus</div>
                    <div class="orca-ticket-name">{office['name']}</div>
                    <div class="orca-ticket-text">{office['role']}</div>
                    <div class="orca-ticket-well">
                        <div class="orca-ticket-label">Intent posterior (uncalibrated)</div>
                        {ranking_items}
                    </div>
                </div>
                <div>
                    <div class="orca-ticket-label">Self-service channel</div>
                    <div class="orca-ticket-name">{office['contact']}</div>
                    <div class="orca-ticket-text">Source: <code>{office['evidence']}</code>. The corpus lists no buildings, rooms or opening hours.</div>
                </div>
            </div>
        </div>
        """
        render_html(ticket_html)

    elif should_retrieve and query.strip():
        # Retrieve candidate documents through the dual gate (cosine + intent posterior)
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
            ranked = _get_retriever().rank(query)
            best_cosine = ranked[0][1] if ranked else 0.0

            def gate(value: float, limit: float, as_pct: bool) -> str:
                shown, bound = (f"{value:.0%}", f"{limit:.0%}") if as_pct else (f"{value:.2f}", f"{limit:.2f}")
                return f"{shown} (gate ≥ {bound}, {'passed' if value >= limit else 'failed'})"

            st.info(
                f"**Outside the indexed documents.** None of the {len(documents)} FAQs and notices matches well enough.\n\n"
                f"**Why it was rejected:** best cosine similarity {gate(best_cosine, similarity_thresh, False)} · "
                f"intent confidence {gate(confidence, intent_thresh, True)}.\n\n"
                f"**Topics it covers:** {topic_list}.\n\n"
                f"**Tips:**\n"
                f"- Rephrase with campus terms: *tuition payment*, *course add/drop*, *final exam*.\n"
                f"- Check spelling and expand abbreviations.\n"
                f"- Otherwise ask the university: the corpus has nothing on this."
            )
        else:
            # Successful retrieval: Render green success banner with intent, confidence, and office routing
            st.success(f"Intent: {intent} · confidence {confidence:.0%} · Contact: {office['name']}")
            # The dual-gate readout: the same two gates the refusal panel reports, here both passed.
            st.caption(
                f"Passed both gates: best cosine {results[0][1]:.2f} ≥ {similarity_thresh:.2f} · "
                f"intent {confidence:.0%} ≥ {intent_thresh:.0%}"
            )
            st.markdown(f"### {len(results)} matching documents")

            retriever = _get_retriever()
            for rank_idx, (doc, score) in enumerate(results, start=1):
                label_text = match_label(score)
                badge_str = match_badge(score)
                badge_class = "orca-badge-strong" if label_text == "Strong match" else ("orca-badge-possible" if label_text == "Possible match" else "orca-badge-weak")

                doc_date = notice_dates.get(doc["id"], "")
                src_file = doc.get("source") or ("notices.json" if doc["id"].startswith("notice_") else "faq.json")
                if doc["id"].startswith("notice_") or src_file == "notices.json":
                    src_tag = f"Notice ({src_file}) · Published {doc_date}" if doc_date else f"Notice ({src_file})"
                    src_class = "orca-badge-notice"
                else:
                    src_tag = f"FAQ ({src_file})"
                    src_class = "orca-badge-faq"

                # HTML-safe highlighting using <mark> (Fixes BE-1)
                highlighted_answer = highlight_matched_terms_html(doc["answer"], query)
                card_class = "orca-card-featured" if rank_idx == 1 else "orca-card"
                # The bar is the cosine itself on a 0-1 scale, with no minimum stub.
                meter_pct = min(max(score, 0.0), 1.0) * 100

                card_html = f"""
                <div class="{card_class}">
                    <div class="orca-meta-row">
                        <span class="orca-badge {src_class}">{src_tag}</span>
                        <span class="orca-badge {badge_class}">{badge_str}</span>
                    </div>
                    <div class="orca-question">{rank_idx}. {html.escape(doc['question'])}</div>
                    <div class="orca-meter-container">
                        <span>Cosine <strong>{score:.3f}</strong></span>
                        <div class="orca-meter-track" role="img" aria-label="Cosine {score:.3f} on a 0 to 1 scale">
                            <div class="orca-meter-fill" style="width:{meter_pct:.1f}%;"></div>
                        </div>
                    </div>
                    <div class="orca-answer">{highlighted_answer}</div>
                    <details>
                        <summary>Document details</summary>
                        <p class="orca-provenance">ID <code>{doc['id']}</code> · source <code>{html.escape(src_file)}</code> · cosine {score:.4f} · intent <code>{doc['intent']}</code></p>
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

            # Feedback mechanism
            render_html("<p class='orca-section-note'>Was the top answer helpful?</p>")
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
            <div>
                <h2 class="orca-section-title">Topic Directory & Contact Points</h2>
                <p class="orca-section-note">{len(documents)} documents across {len(DOMAIN_PALETTE)} topics, with the contact the corpus names for each.</p>
            </div>
            """
        )

        domain_catalog = get_domain_catalog(documents)
        cards_html = []
        for item in domain_catalog:
            c_html = f"""
            <div class="orca-directory-card">
                <div>
                    <div class="orca-directory-office">{item['office_name']}</div>
                    <div class="orca-directory-title">{item['title']}</div>
                    <div class="orca-directory-desc">{item['desc']}</div>
                </div>
                <div class="orca-directory-footer">{item['faq_count']} FAQs · {item['notice_count']} notices</div>
            </div>
            """
            cards_html.append(clean_html(c_html))

        grid_container = f'<div class="orca-directory-grid">{"".join(cards_html)}</div>'
        render_html(grid_container)

        render_html(
            """
            <div>
                <h2 class="orca-section-title">Recent Campus Notices</h2>
                <p class="orca-section-note">The three latest notices in the corpus.</p>
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
            text = notice["answer"]
            excerpt = text if len(text) <= 120 else text[:120].rsplit(" ", 1)[0] + "…"
            render_html(
                f"""
                <div class="orca-notice-card">
                    <div class="orca-meta-row">
                        <span class="orca-badge orca-badge-notice">Notice (notices.json){date_part}</span>
                    </div>
                    <div class="orca-notice-title">{html.escape(notice['question'])}</div>
                    <div class="orca-notice-text">{html.escape(excerpt)}</div>
                </div>
                """
            )

# ----------------- TAB 2: EVALUATION DASHBOARD -----------------
with tab_eval:
    n_bench = kpis["total_queries"] if kpis["total_queries"] is not None else "n/a"
    render_html(
        f"""
        <div class="orca-title-row">
            <h2 class="orca-dash-title">Benchmark Evaluation & Operational Business Dashboard</h2>
            <p class="orca-subtitle">Measured on the course's {n_bench} benchmark queries and {len(documents)} corpus documents
            (read from <code>experiments/results/midterm-sample/</code> and <code>experiments/results/business/</code>).</p>
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
    kpi(col_m1, "Overall Full MRR", fmt_rate(kpis["mrr"], ".3f"),
        f"{kpis['in_corpus_queries'] or 'n/a'} in-corpus queries",
        help_text="Mean Reciprocal Rank over the full ranking of the in-corpus benchmark queries")
    kpi(col_m2, "Intent Accuracy", fmt_rate(kpis["intent_accuracy"]), intent_detail)
    kpi(col_m3, "Self-Service Deflection", fmt_rate(kpis["deflection_rate"]),
        f"{fmt_count(kpis['deflection_rate'], kpis['total_queries'])} queries resolved at Top-1")
    kpi(col_m4, "Top-3 Delivered", fmt_rate(kpis["top3_rescue_rate"]),
        f"{fmt_count(kpis['top3_rescue_rate'], kpis['in_corpus_queries'])} answered in Top-3 "
        f"(raw Hit@3 {fmt_rate(kpis['raw_hit3'])})")

    col_m5, col_m6, col_m7, col_m8 = st.columns(4)
    kpi(col_m5, "OOC Rejection", fmt_rate(kpis["ooc_rejection_rate"]),
        f"{fmt_count(kpis['ooc_rejection_rate'], kpis['ooc_queries'])} out-of-corpus blocked")
    kpi(col_m6, "Safe Escalation", fmt_rate(kpis["safe_escalation_rate"]),
        f"{fmt_count(kpis['safe_escalation_rate'], kpis['total_queries'])} abstained and referred onward")
    kpi(col_m7, "False Abstention", fmt_rate(kpis["false_abstention_rate"]),
        f"{fmt_count(kpis['false_abstention_rate'], kpis['in_corpus_queries'])} in-corpus queries rejected")
    kpi(col_m8, "Expected Cost / Query", fmt_rate(kpis["expected_cost"], ".4f"), weights)

    dev = load_dev_split_summary()
    if dev is None:
        dev_text = (
            "Held-out dev split: result file missing. Run <code>python scripts/evaluate.py --split dev</code>."
        )
    else:
        dev_text = (
            f"<strong>Held-out dev split</strong> ({dev['total_queries']} queries outside the course benchmark, "
            f"<code>experiments/results/final-dev/</code>): end-to-end {dev['e2e_count']}/{dev['total_queries']}, "
            f"Balanced E2E {dev['balanced_e2e']:.3f}, OOC refused {dev['ooc_refused']}/{dev['ooc_queries']}, "
            f"paraphrase Hit@1 {dev['paraphrase_hit1']}/{dev['paraphrase_queries']}. "
            "The thresholds were chosen on the benchmark above, so the benchmark OOC rate is optimistic."
        )
    render_html(
        f"<p class='orca-section-note' style='margin-top:0.5rem;'>{dev_text}</p>"
    )

    st.markdown("---")
    # Figures sit in pairs; wide tables get the full width so they never overlap a figure.
    fig_col1, fig_col2 = st.columns(2)
    with fig_col1:
        st.markdown("#### Intent Confusion Matrix (7x7)")
        cm_img = PROJECT_ROOT / "experiments" / "results" / "figures" / "intent_confusion.png"
        if cm_img.exists():
            st.image(
                str(cm_img),
                caption=f"7x7 Intent Confusion Matrix ({intent_detail}, {fmt_rate(kpis['intent_accuracy'])})",
                use_column_width=True,
            )
    with fig_col2:
        st.markdown("#### Noise Degradation Curve (E3b: 0..3 Typo Swaps)")
        noise_img = PROJECT_ROOT / "experiments" / "results" / "figures" / "noise_curve.png"
        if noise_img.exists():
            st.image(str(noise_img), caption="Hit@1 & MRR@10 vs. Number of Typo Injections", use_column_width=True)
        else:
            st.info("Noise curve figure pending.")

    gate_col1, gate_col2 = st.columns(2)
    with gate_col1:
        st.markdown("#### Dual-Gate Ablation Study")
        ablation_file = PROJECT_ROOT / "experiments" / "results" / "midterm-sample" / "ablation.csv"
        if not ablation_file.exists():
            ablation_file = PROJECT_ROOT / "experiments" / "results" / "dev" / "ablation.csv"
        if ablation_file.exists():
            df_ab = pd.read_csv(ablation_file)
            # Five short columns so the key counts stay visible in a half-width column.
            compact_ab = pd.DataFrame({
                "Gate": df_ab["rule"].str.replace("_", " "),
                "Cosine ≥": df_ab["cosine_threshold"],
                "Intent ≥": df_ab["intent_threshold"],
                "Correct": df_ab["correct"].astype(int).astype(str) + "/" + df_ab["total"].astype(int).astype(str),
                "OOC rejected": df_ab["ooc_rejected"].astype(int).astype(str) + "/"
                + df_ab["ooc_total"].astype(int).astype(str),
            })
            show_table(compact_ab, caption=f"Empirical Ablation Across {n_bench} Benchmark Queries")
        else:
            st.info("Ablation file not found.")
    with gate_col2:
        # This figure is the preliminary E6 sweep (146 dev queries): cosine gate only, word TF-IDF +
        # sublinear TF, dev split. The shipped dual-gate char_wb config is evidenced by the
        # "Dual-Gate Ablation Study" table, not by this curve.
        st.markdown("#### Preliminary Threshold Sweep (E6, word TF-IDF)")
        sweep_img = PROJECT_ROOT / "experiments" / "results" / "figures" / "threshold_sweep_sublinear_tf.png"
        if sweep_img.exists():
            st.image(
                str(sweep_img),
                caption=(
                    "Cosine-only threshold sweep for word TF-IDF + sublinear TF on the dev split (146 dev queries). "
                    "Not the production config: see the Dual-Gate Ablation table for char_wb 3-5 "
                    f"with cosine ≥ {RETRIEVAL_THRESHOLD} and intent ≥ {INTENT_THRESHOLD}."
                ),
                use_column_width=True,
            )
        else:
            st.info("Threshold sweep figure pending.")

    st.markdown("#### Operational Business Metrics & Segment Breakdown")
    per_intent_file = PROJECT_ROOT / "experiments" / "results" / "business" / "per_intent_business.csv"
    if per_intent_file.exists():
        show_table(pd.read_csv(per_intent_file), caption="Operational Performance Breakdown by Intent & Query Type")
    else:
        st.info("Run `python experiments/business_metrics.py` to generate segment metrics.")

    st.markdown("#### Cost Sensitivity Analysis across Penalty Ratios")
    sensitivity_file = PROJECT_ROOT / "experiments" / "results" / "business" / "cost_sensitivity.csv"
    if sensitivity_file.exists():
        show_table(pd.read_csv(sensitivity_file), caption="Cost Sensitivity under 1:1, 3:1, 5:1, and 10:1 Penalty Ratios")
    else:
        st.info("Run `python experiments/business_metrics.py` to generate sensitivity table.")

    st.markdown("#### 5-Fold Stratified Intent Cross-Validation (E5b)")
    cv_file = PROJECT_ROOT / "experiments" / "results" / "dev" / "intent_cv.csv"
    if cv_file.exists():
        show_table(pd.read_csv(cv_file), caption="Stratified 5-Fold Intent Cross-Validation on 112 Documents")
    else:
        st.info("Intent CV results pending.")

    noise_curve_file = PROJECT_ROOT / "experiments" / "results" / "dev" / "noise_curve.csv"
    if noise_curve_file.exists():
        with st.expander("Noise Curve Raw Data (E3b)"):
            show_table(pd.read_csv(noise_curve_file), caption="Noise Degradation Under Typographic Perturbations")
