# Project Memory

This file tracks the history of tasks, decisions, and current state of the Sentra project to provide context for GitHub Copilot.

## Last Updated: 2026-02-11

## Current State
- `parse_auth_log.py` supports advanced adversarial signal detection and Phase 2/4 AI enrichment.
- **AI-Native Infrastructure (Phase 2)**:
    - Integrated **OpenAI API** for dynamic incident narratives and recommendations.
    - Integrated **ChromaDB** for signal vectorization and cross-fleet correlation.
    - Implemented `ai_engine.py` as a centralized service for LLM and Vector DB interactions.
- Phase 4 SOAR & Outcome Automation is complete:
    - AI-Recommended actions for every signal type.
    - Slack/Webhook notification framework (`notify.py`).
    - **SOAR Integration**: Pre-configured universal webhooks for platforms like **Shuffle** and **Tines**.
    - Justification and outcome tracking in aggregated reports.

## Recent Changes
- Implemented `ai_engine.py` using `openai` and `chromadb`.
- Refactored `parse_auth_log.py` to use `AIEngine` for enrichment and indexing.
- Defined three-tier enrichment strategy (Static, Dynamic, Behavioral) in documentation.
- Created `KAFKA_PLAYBOOK.md` outlining the high-throughput infrastructure required for PB-scale log ingestion.
- Created `FLINK_PLAYBOOK.md` documentation for real-time signal processing and windowed correlation at scale.
- **Three-Tier Storage Strategy**: Defined transition from local ChromaDB to a multi-tiered (Hot/Warm/Cold) distributed storage model.
- **Modular Architecture Refactor**: Formalized system boundaries into four core layers: Ingestion, Signal Abstraction, Narrative Generation, and Evaluation/Ground Truth.
- Updated `deploy_fleet.py` to deploy the AI-native engine across the fleet.

## TODO / Next Steps
- **Transition to Streaming Architecture**: Migrate from batch parsing (`parse_auth_log.py`) to a persistent Kafka/Flink pipeline for real-time signal logic.
- **Advanced Cross-Signal Correlation**: Implement logic in `ai_engine.py` to use ChromaDB similarity searches for linking disparate events into unified narratives.
- **Dynamic Enrichment Service**:
    - **Threat Intel**: Integrate IP reputation APIs (AbuseIPDB, VirusTotal) to enrich log signals.
    - **Identity Correlation**: Map local Unix usernames to organizational identities (LDAP/AzureAD).
    - **Asset Intelligence**: Inject server roles (e.g., "Production DB", "Edge Proxy") from a CMDB into every signal.
- **MITRE ATT&CK & SOC2 Mapping**: Automate the tagging of signals with specific TTPs and compliance controls for enhanced auditor evidence.
- **Analyst Decision Interface**: Develop a lean UI for exploring the signal timeline and managing `overrides.json` across the fleet.
- **Scale-Out AI Engine**: Decouple the embedding and narrative generation into a standalone microservice to support high-throughput log streams.
