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

