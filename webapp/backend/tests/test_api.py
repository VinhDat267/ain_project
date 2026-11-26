"""Integration tests for the Project 12 FastAPI backend."""
from __future__ import annotations

import json
import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from starter.ui_helpers import FEEDBACK_LOG  # noqa: E402
from webapp.backend.main import app  # noqa: E402
from webapp.backend import service  # noqa: E402


@pytest.fixture(scope="module")
def client() -> TestClient:
    with TestClient(app) as tc:
        yield tc


def test_health_and_openapi_docs(client: TestClient) -> None:
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["documents_loaded"] == 112
    assert body["faqs"] == 84
    assert body["notices"] == 28
    assert body["intents"] == 7
    assert body["defaults"]["cosine_threshold"] == pytest.approx(0.15)
    assert body["defaults"]["intent_threshold"] == pytest.approx(0.34)

    docs_resp = client.get("/docs")
    assert docs_resp.status_code == 200


def test_chat_normal_query_and_inspector_trace(client: TestClient) -> None:
    resp = client.post("/api/chat", json={"query": "When is tuition due for the semester?"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["abstained"] is False
    assert data["abstention_message"] is None
    assert data["is_non_english"] is False
    assert data["intent"] == "tuition"
    assert data["office"] is not None
    assert data["office"]["name"] == "Bursar's Office"
    assert len(data["results"]) == 3
    assert data["results"][0]["id"] == "faq_tuition_01"
    assert data["results"][0]["match_label"] == "Strong match"
    assert any(seg["highlighted"] for seg in data["results"][0]["answer_segments"])

    assert len(data["explain_top1"]) > 0
    explain_sum = sum(item["contribution"] for item in data["explain_top1"])
    assert explain_sum > 0.0
    assert explain_sum <= data["results"][0]["score"] + 1e-4

    assert len(data["intent_probs"]) == 7
    assert sum(item["probability"] for item in data["intent_probs"]) == pytest.approx(1.0, abs=1e-3)

    assert data["comparison"] is not None
    assert len(data["comparison"]["char_wb"]) == 3
    assert len(data["comparison"]["word_tfidf"]) == 3
    assert len(data["comparison"]["bm25"]) == 3


def test_chat_typo_query_resolves_cleanly(client: TestClient) -> None:
    resp = client.post("/api/chat", json={"query": "Why can't I conncet to the campus Wi-Fi network?"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["abstained"] is False
    assert data["results"][0]["id"] == "faq_technical_support_02"
    assert data["intent"] == "technical_support"


def test_chat_ooc_abstains_and_never_routes_to_office(client: TestClient) -> None:
    resp = client.post("/api/chat", json={"query": "Can I rent a kayak from the campus recreation center?"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["abstained"] is True
    assert data["abstention_message"] == "Information not found — please contact the administrative office."
    assert data["office"] is None
    assert data["results"] == []
    assert data["gate_details"]["intent_passed"] is False


def test_chat_threshold_override_changes_abstention(client: TestClient) -> None:
    ooc_q = "Can I rent a kayak from the campus recreation center?"
    relaxed = client.post(
        "/api/chat",
        json={"query": ooc_q, "threshold": 0.0, "intent_threshold": 0.0, "top_k": 5},
    )
    assert relaxed.status_code == 200
    data = relaxed.json()
    assert data["abstained"] is False
    assert len(data["results"]) == 5


def test_chat_vietnamese_non_english_flag_and_validation(client: TestClient) -> None:
    vi_resp = client.post("/api/chat", json={"query": "Khi nào đóng học phí học kỳ này?"})
    assert vi_resp.status_code == 200
    assert vi_resp.json()["is_non_english"] is True

    blank_resp = client.post("/api/chat", json={"query": "   "})
    assert blank_resp.status_code == 422


def test_stress_test_presets(client: TestClient) -> None:
    demo = client.post("/api/stress-test", json={"preset": "demo_6"})
    assert demo.status_code == 200
    demo_data = demo.json()
    assert demo_data["summary"]["total"] == 6
    assert demo_data["summary"]["ooc_rejected"] == 1
    assert demo_data["summary"]["ooc_leaked"] == 0

    bal = client.post("/api/stress-test", json={"preset": "balanced_16"})
    assert bal.status_code == 200
    assert bal.json()["summary"]["total"] == 16

    custom = client.post(
        "/api/stress-test",
        json={
            "preset": "custom",
            "custom_queries": ["When is tuition due?", "Can I rent a kayak from the gym?"],
        },
    )
    assert custom.status_code == 200
    assert custom.json()["summary"]["total"] == 2


def test_documents_endpoints(client: TestClient) -> None:
    all_docs = client.get("/api/documents")
    assert all_docs.status_code == 200
    payload = all_docs.json()
    assert payload["total"] == 112
    assert len(payload["catalog"]) == 7

    notices = client.get("/api/documents", params={"source": "notices.json", "intent": "exam"})
    assert notices.status_code == 200
    assert notices.json()["total"] == 4
    assert all(d["date"] is not None for d in notices.json()["documents"])

    search = client.get("/api/documents", params={"q": "transcript"})
    assert search.status_code == 200
    assert search.json()["total"] >= 1

    single = client.get("/api/documents/faq_tuition_01")
    assert single.status_code == 200
    assert single.json()["intent"] == "tuition"

    missing = client.get("/api/documents/nonexistent_doc_id")
    assert missing.status_code == 404


def test_analytics_matches_ground_truth(client: TestClient) -> None:
    resp = client.get("/api/analytics")
    assert resp.status_code == 200
    data = resp.json()

    kpis = data["kpis"]
    assert kpis["top3_rescue_rate"] == pytest.approx(0.9619, abs=1e-3)
    assert kpis["raw_hit3"] == pytest.approx(0.9810, abs=1e-3)
    assert kpis["ooc_rejection_rate"] == pytest.approx(1.0, abs=1e-4)
    assert kpis["intent_correct"] == 102
    dev = data["dev_split"]
    assert (dev["ooc_refused"], dev["ooc_queries"]) == (12, 20)
    assert (dev["e2e_count"], dev["total_queries"]) == (111, 146)

    cm = data["confusion_matrix"]
    assert cm["total"] == 105
    assert cm["correct"] == 102
    assert sum(sum(row) for row in cm["matrix"]) == 105
    assert len(cm["misclassified"]) == 3

    assert len(data["noise_curve"]) == 16
    assert len(data["intent_cv"]) == 9
    assert len(data["threshold_sweep"]) == 101
    assert data["chosen_threshold"] == pytest.approx(0.33, abs=1e-3)
    assert len(data["dual_gate_ablation"]) == 4
    assert len(data["cost_sensitivity"]) == 4


def test_feedback_endpoint_isolated(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    isolated_log = tmp_path / "feedback.jsonl"
    monkeypatch.setattr(
        service,
        "save_feedback",
        lambda q, d, h: service.record_feedback(q, d, h, log_path=isolated_log),
    )
    had_prod_log = FEEDBACK_LOG.exists()

    resp = client.post(
        "/api/feedback",
        json={"query": "When is tuition due?", "doc_id": "faq_tuition_01", "helpful": True},
    )
    assert resp.status_code == 200
    assert resp.json()["saved"] is True
    assert isolated_log.exists()
    entry = json.loads(isolated_log.read_text(encoding="utf-8").strip())
    assert entry["top_doc_id"] == "faq_tuition_01"
    assert entry["helpful"] is True
    if not had_prod_log:
        assert not FEEDBACK_LOG.exists()
