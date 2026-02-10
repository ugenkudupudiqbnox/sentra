# Project Memory

This file tracks the history of tasks, decisions, and current state of the Sentra project to provide context for GitHub Copilot.

## Last Updated: 2026-02-11

## Current State
- `parse_auth_log.py` supports advanced adversarial signal detection (SSH brute force, administrative auth failures).
- Phase 3 Enrichment & Compliance Mapping is complete:
    - Commands mapped to MITRE ATT&CK (e.g., T1078, T1021) and SOC2 (e.g., CC6.1, CC7.1).
    - Probabilistic risk scoring weighted by command intent.
    - Automated "Audit Evidence Bundle" generation for auditors.

## Recent Changes
- Implemented adversarial failure parsing (`ssh_brute_force`, `failed_auth`) with specialized regex for production log patterns (`conversation failed`, `Invalid user`).
- Added Phase 3 `COMMAND_INTENT_MAP` for identity, maintenance, and network configuration intents.
- Updated `aggregate_weekly.py` to include Intent Distribution and failure metrics in fleet narratives.
- Created `generate_audit_bundle.py` to automate the collection of audit-ready evidence (SOC2/ISO).
- Refined `FLEET_REPORT.md` with MITRE/SOC2 tags and improved executive summaries.

## TODO / Next Steps
- Add support for more log sources (e.g., `pau-linux`, custom application logs).
- Implement real-time alerting (Slack/Webhook) for "Action Recommended" signals.
- Add unit tests for `categorize_command` and `parse_line` regex edge cases.
- Consider a web-based dashboard for signal visualization beyond Markdown.
