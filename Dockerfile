# Multi-stage build for Project 12 Standalone Web Application (FastAPI + React SPA)
FROM node:24-alpine AS frontend-builder

WORKDIR /frontend
COPY webapp/frontend/package.json webapp/frontend/package-lock.json ./
RUN npm ci
COPY webapp/frontend/ ./
RUN npm run build

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
COPY webapp/backend/requirements.txt ./webapp/backend/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -r webapp/backend/requirements.txt

COPY data ./data
COPY starter ./starter
COPY experiments/results ./experiments/results
COPY webapp/backend ./webapp/backend
COPY --from=frontend-builder /frontend/dist ./webapp/frontend/dist

RUN mkdir -p /app/output/feedback

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=3)"

CMD ["uvicorn", "webapp.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
