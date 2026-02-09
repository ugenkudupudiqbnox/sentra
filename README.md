# Sentra

**Sentra** is an open-source Linux security signal engine designed to turn noisy system logs into **clear, human-meaningful security signals**.

Sentra is built for **managed infrastructure providers**, **mSOC operators**, and **platform teams** who want security *answers*, not raw logs.

---

## What Sentra Is

- A **security signal generator** for Linux servers
- Focused on **meaningful detection**, not log ingestion
- Designed to run **directly on Ubuntu servers**
- Built to support **AI-driven incident narratives** (later)
- Opinionated, minimal, and auditable

Sentra converts thousands of Linux log events into a **small number of security signals per day**.

---

## What Sentra Is NOT

Sentra is **not**:

- A SIEM
- A log storage system
- A SOC replacement
- An endpoint protection platform
- An autonomous response engine

Sentra intentionally avoids dashboards, alert floods, and over-automation.

---

## Supported Platforms (v0.1)

- Ubuntu 20.04 / 22.04 / 24.04
- Standard Linux logs:
  - `/var/log/auth.log`
  - `/var/log/syslog`

Application support will be added incrementally.

---

## Core Concepts

### 1. Raw Logs → Signals

Linux systems generate thousands of log lines per day.  
Sentra reduces this noise into **security-relevant signals**, such as:

- SSH brute-force attempts
- Suspicious privilege escalation
- Unexpected root access
- Abnormal authentication behavior

### 2. Signals, Not Alerts

A **signal** represents a summarized security-relevant behavior over time.

Example:
- 37 failed SSH attempts → **1 signal**
- Multiple sudo events → **1 signal**

This keeps human attention focused and actionable.

### 3. Human-First Security

Sentra is built to answer:
- What happened?
- Why does it matter?
- What should I do next?

AI and automation are layered **after signal quality is proven**.

---

## Project Status

🚧 **Early development (v0.1)**

Current focus:
- Linux log normalization
- Basic signal reduction logic
- Real-world validation on production servers

No guarantees yet. APIs may change.

---

## Quick Start (Development)

```bash
# Clone the repository
git clone https://github.com/YOUR_ORG/sentra.git
cd sentra

# Run locally on an Ubuntu server (requires sudo)
sudo python3 sentra.py
```

> ⚠️ Sentra currently reads local system logs and should be run on the host itself.

---

## Design Philosophy

- Start simple
- Prefer clarity over coverage
- Reduce noise aggressively
- Earn operator trust before adding automation
- Build for auditors and humans, not just machines

---

## Roadmap (High-Level)

- [x] Linux log reading
- [x] Basic signal schema
- [ ] SSH brute-force signal
- [ ] Privilege escalation signal
- [ ] AI-generated incident summaries
- [ ] Weekly security reports
- [ ] Managed SOC integrations

---

## License

Sentra is released under the **MIT License**.

---

## Contributing

Contributions are welcome, especially:
- New Linux security signals
- Signal quality improvements
- Documentation and examples

Please keep changes **small, focused, and well-explained**.

---

## Why Sentra Exists

Security teams don’t lack data.  
They lack **clarity**.

Sentra exists to close that gap.
