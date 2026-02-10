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
        "high_risk_changes": 0
    }

    for summary in server_summaries:
        highlights = summary.get("highlights", {})
        total_stats["access_patterns"] += highlights.get("access_patterns", 0)
        total_stats["multi_ip_instances"] += highlights.get("multi_ip_instances", 0)
        total_stats["privileged_sessions"] += highlights.get("privileged_sessions", 0)
        total_stats["high_risk_changes"] += highlights.get("high_risk_changes", 0)

    # === SENTRA CANONICAL FLEET RISK RULES (v0.3) ===
    # 1. Action Recommended ONLY if a server explicitly requires action
    # 2. Low (Reviewed) if high-risk changes exist
    # 3. Low otherwise

    if any(s["overall_risk"] == "Action Recommended" for s in server_summaries):
        fleet_risk = "Action Recommended"
    elif total_stats["high_risk_changes"] > 0:
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
            "A small number of security-sensitive administrative changes were detected and reviewed. "
            "No action is required."
        )
    else:
        risk_context = "No security-sensitive changes were detected."

    narrative = (
        f"This week, security activity across your fleet of {len(server_summaries)} servers remained stable. "
        f"{access_desc} {multi_ip_desc} {priv_desc} {risk_context}"
    )

    return {
        "report_type": "fleet_weekly_security_summary",
        "timestamp": datetime.now().isoformat(),
        "overall_risk": fleet_risk,
        "server_count": len(server_summaries),
        "fleet_highlights": total_stats,
        "narrative": narrative
    }


if __name__ == "__main__":
    summaries = []

    # Load only canonical per-server weekly summaries
    for file_path in sys.argv[1:]:
        try:
            with open(file_path, "r") as f:
                for line in f:
                    if not line.strip():
                        continue
                    data = json.loads(line)
                    if data.get("report_type") == CANONICAL_SERVER_REPORT:
                        summaries.append(data)
        except Exception as e:
            print(f"Error loading {file_path}: {e}", file=sys.stderr)

    if not summaries:
        print("No valid weekly_security_summary inputs found.", file=sys.stderr)
        sys.exit(1)

    fleet_summary = aggregate_fleet_summary(summaries)
    print(json.dumps(fleet_summary, indent=2))
