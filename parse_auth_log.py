import sys
import json
import re
from datetime import datetime

def parse_timestamp(ts_str):
    """
    Parses both RFC5424 (ISO 8601) and traditional syslog timestamps.
    """
    try:
        # Remove any fractional seconds and timezone for simpler parsing if needed,
        # but fromisoformat handles most modern formats.
        return datetime.fromisoformat(ts_str)
    except:
        try:
            # Fallback for traditional syslog: Feb 10 18:19:49
            dt = datetime.strptime(ts_str, "%b %d %H:%M:%S")
            return dt.replace(year=datetime.now().year)
        except:
            return None

def parse_line(line):
    line = line.strip()
    if not line:
        return None

    # Regex for standard syslog format:
    # Also support RFC5424 timestamp: 2026-02-10T18:19:49.784667+05:30
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

    # 1) ssh_login: sshd accepts a publickey
    if program == 'sshd' and 'Accepted publickey' in message:
        # Example: Accepted publickey for stpi from 49.204.255.1 port 27141 ssh2: RSA ...
        match = re.search(r'for\s+(\S+)\s+from\s+(\S+)', message)
        if match:
            return {
                "type": "ssh_login",
                "timestamp": dt,
                "hostname": data['hostname'],
                "user": match.group(1),
                "ip": match.group(2)
            }

    # 2) privilege_escalation: sudo executes a command as root
    if program == 'sudo' and 'COMMAND=' in message and 'USER=root' in message:
        # Example: stpi : TTY=pts/0 ; PWD=/home/stpi ; USER=root ; COMMAND=/usr/bin/tail ...
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
        if data.get("severity") == "high":
            return (
                f"User '{data['user']}' performed administrative changes to system security or user permissions. "
                "These actions are typical during system maintenance but are highlighted to ensure they were intended. "
                "Please consult your technical team if these changes were not authorized."
            )
        else:
            return f"User '{data['user']}' performed routine administrative tasks. This is part of normal system operation. No action is required."
    
    return "Routine security event recorded. No action required."

def main():
    log_path = '/var/log/auth.log'
    ssh_groups = {}        # (user, ip, host, window) -> count
    ssh_access_groups = {} # (user, host, window) -> set of IPs
    priv_groups = {}       # (user, host, window) -> [commands]

    # High-risk command keywords
    HIGH_RISK_KEYWORDS = ['visudo', 'passwd', 'chmod', 'chown', 'rm -rf', 'tee /etc/sudoers', 'usermod']

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
                
                elif event['type'] == 'privilege_escalation':
                    window = int(ts.timestamp() // 600) * 600
                    key = (event['user'], event['hostname'], window)
                    if key not in priv_groups:
                        priv_groups[key] = []
                    
                    # Classify command
                    cmd = event['command']
                    is_high_risk = any(kw in cmd for kw in HIGH_RISK_KEYWORDS)
                    priv_groups[key].append({
                        "command": cmd,
                        "risk": "high" if is_high_risk else "normal"
                    })

        # Emit Aggregated Signals
        # 1) SSH Access Patterns (1-hour)
        for (user, host, window), ips in ssh_access_groups.items():
            pattern = "multi_ip_access" if len(ips) > 1 else "single_ip_access"
            signal_data = {
                "signal": "ssh_access_pattern",
                "timestamp": datetime.fromtimestamp(window).isoformat(),
                "hostname": host,
                "user": user,
                "unique_ips": list(ips),
                "ip_count": len(ips),
                "pattern": pattern
            }
            signal_data["narrative"] = generate_narrative("ssh_access_pattern", signal_data)
            print(json.dumps(signal_data))

        # 2) Privilege Escalation (10-min)
        for (user, host, window), entries in priv_groups.items():
            severity = "high" if any(e['risk'] == 'high' for e in entries) else "normal"
            signal_data = {
                "signal": "privilege_escalation",
                "timestamp": datetime.fromtimestamp(window).isoformat(),
                "hostname": host,
                "user": user,
                "severity": severity,
                "commands": entries
            }
            signal_data["narrative"] = generate_narrative("privilege_escalation", signal_data)
            print(json.dumps(signal_data))

    except FileNotFoundError:
        print(f"Error: {log_path} not found.", file=sys.stderr)
    except PermissionError:
        print(f"Error: Permission denied reading {log_path}.", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
