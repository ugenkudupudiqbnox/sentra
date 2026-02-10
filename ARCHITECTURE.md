```
                           ┌───────────────────────────┐
                           │     DATA COLLECTION       │
                           │ (Agents / Collectors)     │
                           └─────────────┬─────────────┘
                                         │
                                      Raw Logs
                                         │
┌──────────────────────────┐   ┌─────────▼──────────┐   ┌─────────────────────┐
│   STREAM NORM & ENRICH   │   │ AI SIGNAL ENGINEER │   │ MODEL REPOSITORIES  │
│ (Flink / Kafka Streams)  │   │ (LLM + embeddings) │   │ (Threat + TTP + ML) │
└────────────┬─────────────┘   └────────────┬───────┘   └─────────────┬───────┘
             │                              │                         │
             │                            Signals (Enriched + Vectorized)
             ▼                              ▼                         ▼
┌──────────────────────────┐   ┌──────────────────────────┐   ┌──────────────────────┐
│ SIGNAL STORE (Vector DB) │   │ AI ANALYTICS LAYER       │   │   CONTROL RULES &    │
│(Pinecone/Milvus/Weaviate)│   │ (LLMs + Transformers)    │   │ POLICY ENGINES (DSL) │
└────────────┬─────────────┘   └──────────────┬───────────┘   └─────────────┬────────┘
             │                                │                             │
             ▼                                ▼                             ▼
┌──────────────────────────┐   ┌──────────────────────────┐   ┌──────────────────────┐
│ PROBABILISTIC SCORING    │   │ SECURITY NARRATIVE GEN.  │   │ ACTION / RESPONSE    │
│ (Risk Models + AI)       │   │ (LLM summarization)      │   │ (SOAR + RL policies) │
└────────────┬─────────────┘   └──────────────┬───────────┘   └─────────────┬────────┘
             │                                │                             │
             ▼                                ▼                             ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         ANALYST & AUDITOR INTERFACE                          │
│  Dashboards / Readouts / Evidence Kits / Auditor-Ready Reports / Playbooks   │
└──────────────────────────────────────────────────────────────────────────────┘

```
---

## System Components (v0.4)

### 1. Signal Engine (`parse_auth_log.py`)
The heart of Sentra. It performs behavioral analysis on `/var/log/auth.log` by:
- **Normalization**: Parsing varied timestamp and log formats into standard events.
- **Aggregation**: Grouping events into 10-minute and 1-hour behavioral windows.
- **Enrichment (Phase 3)**: Mapping commands to **MITRE ATT&CK** tactics and **SOC2** controls.
- **Risk Scoring**: Applying a probabilistic model to evaluate behavior sensitivity.

### 2. Fleet Aggregator (`aggregate_weekly.py`)
Maintains a fleet-wide view by:
- Combining per-server signals into a unified executive summary.
- Calculating fleet-wide intent distributions.
- Applying **Analyst Overrides** (`overrides.json`) to resolve routine maintenance activity.

### 3. Notification Layer (`notify.py`)
The **Phase 4** outcome engine that:
- Filters signals for high-risk thresholds ($\ge 0.5$).
- Delivers priority alerts to Slack or Webhooks.
- Formats signals for human-first investigation.

### 4. Audit Evidence Utility (`generate_audit_bundle.py`)
Automates compliance readiness by gathering all narratives, decisions, and raw JSON signals into a single, timestamped zip archive for auditors.

