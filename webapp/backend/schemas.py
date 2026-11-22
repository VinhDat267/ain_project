"""Pydantic schemas for the Campus Notice & FAQ Assistant FastAPI backend."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class HighlightSegment(BaseModel):
    text: str
    highlighted: bool


class ExplainFeature(BaseModel):
    feature: str
    contribution: float


class IntentProb(BaseModel):
    intent: str
    label: str
    probability: float


class OfficeContact(BaseModel):
    name: str
    role: str
    contact: str
    evidence: str


class RetrievedDocCard(BaseModel):
    id: str
    intent: str
    intent_label: str
    question: str
    answer: str
    answer_segments: list[HighlightSegment]
    source: str
    date: str | None = None
    score: float
    match_label: str


class ComparisonItem(BaseModel):
    id: str
    question: str
    intent: str
    score: float


class ComparisonResult(BaseModel):
    char_wb: list[ComparisonItem]
    word_tfidf: list[ComparisonItem]
    bm25: list[ComparisonItem]


class GateDetails(BaseModel):
    top1_cosine: float
    cosine_threshold: float
    cosine_passed: bool
    intent_confidence: float
    intent_threshold: float | None = None
    intent_passed: bool


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(3, ge=1, le=10)
    threshold: float = Field(0.15, ge=0.0, le=1.0)
    intent_threshold: float | None = Field(0.34, ge=0.0, le=1.0)
    include_inspector: bool = True

    @field_validator("query")
    @classmethod
    def _strip_non_empty(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Query must contain non-whitespace characters.")
        return cleaned


class ChatResponse(BaseModel):
    query: str
    abstained: bool
    abstention_message: str | None = None
    is_non_english: bool
    intent: str
    intent_label: str
    intent_confidence: float
    latency_ms: float
    gate_details: GateDetails
    office: OfficeContact | None = None
    results: list[RetrievedDocCard]
    explain_top1: list[ExplainFeature]
    intent_probs: list[IntentProb]
    comparison: ComparisonResult | None = None


class StressTestRequest(BaseModel):
    preset: Literal["demo_6", "balanced_16", "benchmark_120", "custom"] = "demo_6"
    custom_queries: list[str] = Field(default_factory=list, max_length=50)
    threshold: float = Field(0.15, ge=0.0, le=1.0)
    intent_threshold: float | None = Field(0.34, ge=0.0, le=1.0)
    top_k: int = Field(3, ge=1, le=10)


class StressTestRow(BaseModel):
    query_id: str
    query_type: str
    query: str
    expected_doc_id: str | None = None
    expected_intent: str | None = None
    pred_intent: str
    intent_confidence: float
    top1_doc_id: str | None = None
    top1_cosine: float
    abstained: bool
    status: str
    latency_ms: float


class StressTestSummary(BaseModel):
    total: int
    answered: int
    abstained: int
    in_corpus_total: int
    ooc_total: int
    top1_correct: int
    top3_delivered: int
    ooc_rejected: int
    ooc_leaked: int
    false_abstentions: int
    mean_latency_ms: float


class StressTestResponse(BaseModel):
    preset: str
    threshold: float
    intent_threshold: float | None = None
    summary: StressTestSummary
    rows: list[StressTestRow]


class FeedbackRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    doc_id: str = Field(..., min_length=1, max_length=128)
    helpful: bool

    @field_validator("query", "doc_id")
    @classmethod
    def _strip_fields(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Field must not be blank.")
        return cleaned


class FeedbackResponse(BaseModel):
    saved: bool
    doc_id: str
    helpful: bool


class DocumentItem(BaseModel):
    id: str
    intent: str
    intent_label: str
    question: str
    answer: str
    source: str
    date: str | None = None
    office: OfficeContact


class DomainCatalogItem(BaseModel):
    intent: str
    title: str
    desc: str
    office_name: str
    office_contact: str
    office_role: str
    office_evidence: str
    total_count: int
    faq_count: int
    notice_count: int


class DocumentsResponse(BaseModel):
    total: int
    documents: list[DocumentItem]
    catalog: list[DomainCatalogItem]


class HealthResponse(BaseModel):
    status: str
    documents_loaded: int
    faqs: int
    notices: int
    intents: int
    defaults: dict[str, Any]
