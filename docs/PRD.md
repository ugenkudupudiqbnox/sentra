# PRD: AI-Native Security Control Plane (PB-Scale mSOC Core)

## Document status

* **Version:** v0.1 (Lean PRD)
* **Owner:** Founder / Product
* **Audience:** Engineering, Design Partners, SOC Ops, Early Customers
* **Philosophy:** *Build → Validate → Narrow → Deepen*

---

## 1. Problem Statement (Very Precise)

Security teams are drowning in **petabytes of logs** but still struggle to answer:

* *Is this incident real?*
* *How risky is it?*
* *What do I do next?*
* *How do I prove this to auditors?*

Existing SIEMs:

* Optimize for **data ingestion**
* Produce **alerts, not decisions**
* Require **heavy human correlation**
* Scale data, not understanding

### Core problem

> **Security meaning does not scale with log volume.**

---

## 2. Product Vision

> Build an **AI-native security control plane** that converts raw telemetry into **security narratives, risk decisions, and audit-ready evidence**—at petabyte scale.

This product is:

* Not a SIEM
* Not a log store
* Not a dashboard factory

It is:

> **A decision engine for security operations**

---

## 3. Target Customers (Early)

### Primary (Design Partners – Phase 1)

* mSOC / MSSP operators
* Cloud-native SaaS (SOC 2 / ISO 27001 driven)
* Security teams with:

  * > 50 cloud services
  * Compliance pressure
  * Alert fatigue

### Secondary (Phase 3+)

* Regulated mid-enterprises
* VC portfolio companies (bundled SOC)

---

## 4. Non-Goals (Critical for Focus)

We will **NOT** build:

* A general-purpose SIEM
* Raw log search UI
* Endpoint/XDR replacement
* Autonomous containment (initially)

---

## 5. Product Scope (What We Are Building)

### Core capabilities

1. **Security Signal Model**
2. **AI-assisted correlation & scoring**
3. **Incident narrative generation**
4. **Analyst-first workflows**
5. **Compliance evidence outputs**

---

## 6. Architecture Assumptions (Locked)

* Logs are ingested via Kafka / OTel
* Cold storage = object store
* Hot data = signals only
* Control plane is stateless & multi-tenant
* AI operates on **signals**, not raw logs

---

## 7. Phase-Wise Plan (Lean & Iterative)

---

## **PHASE 0 — Problem Validation (Weeks 0–3)**

🎯 *Validate pain, not solution*

### Goals

* Confirm the problem is painful enough
* Validate willingness to trust AI narratives
* Identify “must-have” vs “nice-to-have”

### Activities

* 10–15 customer interviews:

  * SOC analysts
  * SOC managers
  * Compliance owners
* Shadow 2 live incident investigations
* Collect:

  * Time spent per incident
  * Alert → incident conversion rate
  * Audit preparation time

### Validation questions

* “What’s the last incident that wasted your time?”
* “What proof do auditors always ask for?”
* “What would you trust AI to do *today*?”

### Exit criteria

* Clear top-3 pain points
* Agreement that **summaries & narratives** are valuable
* 3–5 design partners committed

---

## **PHASE 1 — Signal & Narrative MVP (Weeks 4–10)**

🎯 *Prove value with minimal surface area*

### What we build (MVP)

1. **Signal schema (v1)**

   * Auth, IAM, process, network summaries
2. **Basic correlation**

   * Time-window + entity based
3. **AI incident narrative**

   * What happened
   * Why it matters
   * Confidence level
4. **Read-only analyst UI**

   * Timeline
   * Entities
   * Narrative

### What we do NOT build

* No SOAR
* No tuning UI
* No dashboards
* No compliance exports yet

### Customer validation

* Weekly demo with design partners
* Compare:

  * Analyst time with vs without narratives
  * Confidence in incident closure

### Success metrics

* ≥30% reduction in investigation time
* Analysts say: *“This saves me thinking time”*
* At least 1 customer asks: *“Can we use this in production?”*

---

## **PHASE 2 — Risk Scoring & Analyst Workflow (Weeks 11–18)**

🎯 *Make it operational, not just impressive*

### What we add

1. **Probabilistic risk scoring**

   * Confidence bands
   * Severity suggestions
2. **Incident lifecycle**

   * Open → Investigating → Resolved
3. **AI handover notes**

   * Shift-to-shift continuity
4. **Human-in-the-loop controls**

   * Accept / reject AI conclusions

### Customer validation

* Run **shadow mode**:

  * AI system runs alongside existing SOC
  * No production decisions yet
* Measure:

  * False positive reduction
  * Analyst trust score (qualitative)

### Success metrics

* ≥50% alert noise reduction
* Tier-1 analysts rely on AI summaries
* SOC manager accepts AI risk score as input

---

## **PHASE 3 — Compliance Evidence MVP (Weeks 19–26)**

🎯 *Unlock budget owners*

### What we add

1. **Evidence mapping**

   * SOC 2 CC7.x
   * ISO 27001 Annex A
2. **Incident → control traceability**
3. **Auditor-ready exports**

   * Timelines
   * Decisions
   * Proof of monitoring

### Why this matters

This is where:

* CISOs sign contracts
* Finance approves spend
* Splunk alternatives get evaluated

### Customer validation

* Dry-run with a real auditor
* Ask: *“Would this satisfy evidence requirements?”*

### Success metrics

* Auditor says “yes” without caveats
* Customer agrees to use in next audit
* Willingness to pay emerges

---

## **PHASE 4 — SOAR & Outcome Automation (Weeks 27–36)**

🎯 *Turn insight into action*

### What we add

* AI-recommended actions
* Approval-gated playbooks
* Ticketing integration
* Action justification logs

### Validation

* Only with customers who explicitly ask
* Measure:

  * Time-to-containment
  * Error rate

---

## 8. Key UX Principles

* **Narratives > alerts**
* **Timelines > dashboards**
* **Confidence scores everywhere**
* **Explainability by default**
* **Humans always in control**

---

## 9. Trust & Safety Requirements

* Every AI output must be:

  * Traceable
  * Explainable
  * Logged
* No black-box decisions
* No autonomous customer actions (initially)

---

## 10. Success Metrics (North Star)

### Operational

* Mean Time to Understanding (MTTU)
* Analyst hours per incident
* False positive rate

### Business

* Design partner → paying conversion
* Compliance-driven deals
* Expansion from “monitor” → “respond”

---

## 11. Build vs Buy Decisions (Early)

| Component          | Approach                     |
| ------------------ | ---------------------------- |
| Signal schema      | Build                        |
| Correlation engine | Build                        |
| LLMs               | Use (API / hosted / private) |
| Vector DB          | Buy                          |
| UI                 | Build (lean)                 |
| SOAR               | Integrate                    |

---

## 12. Why This PRD Is Lean (By Design)

* No over-engineering
* No premature automation
* Validation at every phase
* Clear kill-criteria if trust isn’t earned

---

## Final note (Founder reality)

> **If customers don’t trust AI summaries by Phase 2, stop and reassess.**
> Everything else depends on that trust.

