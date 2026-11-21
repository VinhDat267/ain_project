"""FastAPI application serving the Project 12 REST API and built React SPA."""
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from webapp.backend import service
from webapp.backend.schemas import (
    ChatRequest,
    ChatResponse,
    DocumentItem,
    DocumentsResponse,
    FeedbackRequest,
    FeedbackResponse,
    HealthResponse,
    StressTestRequest,
    StressTestResponse,
)

FRONTEND_DIST_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    service.warmup()
    yield


app = FastAPI(
    title="HANU Campus Notice & FAQ Assistant API",
    version="1.0.0",
    description="Classical IR/NLP REST backend wrapping Project 12 TF-IDF, cosine dual-gate abstention, and experimental telemetry.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/api/health", response_model=HealthResponse)
def health() -> dict[str, Any]:
    return service.get_health_payload()


@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> dict[str, Any]:
    return service.handle_chat(
        query=payload.query,
        top_k=payload.top_k,
        threshold=payload.threshold,
        intent_threshold=payload.intent_threshold,
        include_inspector=payload.include_inspector,
    )


@app.post("/api/stress-test", response_model=StressTestResponse)
def stress_test(payload: StressTestRequest) -> dict[str, Any]:
    return service.run_stress_test(
        preset=payload.preset,
        custom_queries=payload.custom_queries,
        threshold=payload.threshold,
        intent_threshold=payload.intent_threshold,
        top_k=payload.top_k,
    )


@app.get("/api/documents", response_model=DocumentsResponse)
def list_documents(
    intent: str | None = Query(default=None),
    source: str | None = Query(default=None),
    q: str | None = Query(default=None),
) -> dict[str, Any]:
    return service.list_documents_payload(intent=intent, source=source, q=q)


@app.get("/api/documents/{doc_id}", response_model=DocumentItem)
def get_document(doc_id: str) -> dict[str, Any]:
    doc = service.get_document_by_id(doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")
    return doc


@app.get("/api/analytics")
def analytics() -> JSONResponse:
    return JSONResponse(content=service.get_analytics_payload())


@app.post("/api/feedback", response_model=FeedbackResponse)
def feedback(payload: FeedbackRequest) -> dict[str, Any]:
    service.save_feedback(payload.query, payload.doc_id, payload.helpful)
    return {
        "saved": True,
        "doc_id": payload.doc_id,
        "helpful": payload.helpful,
    }


if (FRONTEND_DIST_DIR / "assets").is_dir():
    app.mount(
        "/assets",
        StaticFiles(directory=str(FRONTEND_DIST_DIR / "assets")),
        name="spa-assets",
    )


@app.get("/", include_in_schema=False)
@app.get("/{full_path:path}", include_in_schema=False)
def serve_spa(full_path: str = ""):
    if full_path == "api" or full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found.")

    index_file = FRONTEND_DIST_DIR / "index.html"
    if not index_file.is_file():
        return JSONResponse(
            status_code=200,
            content={
                "message": "Backend API running. Build webapp/frontend (npm run build) to serve the web UI on /.",
                "docs": "/docs",
                "health": "/api/health",
            },
        )

    if full_path:
        dist_root = FRONTEND_DIST_DIR.resolve()
        candidate = (dist_root / full_path).resolve()
        if dist_root in candidate.parents and candidate.is_file():
            return FileResponse(str(candidate))

    return FileResponse(str(index_file))
