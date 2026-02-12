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

## 🏗️ Platform Status (v0.2 - Feb 2026)

Sentra has evolved into a multi-engine **AI-Native Security Control Plane**. 

### Key Modules:
- **Query Routing Engine (QRE)**: Intelligent NL-to-Engine routing.
- **AI Control Plane**: Narrative summaries and vector correlation.
- **Multi-Tenant Storage**: ClickHouse (Analytics) + Elastic (Forensics).
- **Security Dashboard**: Real-time signal investigation UI.

For deep technical details, see the [Technical Guide](docs/TECHNICAL_GUIDE.md).

---

## 🚀 Getting Started

### 1. Requirements
- Python 3.9+
- OpenAI API Key (exported as `OPENAI_API_KEY`)
- Docker (for ClickHouse/Elastic infrastructure)

### 2. Launching the Dashboard
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python3 -m streamlit run src/dashboard.py
```

### 3. Running a Query
Use the dashboard's **QRE Lab** or the CLI:
```bash
python3 src/query_shell.py
```

---

## Documentation Index
- [Master Roadmap](docs/ROADMAP.md) - Strategic alignment (8 phases).
- [Technical Guide](docs/TECHNICAL_GUIDE.md) - Architecture, routing, and schemas.
- [Execution Plan](docs/EXECUTION.md) - Current development sprint details.
- [Security Model](SECURITY_MODEL.md) - Tenant isolation and data classification.

### Risk Scoring & Analyst Workflow
Sentra uses a probabilistic risk model ($0.0$ to $1.0$) to prioritize signals. Each signal includes a stable, unique ID (e.g., `381521c2a0c1`) that allows analysts to:
- **Correlate** activity across the fleet.
- **Override** signals using an `overrides.json` file to resolve routine maintenance window activities.
- **Maintain Continuity** via a dedicated "AI Handover Notes" section in the weekly executive report.
- Security-sensitive configuration changes

### Compliance & Enrichment
Sentra automates the mapping of security signals to global standards:
- **MITRE ATT&CK Tracking**: Signals are tagged with specific tactics and techniques (e.g., T1078, T1021).
- **SOC 2 & ISO 27001 Evidence**: Direct mapping to trust services criteria (CC6.1, CC7.1) for auditor-ready reporting.
- **Intent Classification**: Uses regex-based behavioral analysis to categorize administrative actions (Maintenance vs. Identity Management vs. Credential Access).
- **Audit Evidence Bundle**: A single-command utility (`generate_audit_bundle.py`) to aggregate all reports, decisions, and raw evidence into a timestamped zip archive for auditors.

### SOAR & Outcome Automation
Sentra turns insights into specific actions:
- **AI-Recommended Actions**: Every signal include a context-aware "Recommended Action" (e.g., "Verify authorization" or "Block IP").
- **Priority Alerts**: Integrated notification system (`notify.py`) for Slack or Webhook delivery of high-risk signals.
- **Action Justification Logs**: Analyst notes and outcomes (Resolved/Reviewed) are captured and displayed in the weekly summary for audit continuity.
- **Priority Playbooks**: Automated grouping of suggested mitigations in the fleet executive report.

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
