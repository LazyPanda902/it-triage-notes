# it-triage-notes

it-triage-notes is a zero-dependency Python CLI for logging, filtering, updating, and reviewing IT support incidents from the terminal.

It stores support notes in a local JSON Lines journal and helps organize tickets by category, severity, status, and tags. The tool is designed for helpdesk, sysadmin, homelab, and Microsoft 365 support workflows where quick local triage notes are useful.

## What it does

it-triage-notes helps track support work without needing a database server or ticketing platform:

- Adds incident notes with title, body, category, severity, and tags.
- Lists notes with filters for status, category, severity, and tag.
- Shows full note details by ID.
- Updates title, body, category, severity, status, and tags.
- Deletes notes by ID.
- Prints status, severity, and category statistics.
- Supports JSON stats output for scripts.
- Stores data locally as JSON Lines.
- Uses a custom database path with `--db`.

## Why this project exists

Support work often starts before a formal ticket is complete. A technician may need to capture quick context from a user, track what was tried, record related systems, and come back later with a clear status.

it-triage-notes is a small local-first CLI for that workflow. It is useful for:

- temporary incident notes
- helpdesk triage
- Microsoft 365 support notes
- Azure or identity troubleshooting notes
- monitoring alerts
- network or hardware issue tracking
- homelab support logs

The project is intentionally simple and testable. It demonstrates CLI design, JSON Lines persistence, dataclass modeling, filtering, update/delete workflows, and Python packaging.

## Features

- Local JSON Lines storage
- Append-only add operation
- CRUD workflow for support notes
- Status tracking: `open`, `in-progress`, `resolved`, `closed`
- Severity tracking: `low`, `medium`, `high`, `critical`
- Category tracking: `azure`, `m365`, `monitoring`, `security`, `network`, `hardware`, `other`
- Tag-based filtering
- Human-readable summary output
- JSON statistics output
- Custom database location support
- Test coverage for data model, persistence, filters, CLI parsing, and error handling
- MIT licensed

## Tech stack

- Python 3.11+
- argparse
- dataclasses
- JSON Lines
- pytest
- setuptools packaging
- GitHub Actions CI

## Installation

Clone the repository:

```bash
git clone https://github.com/LazyPanda902/it-triage-notes.git
cd it-triage-notes
```

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install from source:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

Install with development dependencies:

```bash
python -m pip install -e ".[dev]"
```

## Usage

The CLI command is:

```bash
it-triage
```

By default, notes are stored in a local JSON Lines journal at:

```text
~/.local/share/it-triage/notes.jsonl
```

Use `--db` to write to a custom file:

```bash
it-triage --db ./notes.jsonl list
```

## Add a note

```bash
it-triage add \
  "User cannot access Teams" \
  "User reports Teams login fails after password reset." \
  --category m365 \
  --severity high \
  --tags teams,mfa,password-reset
```

Example result:

```text
Added note abc1234567
```

## List notes

List all notes:

```bash
it-triage list
```

Filter by status:

```bash
it-triage list --status open
```

Filter by category and severity:

```bash
it-triage list --category azure --severity high
```

Filter by tag:

```bash
it-triage list --tag mfa
```

Example list output:

```text
[!] abc1234567  [open       ]  [m365      ]  User cannot access Teams
[X] def9876543  [in-progress]  [monitoring]  Disk usage above 90%

2 note(s)
```

## Show note details

```bash
it-triage show abc1234567
```

Example output:

```text
id       : abc1234567
title    : User cannot access Teams
category : m365
severity : high
status   : open
tags     : teams, mfa, password-reset
created  : 2026-06-28T13:00:00Z
updated  : 2026-06-28T13:00:00Z
body     :
  User reports Teams login fails after password reset.
```

## Update a note

Move a note into progress:

```bash
it-triage update abc1234567 --status in-progress
```

Update title, body, status, category, severity, or tags:

```bash
it-triage update abc1234567 \
  --title "Teams login fails after password reset" \
  --severity critical \
  --tags teams,mfa,identity
```

## Delete a note

```bash
it-triage delete abc1234567
```

## View statistics

Human-readable stats:

```bash
it-triage stats
```

JSON stats for scripts:

```bash
it-triage stats --json
```

## Project structure

```text
README.md
pyproject.toml
src/it_triage/
  __init__.py
  __main__.py
  cli.py
  notes.py
tests/
  test_it_triage.py
docs/
  usage-examples.md
  testing-guide.md
  troubleshooting.md
```

## Data storage

Notes are stored as JSON Lines. Each line is one serialized note object.

Each note includes:

- `id`
- `title`
- `body`
- `category`
- `severity`
- `status`
- `tags`
- `created_at`
- `updated_at`

The `add` operation appends one line to the journal. Updates and deletes rewrite the file with the changed note list.

## Testing

Run the test suite:

```bash
pytest
```

Run tests for this package:

```bash
pytest tests/test_it_triage.py -v
```

The tests cover:

- note defaults and serialization
- CRUD operations
- filtering by status, category, severity, and tag
- JSON Lines persistence
- CLI argument parsing
- stats output
- missing note handling
- corrupt journal line handling
- empty database behavior

## Privacy and security

it-triage-notes stores data locally on disk. It does not intentionally send support notes to an external service.

Support notes may contain sensitive operational details, usernames, systems, or incident context. Store the database file in a protected location, avoid committing real notes to Git, and do not paste secrets, tokens, passwords, or private customer information into shared examples.

## Current limitations

- Local file storage only.
- No encryption layer.
- No multi-user locking.
- No remote sync.
- No built-in ticketing-system integration.
- Updates and deletes rewrite the journal file.

## Planned improvements

- Export notes to Markdown or CSV.
- Add richer search.
- Add optional encryption for the local journal.
- Add shell completion.
- Add more example workflows in `docs/`.
- Add optional import/export support for ticketing systems.

## License

MIT License. See `LICENSE`.
