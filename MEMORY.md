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
- Updated `deploy_fleet.py` to deploy the AI-native engine across the fleet.
- Added graceful fallbacks for systems without AI dependencies.
- Implemented `generate_recommendation` in `parse_auth_log.py` to provide actionable mitigation steps.

## TODO / Next Steps
- Implement real-time log tailing (using `tail -f` or a persistent watcher) to reduce alert latency from "batch" to "near real-time".
- Add support for application-level logs (Moodle, WordPress).
- Develop a lean web UI for exploring the signal timeline.
- Refine risk weighting based on historical fleet baseline.
