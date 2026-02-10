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

## Probabilistic Risk Scoring (Phase 2 & 3)

Sentra uses a probabilistic risk model ($0.0$ to $1.0$) to prioritize signals. 
- **Base Scores**: Every signal type has a baseline risk (e.g., `ssh_brute_force` = 0.3).
- **Intent Weighting**: Scores are escalated based on the intent of the action (e.g., `Impact / Destructive` = +0.8).
- **Confidence Multiplier**: Scores are adjusted based on the reliability of the attribution (High/Medium/Low).

Risk scores provide a relative priority, allowing analysts to focus on the most sensitive changes first.

---

## Risk Levels

Sentra uses exactly three canonical risk states:

### Low
Routine access and administration only.

### Low (Reviewed)
Security-sensitive activity (e.g., IAM changes or high-risk commands) detected but reviewed or consistent with maintenance baselines.

### Action Recommended
Signals with high risk scores ($\ge 0.5$) or unverified adversarial activity (e.g., sustained brute force) requiring operator confirmation.

---

## AI Usage

AI is used to:
- **Narrative Generation**: Translating complex log patterns into plain-language security facts.
- **Action Recommendations (Phase 4)**: Suggesting specific mitigation steps based on signal context and risk.
- **Intent Classification**: Mapping raw commands to behavioral categories (e.g., Identity Management).

AI never:
- Takes autonomous actions without human approval.
- Is used as a black-box; all mappings are deterministic and rule-based.

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
