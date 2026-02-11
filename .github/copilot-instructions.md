# Project Memory

This file tracks the history of tasks, decisions, and current state of the Sentra project to provide context for GitHub Copilot.

## Last Updated: 2026-02-11

## Current State
- `parse_auth_log.py` supports advanced adversarial signal detection, identity intelligence, and Pydantic-validated v1 signals.
- `ai_engine.py` provides centralized AI services with confidence scoring and model drift logging.
- `qre.py` (Query Routing Engine) handles **cost-aware**, intent-based routing to ClickHouse/Elastic/VectorDB.
- `schema.py` formalizes the v1 Signal Entity Model with identity and playbook metadata.
- `playbooks.py` defines the **SOAR Playbook DSL** for Phase 3 readiness.

## Workflow & Constraints
- Do not commit or push code changes (check-in) unless explicitly instructed by the user.
- **Strategic Alignment**: Follow the 8-phase Master Roadmap ([docs/ROADMAP.md](docs/ROADMAP.md)).
- **Execution Timing**: Concluding Quarter 2 (Query Layer).

## Recent Changes
- Implemented **Cost-Aware Routing** and **Identity Intelligence**.
- Defined **SOAR Playbook DSL** and integrated recommendations into the signal pipeline.
- Created `qre.py`, `storage.py`, and `identity.py` to establish the multi-engine intelligence layer.
- Updated `parse_auth_log.py` to utilize the new schema, cost, and identity architectures.

## TODO / Next Steps
- **Q2 Priority**: Deepen the **Query Routing Engine (QRE)** with LLM classification and compound query decomposition.
- **Analytic Scaling**: Map signals to ClickHouse schemas and implement analytical aggregates.
- **Persistence**: Finalize ClickHouse/Elastic integrations.
- **Hardening**: Add token budget control and finalize Signal Schema v1 as part of Phase 0.
