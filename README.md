# 🇬🇧 UK Finance Domain Intelligence System (DIS)

## 🚀 Live Deployment

- **API (Cloud Run):** https://finance-dis-521270728838.europe-west1.run.app
- **Web UI (Streamlit):** https://finance-dis-ui-521270728838.europe-west1.run.app

The system is fully deployed on Google Cloud Platform using a container-first workflow.

## Overview

The **UK Finance Domain Intelligence System (DIS)** is an end-to-end AI/ML project that enables **question answering over real UK financial documents** using **retrieval-augmented generation (RAG)**.

The system ingests public financial reports, retrieves relevant evidence via semantic search, and generates **grounded, citation-backed answers** using large language models.

This project is designed as a **hire-ready ML engineering portfolio project**, demonstrating modern practices in:

- Document intelligence
- Retrieval-augmented generation (RAG)
- API design
- Containerization
- CI/CD
- Cloud deployment

The focus is on **correctness, traceability, and production realism, with deployment to Google Cloud Platform (GCP)**.

---

## Objectives

- Build a finance-domain AI system grounded in **real UK financial data**
- Implement a **transparent and debuggable RAG pipeline**
- Prevent hallucinations via evidence-based generation
- Deploy a containerized service to the cloud
- Demonstrate ML engineering skills relevant to **ML / AI Engineer roles**

---

## Problem Statement

Financial documents such as annual reports and regulatory filings are:

- Long
- Dense
- Hard to query programmatically

This project solves the problem of **answering natural-language questions over financial documents** while ensuring:

- Answers are grounded in source documents
- Evidence is explicitly cited
- Uncertainty is acknowledged when information is missing

---

## Scope

### Domain
- UK finance and publicly listed companies

### Initial Document Types
- Annual reports
- Regulatory filings
- Investor disclosures

### Target Users
- Analysts
- Engineers
- Researchers
- Interview reviewers evaluating ML system design

---

# Data Sources

This directory defines all external financial document sources used by the system.

All ingested documents must:
- Be publicly available
- Be listed in configuration files
- Carry traceable metadata (company, year, source)

No document may be ingested unless it is declared here.

---

## System Architecture

### High-Level Architecture

```
User (Browser)
   ↓
Streamlit Web UI (Cloud Run)
   ↓
FastAPI RAG Service (Cloud Run)
   ↓
FAISS Vector Store (in-container)
   ↓
OpenAI LLM (Responses API)
```

### Retrieval-Augmented Generation (RAG) Flow

1. User submits a natural-language question via the UI or API
2. The query is embedded using a sentence-transformer model
3. FAISS performs top-K semantic similarity search
4. Retrieved chunks are filtered by metadata (company, fiscal year)
5. Evidence context is constructed from source documents
6. The LLM is prompted to answer **only from retrieved evidence**
7. The response is returned with cited document sources

If no sufficient evidence is found, the system responds with uncertainty rather than hallucinating.

---

## Core Components

### 1. Document Ingestion
- Parses raw financial documents into clean text
- Preserves metadata (company, year, section, source)

### 2. Chunking & Embeddings
- Documents are split into semantically meaningful chunks
- Embeddings generated for semantic search

### 3. Vector Store
- Stores embeddings for efficient similarity search
- Enables top-K retrieval per query

### 4. Retrieval-Augmented Generation (RAG)
- Retrieved chunks injected into LLM prompt
- Model instructed to answer **only from provided context**

### 5. API Layer
- FastAPI backend
- Clear input/output schemas
- Health endpoint for observability

### 6. Deployment
- Dockerized application
- CI/CD via GitHub Actions
- Deployed to cloud infrastructure

---

## Tech Stack

### Frontend
- Streamlit (Python)

### Backend
- FastAPI
- Python 3.12

### Retrieval & ML
- Sentence Transformers (MiniLM)
- FAISS (vector similarity search)
- Metadata-based filtering

### LLM
- OpenAI Responses API

### Infrastructure & DevOps
- Docker
- Google Cloud Run
- Google Artifact Registry
- GitHub Actions (CI/CD)

---

## API Endpoints

### Health Check

```
GET /health
```

