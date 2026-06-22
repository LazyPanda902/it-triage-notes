# Testing Guide

## Running Tests

Install test dependencies:

```bash
pip install -e ".[dev]"
```

Run all tests:

```bash
pytest
```

With verbose output:

```bash
pytest -v
```

With coverage report:

```bash
pytest --cov=it_triage tests/
```

## Test Structure

The test suite is organized into five main sections:

### 1. Data Model Tests (test_note_* functions)

Tests the `Note` dataclass functionality:

- Default values for status, tags, id, and timestamps
- Serialization to dict and deserialization from dict
- Summary line badge display for each severity level

**Run only data model tests:**

```bash
pytest tests/test_it_triage.py::test_note -v
```

### 2. NoteStore CRUD Tests (test_store_* functions)

Tests the `NoteStore` class for persistence:

- **add_and_get**: Create a note and retrieve it by ID
- **list_all**: Retrieve all notes
- **list_filter_***: Filter by status, category, severity, and tags
- **get_missing**: Handle missing note ID gracefully
- **update_fields**: Modify specific note fields
- **delete**: Remove a note and verify persistence
- **stats**: Aggregate counts by status, severity, and category
- **ignores_corrupt_lines**: Skip malformed JSON in the file
- **creates_parent_dirs**: Auto-create directory structure

**Run storage tests:**

```bash
pytest tests/test_it_triage.py -k "store" -v
```

### 3. Parser Tests (test_parser_* and test_build_parser_* functions)

Tests the argparse CLI parser:

- Parser construction and program name
- All subcommands (add, list, show, update, delete, stats)
- Default argument values
- Option parsing for all flags
- Invalid input handling (unknown commands, invalid choices)

**Run parser tests:**

```bash
pytest tests/test_it_triage.py -k "parser" -v
```

### 4. Command Handler Tests (test_cmd_* functions)

Tests individual CLI command implementations:

- **cmd_add**: Create notes and verify return codes
- **cmd_list**: Display notes and handle empty results
- **cmd_show**: Display note details or error messages
- **cmd_update**: Modify note fields or handle missing notes
- **cmd_delete**: Remove notes or handle missing notes
- **cmd_stats**: Aggregate statistics in text and JSON format

**Run command tests:**

```bash
pytest tests/test_it_triage.py -k "cmd" -v
```

### 5. Integration Tests (test_main_* functions)

Tests the full CLI pipeline with the `main()` entry point:

- add and list integration
- stats after adding notes
- Show missing note (exit code 1)
- No subcommand provided (exit code 2)

**Run integration tests:**

```bash
pytest tests/test_it_triage.py -k "main" -v
```

## Test Coverage

To see which code paths are tested:

```bash
pytest --cov=it_triage --cov-report=html tests/
```

Then open `htmlcov/index.html` in your browser.

## Common Test Commands

```bash
# Run a single test by name
pytest tests/test_it_triage.py::test_note_defaults -v

# Run all tests matching a pattern
pytest tests/test_it_triage.py -k "add" -v

# Stop on first failure
pytest -x

# Show print statements and logging
pytest -s

# Run with detailed assertion rewriting
pytest -vv

# Run a specific test module
pytest tests/test_it_triage.py
```

## Testing Locally with Custom Database

Create temporary test databases without affecting your real data:

```bash
# Create a test note
it-triage --db /tmp/test.jsonl add "Test incident" "Test details" --category azure --severity high

# List test notes
it-triage --db /tmp/test.jsonl list

# Stats on test database
it-triage --db /tmp/test.jsonl stats

# Cleanup
rm /tmp/test.jsonl
```

## Known Test Fixtures

The test suite uses pytest fixtures for shared test setup:

- **store**: A fresh NoteStore in a temporary directory
- **populated_store**: A NoteStore with three sample incidents (Azure login, M365 license, disk alert)
- **tmp_path**: Pytest's built-in temporary directory (provides isolation)

Fixtures are auto-injected into test functions by argument name.

## Troubleshooting Tests

### Test fails with "module not found"

Install the package in development mode:

```bash
pip install -e .
```

### Permission denied on notes.jsonl

The test suite creates temporary files with proper permissions. If you see permission errors, ensure `/tmp` or your temp directory is writable:

```bash
chmod 1777 /tmp
```

### Tests are slow

Tests use temporary files, which may be slow on some systems. To speed up:

```bash
export TMPDIR=/dev/shm/tmp
mkdir -p /dev/shm/tmp
pytest
```

### Specific test fails but others pass

Check if the failing test has specific preconditions in its `populate_store` fixture or setUp code. Some tests depend on a specific order of notes.

## Manual Testing Checklist

Before a release, manually test:

```bash
# Basic workflow
it-triage add "Manual test" "Testing the CLI"
it-triage list
it-triage stats
it-triage show <note-id>
it-triage update <note-id> --status in-progress
it-triage delete <note-id>

# Filtering
it-triage add "Category test" "Test" --category azure
it-triage list --category azure

# Tags
it-triage add "Tag test" "Test" --tags prod,urgent
it-triage list --tag prod

# Custom database
it-triage --db /tmp/test.jsonl add "Custom" "DB test"
it-triage --db /tmp/test.jsonl list

# JSON output
it-triage stats --json

# Error cases
it-triage show nonexistent  # Should return exit code 1
it-triage delete nonexistent  # Should return exit code 1
```

All commands should complete without errors and produce expected output.
