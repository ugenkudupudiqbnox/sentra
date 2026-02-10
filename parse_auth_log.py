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

def main():
    log_path = '/var/log/auth.log'
    ssh_groups = {}  # (user, ip, host, window) -> count
    priv_groups = {} # (user, host, window) -> [commands]

    try:
        with open(log_path, 'r') as f:
            for line in f:
                event = parse_line(line)
                if not event:
                    continue
                
                ts = event['timestamp']
                
                if event['type'] == 'ssh_login':
                    window = int(ts.timestamp() // 300) * 300
                    key = (event['user'], event['ip'], event['hostname'], window)
                    ssh_groups[key] = ssh_groups.get(key, 0) + 1
                
                elif event['type'] == 'privilege_escalation':
                    window = int(ts.timestamp() // 600) * 600
                    key = (event['user'], event['hostname'], window)
                    if key not in priv_groups:
                        priv_groups[key] = []
                    priv_groups[key].append(event['command'])

        # Emit Aggregated Signals
        for (user, ip, host, window), count in ssh_groups.items():
            print(json.dumps({
                "signal": "ssh_login_summary",
                "timestamp": datetime.fromtimestamp(window).isoformat(),
                "hostname": host,
                "user": user,
                "ip": ip,
                "login_count": count
            }))

        for (user, host, window), commands in priv_groups.items():
            print(json.dumps({
                "signal": "privilege_escalation",
                "timestamp": datetime.fromtimestamp(window).isoformat(),
                "hostname": host,
                "user": user,
                "commands": commands
            }))

    except FileNotFoundError:
        print(f"Error: {log_path} not found.", file=sys.stderr)
    except PermissionError:
        print(f"Error: Permission denied reading {log_path}.", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
