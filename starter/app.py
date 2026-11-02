"""Offline Streamlit demo for the integrated Project 12 midterm sample."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from starter.student_core import classify_intent, load_documents, retrieve  # noqa: E402

st.set_page_config(page_title="Campus Notice and FAQ Assistant", layout="wide")
st.title("Campus Notice and FAQ Assistant")
st.markdown(
    "Ask a question about campus services. Answers are retrieved from the "
    "provided FAQs and notices, with source and similarity scores."
)

documents = load_documents()

with st.sidebar:
    st.header("Available documents")
    st.caption(
        f"{len(documents)} FAQ/notice entries loaded from "
        "data/faq.json and data/notices.json."
    )
    intents = sorted({doc["intent"] for doc in documents})
    chosen_intent = st.selectbox("Filter by intent", ["(all)"] + intents)
    shown = documents if chosen_intent == "(all)" else [d for d in documents if d["intent"] == chosen_intent]
    for doc in shown[:30]:
        st.caption(f"`{doc['id']}` — {doc['question']}")

query = st.text_input("Ask a campus question")

col1, col2 = st.columns(2)
with col1:
    if st.button("Classify intent") and query.strip():
        intent, confidence = classify_intent(query)
        st.success(f"Intent: {intent} · confidence {confidence:.0%}")
with col2:
    if st.button("Retrieve documents") and query.strip():
        intent, confidence = classify_intent(query)
        st.success(f"Intent: {intent} · confidence {confidence:.0%}")
        results = retrieve(query)
        if not results:
            st.error("Information not found — please contact the administrative office.")
        for doc, score in results:
            st.markdown(f"**{doc['question']}** · `{doc['id']}` · {doc['source']} · cosine {score:.2f}")
            st.caption(doc["answer"])

st.info(
    "If no document is relevant enough, the correct behavior is to say so "
    "(low confidence / no match) rather than inventing an answer."
)
