"""Service layer bridging FastAPI routes with Project 12's classical IR/NLP core."""
from __future__ import annotations

import csv
import json
import math
import re
import time
from pathlib import Path
from typing import Any

from starter.bm25 import BM25Retriever
from starter.intent import INTENTS
from starter.retrieval import RetrievalConfig, Retriever
from starter.student_core import (
    INTENT_THRESHOLD,
    RETRIEVAL_THRESHOLD,
    _get_classifier,
    _get_retriever,
    classify_intent,
    load_documents,
    retrieve,
)
from starter.ui_helpers import (
    DOMAIN_PALETTE,
    HIGHLIGHT_STOPWORDS,
    OFFICE_REGISTRY,
    get_domain_catalog,
    get_intent_ranking,
    is_non_english_query,
    load_dashboard_kpis,
    load_notice_dates,
    match_label,
    office_for_intent,
    record_feedback,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ABSTENTION_MESSAGE = "Information not found — please contact the administrative office."
DEMO_6_IDS = ("q_006", "q_003", "q_028", "q_026", "q_064", "q_086")

SHORT_INTENT_LABELS: dict[str, str] = {
    "course_registration": "Course Reg",
    "exam": "Examinations",
    "tuition": "Tuition",
    "class_schedule": "Schedules",
    "student_services": "Services",
    "graduation": "Graduation",
    "technical_support": "IT Support",
}


class _RuntimeState:
    """Lazy-initialized cache of documents, retrievers, and benchmark queries."""

    def __init__(self) -> None:
        self.initialized = False
        self.documents: list[dict[str, Any]] = []
        self.docs_by_id: dict[str, dict[str, Any]] = {}
        self.notice_dates: dict[str, str] = {}
        self.word_retriever: Retriever | None = None
        self.bm25_retriever: BM25Retriever | None = None
        self.test_queries: list[dict[str, str]] = []

    def ensure_ready(self) -> None:
        if self.initialized:
            return
        self.documents = load_documents()
        self.docs_by_id = {doc["id"]: doc for doc in self.documents}
        self.notice_dates = load_notice_dates()

        # Pre-warm primary TF-IDF retriever and Logistic Regression intent classifier.
        _get_retriever()
        _get_classifier()

        # Pre-warm comparison retrievers so Inspector mode answers without re-indexing delay.
        self.word_retriever = Retriever(self.documents, RetrievalConfig(analyzer="word", sublinear_tf=True))
        self.bm25_retriever = BM25Retriever(self.documents)

        queries_path = PROJECT_ROOT / "data" / "queries_test.csv"
        if queries_path.exists():
            with queries_path.open(newline="", encoding="utf-8") as fh:
                self.test_queries = list(csv.DictReader(fh))
        self.initialized = True


_STATE = _RuntimeState()


def warmup() -> None:
    """Warm all classical IR/NLP models at server startup."""
    _STATE.ensure_ready()


def _sanitize_value(val: Any) -> Any:
    if isinstance(val, float):
        return None if (math.isnan(val) or math.isinf(val)) else round(val, 6)
    if isinstance(val, dict):
        return {k: _sanitize_value(v) for k, v in val.items()}
    if isinstance(val, list):
        return [_sanitize_value(v) for v in val]
    return val


def _intent_title(intent: str) -> str:
    return DOMAIN_PALETTE.get(intent, {}).get("title", intent)


def segment_highlights(text: str, query: str) -> list[dict[str, Any]]:
    """Split text into safe highlighted and plain spans using HIGHLIGHT_STOPWORDS rules."""
    if not text:
        return []
    words = re.findall(r"\b[A-Za-z0-9_-]{3,}\b", query.lower()) if query else []
    terms = {w for w in words if w not in HIGHLIGHT_STOPWORDS}
    if not terms:
        return [{"text": text, "highlighted": False}]

    sorted_terms = sorted(terms, key=len, reverse=True)
    pattern = re.compile(r"\b(" + "|".join(re.escape(t) for t in sorted_terms) + r")\b", re.IGNORECASE)

    segments: list[dict[str, Any]] = []
    last = 0
    for match in pattern.finditer(text):
        if match.start() > last:
            segments.append({"text": text[last:match.start()], "highlighted": False})
        segments.append({"text": match.group(0), "highlighted": True})
        last = match.end()
    if last < len(text):
        segments.append({"text": text[last:], "highlighted": False})
    return segments


def get_health_payload() -> dict[str, Any]:
    _STATE.ensure_ready()
    n_faqs = sum(1 for d in _STATE.documents if d["id"].startswith("faq_") or d["source"] == "faq.json")
    n_notices = sum(1 for d in _STATE.documents if d["id"].startswith("notice_") or d["source"] == "notices.json")
    return {
        "status": "ok",
        "documents_loaded": len(_STATE.documents),
        "faqs": n_faqs,
        "notices": n_notices,
        "intents": len(INTENTS),
        "defaults": {
            "top_k": 3,
            "cosine_threshold": float(RETRIEVAL_THRESHOLD),
            "intent_threshold": float(INTENT_THRESHOLD),
        },
    }


def _to_doc_card(doc: dict[str, Any], score: float, query: str) -> dict[str, Any]:
    return {
        "id": doc["id"],
        "intent": doc["intent"],
        "intent_label": _intent_title(doc["intent"]),
        "question": doc["question"],
        "answer": doc["answer"],
        "answer_segments": segment_highlights(doc["answer"], query),
        "source": doc["source"],
        "date": _STATE.notice_dates.get(doc["id"]) or None,
        "score": round(float(score), 6),
        "match_label": match_label(float(score)),
    }


def handle_chat(
    query: str,
    top_k: int = 3,
    threshold: float = RETRIEVAL_THRESHOLD,
    intent_threshold: float | None = INTENT_THRESHOLD,
    include_inspector: bool = True,
) -> dict[str, Any]:
    _STATE.ensure_ready()
    retriever = _get_retriever()

    start = time.perf_counter()
    results = retrieve(
        query,
        top_k=top_k,
        threshold=threshold,
        intent_threshold=intent_threshold,
    )
    intent, confidence = classify_intent(query)
    latency_ms = round((time.perf_counter() - start) * 1000.0, 3)

    ranked_char = retriever.rank(query)
    top1_cosine = float(ranked_char[0][1]) if ranked_char else 0.0
    cosine_passed = bool(ranked_char and (threshold < 0 or (top1_cosine > 0.0 and top1_cosine >= threshold)))
    intent_passed = True if intent_threshold is None else (float(confidence) >= float(intent_threshold))

    abstained = len(results) == 0
    # Never route an abstained query to a classifier-guessed office contact.
    office = None if abstained else office_for_intent(intent)

    result_cards = [_to_doc_card(doc, score, query) for doc, score in results]

    explain_top1: list[dict[str, Any]] = []
    intent_probs: list[dict[str, Any]] = []
    comparison: dict[str, Any] | None = None

    if include_inspector:
        target_doc_id = results[0][0]["id"] if results else (ranked_char[0][0]["id"] if ranked_char else None)
        if target_doc_id:
            explain_top1 = [
                {"feature": feat, "contribution": round(float(val), 6)}
                for feat, val in retriever.explain(query, target_doc_id, top_n=10)
            ]

        intent_probs = [
            {
                "intent": intent_name,
                "label": _intent_title(intent_name),
                "probability": round(float(prob), 6),
            }
            for intent_name, prob in get_intent_ranking(query, top_n=len(INTENTS))
        ]

        word_ranked = _STATE.word_retriever.rank(query)[:3] if _STATE.word_retriever else []
        bm25_ranked = _STATE.bm25_retriever.rank(query)[:3] if _STATE.bm25_retriever else []
        comparison = {
            "char_wb": [
                {
                    "id": doc["id"],
                    "question": doc["question"],
                    "intent": doc["intent"],
                    "score": round(float(score), 6),
                }
                for doc, score in ranked_char[:3]
            ],
            "word_tfidf": [
                {
                    "id": doc["id"],
                    "question": doc["question"],
                    "intent": doc["intent"],
                    "score": round(float(score), 6),
                }
                for doc, score in word_ranked
            ],
            "bm25": [
                {
                    "id": doc["id"],
                    "question": doc["question"],
                    "intent": doc["intent"],
                    "score": round(float(score), 6),
                }
                for doc, score in bm25_ranked
            ],
        }

    return {
        "query": query,
        "abstained": abstained,
        "abstention_message": ABSTENTION_MESSAGE if abstained else None,
        "is_non_english": is_non_english_query(query),
        "intent": intent,
        "intent_label": _intent_title(intent),
        "intent_confidence": round(float(confidence), 6),
        "latency_ms": latency_ms,
        "gate_details": {
            "top1_cosine": round(top1_cosine, 6),
            "cosine_threshold": round(float(threshold), 6),
            "cosine_passed": cosine_passed,
            "intent_confidence": round(float(confidence), 6),
            "intent_threshold": round(float(intent_threshold), 6) if intent_threshold is not None else None,
            "intent_passed": intent_passed,
        },
        "office": office,
        "results": result_cards,
        "explain_top1": explain_top1,
        "intent_probs": intent_probs,
        "comparison": comparison,
    }


def _select_stress_cases(preset: str, custom_queries: list[str]) -> list[dict[str, str]]:
    if preset == "custom":
        cleaned = [q.strip() for q in custom_queries if isinstance(q, str) and q.strip()][:50]
        return [
            {
                "id": f"custom_{idx:02d}",
                "type": "custom",
                "query": q,
                "expected_intent": "",
                "expected_doc_id": "",
            }
            for idx, q in enumerate(cleaned, start=1)
        ]

    by_id = {row["id"]: row for row in _STATE.test_queries}
    if preset == "demo_6":
        return [by_id[qid] for qid in DEMO_6_IDS if qid in by_id]

    if preset == "balanced_16":
        picked: list[dict[str, str]] = []
        for qtype in ("normal", "paraphrase", "typo", "out_of_corpus"):
            matches = [row for row in _STATE.test_queries if row["type"] == qtype][:4]
            picked.extend(matches)
        return picked

    return list(_STATE.test_queries)


def run_stress_test(
    preset: str = "demo_6",
    custom_queries: list[str] | None = None,
    threshold: float = RETRIEVAL_THRESHOLD,
    intent_threshold: float | None = INTENT_THRESHOLD,
    top_k: int = 3,
) -> dict[str, Any]:
    _STATE.ensure_ready()
    retriever = _get_retriever()
    cases = _select_stress_cases(preset, custom_queries or [])

    rows: list[dict[str, Any]] = []
    answered = 0
    abstained_count = 0
    in_corpus_total = 0
    ooc_total = 0
    top1_correct = 0
    top3_delivered = 0
    ooc_rejected = 0
    ooc_leaked = 0
    false_abstentions = 0
    latencies: list[float] = []

    for case in cases:
        query = case["query"]
        qtype = case.get("type", "custom")
        expected_doc = (case.get("expected_doc_id") or "").strip() or None
        expected_intent = (case.get("expected_intent") or "").strip() or None

        start = time.perf_counter()
        results = retrieve(
            query,
            top_k=top_k,
            threshold=threshold,
            intent_threshold=intent_threshold,
        )
        pred_intent, intent_conf = classify_intent(query)
        elapsed_ms = round((time.perf_counter() - start) * 1000.0, 3)
        latencies.append(elapsed_ms)

        ranked = retriever.rank(query)
        top1_cosine = round(float(ranked[0][1]), 6) if ranked else 0.0
        abstained = len(results) == 0
        top1_doc_id = results[0][0]["id"] if results else None
        result_ids = [doc["id"] for doc, _ in results]

        if abstained:
            abstained_count += 1
        else:
            answered += 1

        if qtype == "out_of_corpus":
            ooc_total += 1
            if abstained:
                ooc_rejected += 1
                status = "ooc_rejected"
            else:
                ooc_leaked += 1
                status = "ooc_leaked"
        elif expected_doc is not None:
            in_corpus_total += 1
            if abstained:
                false_abstentions += 1
                status = "false_abstain"
            elif top1_doc_id == expected_doc:
                top1_correct += 1
                top3_delivered += 1
                status = "top1_pass"
            elif expected_doc in result_ids:
                top3_delivered += 1
                status = "top3_rescue"
            else:
                status = "wrong_answer"
        else:
            status = "abstained" if abstained else "answered"

        rows.append(
            {
                "query_id": case["id"],
                "query_type": qtype,
                "query": query,
                "expected_doc_id": expected_doc,
                "expected_intent": expected_intent,
                "pred_intent": pred_intent,
                "intent_confidence": round(float(intent_conf), 6),
                "top1_doc_id": top1_doc_id,
                "top1_cosine": top1_cosine,
                "abstained": abstained,
                "status": status,
                "latency_ms": elapsed_ms,
            }
        )

    mean_latency = round(sum(latencies) / len(latencies), 3) if latencies else 0.0
    return {
        "preset": preset,
        "threshold": float(threshold),
        "intent_threshold": float(intent_threshold) if intent_threshold is not None else None,
        "summary": {
            "total": len(rows),
            "answered": answered,
            "abstained": abstained_count,
            "in_corpus_total": in_corpus_total,
            "ooc_total": ooc_total,
            "top1_correct": top1_correct,
            "top3_delivered": top3_delivered,
            "ooc_rejected": ooc_rejected,
            "ooc_leaked": ooc_leaked,
            "false_abstentions": false_abstentions,
            "mean_latency_ms": mean_latency,
        },
        "rows": rows,
    }


def list_documents_payload(
    intent: str | None = None,
    source: str | None = None,
    q: str | None = None,
) -> dict[str, Any]:
    _STATE.ensure_ready()
    needle = q.strip().lower() if q else ""

    filtered: list[dict[str, Any]] = []
    for doc in _STATE.documents:
        if intent and doc["intent"] != intent:
            continue
        if source and doc["source"] != source:
            continue
        if needle:
            haystack = f"{doc['id']} {doc['question']} {doc['answer']}".lower()
            if needle not in haystack:
                continue
        filtered.append(
            {
                "id": doc["id"],
                "intent": doc["intent"],
                "intent_label": _intent_title(doc["intent"]),
                "question": doc["question"],
                "answer": doc["answer"],
                "source": doc["source"],
                "date": _STATE.notice_dates.get(doc["id"]) or None,
                "office": office_for_intent(doc["intent"]),
            }
        )

    catalog = []
    for item in get_domain_catalog(_STATE.documents):
        reg = OFFICE_REGISTRY[item["intent"]]
        catalog.append(
            {
                "intent": item["intent"],
                "title": item["title"],
                "desc": item["desc"],
                "office_name": reg["name"],
                "office_contact": reg["contact"],
                "office_role": reg["role"],
                "office_evidence": reg["evidence"],
                "total_count": item["total_count"],
                "faq_count": item["faq_count"],
                "notice_count": item["notice_count"],
            }
        )

    return {
        "total": len(filtered),
        "documents": filtered,
        "catalog": catalog,
    }


def get_document_by_id(doc_id: str) -> dict[str, Any] | None:
    _STATE.ensure_ready()
    doc = _STATE.docs_by_id.get(doc_id)
    if doc is None:
        return None
    return {
        "id": doc["id"],
        "intent": doc["intent"],
        "intent_label": _intent_title(doc["intent"]),
        "question": doc["question"],
        "answer": doc["answer"],
        "source": doc["source"],
        "date": _STATE.notice_dates.get(doc["id"]) or None,
        "office": office_for_intent(doc["intent"]),
    }


def _read_csv_records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    import pandas as pd

    df = pd.read_csv(path)
    records = df.to_dict(orient="records")
    return [_sanitize_value(rec) for rec in records]


def _build_confusion_matrix(per_query_path: Path) -> dict[str, Any] | None:
    if not per_query_path.exists():
        return None
    with per_query_path.open(newline="", encoding="utf-8") as fh:
        rows = [row for row in csv.DictReader(fh) if row.get("type") != "out_of_corpus"]

    idx_map = {label: i for i, label in enumerate(INTENTS)}
    n = len(INTENTS)
    matrix = [[0 for _ in range(n)] for _ in range(n)]
    misclassified: list[dict[str, Any]] = []
    correct = 0

    for row in rows:
        exp = row.get("expected_intent", "")
        pred = row.get("pred_intent", "")
        if exp in idx_map and pred in idx_map:
            matrix[idx_map[exp]][idx_map[pred]] += 1
            if exp == pred:
                correct += 1
            else:
                misclassified.append(
                    {
                        "query_id": row.get("query_id", ""),
                        "query_type": row.get("type", ""),
                        "query": row.get("query", ""),
                        "expected_intent": exp,
                        "expected_label": _intent_title(exp),
                        "pred_intent": pred,
                        "pred_label": _intent_title(pred),
                        "intent_conf": round(float(row.get("intent_conf") or 0.0), 4),
                    }
                )

    total = len(rows)
    return {
        "labels": list(INTENTS),
        "display_labels": [SHORT_INTENT_LABELS[i] for i in INTENTS],
        "matrix": matrix,
        "correct": correct,
        "total": total,
        "accuracy": round(correct / total, 6) if total else 0.0,
        "misclassified": misclassified,
    }


def get_analytics_payload(results_dir: Path | None = None) -> dict[str, Any]:
    base = results_dir or (PROJECT_ROOT / "experiments" / "results")
    kpis = _sanitize_value(load_dashboard_kpis(base))

    manifest_path = base / "report_verification_manifest.json"
    manifest: dict[str, Any] = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    sweep_rows = _read_csv_records(base / "dev" / "E2" / "sublinear_tf" / "threshold_sweep.csv")
    chosen_threshold = None
    if sweep_rows:
        candidates = [r for r in sweep_rows if (r.get("ooc_rejection") or 0.0) >= 0.8]
        best_row = max(candidates or sweep_rows, key=lambda r: float(r.get("balanced_e2e") or 0.0))
        chosen_threshold = best_row.get("threshold")

    dev_ablations: dict[str, list[dict[str, Any]]] = {}
    for exp_id in ("E0", "E1", "E2", "E3", "E4", "E5", "E7"):
        dev_ablations[exp_id] = _read_csv_records(base / "dev" / f"ablation_{exp_id}_compare.csv")

    return {
        "kpis": kpis,
        "manifest": manifest,
        "midterm_summary": _read_csv_records(base / "midterm-sample" / "summary.csv"),
        "dual_gate_ablation": _read_csv_records(base / "midterm-sample" / "ablation.csv"),
        "confusion_matrix": _build_confusion_matrix(base / "midterm-sample" / "per_query.csv"),
        "business_summary": _read_csv_records(base / "business" / "business_summary.csv"),
        "cost_sensitivity": _read_csv_records(base / "business" / "cost_sensitivity.csv"),
        "per_intent_business": _read_csv_records(base / "business" / "per_intent_business.csv"),
        "noise_curve": _read_csv_records(base / "dev" / "noise_curve.csv"),
        "intent_cv": _read_csv_records(base / "dev" / "intent_cv.csv"),
        "threshold_sweep": sweep_rows,
        "chosen_threshold": chosen_threshold,
        "dev_ablations": dev_ablations,
    }


def save_feedback(query: str, doc_id: str, helpful: bool, log_path: Path | None = None) -> Path:
    return record_feedback(query, doc_id, helpful, log_path=log_path)
