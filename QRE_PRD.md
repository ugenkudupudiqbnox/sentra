Below is a **lean, execution-ready PRD** for the **Query Routing Engine (QRE)** — the component that **replaces Splunk Indexer centrality** by intelligently routing every question to the *right engine*.

This PRD is written so you can:

* Hand it to engineering
* Validate it with design partners
* Build it iteratively without over-engineering

---

# PRD: Query Routing Engine (QRE)

## Version

* **v0.1 (Lean / Iterative)**
* Status: Design-partner ready

---

## 1. Product Summary (One Paragraph)

The **Query Routing Engine (QRE)** is an AI-assisted decision system that determines **where a security query should be executed** — keyword search, analytics engine, vector database, stream processor, or AI control plane — based on **query intent, context, and cost-awareness**.

> QRE ensures that **questions choose the engine**, not the other way around.

---

## 2. Problem Statement

Modern SOC platforms use a **single search engine** (e.g., a SIEM indexer) to answer **all types of questions**, causing:

* High cost
* Slow investigations
* Poor support for similarity & reasoning
* Analyst cognitive overload

At PB scale, this model breaks.

### Core problem

> **Different security questions require fundamentally different query engines — but SOCs force them through one.**

---

## 3. Goals & Non-Goals

### Goals

* Correctly classify query intent
* Route queries to the optimal engine
* Support compound (multi-engine) queries
* Be auditable, deterministic, and explainable
* Reduce reliance on monolithic SIEM search

### Non-Goals (Phase 1)

* Not a query execution engine
* Not a data store
* Not a full natural-language-to-SQL system
* Not autonomous decision-making

---

## 4. Supported Query Types (Canonical Taxonomy)

| Intent Category          | Description                           | Examples                           |
| ------------------------ | ------------------------------------- | ---------------------------------- |
| **Exact / Forensic**     | Precise matching, regex, time-bounded | “Failed logins from IP X at 10:05” |
| **Analytical**           | Aggregation, trends, baselines        | “Top auth failures by region”      |
| **Similarity / Pattern** | “Like this”, fuzzy recall             | “Have we seen this attack before?” |
| **Streaming / Reactive** | Continuous evaluation                 | “Alert on spike within 2 minutes”  |
| **Decision / Risk**      | Judgment & synthesis                  | “Is this incident severe?”         |

---

## 5. Engine Mapping (Authoritative)

| Query Intent     | Engine                                      |
| ---------------- | ------------------------------------------- |
| Exact / Forensic | **Elastic** (or Splunk-like keyword engine) |
| Analytical       | **ClickHouse**                              |
| Similarity       | Vector DB (Milvus / Weaviate class)         |
| Streaming        | **Apache Kafka** / Flink                    |
| Decision         | AI Control Plane (LLM + policies)           |

---

## 6. High-Level Architecture

![Image](https://miro.medium.com/0%2AHcdvTMmMVfj0ZKxs.jpg)

![Image](https://sf-zdocs-cdn-prod.zoominsoftware.com/tdta-data_cloud-260-0-0-production-enus/2a366b50-eaf4-453b-96ff-b296bb728edb/data_cloud/images/hs-queryflow-v2.png)

![Image](https://substackcdn.com/image/fetch/%24s_%21hcmb%21%2Cf_auto%2Cq_auto%3Agood%2Cfl_progressive%3Asteep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fe38b39e0-0d3a-4999-a86e-24939b2100f7_2400x1350.png)

```
User / API / UI
      │
      ▼
┌─────────────────────────────┐
│   QUERY ROUTING ENGINE      │
│                             │
│  1. Intent Classifier       │
│  2. Confidence Scorer       │
│  3. Query Decomposer        │
│  4. Routing Decision Logic  │
│  5. Audit Logger            │
└──────────────┬──────────────┘
               │
   ┌───────────┼───────────┬────────────┬─────────────┐
   ▼           ▼           ▼            ▼             ▼
Elastic     ClickHouse   Vector DB     Kafka       AI Control
```

---

## 7. Functional Requirements

### FR-1: Intent Classification

* Accepts:

  * Natural language queries
  * Structured API queries
  * UI-contextual queries (incident view, hunt mode)
* Outputs:

```json
{
  "intent": "similarity",
  "confidence": 0.91
}
```

---

### FR-2: Query Decomposition

QRE must detect compound queries and split them.

**Example**

> “Is this incident similar to previous ransomware cases and how often did it happen last quarter?”

Produces:

* Similarity sub-query → Vector DB
* Frequency sub-query → ClickHouse
* Synthesis → AI plane

---

### FR-3: Routing Decision Logic

* Deterministic rules
* Cost-aware (prefer cheaper engines)
* Confidence thresholding:

  * If confidence < X → fallback to keyword search

---

### FR-4: Auditability (Non-Negotiable)

Every routing decision must log:

* Original query
* Classified intent
* Confidence score
* Engine selected
* Timestamp
* Version of routing logic

This is critical for:

* SOC audits
* Customer trust
* Legal defensibility

---

### FR-5: Fallback & Safety

* If downstream engine fails:

  * Retry alternate engine (if valid)
  * Escalate to analyst
* Never silently drop queries

---

## 8. Non-Functional Requirements

| Requirement            | Target                  |
| ---------------------- | ----------------------- |
| Latency (routing only) | <100ms                  |
| Availability           | ≥99.9%                  |
| Determinism            | Same input → same route |
| Explainability         | Human-readable reason   |
| Multi-tenancy          | Strict isolation        |

---

## 9. Phased Delivery Plan (Lean)

---

### **Phase 1 — Rule-Based Router (Weeks 1–4)**

**Goal:** Replace manual engine choice

* Hardcoded intent rules
* 3 intents: exact / analytical / similarity
* Static engine mapping
* JSON-based API

**Validation**

* Analysts agree routing “makes sense”
* <10% misroutes

---

### **Phase 2 — AI-Assisted Intent Classification (Weeks 5–10)**

**Goal:** Handle natural language

* Lightweight LLM or fine-tuned classifier
* Confidence scoring
* Analyst feedback loop

**Validation**

* Analysts trust routing without override
* Reduced query retries

---

### **Phase 3 — Compound Queries & Cost Awareness (Weeks 11–18)**

**Goal:** Outperform SIEM UX

* Multi-engine decomposition
* Cost-aware routing
* Partial result synthesis

**Validation**

* Analysts ask fewer follow-up questions
* Time-to-answer drops measurably

---

### **Phase 4 — Learning Router (Optional)**

**Goal:** Self-optimizing system

* Feedback-based re-weighting
* Customer-specific routing profiles
* Query success metrics

---

## 10. Success Metrics

### Operational

* % queries correctly routed (analyst-confirmed)
* Average time-to-answer
* Reduction in keyword-search load

### Business

* Reduced SIEM dependency
* Lower infra cost per investigation
* Increased analyst throughput

---

## 11. Key Risks & Mitigations

| Risk              | Mitigation                      |
| ----------------- | ------------------------------- |
| Misclassification | Confidence threshold + fallback |
| Analyst mistrust  | Explainable routing             |
| Overuse of AI     | Rules-first, AI-assisted        |
| Audit rejection   | Deterministic logs              |

---

## 12. Why This Is Strategic (Founder View)

> **Splunk Indexers lose power when they stop being the first place questions go.**

The QRE ensures:

* Search engines become interchangeable
* AI becomes the decision layer
* Your platform owns the workflow

This is the **architectural wedge** that enables:

* AI-native SOCs
* PB-scale economics
* Splunk displacement without direct competition