Response:
```json
{
  "status": "OK"
}
```

### Query Endpoint

```
POST /query
```

Request:
```json
{
  "question": "What were the key risk factors mentioned in the latest annual report?"
}
```

Response:
```json
{
  "answer": "…",
  "citations": [
    {
      "source": "Annual Report 2023",
      "company": "Example PLC",
      "section": "Risk Factors",
      "snippet": "…"
    }
  ]
}
```

---

## Example Queries

- "Summarise the liquidity risks Barclays highlighted in 2024."
- "What economic crime risks did Lloyds Banking Group report?"
- "What funding risks were common across UK banks in 2024?"
- "Did the report mention cybersecurity-related risks?"

Each response is grounded in retrieved documents and includes explicit source citations.

---

## Deployment

The service is fully containerized using Docker and deployed to **Google Cloud Platform (GCP)**.

### Local Run
```bash
docker build -t uk-finance-dis .
docker run -p 8000:8000 uk-finance-dis
```

### Cloud Deployment (GCP)
The application is deployed on **GCP Cloud Run** using a container-first workflow:
- Docker images are built via GitHub Actions
- Images are pushed to **Google Artifact Registry**
- Cloud Run pulls and serves the image as a managed, autoscaling service

This setup provides a production-grade, serverless deployment model with minimal operational overhead.

---

## CI/CD Pipeline

This project includes an automated CI/CD pipeline that:

- Builds the Docker image on every push
- Runs health checks against the container
- Fails fast if the service is unhealthy
- Produces a deployable artifact per commit

This ensures reproducibility, reliability, and production readiness.

After passing all CI checks, the pipeline produces a deployable container artifact that is compatible with **Google Cloud Run**, enabling automated or manual promotion to production on GCP.

---

## Evaluation

A lightweight but explicit evaluation is included:

- A curated set of finance-domain questions
- Manual verification that:
  - Retrieved documents are relevant
  - Answers are grounded in cited evidence
- Known failure cases are documented

The focus is on system correctness rather than benchmark scores.

---

## Project Structure

```
uk-finance-domain-intelligence/
├── .github/
│   └── workflows/
│       └── ci.yml                # CI/CD pipeline (build, test, deploy)
│
├── api/                           # FastAPI backend (RAG service)
│   ├── main.py
│   ├── routes.py
│   └── services/
│       └── rag_service.py
│
├── ui/                            # Streamlit web UI
│   ├── app.py
│   └── requirements.txt
│
├── ingestion/                     # Document ingestion pipelines
├── processing/                    # Text cleaning & chunking
├── embedding/                     # Embedding generation logic
├── retrieval/                     # FAISS search, filters, evidence building
├── vectorstore/                   # Persisted FAISS indexes & metadata
├── llm/                           # LLM prompt & generation logic
│
├── data_sources/                  # Declared external document sources
├── data/                          # Raw / processed document data
│
├── tests/                         # Unit and integration tests
├── misc/                          # Experiments, scratch, notes (non-core)
│
├── .llm_cache/                    # Local LLM cache (ignored in production)
├── .dockerignore
├── .gitattributes
├── docker-compose.yml             # Local multi-service dev (API + UI)
├── Dockerfile                     # Production container build
├── requirements.txt               # Backend dependencies
│
├── OBSERVABILITY.md               # Logging & monitoring notes
└── README.md                      # Project documentation
```

---

## Design Decisions

Key design decisions are documented, including:

- **Cloud Provider:** Google Cloud Platform (GCP), chosen for its strong ML ecosystem, managed container services (Cloud Run), and relevance to ML/AI engineering roles.
- Choice of embedding model
- Choice of LLM
- Chunking strategy
- Retrieval parameters
- Deployment architecture

Trade-offs are explicitly explained where relevant.

---

## Future Extensions

After the core system is complete, potential extensions include:

- Additional UK financial document sources
- Re-ranking and hybrid retrieval
- Query decomposition
- Observability and monitoring
- Cost optimization

These are optional enhancements beyond the core system.

---

## Disclaimer

This project is for educational and portfolio purposes only and does not constitute financial advice.

---

## Author

Sanjit Jeevanand