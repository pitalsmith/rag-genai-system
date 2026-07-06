# RAG GenAI System: Fraud Investigation Copilot

A production-ready Retrieval-Augmented Generation (RAG) system designed to assist fraud analysts by providing context-aware, cited answers from internal compliance documents.

## Architecture
- **Backend:** FastAPI (Python)
- **Frontend:** Next.js (TypeScript, Vercel AI SDK)
- **Database:** PostgreSQL + pgvector
- **Deployment:** Docker & IaC (Terraform)

## Features
- **Hybrid Search:** Combines vector similarity with keyword matching.
- **Reranking:** Implements cross-encoder reranking for precision.
- **Evaluation:** Automated testing pipeline using Ragas metrics.

## Getting Started
1. **Infrastructure:** `docker-compose up -d`
2. **Backend:** `cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload`
3. **Frontend:** `cd frontend && npm install && npm run dev`
# rag-genai-system
