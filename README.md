# it-triage-notes

A command-line tool for logging and triaging IT support incidents. Organize tickets by category (Azure, Microsoft 365, monitoring, security, network, hardware, or other), severity level, and status to manage your IT support workflow.

## Installation

Clone the repository and install in development mode:

```bash
git clone <repo-url>
cd it-triage-notes
pip install -e .
```

Install with test dependencies:

```bash
pip install -e ".[dev]"
```

## Usage

The tool stores all notes in a JSON Lines journal file at `~/.local/share/it-triage/notes.jsonl` by default. Use the `--db` flag to specify a custom location.

### Add a note

```bash
it-triage add "User cannot access Teams" "User john.doe@example.com reports Teams login fails after password reset" \
  --category m365 --severity high --tags vpn,mfa
```

Available categories: `azure`, `m365`, `monitoring`, `security`, `network`, `hardware`, `other` (default: `other`)

Available severity levels: `low`, `medium` (default), `high`, `critical`

### List notes

View all notes:

```bash
it-triage list
```

Filter by status:

```bash
it-triage list --status open
```

Filter by category:

```bash
it-triage list --category azure --severity high
```

Filter by tag:

```bash
it-triage list --tag vpn
```

Available statuses: `open`, `in-progress`, `resolved`, `closed` (default: all)

### Show note details

```bash
it-triage show abc1234567
```

Output includes title, category, severity, status, tags, timestamps, and full body.

### Update a note

```bash
it-triage update abc1234567 --title "New title" --status in-progress
```

You can update: `--title`, `--body`, `--category`, `--severity`, `--status`, or `--tags`.

### Delete a note

```bash
it-triage delete abc1234567
```

### View statistics

Show counts by status, severity, and category:

```bash
it-triage stats
```

Output as JSON:

```bash
it-triage stats --json
```

## Testing

Run the test suite:

```bash
pytest
```

With verbose output:

```bash
pytest -v
```

Run tests for a specific module:

```bash
pytest tests/test_it_triage.py -v
```

The test suite includes:
- Data model serialization and deserialization
- CRUD operations (add, read, update, delete)
- Filtering by status, category, severity, and tags
- JSON Lines journal persistence
- CLI argument parsing for all subcommands
- Error handling for missing notes and invalid inputs
- Empty database and corrupt line handling

## Data Storage

Notes are stored in JSON Lines format (one note per line) in a local file. Each note contains:

- **id**: 10-character UUID hex string (auto-generated)
- **title**: Short incident title
- **body**: Detailed description or steps taken
- **category**: One of the predefined categories
- **severity**: Incident severity (low, medium, high, critical)
- **status**: Current state (open, in-progress, resolved, closed)
- **tags**: List of comma-separated labels
- **created_at**: ISO 8601 timestamp (UTC)
- **updated_at**: ISO 8601 timestamp (UTC)

The file is append-only for the `add` operation; updates and deletes rewrite the entire file.

## Configuration

Set a custom database location via the `--db` flag:

```bash
it-triage --db /path/to/custom/notes.jsonl add "Title" "Body"
```

Or set the environment variable (if implemented):

```bash
export IT_TRIAGE_DB=/path/to/custom/notes.jsonl
it-triage add "Title" "Body"
```
