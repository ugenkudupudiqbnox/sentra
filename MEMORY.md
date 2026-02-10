# Project Memory

This file tracks the history of tasks, decisions, and current state of the Sentra project to provide context for GitHub Copilot.

## Last Updated: 2026-02-10

## Current State
- `parse_auth_log.py` contains the core logic for parsing `/var/log/auth.log`.
- Successfully extracts users from `sshd`, `sudo`, and `cron` logs.
- Outputs JSON.

## Recent Changes
- Created `.github/copilot-instructions.md` to define project-wide rules and context.
- Initialized `MEMORY.md` to track project evolution.
- Added workflow constraint to `.github/copilot-instructions.md`: no commits or pushes without explicit user instruction.

## TODO / Next Steps
- Add support for more log sources (e.g., `su`, `pau-linux`).
- Implement command-line arguments for input file path and output format.
- Add unit tests for `extract_user` and `parse_line`.
