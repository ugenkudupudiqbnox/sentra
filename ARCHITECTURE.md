```
Raw Log
   ↓
Kafka (single source of truth)
   ↓
Stream Processing / Signal Factory
   ├──► Elastic        (only if searchable)
   ├──► ClickHouse     (only aggregates)
   ├──► Vector DB      (only embeddings)
   └──► AI Control     (only signals)
```

```
                           ┌───────────────────────────┐
                           │     DATA COLLECTION       │
                           │ (Agents / Collectors)     │
                           └─────────────┬─────────────┘
                                         │
                                      Raw Logs
                                         │
┌──────────────────────────┐   ┌─────────▼──────────┐   ┌─────────────────────┐
│   STREAM NORM & ENRICH   │   │ AI SIGNAL ENGINEER │   │ MODEL REPOSITORIES  │
│ (Flink / Kafka Streams)  │   │ (LLM + embeddings) │   │ (Threat + TTP + ML) │
└────────────┬─────────────┘   └────────────┬───────┘   └─────────────┬───────┘
             │                              │                         │
             │                            Signals (Enriched + Vectorized)
             ▼                              ▼                         ▼
┌──────────────────────────┐   ┌──────────────────────────┐   ┌──────────────────────┐
│ SIGNAL STORE (Vector DB) │   │ AI ANALYTICS LAYER       │   │   CONTROL RULES &    │
│(Pinecone/Milvus/Weaviate)│   │ (LLMs + Transformers)    │   │ POLICY ENGINES (DSL) │
└────────────┬─────────────┘   └──────────────┬───────────┘   └─────────────┬────────┘
             │                                │                             │
             ▼                                ▼                             ▼
┌──────────────────────────┐   ┌──────────────────────────┐   ┌──────────────────────┐
│ PROBABILISTIC SCORING    │   │ SECURITY NARRATIVE GEN.  │   │ ACTION / RESPONSE    │
│ (Risk Models + AI)       │   │ (LLM summarization)      │   │ (SOAR + RL policies) │
└────────────┬─────────────┘   └──────────────┬───────────┘   └─────────────┬────────┘
             │                                │                             │
             ▼                                ▼                             ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         ANALYST & AUDITOR INTERFACE                          │
│  Dashboards / Readouts / Evidence Kits / Auditor-Ready Reports / Playbooks   │
└──────────────────────────────────────────────────────────────────────────────┘

```
---

Absolutely — let’s **explore Option B: an AI-native Security Control Plane** built as the core of your PB-scale Managed SOC. This is the *most differentiated, long-term, and defensible* architecture you can build — one that *never shoehorns legacy SIEM thinking* and instead surfaces **security meaning, not just data**.

---

## 🧠 What “AI-Native Security Control Plane” Really Means

Instead of bending an existing SIEM to scale, you:

### 1️⃣ Treat security signals as **first-class entities**

### 2️⃣ Treat threats as **patterns & behaviors**, not rule hits

### 3️⃣ Use AI *strategically* to synthesize, summarize, and automate

### 4️⃣ Build everything as composable pipelines that scale horizontally

In short:

> Don’t bolt AI onto SIEM — build SOC automation *around AI* as its backbone.

---

## 🧩 Key Concepts You Must Master

Before architecture, you need a vocabulary shift:

### 🔹 Raw Logs vs Security Signals

* **Raw Logs** – verbose events (PBs)
* **Security Signals** – normalized, contextualized, enhanced events (KBs)

AI should operate on **signals**, not raw logs.

### 🔹 Security Narrative

Instead of simple alerts, we want:

> “At 03:14 UTC, multiple idp failures → unusual lateral auth → enrichment showed anomalous process → risk prioritized → recommended response AAA.”

That’s a **narrative**, not noise.

### 🔹 AI Agents as First-Class Workers

AI is not:

* A replacement for analysts
* A vague assistant

AI is:

* A **trusted operational layer**
* A **security workflow actor**
* A **context aggregator**

---

## 🏗️ High-Level Architecture: AI-Native Security Control Plane

