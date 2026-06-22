# Security Policy

## Reporting Security Issues

If you discover a security vulnerability, please email security@example.com with:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Any proposed fix

Do not open a public GitHub issue for security vulnerabilities.

## What Not to Commit

Do not commit or push:

- `.env` files or environment variable files
- API keys, tokens, or credentials
- Passwords or authentication secrets
- Private personal data (real names, email addresses, phone numbers)
- Real customer or incident data from production systems
- Any file matching `.env*` pattern

The `.gitignore` file already excludes common sensitive files.

## Data Security Considerations

### Local Storage

Notes are stored in a local JSON Lines file without encryption. The default location is `~/.local/share/it-triage/notes.jsonl`, which is readable by your user account only.

**Security recommendation**: If storing sensitive incident details (e.g., security vulnerabilities, credential compromises), consider:
- Using a custom `--db` location on an encrypted filesystem
- Restricting file permissions: `chmod 600 notes.jsonl`
- Regularly reviewing stored incidents for sensitive information

### In Transit

This tool is CLI-only and does not communicate with external services. All data remains local.

### No Authentication

The tool does not implement authentication or authorization. Anyone with filesystem access can read and modify the notes database.

## Secure Usage

1. **Anonymize data**: Use generic titles like "User account lockout" instead of real usernames
2. **Avoid secrets**: Do not record API keys, tokens, or passwords in note bodies
3. **File permissions**: Keep your notes file private with `chmod 600 notes.jsonl`
4. **Backup security**: If backing up notes, secure the backup location the same way
5. **Incident details**: For sensitive security incidents, use high-level descriptions without technical details that could aid exploitation

## Dependencies

This tool has zero runtime dependencies. All data handling is performed with Python standard library modules only. The test suite uses pytest, which is a development dependency only.

## Code Review

Security reviews and suggestions are welcome. Please contact the maintainers for security-related questions.
