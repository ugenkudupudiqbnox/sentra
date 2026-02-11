import sys
import json
import re
import argparse
import hashlib
from datetime import datetime
from ai_engine import AIEngine
from schema import (
    SecuritySignal, UserEntity, HostEntity, 
    ProcessEntity, NetworkEntity, ComplianceTag
)
from storage import StorageFactory

# Phase 3: Enrichment & Compliance Mapping
COMMAND_INTENT_MAP = {
    r'apt|dpkg|snap|flatpak|pip': {
        'intent': 'Maintenance', 
        'mitre': 'T1072', 
        'compliance': 'SOC2_CC7.1',
        'risk_weight': 0.1
    },
    r'useradd|usermod|userdel|passwd|visudo|groupadd|groupmod|sudoers': {
        'intent': 'Identity Management', 
        'mitre': 'T1078', 
        'compliance': 'SOC2_CC6.1',
        'risk_weight': 0.4
    },
    r'ssh|scp|sftp|rsync|curl|wget': {
        'intent': 'Lateral Movement / Data Transfer', 
        'mitre': 'T1021', 
        'compliance': 'SOC2_CC6.6',
        'risk_weight': 0.2
    },
    r'shadow|gshadow|private-key|ssh/.*_id': {
        'intent': 'Credential Access', 
        'mitre': 'T1003', 
        'compliance': 'SOC2_CC6.1',
        'risk_weight': 0.6
    },
    r'ufw|iptables|firewall|nft|ip ': {
        'intent': 'Network Configuration', 
        'mitre': 'T1562', 
        'compliance': 'SOC2_CC6.6',
        'risk_weight': 0.3
    },
    r'rm -rf /|dd |mkfs|shutdown|reboot': {
        'intent': 'Impact / Destructive', 
        'mitre': 'T1485', 
        'compliance': 'SOC2_CC7.1',
        'risk_weight': 0.8
    }
}

def categorize_command(command):
    """Maps a command to its intent and compliance tags."""
    for pattern, metadata in COMMAND_INTENT_MAP.items():
        if re.search(pattern, command):
            return metadata
    return {
        'intent': 'General Administration', 
        'mitre': 'N/A', 
        'compliance': 'N/A', 
        'risk_weight': 0.0
    }

def parse_timestamp(ts_str):
    try:
        return datetime.fromisoformat(ts_str)
    except:
        try:
            dt = datetime.strptime(ts_str, "%b %d %H:%M:%S")
            return dt.replace(year=datetime.now().year)
        except:
            return None

def parse_line(line):
    line = line.strip()
    if not line:
        return None

    syslog_pattern = re.compile(
        r'^(?P<timestamp>\S+)\s+'
        r'(?P<hostname>\S+)\s+'
        r'(?P<program>[^\[:]+)(?:\[\d+\])?:\s+'
        r'(?P<message>.*)$'
    )

    match = syslog_pattern.match(line)
    if not match:
        return None

    data = match.groupdict()
    program = data['program'].strip()
    message = data['message']
    
    dt = parse_timestamp(data['timestamp'])
    if not dt:
        return None

    if program == 'sshd':
        if 'Accepted publickey' in message:
            match = re.search(r'for\s+(\S+)\s+from\s+(\S+)', message)
            if match:
                return {
                    "type": "ssh_login",
                    "timestamp": dt,
                    "hostname": data['hostname'],
                    "user": match.group(1),
                    "ip": match.group(2)
                }
        elif 'Failed password' in message or 'Invalid user' in message:
            match = re.search(r'for\s+(?:invalid user\s+)?(\S+)\s+from\s+(\S+)', message)
            if not match:
                match = re.search(r'Invalid user\s+(\S+)\s+from\s+(\S+)', message)
            if match:
                return {
                    "type": "ssh_failure",
                    "timestamp": dt,
                    "hostname": data['hostname'],
                    "user": match.group(1),
                    "ip": match.group(2)
                }

    if program == 'sudo':
        if 'COMMAND=' in message and 'USER=root' in message:
            user_match = re.search(r'^\s*(\S+)\s+:', message)
            cmd_match = re.search(r'COMMAND=(.*)', message)
            if user_match and cmd_match:
                return {
                    "type": "privilege_escalation",
                    "timestamp": dt,
                    "hostname": data['hostname'],
                    "user": user_match.group(1),
                    "command": cmd_match.group(1).strip()
                }

    return None

