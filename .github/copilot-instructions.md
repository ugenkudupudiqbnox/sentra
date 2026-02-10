# Sentra – Copilot Instructions

## Project Context
Sentra is an open-source Linux security signal engine.
Its goal is to convert Linux logs into low-noise, human-readable security signals and narratives.

Used in:
- Managed hosting (Moodle, PressBooks, WordPress)
- Managed SOC offerings
- Compliance-focused environments

---

## Core Principles (Do Not Violate)

1. Signals over events
2. Low volume output
3. Non-alarmist language
4. Deterministic logic
5. Customer trust first

---

## Canonical Signals (v0.3)

- ssh_access_pattern
  - single_ip_access
  - multi_ip_access

- privilege_escalation
  - high: persistent security changes
  - normal: routine admin work

No new external signals without review.

---

## AI Usage Rules

AI may:
- Generate narratives
- Format weekly reports

AI must not:
- Decide severity
- Trigger actions
- Change logic

---

## Weekly Report Rules

Overall risk values:
- Low
- Low (Reviewed)
- Action Recommended

High severity does not automatically imply elevated risk.

---

## What Not to Build

- Dashboards
- Alert floods
- Autonomous remediation
- Raw log exposure

---

## North Star

If the customer does not need to care, do not emit a signal.
