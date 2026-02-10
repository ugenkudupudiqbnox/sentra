import sys
import json
import urllib.request
import os

SLACK_WEBHOOK_URL = os.environ.get("SENTRA_SLACK_WEBHOOK", "")
SOAR_WEBHOOK_URL = os.environ.get("SENTRA_SOAR_WEBHOOK", "")
SOAR_API_KEY = os.environ.get("SENTRA_SOAR_API_KEY", "")

def send_soar_event(signal):
    """
    Phase 4+: SOAR Integration (Shuffle/Tines).
    Sends a universal JSON payload to a SOAR platform for automated response.
    """
    if not SOAR_WEBHOOK_URL:
        return

    # Metadata for SOAR routing and orchestration
    payload = {
        "event_type": "sentra_security_signal",
        "timestamp_utc": signal.get("timestamp"),
        "severity": "CRITICAL" if signal.get("risk_score", 0) >= 0.7 else "HIGH",
        "source": "sentra-signal-engine-v0.4",
        "data": signal,
        "context": {
            "is_actionable": True,
            "requires_human_approval": signal.get("risk_score", 0) < 0.8
        }
    }

    try:
        req = urllib.request.Request(SOAR_WEBHOOK_URL)
        req.add_header('Content-Type', 'application/json')
        if SOAR_API_KEY:
            req.add_header('X-API-Key', SOAR_API_KEY)
            
        with urllib.request.urlopen(req, data=json.dumps(payload).encode('utf-8')) as response:
            print(f"SOAR event sent successfully: {SOAR_WEBHOOK_URL}")
            return response.read()
    except Exception as e:
        print(f"Error sending SOAR event: {e}", file=sys.stderr)

def send_slack_notification(signal):
    """
    Phase 4: Ticketing Integration.
    Sends a formatted alert to a Slack webhook for 'Action Recommended' signals.
    """
    if not SLACK_WEBHOOK_URL:
        # Fallback to stdout if no webhook is configured
        print(f"--- NOTIFICATION ALERT ---")
        print(f"Signal: {signal.get('signal')}")
        print(f"Narrative: {signal.get('narrative')}")
        print(f"Recommendation: {signal.get('recommendation')}")
        print(f"--------------------------")
        return

    payload = {
        "text": f"🚨 *Sentra Priority Signal Detected on {signal.get('hostname')}*",
        "attachments": [
            {
                "color": "#e01e5a" if signal.get('risk_score', 0) > 0.5 else "#ecb22e",
                "fields": [
                    {"title": "Type", "value": signal.get('signal'), "short": True},
                    {"title": "User", "value": signal.get('user'), "short": True},
                    {"title": "Risk Score", "value": str(signal.get('risk_score')), "short": True},
                    {"title": "Narrative", "value": signal.get('narrative'), "short": False},
                    {"title": "Recommended Action", "value": signal.get('recommendation'), "short": False}
                ],
                "footer": "Sentra AI-Native MSOC"
            }
        ]
    }

    try:
        req = urllib.request.Request(SLACK_WEBHOOK_URL)
        req.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req, data=json.dumps(payload).encode('utf-8')) as response:
            return response.read()
    except Exception as e:
        print(f"Error sending Slack notification: {e}", file=sys.stderr)

if __name__ == "__main__":
    # Can be called with a JSON signal on stdin
    try:
        data = json.load(sys.stdin)
        if data.get("overall_risk") == "Action Recommended" or data.get("risk_score", 0) >= 0.5:
            send_slack_notification(data)
            send_soar_event(data)
    except Exception as e:
        print(f"Error: {e}")