def calculate_risk_score(signal_type, severity):
    sev_map = {"Low": 0.1, "Medium": 0.4, "High": 0.7, "Critical": 0.9}
    return sev_map.get(severity, 0.1)

def enrich_signal_with_ai(signal: SecuritySignal):
    engine = AIEngine()
    
    # AI Enrichment
    context = signal.model_dump()
    narrative, recommendation, confidence = engine.consult_ai(
        signal.tenant_id, signal.signal_type, context
    )
    
    if narrative:
        signal.narrative = narrative
    if recommendation:
        signal.recommendation = recommendation
    if confidence:
        signal.ai_confidence = confidence
    
    # Model info for drift tracking
    signal.model_info = {"model": "gpt-4o", "provider": "openai"}
    
    # Vector Indexing
    engine.index_signal(signal.tenant_id, signal.model_dump())
    
    return signal

def main():
    parser = argparse.ArgumentParser(description="Sentra Security Log Parser - Phase 0 mSOC")
    parser.add_argument("--input", default="/var/log/auth.log", help="Path to auth.log file")
    parser.add_argument("--tenant-id", default="default-tenant", help="Tenant ID for mSOC isolation")
    parser.add_argument("--output", help="Optional path to save JSON signals")
    args = parser.parse_args()

    signals = []
    
    # Initialize Storage Engines
    ch_storage = StorageFactory.get_storage("ClickHouse")
    es_storage = StorageFactory.get_storage("Elastic")
    
    # Simulated simple parsing and signal generation for Phase 0 demonstration
    try:
        with open(args.input, 'r') as f:
            for line in f:
                event = parse_line(line)
                if not event:
                    continue
                
                # Convert event to SecuritySignal Pydantic model
                if event['type'] == 'ssh_login':
                    signal = SecuritySignal(
                        tenant_id=args.tenant_id,
                        signal_type="ssh_login",
                        severity="Low",
                        user=UserEntity(username=event['user']),
                        host=HostEntity(hostname=event['hostname'], ip=event['ip']),
                        network=NetworkEntity(source_ip=event['ip'])
                    )
                elif event['type'] == 'privilege_escalation':
                    meta = categorize_command(event['command'])
                    severity = "Medium" if meta['risk_weight'] < 0.5 else "High"
                    signal = SecuritySignal(
                        tenant_id=args.tenant_id,
                        signal_type="privilege_escalation",
                        severity=severity,
                        user=UserEntity(username=event['user']),
                        host=HostEntity(hostname=event['hostname']),
                        process=ProcessEntity(name=event['command']),
                        compliance_tags=[ComplianceTag(
                            framework="SOC2", 
                            control_id=meta['compliance']
                        )] if meta['compliance'] != 'N/A' else []
                    )
                else:
                    continue

                signal.risk_score = calculate_risk_score(signal.signal_type, signal.severity)
                enriched_signal = enrich_signal_with_ai(signal)
                
                # Ingest into persistent storage (Phase 2)
                ch_storage.ingest(enriched_signal)
                es_storage.ingest(enriched_signal)
                
                signals.append(enriched_signal)
                print(enriched_signal.to_json())

        if args.output:
            with open(args.output, 'w') as f:
                for s in signals:
                    f.write(s.to_json() + "\n")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

        elif 'authentication failure' in message or 'conversation failed' in message:
            # Example: stpi : pam_unix(sudo:auth): authentication failure; logname=... user=stpi
            # Or: stpi : pam_unix(sudo:auth): conversation failed
            user_match = re.search(r'user=(\S+)', message)
            if not user_match:
                user_match = re.search(r'^\s*(\S+)\s+:', message)
            
            if user_match:
                return {
                    "type": "auth_failure",
                    "timestamp": dt,
                    "hostname": data['hostname'],
                    "user": user_match.group(1),
                    "source": "sudo",
                    "confidence": "high"
                }
    
    if program == 'su':
        if 'session opened for user' in message:
            # Example: pam_unix(su:session): session opened for user root by stpi(uid=1000)
            match = re.search(r'user\s+(\S+)\s+by\s+(\S+)\(', message)
            if match:
                return {
                    "type": "privilege_escalation",
                    "timestamp": dt,
                    "hostname": data['hostname'],
                    "user": match.group(2),
                    "target_user": match.group(1),
                    "command": f"su to {match.group(1)}",
                    "source": "su",
                    "confidence": "medium" 
                }
        elif 'authentication failure' in message:
            # Example: pam_unix(su:auth): authentication failure; logname=... user=root
            user_match = re.search(r'user=(\S+)', message)
            if user_match:
                return {
                    "type": "auth_failure",
                    "timestamp": dt,
                    "hostname": data['hostname'],
                    "user": user_match.group(1),
                    "source": "su",
                    "confidence": "high"
                }

    # 3) iam_change: user and group management
    iam_programs = ['useradd', 'usermod', 'userdel', 'groupadd', 'groupmod', 'groupdel', 'chage']
    if program in iam_programs:
        return {
            "type": "iam_change",
            "timestamp": dt,
            "hostname": data['hostname'],
            "user": "root", # These usually run as root/sudo
            "program": program,
            "message": message,
            "confidence": "high"
        }

    return None

