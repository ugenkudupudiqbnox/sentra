# Project Context: Sentra

Sentra is a lightweight tool for parsing system authentication logs (`/var/log/auth.log`).

## Project Goals
- Efficiently parse syslog-formatted authentication logs.
- Extract key metadata: timestamp, hostname, program, user, and the raw message.
- Output parsed data as JSON for further processing.

## Technology Stack
- **Language**: Python 3.x
- **Libraries**: `json`, `re`, `sys` (standard library only for portability)

## Domain Specific Knowledge
- **Log Source**: Typically `/var/log/auth.log` on Linux systems.
- **Log Formats**: Supports standard syslog formats from `sshd`, `sudo`, and `cron`.

## Coding Preferences
- Use standard libraries where possible to minimize dependencies.
- Use regex for pattern matching in log messages.
- Ensure error handling for file access and parsing issues.

## Workflow & Constraints
- Do not commit or push code changes (check-in) unless explicitly instructed by the user.
