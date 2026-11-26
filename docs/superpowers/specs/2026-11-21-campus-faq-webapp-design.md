# Project 12 Standalone Web Application — Design Specification

Date: 2026-11-21
Status: Approved for execution (Approach A — FastAPI + React/TypeScript/Vite)
UI Language: English (with bilingual advisory when Vietnamese input is detected)

## 1. Intent, Goals, Non-Goals, and Anti-Goals

### Intent
Package **Project 12: HANU Campus Notice & FAQ Assistant** into a standalone, production-ready web application running cleanly alongside [starter/app.py](../../../starter/app.py) on port `8000` (local one-command launcher and multi-stage Docker container), preserving classical IR/NLP fidelity with zero LLM/API dependencies and 100% offline classroom capability.

### Goals
1. **Multi-Turn Conversational Q&A (`Assistant` view):** Student-first Q&A flow with `localStorage` session history, 8 representative starter prompts across all 4 query types (`normal`, `paraphrase`, `typo`, `out_of_corpus`), match-quality calibration (`Strong match` / `Possible match` / `Weak match`), safe keyword highlighting, attested contact routing (`OFFICE_REGISTRY`, strictly suppressed when abstained), helpfulness votes logged to `output/feedback/feedback.jsonl`, and Vietnamese input advisory.
2. **Inspector / Defense Mode & Stress-Test Lab (`InspectorPanel` + `Stress-Test` view):** Interactive dual-gate controls (`θ_sim`, `θ_intent`, `top_k`) with real-time re-evaluation, additive `explain()` feature attribution bars, 7-class intent probability distribution against the `θ_intent` gate, 3-way `char_wb` vs Word TF-IDF vs Okapi BM25 ranking comparison, plus batch defense presets (`demo_6`, `balanced_16`, `benchmark_120`, and custom lecturer prompts).
3. **Interactive Research & Analytics Dashboard (`Analytics` view):** Native accessible React SVG charts backed exclusively by `experiments/results/` CSVs and `report_verification_manifest.json` — KPI strip separating `Delivered Top-3` (`96.2%`, `101/105`) from `Raw Hit@3` (`98.1%`, `103/105`), Dual-Gate Ablation, 7×7 interactive Confusion Matrix with misclassified inspection, E3b Noise Curve (`k = 0..3`), E5b 5-Fold CV (`9` models mean ± std), E6 Threshold Sweep (`146` dev queries, `θ = 0.33`), E0–E7 dev ablations, and Business Cost Sensitivity (`1:1`, `3:1`, `5:1`, `10:1`) + per-intent resolution.
4. **Knowledge Archive (`Archive` view):** Instant filter/search over all `112` corpus documents (`84` FAQs + `28` notices), 7 corpus-attested contact points, and an accessible native `<dialog>` reader modal.
5. **1-Command Packaging:** `scripts/run_webapp.ps1` (single-command production and `-Dev` modes) + multi-stage `Dockerfile` + `docker-compose.yml` on port `8000`.

### Non-Goals & Anti-Goals
- **No LLMs, embeddings, or remote APIs:** Retrieval and intent classification remain 100% deterministic classical IR/NLP (`starter/student_core.py`, `starter/retrieval.py`, `starter/bm25.py`).
- **No external runtime CDNs:** Dealt fonts are self-hosted offline via `@fontsource/*` bundled by Vite into `webapp/frontend/dist/assets/*.woff2`.
- **No course-contract regressions:** Never modify `data/`, `tests/test_project_12_sanity.py`, root `requirements.txt`, `.github/workflows/project-12-tests.yml`, or mutate tracked `experiments/results/` files during tests.
- **No fabricated metadata or OOC office routing:** Never invent buildings/rooms/hours; never return a guessed office contact card when a query abstains.

---

## 2. Design System (`/design-taste-frontend` v2.5.1 + `modern-web-guidance`)

