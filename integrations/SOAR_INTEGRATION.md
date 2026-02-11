# Sentra SOAR Integration Guide

This document explains how to integrate Sentra security signals with SOAR (Security Orchestration, Automation, and Response) platforms like **Shuffle** and **Tines**.

---

## Architecture Overview

Sentra acts as the **Decision Engine**, while the SOAR platform acts as the **Action Engine**.

1.  **Sentra**: Identifies behavior, assigns risk, and suggests recommendations.
2.  **Webhook**: Sentra pushes high-priority signals ($\ge 0.5$) via `notify.py`.
3.  **SOAR**: Ingests JSON, triggers a workflow, and executes playbooks (e.g., blocking an IP).

---

## Integration with Tines

Tines is an enterprise-grade automation platform used to connect security tools.

### 1. Create a Webhook Action
*   Log in to Tines.
*   Drag a **Webhook** action onto your storyboard.
*   Copy the **Webhook URL**.

### 2. Configure Sentra
*   Set the environment variable on your Sentra control plane:
    ```bash
    export SENTRA_SOAR_WEBHOOK="https://<your-tenant>.tines.com/webhook/..."
    ```

### 3. Handle the Payload
Tines will receive a nested JSON object. You can access fields using:
*   `{{.sentra_security_signal.data.signal}}` (Signal Type)
*   `{{.sentra_security_signal.data.recommendation}}` (AI Recommendation)

---

## Integration with Shuffle (Open Source)

Shuffle is an open-source security automation platform.

### 1. Create a Workflow
*   In Shuffle, create a new workflow.
*   Add a **Webhook** trigger.
*   Start the execution to generate a unique URL.

### 2. Configure Sentra
*   Set the environment variable:
    ```bash
    export SENTRA_SOAR_WEBHOOK="https://shuf_url/..."
    ```

### 3. Example Shuffle Playbook: IP Blocking
*   **Condition**: If `data.signal == "ssh_brute_force"`.
*   **Action**: Use the Cloudflare or AWS WAF app in Shuffle to block `data.ip`.

---

## Payload Schema

Sentra sends a universal envelope to SOAR platforms:

```json
{
  "event_type": "sentra_security_signal",
  "timestamp_utc": "2026-02-11T12:00:00Z",
  "severity": "HIGH",
  "source": "sentra-signal-engine-v0.4",
  "data": {
    "id": "...",
    "signal": "ssh_brute_force",
    "risk_score": 0.6,
    "user": "root",
    "ip": "192.168.1.1",
    "recommendation": "Critical: Place IP on temporary firewall blocklist."
  }
}
```

---

## Security

If your SOAR platform requires an API Key, set it in your environment:
```bash
export SENTRA_SOAR_API_KEY="your-secure-key"
```
Sentra will include this in the `X-API-Key` header of every request.
