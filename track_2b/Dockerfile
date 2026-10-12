# Multi-stage Dockerfile for RelayZero (Hack Apertus Track 2B)
# Hardened non-root air-gapped container

# Stage 1: Build Frontend Assets
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
COPY src/frontend/package*.json ./
RUN npm ci
COPY src/frontend/ ./
RUN npm run build

# Stage 2: Production Python Runtime
FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install minimal OS dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python backend dependencies
COPY src/backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy backend application source
COPY src/backend/ /app/track_2b/src/backend/
COPY data/ /app/track_2b/data/
COPY docs/ /app/track_2b/docs/
COPY technical_report.md /app/track_2b/technical_report.md
COPY RelayZero_Report.pdf /app/track_2b/RelayZero_Report.pdf

# Copy built frontend static files to dist
COPY --from=frontend-builder /app/frontend/dist /app/track_2b/src/frontend/dist

# Security hardening: Non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["python", "-m", "uvicorn", "track_2b.src.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
