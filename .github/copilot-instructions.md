# Project Memory

This file tracks the history of tasks, decisions, and current state of the Sentra project to provide context for GitHub Copilot.

## Last Updated: 2026-02-11

## Current State
- `parse_auth_log.py` supports advanced adversarial signal detection, compliance mapping, and Pydantic-validated v1 signals.
- `ai_engine.py` provides centralized AI services with confidence scoring and model drift logging.
- `qre.py` (Query Routing Engine) handles intent-based routing to ClickHouse/Elastic/VectorDB.
- `schema.py` formalizes the v1 Signal Entity Model (User, Host, Session, Process, IP).

## Workflow & Constraints
- Do not commit or push code changes (check-in) unless explicitly instructed by the user.
- **Strategic Alignment**: Follow the 8-phase Master Roadmap ([docs/ROADMAP.md](docs/ROADMAP.md)).
- **Execution Timing**: Transitioning to **Quarter 2 (Query Layer)**.

## Recent Changes
- Implemented **Signal Schema v1** using Pydantic.
- Refactored `ai_engine.py` for LLM provider abstraction, confidence scoring, and usage tracking.
- Created `qre.py` and `storage.py` to establish the multi-engine intelligence layer.
- Updated `parse_auth_log.py` to utilize the new schema and engine architectures.

## TODO / Next Steps
- **Q2 Priority**: Deepen the **Query Routing Engine (QRE)** with LLM classification and compound query decomposition.
- **Analytic Scaling**: Map signals to ClickHouse schemas and implement analytical aggregates.
- **Persistence**: Finalize ClickHouse/Elastic integrations.
- **Hardening**: Add token budget control and finalize Signal Schema v1 as part of Phase 0.
