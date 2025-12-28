# ---------- Stage 1: builder ----------
FROM python:3.12-slim AS builder

WORKDIR /app

ENV PIP_EXTRA_INDEX_URL=https://download.pytorch.org/whl/cpu
ENV HF_HOME=/models
ENV TRANSFORMERS_CACHE=/models
ENV SENTENCE_TRANSFORMERS_HOME=/models

# System deps
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Preload sentence-transformers model at build time into /models
RUN python - <<EOF
from sentence_transformers import SentenceTransformer
SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
EOF


# ---------- Stage 2: runtime ----------
FROM python:3.12-slim

ENV HF_HOME=/models
ENV TRANSFORMERS_CACHE=/models
ENV SENTENCE_TRANSFORMERS_HOME=/models
ENV TRANSFORMERS_OFFLINE=1
ENV HF_HUB_OFFLINE=1
ENV HF_HUB_DISABLE_TELEMETRY=1
ENV HF_DATASETS_OFFLINE=1

# Create non-root user
RUN useradd -m appuser

WORKDIR /app

# Copy Python runtime and preloaded models
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /models /models

COPY api/ api/
COPY retrieval/ retrieval/
COPY llm/ llm/
COPY data/embeddings /app/data/embeddings

# Permissions
RUN chown -R appuser:appuser /app /models

USER appuser

CMD uvicorn api.main:app \
  --host 0.0.0.0 \
  --port $PORT