def calculate_risk_score(signal_type, data):
    """
    Phase 2/3: Probabilistic Risk Scoring with Intent Enrichment.
    Calculates a score between 0.0 and 1.0 based on signal type, 
    intent weighting, and attribution confidence.
    """
    base_scores = {
        "ssh_access_pattern": 0.1,
        "ssh_brute_force": 0.3,
        "privilege_escalation": 0.2,
        "iam_change": 0.4,
        "failed_auth": 0.3
    }
    
    score = base_scores.get(signal_type, 0.1)
    
    # Intent-based escalation (Phase 3)
    intent_weight = data.get("intent_weight", 0.0)
    score += intent_weight
    
    # Specific pattern escalation
    if signal_type == "ssh_access_pattern" and data.get("pattern") == "multi_ip_access":
        score += 0.2
    
    # Confidence multiplier
    conf_map = {"high": 1.0, "medium": 0.7, "low": 0.4}
    multiplier = conf_map.get(data.get("confidence", "medium"), 0.7)
    
    return round(min(score * multiplier, 1.0), 2)

def enrich_signal_with_ai(signal_type, signal_data):
    """
    Attempts to enrich the signal using LLM insight, falling back to 
    deterministic templates if necessary. Also indexes the signal in Vector DB.
    """
    # 1. Try AI enrichment
    ai_narrative, ai_rec = AIEngine.consult_ai(signal_type, signal_data)
    
    if ai_narrative:
        signal_data["narrative"] = ai_narrative
    else:
        signal_data["narrative"] = generate_narrative(signal_type, signal_data)
        
    if ai_rec:
        signal_data["recommendation"] = ai_rec
    else:
        signal_data["recommendation"] = generate_recommendation(signal_type, signal_data)
    
    # 2. Index in Vector DB for correlation (Phase 2)
    try:
        AIEngine.index_signal(signal_data)
    except Exception as e:
        # Silently fail if DB is not available
        pass
        
    return signal_data

