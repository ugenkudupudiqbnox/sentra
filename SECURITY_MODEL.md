# Sentra Security Model

This document defines Sentra’s security philosophy and operational model.

---

## Design Goals

Sentra is built to:
- Provide confidence, not fear
- Reduce operational noise
- Preserve human judgment
- Support managed environments

---

## Core Principle: Behavior Over Events

Sentra does not react to individual log lines.

Instead, it:
- Groups events over time
- Detects patterns of behavior
- Reports intent, not activity volume

---

## Deterministic by Design

All Sentra decisions are:
- Rule-based
- Explainable
- Reproducible

There are no hidden scoring systems or probabilistic risk models.

---

## Risk Levels

Sentra uses exactly three risk states:

### Low
Routine access and administration only.

### Low (Reviewed)
Security-sensitive activity detected but consistent with expected maintenance.

### Action Recommended
Unverified or unexpected activity requiring operator confirmation.

Risk levels are never inferred from raw counts alone.

---

## AI Usage

AI is used only to:
- Improve narrative clarity
- Summarize already-determined outcomes

AI never:
- Determines risk
- Triggers actions
- Alters system behavior

---

## Fleet Aggregation Model

Fleet-level summaries:
- Preserve per-server intent
- Never correlate across hosts
- Never escalate based on volume

The most serious server-level state always wins.

---

## What Sentra Will Not Do

Sentra will not:
- Generate alert floods
- Perform autonomous remediation
- Expose raw logs to customers
- Make irreversible decisions

---

## Intended Usage

Sentra is ideal for:
- Managed hosting providers
- Educational platforms
- SaaS infrastructure teams
- Compliance-driven environments

It is not designed for:
- Real-time SOC automation
- Active threat hunting
- Endpoint protection

---

## Trust First

Sentra assumes:
- Humans remain in control
- Calm communication builds trust
- Security should be predictable

If a customer does not need to care, Sentra will not interrupt them.
