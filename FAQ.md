# Sentra – Security Monitoring FAQ

This FAQ explains how Sentra reports security activity and how to interpret weekly summaries.

---

## Is “Low (Reviewed)” a security alert?

No.

**Low (Reviewed)** means:
- Security-sensitive administrative changes were detected
- These changes match expected maintenance behavior
- Activity has been reviewed or is reviewable without urgency

No immediate action is required unless the activity was unplanned.

---

## What triggers “Action Recommended”?

Only **explicit, unverified activity** triggers *Action Recommended*, such as:
- Unexpected administrative changes
- Activity that does not align with known maintenance windows
- Deviations that require operator confirmation

Raw activity volume never triggers this state.

---

## Why don’t login counts increase risk?

Sentra measures **behavior**, not volume.

Multiple logins or sessions are normal in managed environments.
Counts are reported for visibility but are always interpreted in context.

---

## Why does Sentra not send real-time alerts?

Sentra is designed for **managed environments**, not incident response automation.

Our philosophy:
- Reduce noise
- Provide calm, periodic visibility
- Escalate only when intent is unclear

Real-time alerts are available only in managed response offerings.

---

## Do you block or remediate threats automatically?

No.

Sentra:
- Does not block access
- Does not change system state
- Does not automate remediation

All actions remain under human control.

---

## Is Sentra a SIEM?

No.

Sentra does not:
- Store logs long-term
- Provide search dashboards
- Correlate across data sources

Sentra complements SIEMs but does not replace them.

---

## Who should read Sentra reports?

Sentra reports are written for:
- Platform owners
- IT administrators
- Compliance reviewers
- Auditors

No security expertise is required to understand them.

---

## How does Sentra help with audits?

Sentra provides:
- Clear records of administrative activity
- Evidence of continuous access monitoring
- Human-readable explanations suitable for audits

This supports SOC 2, ISO 27001, and similar frameworks.