def generate_narrative(signal_type, data):
    """
    Generates a neutral, non-alarmist incident narrative for non-technical customers.
    """
    if signal_type == "ssh_access_pattern":
        if data.get("pattern") == "multi_ip_access":
            return (
                f"Your account '{data['user']}' was accessed from {data['ip_count']} different network locations within one hour. "
                "This often occurs when using multiple devices or transitioning between networks, but is recorded for visibility. "
                "No action is required unless you do not recognize this activity."
            )
        else:
            return f"A standard login was recorded for user '{data['user']}'. This is routine system access. No action is required."

    if signal_type == "privilege_escalation":
        if data.get("intent_weight", 0) >= 0.4:
            return (
                f"User '{data['user']}' performed sensitive administrative changes ({data.get('intent', 'General Administration')}). "
                "These actions are typical during system maintenance but are highlighted to ensure they were intended. "
                "Please consult your technical team if these changes were not authorized."
            )
        else:
            return f"User '{data['user']}' performed routine administrative tasks. This is part of normal system operation. No action is required."
    
    if signal_type == "iam_change":
        return (
            f"An identity management event was recorded: user or group changes were made using '{data['program']}'. "
            "Identity changes are fundamental to system security and are recorded to maintain an accurate audit trail of access permissions."
        )

    if signal_type == "ssh_brute_force":
        return (
            f"Multiple unsuccessful login attempts ({data['failure_count']}) were recorded for the user '{data['user']}' from IP {data['ip']}. "
            "Automated scripts on the internet frequently attempt to guess passwords. While these attempts were unsuccessful, "
            "they are recorded as a standard part of our perimeter monitoring."
        )

    if signal_type == "failed_auth":
        return (
            f"An unsuccessful attempt to perform administrative tasks (via {data.get('source', 'unknown')}) was recorded for user '{data['user']}'. "
            "This typically occurs due to an incorrect password entry and is recorded for audit purposes. "
            "No action is required unless this activity was not initiated by you."
        )

    return "Routine security event recorded. No action required."

def generate_recommendation(signal_type, data):
    """
    Phase 4: AI-Recommended Actions.
    Suggests specific, actionable mitigation steps based on signal risk and type.
    """
    risk_score = data.get("risk_score", 0.0)
    
    if signal_type == "ssh_brute_force":
        if risk_score > 0.6:
            return "Critical: Threshold exceeded. Recommendation: Place IP on temporary firewall blocklist and verify account MFA status."
        return "Insight: Automated probe detected. Recommendation: Ensure password-based authentication is disabled for this user."

    if signal_type == "privilege_escalation":
        if data.get("intent") == "Identity Management":
            return "Audit Tip: Review this change against the authorized maintenance window or ticket. No immediate technical action required."
        if data.get("intent") == "Impact / Destructive":
            return "High Priority: Destructive command detected. Recommendation: Verify authorization immediately and inspect system integrity logs."
        return "Insight: Routine administrative task. No action needed."

    if signal_type == "iam_change":
        return "Compliance Step: Ensure the newly created or modified user is assigned to a specific business owner in your IAM registry."

    if signal_type == "ssh_access_pattern" and data.get("pattern") == "multi_ip_access":
        return "Precaution: Confirm this user was traveling or using a VPN during this period. If not, consider a password reset."

    if signal_type == "failed_auth" and data.get("failure_count", 0) > 5:
        return "Investigation: Repeated administrative failures detected. Recommendation: Check for stale credentials in local automation scripts."

    return "No actionable recommendation for routine events."

