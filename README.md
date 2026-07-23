# Enterprise RAG System with Role-Based Access Control (RBAC)

An enterprise-grade Retrieval-Augmented Generation (RAG) system featuring role-based access control, secure multi-format document ingestion, hybrid vector retrieval, safety guardrails, Streamlit UI, and automated evaluation.

---

## 📌 Implementation Task Plan & Roadmap

### Phase 0: Project Setup & Environment Configuration
- [x] **Step 0.1**: Initialize Project Directory Structure & Git Version Control
- [x] **Step 0.2**: Configure Virtual Environment & Dependencies (`requirements.txt`, `pyproject.toml`)
- [x] **Step 0.3**: Create Environment Variables Template & Local Config (`.env.template`, `.env`)
- [x] **Step 0.4**: Implement Application Settings & LLM/RBAC Configuration (`config/settings.py`, `config/llm_config.py`, `config/rbac_config.py`)
- [x] **Step 0.5**: Create Root Entrypoint & Base Modules (`main.py`)
- [x] **Step 0.6**: Create Docker & Container Orchestration (`Dockerfile`, `docker-compose.yml`, `.dockerignore`)

---

### Phase 1: Security, RBAC & Document Ingestion Pipeline
- [ ] **Step 1.1**: User Authentication & Role-Based Access Control (RBAC) Module
- [ ] **Step 1.2**: Multi-Format Document Parsers (PDF, DOCX, XLSX, TXT)
- [ ] **Step 1.3**: Metadata Extraction & Access Control Tagging
- [ ] **Step 1.4**: Context-Aware Document Chunking Strategy
- [ ] **Step 1.5**: Embedding Generation & Qdrant Collection Initialization
- [ ] **Step 1.6**: Batch Vector Ingestion Pipeline with RBAC Metadata

---

### Phase 2: Hybrid Retrieval & Re-ranking Engine
- [ ] **Step 2.1**: Dense Vector Search with RBAC Metadata Payload Filtering
- [ ] **Step 2.2**: Sparse BM25 Keyword Search Indexing & Retrieval
- [ ] **Step 2.3**: Reciprocal Rank Fusion (RRF) Hybrid Merger
- [ ] **Step 2.4**: Cross-Encoder Re-ranking Engine
- [ ] **Step 2.5**: Context Compressor & Prompt Payload Formatter

---

### Phase 3: Guardrails, Safety & LLM Generation Chain
- [ ] **Step 3.1**: Input PII Detection & Anonymization (Microsoft Presidio)
- [ ] **Step 3.2**: Input Prompt Injection & Content Safety Filtering
- [ ] **Step 3.3**: Groq / Azure OpenAI LLM Chain Integration
- [ ] **Step 3.4**: Output PII Deanonymization & Response Sanitization
- [ ] **Step 3.5**: Hallucination & Faithfulness Verification Guard

---

### Phase 4: Streamlit UI & Interactive Chat Interface
- [ ] **Step 4.1**: Role-based Login & Session Management UI
- [ ] **Step 4.2**: Document Ingestion & Management Portal
- [ ] **Step 4.3**: Interactive Chat Interface with Citation & Source Drawer
- [ ] **Step 4.4**: System Telemetry & Access Audit Dashboard

---

### Phase 5: Evaluation, Monitoring & End-to-End Testing
- [ ] **Step 5.1**: LangSmith Tracing & Observability Setup
- [ ] **Step 5.2**: Automated RAGAS Evaluation Framework (Faithfulness, Relevancy, Precision)
- [ ] **Step 5.3**: Unit & Integration Test Suite (`pytest`)
- [ ] **Step 5.4**: End-to-End System Verification & Deployment Documentation

---

## 🛠️ Quick Start

```bash
# 1. Clone repository
git clone https://github.com/MaahmoudAbdelghany/Rag_For_Enterprise.git
cd Rag_For_Enterprise

# 2. Copy environment template and set your API keys
cp .env.template .env

# 3. Launch via Docker Compose
docker compose up --build
```