### Dealt Palette & Typography
- `palette cool-white-slate` ("Frost and slate") — An off-white paper ground (`#f7f9fa`), cool stone card surface (`#ecf0f2`), slate ink (`#1f3038`), and deep teal accent (`#0d7480`) provide glare-free legibility for student Q&A text and dense IR tables on classroom projectors while avoiding violet hues entirely.
- Type pairing `funnel` (`Funnel Display` weight `400` + `Funnel Sans` weights `400/500/600` + `DM Mono` weights `400/500`), bundled offline via `@fontsource/funnel-display`, `@fontsource/funnel-sans`, and `@fontsource/dm-mono`.
- Token block (generated verbatim by `start.mjs css --page software --palette cool-white-slate --type funnel --radius soft`):
  - `--p-bg: #f7f9fa`, `--p-surface: #ecf0f2`, `--p-ink: #1f3038`, `--p-muted: #5d6b72`
  - `--p-accent: #0d7480`, `--p-accent-ink: #ffffff`, `--p-action: #0d7480`, `--p-action-ink: #ffffff`
  - `--p-inv-bg: #1f3038`, `--p-inv-surface: #2c3c44`, `--p-inv-ink: #f7f9fa`, `--p-inv-muted: #9ea7ab`
  - `--r-sm: 8px`, `--r-md: 12px`, `--r-lg: 20px`, `--r-btn: 8px`, `--btn-h: 44px`, `--container: 1280px`
- **Topic Badge Palette (Strictly Non-Violet):** Uses distinct high-contrast hues within cobalt blue (`#1d4ed8`), emerald teal (`#047857`), crimson rose (`#be123c`), slate steel (`#334155`), warm amber (`#b45309`), deep teal (`#0d7480`), and ocean sky (`#0369a1`) — zero purple, indigo, or violet.

### Voice Card (`technical-dry`)
- **Voice:** `technical-dry`
- **Pairs:** exact, not cold; sure, not loud; dry only in empty states.
- **Person:** neutral system voice; active verb+object labels on every button (`Ask question`, `Run batch test`, `Inspect trace`, `Open document`, `Reset thresholds`).
- **House words:** dual-gate, cosine similarity, character n-gram, abstention, attested contact, synthetic corpus.
- **Never:** AI-slop praise words (*seamless, effortless, cutting-edge, powerful, robust, unlock, elevate*), exclamation marks in headings, or captions under charts/visuals.

### Modern Web Guidance Applied
- `responsive-table`: `.table-wrapper` with `container-type: inline-size`, sticky `thead`, and `@container (width < 600px)` stacked row cards.
- `tabs`: Primary views use semantic `<nav>` + `aria-current="page"`; secondary Inspector & Analytics panels use ARIA `tablist` (`role="tab"`, `aria-selected`, `::after` `2px` underline indicator, single row `overflow-x: auto`).
- `dialog`: Full document viewer uses native `<dialog>` + `showModal()`, `closedby="any"` + pointerdown/pointerup fallback, `dialog[open]` layout scoping, and `overscroll-behavior: contain`.
- `accessibility`: Skip link to `#main-content`, semantic landmarks (`<header>`, `<nav>`, `<main>`, `<aside>`), single `<h1>` per view, explicit `<label htmlFor>`, `:focus-visible`, `role="img"` + `<title>`/`aria-label` on informative SVGs, `aria-live="polite"`, and `lang="vi"` on the Vietnamese advisory clause.

---

## 3. Architecture Summary

- **Backend (`webapp/backend/`):** FastAPI (`main.py`), Pydantic schemas (`schemas.py`), pre-warmed IR service (`service.py`), isolated dependencies (`requirements.txt`), pytest suite (`tests/test_api.py`).
  - `GET /api/health`
  - `POST /api/chat`
  - `POST /api/stress-test`
  - `GET /api/documents`, `GET /api/documents/{doc_id}`
  - `GET /api/analytics`
  - `POST /api/feedback`
- **Frontend (`webapp/frontend/`):** React 18 + TypeScript + Vite SPA proxying `/api` in dev and statically served by FastAPI from `webapp/frontend/dist` in production on port `8000`.
- **Packaging:** `scripts/run_webapp.ps1`, `Dockerfile` (multi-stage Node 24 + Python 3.11-slim), `docker-compose.yml`, `.dockerignore`.