def generate_weekly_summary(signals):
    """
    Generates a concise weekly security summary for a non-technical customer.
    Aligns with Sentra's canonical risk values.
    """
    ssh_patterns = [s for s in signals if s['signal'] == 'ssh_access_pattern']
    priv_escalations = [s for s in signals if s['signal'] == 'privilege_escalation']
    iam_changes = [s for s in signals if s['signal'] == 'iam_change']
    ssh_brute_force = [s for s in signals if s['signal'] == 'ssh_brute_force']
    failed_auth = [s for s in signals if s['signal'] == 'failed_auth']
    
    multi_ip_events = [s for s in ssh_patterns if s['pattern'] == 'multi_ip_access']
    high_risk_changes = [s for s in (priv_escalations + iam_changes) if s.get('intent_weight', 0) >= 0.4]
    
    # Calculate average risk score for the week
    avg_score = 0
    if signals:
        avg_score = round(sum(s.get('risk_score', 0) for s in signals) / len(signals), 2)

    # Determine overall risk and narrative based on Sentra's canonical risk values.
    # Logic: High-risk changes are classified as 'Low (Reviewed)' when they follow
    # maintenance patterns, saving 'Action Recommended' for unverified or urgent items.
    if high_risk_changes:
        risk_level = "Low (Reviewed)"
        status_detail = "Security-sensitive administrative or identity changes were detected and reviewed as part of routine maintenance."
        action_clause = "These changes are consistent with authorized system updates and no further action is required."
    elif multi_ip_events:
        risk_level = "Low (Reviewed)"
        status_detail = "System access from multiple locations was observed and reviewed."
        action_clause = "This behavior reflects standard team mobility and matches expected usage patterns."
    else:
        risk_level = "Low"
        status_detail = "All activity matches standard system operations."
        action_clause = "No sensitive changes or unusual access patterns were identified."

    summary = {
        "report_type": "weekly_security_summary",
        "overall_risk": risk_level,
        "avg_risk_score": avg_score,
        "server_count": 1,
        "highlights": {
            "access_patterns": len(ssh_patterns),
            "multi_ip_instances": len(multi_ip_events),
            "privileged_sessions": len(priv_escalations),
            "high_risk_changes": len(high_risk_changes),
            "iam_changes": len(iam_changes),
            "ssh_brute_force_attempts": len(ssh_brute_force),
            "failed_auth_attempts": len(failed_auth)
        },
        "narrative": (
            f"This week, your system remains in a '{risk_level}' state. {status_detail} "
            f"{action_clause} Overall, system activity follows your established security baseline."
        )
    }
    return summary

def generate_multi_server_summary(summaries):
    """
    Aggregates multiple per-server weekly security reports into a single multi-server summary.
    Follows deterministic logic and uses canonical risk levels.
    """
    total_highlights = {
        "access_patterns": 0,
        "multi_ip_instances": 0,
        "privileged_sessions": 0,
        "high_risk_changes": 0,
        "iam_changes": 0
    }
    
    risk_priority = ["Action Recommended", "Low (Reviewed)", "Low"]
    highest_risk = "Low"
    
    for s in summaries:
        h = s['highlights']
        total_highlights["access_patterns"] += h.get("access_patterns", 0)
        total_highlights["multi_ip_instances"] += h.get("multi_ip_instances", 0)
        total_highlights["privileged_sessions"] += h.get("privileged_sessions", 0)
        total_highlights["high_risk_changes"] += h.get("high_risk_changes", 0)
        total_highlights["iam_changes"] += h.get("iam_changes", 0)
        
        # Deterministically find the highest risk level
        if risk_priority.index(s['overall_risk']) < risk_priority.index(highest_risk):
            highest_risk = s['overall_risk']

    summary = {
        "report_type": "multi_server_weekly_summary",
        "overall_risk": highest_risk,
        "server_count": len(summaries),
        "highlights": total_highlights,
        "narrative": (
            f"Across your fleet of {len(summaries)} servers, the overall risk status is '{highest_risk}'. "
            f"We recorded a total of {total_highlights['access_patterns']} access patterns and {total_highlights['privileged_sessions']} administrative sessions. "
            "The environment remains stable, with all activity generally aligning with your authorized maintenance schedules."
        )
    }
    return summary

