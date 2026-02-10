import json
import sys
from datetime import datetime

CANONICAL_SERVER_REPORT = "weekly_security_summary"

def aggregate_fleet_summary(server_summaries):
    """
    Aggregates multiple per-server weekly security reports into a single fleet-level weekly summary.
    Follows Sentra v0.3 deterministic logic.
    """

    if not server_summaries:
        return None

    total_stats = {
        "access_patterns": 0,
        "multi_ip_instances": 0,
        "privileged_sessions": 0,
        "high_risk_changes": 0,
        "iam_changes": 0
    }

    for summary in server_summaries:
        highlights = summary.get("highlights", {})
        total_stats["access_patterns"] += highlights.get("access_patterns", 0)
        total_stats["multi_ip_instances"] += highlights.get("multi_ip_instances", 0)
        total_stats["privileged_sessions"] += highlights.get("privileged_sessions", 0)
        total_stats["high_risk_changes"] += highlights.get("high_risk_changes", 0)
        total_stats["iam_changes"] += highlights.get("iam_changes", 0)

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
        f"{access_desc} {multi_ip_desc} {iam_desc} {priv_desc} {risk_context}"
    )

    return {
        "report_type": "fleet_weekly_security_summary",
        "timestamp": datetime.now().isoformat(),
        "overall_risk": fleet_risk,
        "server_count": len(server_summaries),
        "fleet_highlights": total_stats,
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
        f"**Fleet Risk Status**: {risk_color} `{fleet_summary['overall_risk']}`",
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
        "",
        "## 3. Incident Timeline",
        "The following signals were correlated across the fleet during this period:",
        ""
    ]

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
        
        # Confidence visual aid
        conf_icon = "🛡️" if conf == "HIGH" else "🔍"
        
        md.append(f"### {ts} | {sig_type} on `{host}`")
        md.append(f"- **User**: `{user}`")
        md.append(f"- **Confidence**: {conf_icon} `{conf}`")
        md.append(f"- **Narrative**: {s.get('narrative', 'No narrative available.')}")
        
        if s.get('signal') == 'privilege_escalation' and 'commands' in s:
            md.append("- **Audit Details**:")
            for cmd in s['commands']:
                risk = " [HIGH RISK]" if cmd.get('risk') == 'high' else ""
                md.append(f"  - `{cmd.get('command')}`{risk}")
        
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

    fleet_summary = aggregate_fleet_summary(summaries)
    
    # Output JSON for machine consumption
    print(json.dumps(fleet_summary, indent=2))

    # Generate Analyst Markdown Report
    report_md = generate_markdown_report(fleet_summary, all_signals)
    with open("FLEET_REPORT.md", "w") as f:
        f.write(report_md)
    print("\nAnalyst report generated: FLEET_REPORT.md", file=sys.stderr)
