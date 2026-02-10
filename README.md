# Sentra

**Sentra** is an open-source Linux security signal engine that converts noisy system logs into **clear, human-readable security signals and narratives**.

Sentra is designed for **managed hosting providers, mSOC operators, and platform teams** who want security clarity instead of dashboards and alert fatigue.

---

## What Sentra Is

- A Linux security signal engine
- Focused on behavior and intent, not raw events
- Designed to run directly on Ubuntu servers
- Produces low-volume, high-meaning signals
- Generates customer- and auditor-friendly narratives

Sentra turns thousands of log lines into a handful of security facts per day.

---

## What Sentra Is NOT

Sentra is intentionally not:
- A SIEM
- A log storage or search platform
- An endpoint protection agent
- A SOC replacement
- An autonomous response system

Sentra does not alert aggressively or automate decisions.

---

## Supported Platforms (v0.3)

- Ubuntu 20.04 / 22.04 / 24.04
- Standard Linux logs:
  - /var/log/auth.log
  - /var/log/syslog

Application-specific signals (Moodle, PressBooks, WordPress) are layered on top.

---

## Core Concepts

### Signals, Not Logs
Sentra reduces raw events into security signals that represent behavior over time, such as:
- Access patterns
- Privileged activity

### Risk Scoring & Analyst Workflow (Phase 2)
Sentra uses a probabilistic risk model ($0.0$ to $1.0$) to prioritize signals. Each signal includes a stable, unique ID (e.g., `381521c2a0c1`) that allows analysts to:
- **Correlate** activity across the fleet.
- **Override** signals using an `overrides.json` file to resolve routine maintenance window activities.
- **Maintain Continuity** via a dedicated "AI Handover Notes" section in the weekly executive report.
- Security-sensitive configuration changes

### Phase 3: Compliance & Enrichment
Sentra automates the mapping of security signals to global standards:
- **MITRE ATT&CK Tracking**: Signals are tagged with specific tactics and techniques (e.g., T1078, T1021).
- **SOC 2 & ISO 27001 Evidence**: Direct mapping to trust services criteria (CC6.1, CC7.1) for auditor-ready reporting.
- **Intent Classification**: Uses regex-based behavioral analysis to categorize administrative actions (Maintenance vs. Identity Management vs. Credential Access).
- **Audit Evidence Bundle**: A single-command utility (`generate_audit_bundle.py`) to aggregate all reports, decisions, and raw evidence into a timestamped zip archive for auditors.

### Human-First Output
Every signal includes:
- Calm, plain-language explanations
- Clear indication of whether action is required
- No alarmist language

### Deterministic by Design
Sentra:
- Uses explicit rules and aggregation
- Avoids black-box decisions
- Produces explainable, auditable output

AI is used only for formatting and summarization.

---

## Weekly Security Summary

Sentra generates a weekly security report suitable for customers and auditors.

Example:
"This week, your system remained stable. Some administrative changes were detected as part of routine maintenance and were reviewed. No action is required."

---

## Design Philosophy

- Reduce noise aggressively
- Prefer behavior over events
- Communicate calmly and clearly
- Build trust before automation

---

## License

MIT License

---

## Why Sentra Exists

Security teams don’t lack data.
They lack confidence.

Sentra exists to provide calm, reliable security visibility for managed infrastructure.