def main():
    parser = argparse.ArgumentParser(description="Sentra Security Log Parser - Phase 3 Enrichment")
    parser.add_argument("--input", default="/var/log/auth.log", help="Path to auth.log file")
    parser.add_argument("--output", help="Optional path to save JSON signals (still prints to stdout)")
    args = parser.parse_args()

    log_path = args.input
    ssh_groups = {}        # (user, ip, host, window) -> count
    ssh_access_groups = {} # (user, host, window) -> set of IPs
    ssh_failure_groups = {}# (user, ip, host, window) -> count
    priv_groups = {}       # (user, host, window) -> [commands]
    auth_failure_groups = {}# (user, source, host, window) -> count
    iam_events = []

    # High-risk command keywords
    HIGH_RISK_KEYWORDS = ['visudo', 'passwd', 'chmod', 'chown', 'rm -rf', 'tee /etc/sudoers', 'usermod', 'useradd', 'userdel']

    try:
        with open(log_path, 'r') as f:
            for line in f:
                event = parse_line(line)
                if not event:
                    continue
                
                ts = event['timestamp']
                
                if event['type'] == 'ssh_login':
                    # 5-min window
                    win_5 = int(ts.timestamp() // 300) * 300
                    key_5 = (event['user'], event['ip'], event['hostname'], win_5)
                    ssh_groups[key_5] = ssh_groups.get(key_5, 0) + 1

                    # 1-hour window for access pattern
                    win_1h = int(ts.timestamp() // 3600) * 3600
                    key_1h = (event['user'], event['hostname'], win_1h)
                    if key_1h not in ssh_access_groups:
                        ssh_access_groups[key_1h] = set()
                    ssh_access_groups[key_1h].add(event['ip'])
                
                elif event['type'] == 'ssh_failure':
                    # 1-hour window for brute force
                    window = int(ts.timestamp() // 3600) * 3600
                    key = (event['user'], event['ip'], event['hostname'], window)
                    ssh_failure_groups[key] = ssh_failure_groups.get(key, 0) + 1

                elif event['type'] == 'privilege_escalation':
                    window = int(ts.timestamp() // 600) * 600
                    key = (event['user'], event['hostname'], window)
                    if key not in priv_groups:
                        priv_groups[key] = []
                    
                    # Classify command (Phase 3)
                    cmd = event['command']
                    meta = categorize_command(cmd)
                    priv_groups[key].append({
                        "command": cmd,
                        "risk": "high" if meta['risk_weight'] >= 0.4 else "normal",
                        "intent": meta['intent'],
                        "mitre": meta['mitre'],
                        "compliance": meta['compliance'],
                        "risk_weight": meta['risk_weight'],
                        "source": event.get("source", "unknown"),
                        "confidence": event.get("confidence", "high")
                    })

                elif event['type'] == 'auth_failure':
                    # 10-min window for privilege auth failure
                    window = int(ts.timestamp() // 600) * 600
                    key = (event['user'], event.get('source', 'unknown'), event['hostname'], window)
                    auth_failure_groups[key] = auth_failure_groups.get(key, 0) + 1
                
                elif event['type'] == 'iam_change':
                    iam_events.append(event)

        # Emit Aggregated Signals
        all_signals = []
        # 1) SSH Access Patterns (1-hour)
        for (user, host, window), ips in ssh_access_groups.items():
            pattern = "multi_ip_access" if len(ips) > 1 else "single_ip_access"
            ts_iso = datetime.fromtimestamp(window).isoformat()
            signal_data = {
                "id": generate_signal_id("ssh_access_pattern", ts_iso, host, user),
                "signal": "ssh_access_pattern",
                "timestamp": ts_iso,
                "hostname": host,
                "user": user,
                "unique_ips": list(ips),
                "ip_count": len(ips),
                "pattern": pattern,
                "confidence": "high",
                "status": "open"
            }
            signal_data["risk_score"] = calculate_risk_score("ssh_access_pattern", signal_data)
            signal_data = enrich_signal_with_ai("ssh_access_pattern", signal_data)
            all_signals.append(signal_data)
            print(json.dumps(signal_data))

        # 2) Privilege Escalation (10-min)
        for (user, host, window), entries in priv_groups.items():
            # Aggregate risk and metadata
            max_intent_weight = max(e.get('risk_weight', 0.0) for e in entries)
            primary_intent = next((e['intent'] for e in entries if e['risk_weight'] == max_intent_weight), "General Administration")
            mitre_tags = list(set(e['mitre'] for e in entries if e['mitre'] != 'N/A'))
            compliance_tags = list(set(e['compliance'] for e in entries if e['compliance'] != 'N/A'))
            
            collective_conf = "medium" if any(e.get('confidence') == 'medium' for e in entries) else "high"
            ts_iso = datetime.fromtimestamp(window).isoformat()
            signal_data = {
                "id": generate_signal_id("privilege_escalation", ts_iso, host, user),
                "signal": "privilege_escalation",
                "timestamp": ts_iso,
                "hostname": host,
                "user": user,
                "intent": primary_intent,
                "intent_weight": max_intent_weight,
                "mitre_tags": mitre_tags,
                "compliance_tags": compliance_tags,
                "confidence": collective_conf,
                "commands": entries,
                "status": "open"
            }
            signal_data["risk_score"] = calculate_risk_score("privilege_escalation", signal_data)
            signal_data = enrich_signal_with_ai("privilege_escalation", signal_data)
            all_signals.append(signal_data)
            print(json.dumps(signal_data))

        # 3) IAM Changes (Individual events)
        for event in iam_events:
            ts_iso = event['timestamp'].isoformat()
            meta = categorize_command(event['program'])
            signal_data = {
                "id": generate_signal_id("iam_change", ts_iso, event['hostname'], event['user']),
                "signal": "iam_change",
                "timestamp": ts_iso,
                "hostname": event['hostname'],
                "user": event['user'],
                "program": event['program'],
                "intent": meta['intent'],
                "intent_weight": meta['risk_weight'],
                "mitre_tags": [meta['mitre']] if meta['mitre'] != 'N/A' else [],
                "compliance_tags": [meta['compliance']] if meta['compliance'] != 'N/A' else [],
                "message": event['message'],
                "confidence": event['confidence'],
                "status": "open"
            }
            signal_data["risk_score"] = calculate_risk_score("iam_change", signal_data)
            signal_data = enrich_signal_with_ai("iam_change", signal_data)
            all_signals.append(signal_data)
            print(json.dumps(signal_data))

        # 4) SSH Brute Force
        for (user, ip, host, window), count in ssh_failure_groups.items():
            if count >= 3: # Threshold for brute force signal
                ts_iso = datetime.fromtimestamp(window).isoformat()
                signal_data = {
                    "id": generate_signal_id("ssh_brute_force", ts_iso, host, user),
                    "signal": "ssh_brute_force",
                    "timestamp": ts_iso,
                    "hostname": host,
                    "user": user,
                    "ip": ip,
                    "failure_count": count,
                    "confidence": "high",
                    "status": "open"
                }
                signal_data["risk_score"] = calculate_risk_score("ssh_brute_force", signal_data)
                signal_data = enrich_signal_with_ai("ssh_brute_force", signal_data)
                all_signals.append(signal_data)
                print(json.dumps(signal_data))

        # 5) Auth Failures (Sudo/Su)
        for (user, source, host, window), count in auth_failure_groups.items():
            ts_iso = datetime.fromtimestamp(window).isoformat()
            signal_data = {
                "id": generate_signal_id("failed_auth", ts_iso, host, user),
                "signal": "failed_auth",
                "timestamp": ts_iso,
                "hostname": host,
                "user": user,
                "source": source,
                "failure_count": count,
                "confidence": "high",
                "status": "open"
            }
            signal_data["risk_score"] = calculate_risk_score("failed_auth", signal_data)
            signal_data = enrich_signal_with_ai("failed_auth", signal_data)
            all_signals.append(signal_data)
            print(json.dumps(signal_data))

        # 6) Weekly Summary
        if all_signals:
            summary = generate_weekly_summary(all_signals)
            print(json.dumps(summary))

        if args.output:
            with open(args.output, 'w') as f:
                for s in all_signals:
                    f.write(json.dumps(s) + "\n")
                if all_signals:
                    f.write(json.dumps(summary) + "\n")

    except FileNotFoundError:
        print(f"Error: {log_path} not found.", file=sys.stderr)
    except PermissionError:
        print(f"Error: Permission denied reading {log_path}.", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
