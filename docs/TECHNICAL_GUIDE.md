# Sentra Technical Documentation (Q2 Update)

Sentra is an AI-native security control plane designed to convert petabyte-scale telemetry into structured security narratives. This document covers the architecture and operations as of February 2026.

---

## 🏗️ System Architecture

Sentra follows a multi-engine intelligence architecture coordinated by a **Query Routing Engine (QRE)**.

### 1. AI Control Plane (`src/ai_engine.py`)
The centralized intelligence layer managing:
- **Narrative Generation**: Converting raw events into human-readable stories.
- **Provider Abstraction**: Swapping between OpenAI, Anthropic, or local models.
- **Vector Intelligence**: Similarity search via ChromaDB for pattern correlation.
- **Usage Tracking**: Real-time token and cost observability.

### 2. Query Routing Engine (`src/qre.py`)
An intelligent layer that classifies security questions and directs them to the optimal engine:
- **EXACT**: forensic search via **ElasticSearch**.
- **ANALYTICAL**: Large-scale trends via **ClickHouse**.
- **SIMILARITY**: Pattern matching via **VectorDB**.
- **DECISION**: Judgment calls via **LLM Consultation**.

### 3. Multi-Engine Storage (`src/storage.py`)
Abstracted storage interfaces for dual-speed processing:
- **Analytical Plane**: Flattened ClickHouse tables for high-velocity aggregates.
- **Forensic Plane**: Full JSON document indexing in ElasticSearch.

---

## 🧬 Data Model (Signal Schema v1)

All signals in Sentra are strongly typed via Pydantic (`src/schema.py`) to ensure cross-engine compatibility:
- **Entities**: User, Host, Process, Network, Session.
- **Metadata**: MITRE ATT&CK techniques, Compliance controls (SOC2/HIPAA), and AI confidence scores.

---

## 🚀 Operations

### Running the Control Plane (UI)
The Sentra Dashboard provides real-time signal visibility and QRE exploration.
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python3 -m streamlit run src/dashboard.py
```

### Running the Query Shell (CLI)
For rapid forensic investigation via terminal.
```bash
python3 src/query_shell.py --tenant-id <tenant_name>
```

### Signal Ingestion (Batch)
Currently supports parsing standard Linux `auth.log`.
```bash
python3 src/parse_auth_log.py --file /var/log/auth.log --tenant-id <tenant_name>
```

---

## 🛡️ Governance & Audit

- **Routing Audit**: Every QRE decision is logged to `qre_audit.json` for performance auditing.
- **Model Drift**: LLM consistency is logged to `model_drift.log`.
- **Cost Isolation**: Every AI request is tracked by `tenant_id` for accurate billing groundwork.

---

## 🗺️ Roadmap Reference
See [ROADMAP.md](docs/ROADMAP.md) for Phase 3 (SOAR Playbooks) and Streaming integration plans.
