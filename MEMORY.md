# Project Memory

This file tracks the history of tasks, decisions, and current state of the Sentra project to provide context for GitHub Copilot.

## Last Updated: 2026-02-11

## Current State
- `parse_auth_log.py` supports advanced adversarial signal detection, compliance mapping, and Pydantic-validated v1 signals.
- **AI-Native Infrastructure (Quarter 2 - Query Layer)**:
    - **Query Routing Engine (QRE)**: Implemented in `src/qre.py` with intent classification and compound query decomposition.
    - **Multi-Engine Storage**: Implemented `src/storage.py` with ingestion and query abstractions for **ClickHouse** and **Elastic**.
    - **Analytic Scaling**: Defined ClickHouse schemas (`src/db_setup.sql`) and materialized views for security metrics.
    - **Persistence**: Integrated ClickHouse/Elastic ingestion into the main parsing pipeline.
    - **Streaming Foundation**: Created `src/stream_processor.py` for real-time signal processing.
    - **Query UX**: Launched `src/query_shell.py` for demonstrating intent-based routing.

## Recent Changes
- Established Quarter 2 Infrastructure with `docker-compose.yml`.
- Created `src/db_setup.sql` for high-throughput signal storage.
- Refactored `src/storage.py` to move beyond mocks into specific engine ingestion logic.
- Implemented `QueryDecomposer` in `src/qre.py` to handle multi-part security questions.
- Integrated storage ingestion into `src/parse_auth_log.py`.
- Created `src/query_shell.py` as the initial user interface for the QRE.

## TODO / Next Steps
- **Q2 Hardening**:
    - Implement the actual `requests` based communication in `storage.py` (pending Docker deployment).
    - Add cost estimation logic to the QRE (e.g., predicted Elastic vs ClickHouse cost).
- **SOAR Transition (Q3 Preview)**:
    - Begin mapping Playbook DSL as per `docs/ROADMAP.md`.
- **Identity Enrichment**: Integrate LDAP/AzureAD mapping into the `schema.py` and signal factory.
    - Map `SecuritySignal` to ClickHouse analytical tables.
- **Streaming Migration**: Begin implementing the persistent Kafka/Flink consumer to replace the batch parser.
- **UX Foundation**: Develop the "Query UI" mockups or a lean CLI for the QRE.