![Image](https://substackcdn.com/image/fetch/%24s_%21qnzZ%21%2Cf_auto%2Cq_auto%3Agood%2Cfl_progressive%3Asteep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F212ec79e-d426-481d-9289-f973b794b9ef_2400x1350.png)

![Image](https://miro.medium.com/1%2Al1Hy9lOoR5uf6gHk90Cytg.png)

![Image](https://www.researchgate.net/publication/283914038/figure/fig1/AS%3A669006759477251%401536515049679/a-Traditional-signal-processing-architecture-b-traditional-signal-processing-after-a.png)

![Image](https://image.slidesharecdn.com/digitalsignalprocessor-161122174340/75/Digital-signal-processor-architecture-4-2048.jpg)

---

## 🧠 Architecture Diagram (Text + Function)

```
                           ┌───────────────────────────┐
                           │     DATA COLLECTION       │
                           │ (Agents / Collectors)      │
                           └─────────────┬─────────────┘
                                         │
                                        Raw
                                       Logs
                                         │
┌──────────────────────────┐   ┌─────────▼──────────┐   ┌─────────────────────┐
│   STREAM NORM & ENRICH   │   │ AI SIGNAL ENGINEER │   │ MODEL REPOSITORIES   │
│ (Flink / Kafka Streams)  │   │ (LLM + embeddings) │   │ (Threat + TTP + ML) │
└────────────┬─────────────┘   └────────┬───────────┘   └────────────┬────────┘
             │                              │                         │
             │                          Signals (Enriched + Vectorized)
             ▼                              ▼                         ▼
┌──────────────────────────┐   ┌──────────────────────────┐   ┌──────────────────────┐
│ SIGNAL STORE (Vector DB) │   │ AI ANALYTICS LAYER       │   │   CONTROL RULES &    │
│ (Pinecone / Milvus / Weaviate) │   │ (LLMs + Transformers)     │   │ POLICY ENGINES (DSL) │
└────────────┬─────────────┘   └──────────┬────────────────┘   └────────────┬────────┘
             │                                │                             │
             ▼                                ▼                             ▼
┌──────────────────────────┐   ┌──────────────────────────┐   ┌──────────────────────┐
│ PROBABILISTIC SCORING    │   │ SECURITY NARRATIVE GEN.  │   │ ACTION / RESPONSE     │
│ (Risk Models + AI)       │   │ (LLM summarization)       │   │ (SOAR + RL policies) │
└────────────┬─────────────┘   └────────────┬─────────────┘   └────────────┬────────┘
             │                                │                             │
             ▼                                ▼                             ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         ANALYST & AUDITOR INTERFACE                          │
│  Dashboards / Readouts / Evidence Kits / Auditor-Ready Reports / Playbooks   │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔥 Core Principles (AI-driven)

### Principle #1 — **AI works on signals**, not raw logs

Logs are too noisy. AI doesn’t digest petabytes directly.

Your system converts logs → **normalized vectors** → signals → AI.

---

### Principle #2 — **AI writes narratives, not alerts**

Alerts are not decisions. Narratives are.

Your AI models produce:

* Incident summaries
* Root-cause rationales
* Suggested actions
* Risk trade-offs
* Communication drafts

This accelerates analysts by **3–5×**.

---

### Principle #3 — **AI supports hypothesis triage**

Security investigation is hypothesis testing.

AI helps you:

* Generate hypotheses
* Validate/invalidate with data
* Prioritize next steps

This is closer to human cognition than rules.

---

### Principle #4 — **AI-assisted compliance (automated evidence)**

Every AI narrative is:

* Traceable
* Version-controlled
* Mapped to compliance frameworks (SOC 2, ISO 27001, PCI)

This is **game-changing** for auditors.

---

## 💎 The Enrichment Lifecycle: Turning Noise into Meaning

Enrichment is where a raw log event earns its "Security Signal" status. In our AI-native control plane, enrichment happens at three stages:

### 1. Static Enrichment (at Ingestion)
- **Identity Mapping**: Converting `stpi` to `Employee ID 88219 (SRE Team)`.
- **Asset Role**: Tagging the host as `Tier 1: Production Database` vs `Tier 3: Dev Sandbox`.
- **Geo-IP**: Mapping `1.1.1.1` to its physical location and ISP.

### 2. Dynamic Intelligence (Real-Time)
- **Threat Intel**: Querying IP reputation (AbuseIPDB, VirusTotal) for current maliciousness.
- **TTP Mapping**: Matching commands to **MITRE ATT&CK** techniques (e.g., `rm -rf` → `T1485 Data Destruction`).
- **Compliance Tagging**: Labeling events with **SOC 2** controls (e.g., `CC6.1 Access Management`).

### 3. Behavioral Enrichment (Contextual)
- **Frequency Analysis**: "User has run `sudo` 5 times in the last 10 minutes (3σ above baseline)."
- **Vector Similarity**: "This command pattern is 92% similar to a known data-exfiltration TTP in our Vector DB."

---

## 🏗️ System Module Boundaries

Sentra is organized into four logical layers with strict boundaries to ensure scalability and maintainability:

### 1. Ingestion / Parser Layer
- **Responsibility**: Raw log collection and normalization.
- **Components**: `parse_auth_log.py` (Local), Kafka Connectors (PB-scale).
- **Output**: Structured JSON events with standardized timestamps (RFC5424/ISO8601).
- **Boundary**: Does not perform security analysis; only ensures data types and schemas are correct.

### 2. Signal Abstraction Layer
- **Responsibility**: Behavioral aggregation and contextual enrichment.
- **Components**: Flink Stream processors, `COMMAND_INTENT_MAP`.
- **Logic**: Maps "commands" to "intents" and "compliance controls". Groups events into behavioral windows (10m/1h).
- **Boundary**: Produces vectorized signals. It knows "what" happened but doesn't yet explain "why" to a human.

### 3. Summarizer / Narrative Generator
- **Responsibility**: Human-first synthesis of signal patterns.
- **Components**: `ai_engine.py`, OpenAI/LLM integration.
- **Logic**: Consumes a "signal cluster" and generates a natural language narrative and executive recommendation.
- **Boundary**: Operates only on signals, never on raw logs. Provides the "Meaning" and "Response" logic.

### 4. Evaluation / Ground Truth Reference
- **Responsibility**: Quality control and probabilistic calibration.
- **Components**: `overrides.json`, Analyst Feedback loop, Risk scoring models.
- **Logic**: Compares AI-generated narratives against historical "reviewed" signals to reduce false positives.
- **Boundary**: Acts as the system's "Self-Correction" layer, preventing LLM hallucinations and alert fatigue.

---

## 💾 Storage Strategy & Data Lifecycle

To handle PB-scale signals, Sentra is transitioning from local storage to a distributed, multi-tiered model:

### 1. Hot Tier (Real-Time State)
- **Engine**: Apache Flink + RocksDB.
- **Data**: Active windowed events (last 1-24 hours).
- **Purpose**: Real-time correlation, frequency analysis, and immediate triage.

### 2. Warm Tier (Search & AI Analytics)
- **Engine**: Distributed Vector DB (Pinecone / Milvus / Weaviate).
- **Data**: Vectorized security signals (last 30-90 days).
- **Purpose**: Cross-fleet signal correlation, similarity searches, and AI-driven pattern discovery.

### 3. Cold Tier (Compliance & Forensics)
- **Engine**: Cloud Object Storage (S3 / GCS / Azure Blob).
- **Data**: Enriched signals and raw logs (1-7 years).
- **Purpose**: Long-term audit evidence, forensic reconstruction, and model retraining.

---

## 🧠 Component Breakdown

### 🔹 1. Signal Normalizer & Enricher

Transforms:

```
Raw logs → structured vectors → domain entities (user, host, process)
```

Enrichment sources:

* Identity context
* Geo/IP intelligence
* Threat intel
* Behavior baselines

---

### 🔹 2. AI Signal Engineer

Generates:

* Contextual embeddings
* Pattern signatures
* Feature vectors
  Used for:
* Clustering
* Similarity search
* Predictive risk scoring

Tech:

* Vector databases
* Transformers
* Contrastive learning

---

### 🔹 3. Probabilistic Risk & Scoring Models

AI fuses:

* Statistical models
* Deep patterns
* Behavioral deviations
  to produce:
* Continuous risk scores
* Confidence intervals
* Alert severity

This replaces brittle rule thresholds.

---

### 🔹 4. Narrative & Explanation Engine

AI crafts:

* Incident story
* Temporal reasoning
* Causal inference
* Suggested responses

This is where AI *creates meaning*.

---

### 🔹 5. SOAR + AI Policy Actors

Use:

* Reinforcement learning policies
* Safety grammars
* Human approval gates

This layer:

* Proposes actions
* Executes playbooks
* Logs decisions

---

### 🔹 6. Analyst & Auditor UI

Not dashboards — **Decision UIs** that show:

* What happened
* Why it matters
* Next actions
* Confidence & trade-offs
* Compliance evidence packs

---

## 🧠 AI Workflows That Matter

### ➤ Incident Triage

```
Signals → AI cluster → risk sheet → narrative
```

### ➤ Threat Hunting

```
Vector similarity search → pattern mining → anomaly clusters
```

### ➤ Compliance Reporting

```
Narratives + evidence kits → auditor-ready exports
```

### ➤ Playbook Execution

```
AI recommended actions → approval → SOAR enactment
```

---

## 🔥 Why This Wins Over Traditional SIEM

| Traditional SIEM      | AI-Native Control Plane        |
| --------------------- | ------------------------------ |
| Rules & thresholds    | Probabilistic AI models        |
| Alert floods          | Narrative clusters             |
| Query-based search    | Embeddings + similarity search |
| Manual investigations | Hypothesis-driven AI workflows |
| Data volume pricing   | Outcome pricing                |
| Static dashboards     | Insight narratives             |

---

## 🏁 Your Competitive Playbook

### 🪖 Build Real Signals, Not Raw Indexes

Discard legacy log-first thinking.
Logs → vectorized, context-rich signals.

### 📚 Ship Detection Packs as Code

Versioned, auditable, reusable policies + narrative templates.

### 🧠 Use AI for:

* Triage acceleration
* Pattern inference
* Narrative generation
* Evidence collection

Not for unverified decisions.

### 🔐 Humans in the Safety Loop

AI recommends, analysts validate.

---

## 🧪 Prototype Path (6–12 Weeks)

**Week 1–2**

* Define signal schema
* Pick vector DB

**Week 3–4**

* Integrate Kafka + enrichment

**Week 5–6**

* Build AI signal models

**Week 7–8**

* Narrative engine + UI

**Week 9–10**

* SOAR integration

**Week 11–12**

* Compliance reporters

You go from zero → working prototype that beats SIEM semantics.

---

## 📈 Business Impact You Can Sell

* 3× analyst efficiency
* 70% fewer false alerts
* Auditable evidence with narrative
* Outcome-based pricing (not GBs)
* Competitive against Splunk / Elastic

---

## System Components (v0.4)

### 1. Signal Engine (`parse_auth_log.py`)
The heart of Sentra. It performs behavioral analysis on `/var/log/auth.log`. For PB-scale ingestion and processing deployment architectures, refer to the [Kafka Playbook](KAFKA_PLAYBOOK.md) and the [Flink Playbook](FLINK_PLAYBOOK.md).
- **Normalization**: Parsing varied timestamp and log formats into standard events.
- **Aggregation**: Grouping events into 10-minute and 1-hour behavioral windows.
- **Enrichment (Phase 3)**: Mapping commands to **MITRE ATT&CK** tactics and **SOC2** controls.
- **Risk Scoring**: Applying a probabilistic model to evaluate behavior sensitivity.

### 2. Fleet Aggregator (`aggregate_weekly.py`)
Maintains a fleet-wide view by:
- Combining per-server signals into a unified executive summary.
- Calculating fleet-wide intent distributions.
- Applying **Analyst Overrides** (`overrides.json`) to resolve routine maintenance activity.

### 3. Notification Layer (`notify.py`)
The **Phase 4** outcome engine that:
- Filters signals for high-risk thresholds ($\ge 0.5$).
- Delivers priority alerts to Slack or Webhooks.
- Formats signals for human-first investigation.

### 4. Audit Evidence Utility (`generate_audit_bundle.py`)
Automates compliance readiness by gathering all narratives, decisions, and raw JSON signals into a single, timestamped zip archive for auditors.

