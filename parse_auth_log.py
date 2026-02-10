import sys
import json
import re

def extract_user(program, message):
    """
    Attempts to extract the user from the log message based on the program.
    """
    if program == 'sshd':
        # Patterns for sshd
        match = re.search(r'for\s+(\S+)\s+from', message)
        if match:
            return match.group(1)
        match = re.search(r'User\s+(\S+)\s+from', message)
        if match:
            return match.group(1)
        match = re.search(r'Invalid user\s+(\S+)', message)
        if match:
            return match.group(1)
    elif program == 'sudo':
        # Pattern for sudo: user : TTY=...
        match = re.search(r'^\s*(\S+)\s+:', message)
        if match:
            return match.group(1)
    elif program.lower() == 'cron':
        # Pattern for cron: (user) CMD
        match = re.search(r'^\(([^)]+)\)', message)
        if match:
            return match.group(1)
    
    return None

def parse_line(line):
    line = line.strip()
    if not line:
        return None

    # Regex for standard syslog format:
    # Month Day Time Hostname Program[PID]: Message
    # Example: Feb 10 10:25:21 host sshd[1234]: Accepted password for user1 from 1.2.3.4
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
    
    user = extract_user(program, data['message'])
    
    result = {
        "timestamp": data['timestamp'],
        "hostname": data['hostname'],
        "program": program,
        "user": user,
        "raw_message": data['message']
    }
    return result

def main():
    log_path = '/var/log/auth.log'
    try:
        with open(log_path, 'r') as f:
            for line in f:
                parsed = parse_line(line)
                if parsed:
                    print(json.dumps(parsed))
    except FileNotFoundError:
        print(f"Error: {log_path} not found.", file=sys.stderr)
    except PermissionError:
        print(f"Error: Permission denied reading {log_path}.", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
