# Project Memory

This file tracks the history of tasks, decisions, and current state of the Sentra project to provide context for GitHub Copilot.

## Last Updated: 2026-02-11

## Current State
- `parse_auth_log.py` supports advanced adversarial signal detection, compliance mapping, and Pydantic-validated v1 signals with **Identity Intelligence**.
- **AI-Native Infrastructure (Quarter 2 - Query Layer)**:
    - **Query Routing Engine (QRE)**: Implemented in `src/qre.py` with intent classification, compound query decomposition, and **Cost-Aware Routing**.
    - **Multi-Engine Storage**: Implemented `src/storage.py` with ingestion and query abstractions for **ClickHouse** and **Elastic**.
    - **Analytic Scaling**: Defined ClickHouse schemas (`src/db_setup.sql`) and materialized views for security metrics.
    - **Identity Intelligence**: Integrated `src/identity.py` (LDAP/AzureAD bridge) to resolve local usernames to organizational identities.
    - **SOAR Groundwork (Phase 3 Preview)**: Introduced `src/playbooks.py` and a **Playbook DSL** for automated security responses.
    - **Query UX**: Launched `src/query_shell.py` with cost-visibility for routing decisions.

## Recent Changes
- Implemented **Cost-Aware Routing** in `src/qre.py` and visualized costs in `src/query_shell.py`.
- Integrated **Identity Intelligence** to enrich signals with job roles and corporate emails.
- Defined the initial **SOAR Playbook DSL** and integrated playbook recommendations into the signal factory.
- Updated `src/schema.py` to support `UserEntity` extensions and `recommended_playbooks`.
- Established Quarter 2 Infrastructure with `docker-compose.yml` and `src/db_setup.sql`.
- **Q2 Hardening**: Implemented hybrid AI intent classification, health-aware routing fallback, and persistent decision audit logging in `qre.py`.
- **UI Launch**: Created `src/dashboard.py` providing a consolidated view of Signal Streams, QRE Explorations, and AI Governance.

## TODO / Next Steps
- **Q2 Finalization**:
    - Add Latency SLO tracking to routing decisions.
    - Implement real `requests` based communication in `storage.py`.
    - Map `SecuritySignal` to ClickHouse analytical tables.
- **Q3 Transition - SOAR Integration**:
    - Develop the **SOAR Connector Framework** for Jira/Slack/IAM APIs.
    - Implement human-approval gates for playbook execution.
- **Streaming Migration**: Transition batch parsing to a persistent Kafka/Flink pipeline.
- **UX Foundation**: Maintain and expand the **Sentra Control Plane** (Streamlit).
