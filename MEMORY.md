# Project Memory

This file tracks the history of tasks, decisions, and current state of the Sentra project to provide context for GitHub Copilot.

## Last Updated: 2026-02-11

## Current State
- `parse_auth_log.py` supports advanced adversarial signal detection and Phase 4 AI recommendations.
- Phase 4 SOAR & Outcome Automation is complete:
    - AI-Recommended actions for every signal type.
    - Slack/Webhook notification framework (`notify.py`).
    - **SOAR Integration**: Pre-configured universal webhooks for platforms like **Shuffle** and **Tines**.
    - Justification and outcome tracking in aggregated reports.
- Fleet deployment includes automated priority alerting for signals with risk scores ≥ 0.5.

## Recent Changes
- Implemented `generate_recommendation` in `parse_auth_log.py` to provide actionable mitigation steps.
- Created `notify.py` for ticketing and Slack/SOAR integration (Phase 4).
- Added dedicated `SOAR_INTEGRATION.md` guide for Shuffle and Tines.
- Updated `aggregate_weekly.py` to include "Priority Playbooks" and "Outcome/Justification" logs in the narrative.
- Integrated `notify.py` into the `deploy_fleet.py` workflow for real-time (stdout/Slack/SOAR) alerting.
- Updated documentation to reflect v0.4 (Phase 4) capabilities.

## TODO / Next Steps
- Implement real-time log tailing (using `tail -f` or a persistent watcher) to reduce alert latency from "batch" to "near real-time".
- Add support for application-level logs (Moodle, WordPress).
- Develop a lean web UI for exploring the signal timeline.
- Refine risk weighting based on historical fleet baseline.
