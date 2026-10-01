"""Streamlit starter — Project 12 campus notice/FAQ assistant.

This page lists the available documents and takes a question as input. It
must not answer: ``classify_intent`` and ``retrieve`` are empty stubs
until you implement them yourself with classical IR/classification (see
``README.md``). A hosted ChatGPT-style API may not replace this
core.
"""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from starter.student_core import classify_intent, load_documents, retrieve  # noqa: E402

st.set_page_config(page_title="Campus Notice and FAQ Assistant — starter", layout="wide")
st.title("Campus Notice and FAQ Assistant — starter")
st.markdown(
    "The **AI core is student work**. This page only lists documents and "
    "takes a question; it must not classify, retrieve, or call a hosted "
    "model. A hosted ChatGPT-style API may not replace this core — see "
    "`README.md`."
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
    if st.button("Classify intent"):
        try:
            classify_intent(query)
        except NotImplementedError as exc:
            st.warning(f"Core not implemented yet: {exc}")
with col2:
    if st.button("Retrieve documents"):
        try:
            retrieve(query)
        except NotImplementedError as exc:
            st.warning(f"Core not implemented yet: {exc}")

st.info(
    "If no document is relevant enough, the correct behavior is to say so "
    "(low confidence / no match) rather than inventing an answer."
)
