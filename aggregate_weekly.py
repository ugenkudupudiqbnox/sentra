import json
import sys
import os
from datetime import datetime

CANONICAL_SERVER_REPORT = "weekly_security_summary"
OVERRIDES_FILE = "overrides.json"

def load_overrides():
    """Phase 2: Human-in-the-loop controls. Loads analyst overrides."""
    if os.path.exists(OVERRIDES_FILE):
        try:
            with open(OVERRIDES_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def aggregate_fleet_summary(server_summaries, all_signals, overrides):
    """
    Aggregates multiple per-server weekly security reports into a single fleet-level weekly summary.
    Follows Sentra v0.3 deterministic logic.
    """

    if not server_summaries:
        return None

    # Apply Overrides to signals first
    for s in all_signals:
        sig_id = s.get('id')
        if sig_id in overrides:
            override = overrides[sig_id]
            s['status'] = override.get('status', s['status'])
            s['analyst_note'] = override.get('note', '')
            # If resolved/reviewed, we might choose to lower the risk score weight
            if s['status'] in ['RESOLVED', 'REVIEWED']:
                s['risk_score'] = 0.0

    total_stats = {
        "access_patterns": 0,
        "multi_ip_instances": 0,
        "privileged_sessions": 0,
        "high_risk_changes": 0,
        "iam_changes": 0,
        "ssh_brute_force": 0,
        "failed_auth": 0,
        "avg_risk_scores": []
    }

    for summary in server_summaries:
        highlights = summary.get("highlights", {})
        total_stats["access_patterns"] += highlights.get("access_patterns", 0)
        total_stats["multi_ip_instances"] += highlights.get("multi_ip_instances", 0)
        total_stats["privileged_sessions"] += highlights.get("privileged_sessions", 0)
        total_stats["high_risk_changes"] += highlights.get("high_risk_changes", 0)
        total_stats["iam_changes"] += highlights.get("iam_changes", 0)
        total_stats["ssh_brute_force"] += highlights.get("ssh_brute_force_attempts", 0)
        total_stats["failed_auth"] += highlights.get("failed_auth_attempts", 0)
        if "avg_risk_score" in summary:
            total_stats["avg_risk_scores"].append(summary["avg_risk_score"])

    # Phase 3: Aggregate Intents
    intent_counts = {}
    for s in all_signals:
        intent = s.get('intent', 'General Administration')
        intent_counts[intent] = intent_counts.get(intent, 0) + 1

    # Calculate fleet-wide average risk
    fleet_avg_score = 0
    if total_stats["avg_risk_scores"]:
        fleet_avg_score = round(sum(total_stats["avg_risk_scores"]) / len(total_stats["avg_risk_scores"]), 2)

    # === SENTRA CANONICAL FLEET RISK RULES (v0.3) ===
    # 1. Action Recommended ONLY if a server explicitly requires action
    # 2. Low (Reviewed) if high-risk changes or IAM changes exist
    # 3. Low otherwise

    if any(s["overall_risk"] == "Action Recommended" for s in server_summaries):
        fleet_risk = "Action Recommended"
    elif total_stats["high_risk_changes"] > 0 or total_stats["iam_changes"] > 0:
        fleet_risk = "Low (Reviewed)"
    else:
        fleet_risk = "Low"

    # ---- Narrative interpretation (human-first) ----

    access_desc = (
        f"Routine logins were recorded across the fleet ({total_stats['access_patterns']} sessions), "
        "reflecting normal operational access."
    )

    if total_stats["multi_ip_instances"] > 0:
        multi_ip_desc = (
            f"{total_stats['multi_ip_instances']} instance(s) of access from multiple network locations were observed. "
            "This typically reflects normal team mobility between devices or networks."
        )
    else:
        multi_ip_desc = "Login activity originated from consistent network locations."

    iam_desc = ""
    if total_stats["iam_changes"] > 0:
        iam_desc = f"Identity management tools recorded {total_stats['iam_changes']} audited modifications to systems users or groups."

    priv_desc = (
        f"Administrative activity accounted for {total_stats['privileged_sessions']} sessions, "
        "consistent with routine system management."
    )

    failure_desc = ""
    if total_stats["ssh_brute_force"] > 0 or total_stats["failed_auth"] > 0:
        failure_desc = (
            f"Perimeter monitoring blocked {total_stats['ssh_brute_force']} automated probe(s) and recorded "
            f"{total_stats['failed_auth']} unsuccessful administrative login attempt(s). This is normal background noise."
        )

    if fleet_risk == "Action Recommended":
        risk_context = (
            "One or more servers reported administrative activity requiring follow-up. "
            "Please review the corresponding server-level reports."
        )
    elif fleet_risk == "Low (Reviewed)":
        risk_context = (
            "A small number of security-sensitive administrative or identity changes were detected and reviewed. "
            "No action is required."
        )
    else:
        risk_context = "No security-sensitive changes were detected."

    narrative = (
        f"This week, security activity across your fleet of {len(server_summaries)} servers remained stable. "
        f"{access_desc} {multi_ip_desc} {iam_desc} {priv_desc} {failure_desc} {risk_context}"
    )

    return {
        "report_type": "fleet_weekly_security_summary",
        "timestamp": datetime.now().isoformat(),
        "overall_risk": fleet_risk,
        "fleet_risk_score": fleet_avg_score,
        "server_count": len(server_summaries),
        "fleet_highlights": total_stats,
        "intent_summary": intent_counts,
        "narrative": narrative
    }

def generate_markdown_report(fleet_summary, signals):
    """
    Generates a human-readable analyst report in Markdown format.
    Focuses on narratives, timelines, and confidence scores per PRD Phase 1.
    """
    # Sort signals by timestamp
    sorted_signals = sorted(signals, key=lambda x: x.get('timestamp', ''))
    
    risk_color = {
        "Low": "🟢",
        "Low (Reviewed)": "🟡",
        "Action Recommended": "🔴"
    }.get(fleet_summary['overall_risk'], "⚪")

    md = [
        f"# Fleet Security Narrative Report",
        f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Fleet Risk Status**: {risk_color} `{fleet_summary['overall_risk']}` | **Risk Score**: `{fleet_summary['fleet_risk_score']}/1.0`",
        "",
        "## 1. Executive Summary",
        fleet_summary['narrative'],
        "",
        "## 2. Fleet Highlights",
        "| Metric | Count |",
        "| :--- | :--- |",
        f"| Access Patterns | {fleet_summary['fleet_highlights']['access_patterns']} |",
        f"| Multi-IP Instances | {fleet_summary['fleet_highlights']['multi_ip_instances']} |",
        f"| Privileged Sessions | {fleet_summary['fleet_highlights']['privileged_sessions']} |",
        f"| High-Risk Changes | {fleet_summary['fleet_highlights']['high_risk_changes']} |",
        f"| Identity Changes (IAM) | {fleet_summary['fleet_highlights']['iam_changes']} |",
        f"| SSH Brute Force Attempts | {fleet_summary['fleet_highlights']['ssh_brute_force']} |",
        f"| Failed Auth (Sudo/Su) | {fleet_summary['fleet_highlights']['failed_auth']} |",
        "",
        "### Intent Distribution",
    ]
    
    for intent, count in fleet_summary.get('intent_summary', {}).items():
        md.append(f"- **{intent}**: {count}")
    
    md.extend([
        "",
        "## 3. Incident Timeline",
        "The following signals were correlated across the fleet during this period:",
        ""
    ])

    for s in sorted_signals:
        ts = s.get('timestamp', 'N/A')
        # Format timestamp for readability if it's ISO
        try:
            ts = datetime.fromisoformat(ts).strftime('%Y-%m-%d %H:%M')
        except:
            pass

        sig_type = s.get('signal', 'unknown').replace('_', ' ').title()
        host = s.get('hostname', 'unknown')
        user = s.get('user', 'unknown')
        conf = s.get('confidence', 'medium').upper()
        score = s.get('risk_score', 0.0)
        status = s.get('status', 'open').upper()
        sig_id = s.get('id', 'n/a')
        
        # Confidence visual aid
        conf_icon = "🛡️" if conf == "HIGH" else "🔍"
        
        md.append(f"### {ts} | {sig_type} on `{host}`")
        md.append(f"- **ID**: `{sig_id}` | **Intent**: `{s.get('intent', 'N/A')}`")
        md.append(f"- **User**: `{user}`")
        md.append(f"- **Risk Score**: `{score}` | **Confidence**: {conf_icon} `{conf}` | **Status**: `{status}`")
        
        mitre = s.get('mitre_tags', [])
        compliance = s.get('compliance_tags', [])
        if mitre:
            md.append(f"- **MITRE ATT&CK**: `{', '.join(mitre)}`")
        if compliance:
            md.append(f"- **Compliance**: `{', '.join(compliance)}`")
            
        md.append(f"- **Narrative**: {s.get('narrative', 'No narrative available.')}")
        
        if s.get('signal') == 'privilege_escalation' and 'commands' in s:
            md.append("- **Audit Details**:")
            for cmd in s['commands']:
                risk = " [HIGH RISK]" if cmd.get('risk') == 'high' else ""
                md.append(f"  - `{cmd.get('command')}`{risk}")
        
        md.append("")

    # Section 4: AI Handover Notes (Phase 2)
    md.append("## 4. AI Handover Notes")
    md.append("Summarizing critical state for shift continuity:")
    
    high_risk_signals = [s for s in signals if s.get('risk_score', 0) >= 0.5]
    if high_risk_signals:
        md.append(f"- **High Risk Focus**: There are {len(high_risk_signals)} signals with a risk score ≥ 0.5. These primarily involve sensitive administrative changes.")
    else:
        md.append("- **High Risk Focus**: No high-risk signals (≥ 0.5) were detected this period.")
    
    open_signals = [s for s in signals if s.get('status') == 'open']
    md.append(f"- **Incident Status**: {len(open_signals)} signals remain in `OPEN` status and require validation against your team's maintenance schedule.")
    
    servers_affected = len(set(s.get('hostname') for s in signals))
    md.append(f"- **Scope**: Activity is distributed across {servers_affected} server(s).")
    md.append("")

    md.append("---")
    md.append("Generated by Sentra AI-Native Control Plane v0.1")
    
    return "\n".join(md)

if __name__ == "__main__":
    summaries = []
    all_signals = []

    # Load canonical per-server weekly summaries and individual signals
    for file_path in sys.argv[1:]:
        try:
            with open(file_path, "r") as f:
                for line in f:
                    if not line.strip():
                        continue
                    data = json.loads(line)
                    if data.get("report_type") == CANONICAL_SERVER_REPORT:
                        summaries.append(data)
                    elif "signal" in data:
                        all_signals.append(data)
        except Exception as e:
            print(f"Error loading {file_path}: {e}", file=sys.stderr)

    if not summaries:
        print("No valid weekly_security_summary inputs found.", file=sys.stderr)
        sys.exit(1)

    # Phase 2: Load analyst overrides
    overrides = load_overrides()

    fleet_summary = aggregate_fleet_summary(summaries, all_signals, overrides)
    
    # Output JSON for machine consumption
    print(json.dumps(fleet_summary, indent=2))

    # Generate Analyst Markdown Report
    report_md = generate_markdown_report(fleet_summary, all_signals)
    with open("FLEET_REPORT.md", "w") as f:
        f.write(report_md)
    print("\nAnalyst report generated: FLEET_REPORT.md", file=sys.stderr)
