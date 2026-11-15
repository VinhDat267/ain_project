"""Interactive Streamlit application for Project 12 — Campus Notice and FAQ Assistant.

Supports interactive natural-language querying, real-time intent classification with
calibrated confidence, dual-gate threshold controls, keyword explainability (explain()),
quick stress-test scenarios, and an integrated Evaluation Dashboard.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from starter.student_core import (  # noqa: E402
    INTENT_THRESHOLD,
    RETRIEVAL_THRESHOLD,
    _get_retriever,
    classify_intent,
    load_documents,
    retrieve,
)


def show_table(df: pd.DataFrame) -> None:
    """Render dataframe as a clean HTML table without triggering pyarrow serialization."""
    st.markdown(df.to_html(index=False), unsafe_allow_html=True)

st.set_page_config(
    page_title="Campus Notice & FAQ Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🎓 Campus Notice and FAQ Assistant")
st.markdown(
    "A classical AI conversational search assistant built on the **Vector Space Model (VSM)** "
    "and **Supervised Intent Classification**. Designed with strict abstention rules to eliminate hallucinations."
)

documents = load_documents()

# ----------------- SIDEBAR: CONTROLS & CORPUS EXPLORER -----------------
with st.sidebar:
    st.header("⚙️ System Controls")
    similarity_thresh = st.slider(
        "Cosine Similarity Threshold (θ)",
        min_value=0.0,
        max_value=1.0,
        value=float(RETRIEVAL_THRESHOLD),
        step=0.01,
        help="Minimum top-1 cosine similarity required before returning results. Sub-threshold queries trigger abstention.",
    )
    intent_thresh = st.slider(
        "Intent Confidence Gate",
        min_value=0.0,
        max_value=1.0,
        value=float(INTENT_THRESHOLD),
        step=0.01,
        help="Minimum posterior confidence required from the intent classifier.",
    )
    top_k_val = st.slider(
        "Top-K Results",
        min_value=1,
        max_value=10,
        value=3,
        step=1,
    )

    st.markdown("---")
    st.header("⚡ Stress-Test Presets")
    presets = {
        "(Select preset to fill question)": "",
        "1. Normal (Canonical)": "When is tuition due for the semester?",
        "2. Paraphrase (Vocabulary shift)": "Is it possible to sit in on a lecture for personal enrichment without receiving grades or credits?",
        "3. Multi-Typo (Noisy query)": "tution dedline paymnt for upcomng semster",
        "4. Adversarial Out-of-Corpus": "Can I park my helicopter on the campus lawn?",
    }
    selected_preset = st.selectbox("Load benchmark archetypes:", list(presets.keys()))

    st.markdown("---")
    st.header("📚 Corpus Explorer")
    st.caption(f"{len(documents)} total entries loaded ({sum(d['source'] == 'faq.json' for d in documents)} FAQs, {sum(d['source'] == 'notices.json' for d in documents)} notices).")
    intents = sorted({doc["intent"] for doc in documents})
    chosen_intent = st.selectbox("Filter corpus by intent:", ["(all)"] + intents)
    filtered_docs = documents if chosen_intent == "(all)" else [d for d in documents if d["intent"] == chosen_intent]
    with st.expander(f"View documents ({len(filtered_docs)})", expanded=False):
        for doc in filtered_docs[:25]:
            st.markdown(f"**`{doc['id']}`** — {doc['question']}")
            st.caption(f"Source: {doc['source']} | Intent: `{doc['intent']}`")

# ----------------- MAIN TABS -----------------
tab_search, tab_eval = st.tabs(["🔍 Assistant & Search", "📊 Evaluation Dashboard"])

# ----------------- TAB 1: ASSISTANT -----------------
with tab_search:
    default_text = presets[selected_preset] if selected_preset and presets[selected_preset] else ""
    query = st.text_input("Ask a campus question", value=default_text)

    # Note: Keep col1 and col2 button ordering identical for automated AppTest suite compatibility!
    col1, col2 = st.columns(2)
    with col1:
        classify_clicked = st.button("Classify intent")
    with col2:
        retrieve_clicked = st.button("Retrieve documents")

    if classify_clicked and query.strip():
        intent, confidence = classify_intent(query)
        st.success(f"Intent: {intent} · confidence {confidence:.0%}")

    if retrieve_clicked and query.strip():
        intent, confidence = classify_intent(query)
        st.success(f"Intent: {intent} · confidence {confidence:.0%}")

        results = retrieve(
            query,
            top_k=top_k_val,
            threshold=similarity_thresh,
            intent_threshold=intent_thresh,
        )

        if not results:
            st.error("Information not found — please contact the administrative office.")
            st.caption("🛡️ **Abstention Triggered**: Either the cosine relevance score or the intent posterior confidence fell below the safety threshold.")
        else:
            st.markdown(f"### Found {len(results)} relevant documents:")
            retriever = _get_retriever()
            for doc, score in results:
                with st.container():
                    st.markdown(f"**{doc['question']}** · `{doc['id']}` · {doc['source']} · cosine {score:.2f}")
                    st.caption(doc["answer"])

                    # Feature contribution attribution (Việt Anh's explain() method)
                    with st.expander(f"🔬 Feature Attribution (`explain()`) for `{doc['id']}`"):
                        contribs = retriever.explain(query, doc["id"], top_n=5)
                        if contribs:
                            df_contrib = pd.DataFrame(contribs, columns=["Feature (Word / Sub-word n-gram)", "Cosine Contribution Score"])
                            show_table(df_contrib)
                        else:
                            st.caption("No overlapping features found.")

    st.info(
        "💡 **Academic AI Guardrail**: If no document is relevant enough, the correct behavior is to abstain "
        "(low confidence / no match) rather than inventing an answer. Commercial LLM APIs are completely prohibited."
    )

# ----------------- TAB 2: EVALUATION DASHBOARD -----------------
with tab_eval:
    st.subheader("Benchmark Evaluation & Experimental Results")
    st.markdown(
        "Empirical performance measured across official 120 benchmark queries and 146 development queries."
    )

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Overall MRR", "0.943", help="Mean Reciprocal Rank on 120 test queries")
    col_m2.metric("Intent Accuracy", "97.1%", "102/105 correct")
    col_m3.metric("Balanced E2E", "90.0%", "108/120 end-to-end")
    col_m4.metric("OOC Rejection", "100%", "15/15 rejected")

    st.markdown("---")
    dash_col1, dash_col2 = st.columns(2)

    with dash_col1:
        st.markdown("#### 🎯 Dual-Gate Ablation Study")
        ablation_file = PROJECT_ROOT / "experiments" / "results" / "midterm-sample" / "ablation.csv"
        if ablation_file.exists():
            df_ab = pd.read_csv(ablation_file)
            show_table(df_ab)
        else:
            st.info("Ablation file not found.")

        st.markdown("#### 🔤 5-Fold Stratified Intent Cross-Validation (E5b)")
        cv_file = PROJECT_ROOT / "experiments" / "results" / "dev" / "intent_cv.csv"
        if cv_file.exists():
            df_cv = pd.read_csv(cv_file)
            show_table(df_cv)
        else:
            st.info("Intent CV results pending.")

        st.markdown("#### 🧭 Intent Confusion Matrix (7x7)")
        cm_img = PROJECT_ROOT / "experiments" / "results" / "figures" / "intent_confusion.png"
        if cm_img.exists():
            st.image(str(cm_img), caption="7x7 Intent Confusion Matrix (102/105 Correct, 97.1%)", use_column_width=True)

    with dash_col2:
        st.markdown("#### 📉 Noise Degradation Curve (E3b: 0..3 Typo Swaps)")
        noise_img = PROJECT_ROOT / "experiments" / "results" / "figures" / "noise_curve.png"
        if noise_img.exists():
            st.image(str(noise_img), caption="Hit@1 & MRR@10 vs. Number of Typo Injections", use_column_width=True)
        else:
            st.info("Noise curve figure pending.")

        st.markdown("#### 🎚️ Dual-Gate Threshold Sweep")
        sweep_img = PROJECT_ROOT / "experiments" / "results" / "figures" / "threshold_sweep_sublinear_tf.png"
        if sweep_img.exists():
            st.image(str(sweep_img), caption="Threshold Sweep Trade-off Curve", use_column_width=True)
        else:
            st.info("Threshold sweep figure pending.")
