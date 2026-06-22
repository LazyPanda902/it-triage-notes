# Configuration Guide

## Default Storage Location

By default, notes are stored in the XDG Base Directory location:

```
~/.local/share/it-triage/notes.jsonl
```

If the `XDG_DATA_HOME` environment variable is set, notes are stored there:

```
$XDG_DATA_HOME/it-triage/notes.jsonl
```

The directory is created automatically on first use.

## Custom Database Location

Use the `--db` flag to specify a custom notes file:

```bash
it-triage --db ~/.config/my-notes/incidents.jsonl list
```

This works with all commands:

```bash
it-triage --db /tmp/test-notes.jsonl add "Title" "Body"
it-triage --db /tmp/test-notes.jsonl list
it-triage --db /tmp/test-notes.jsonl stats
```

## Environment Variables

You can set the database path via environment variable in your shell configuration:

```bash
export IT_TRIAGE_DB=~/.local/share/it-triage/prod-notes.jsonl
it-triage list
```

Then always use the same database without repeating `--db` each time.

### Bash/Zsh Setup

Add to `~/.bashrc` or `~/.zshrc`:

```bash
export IT_TRIAGE_DB=$HOME/.local/share/it-triage/production.jsonl
```

Then reload:

```bash
source ~/.bashrc
```

## File Permissions

The tool does not modify file permissions. For security, restrict your notes database:

```bash
# Make the file readable/writable by owner only
chmod 600 ~/.local/share/it-triage/notes.jsonl

# Or restrict the directory
chmod 700 ~/.local/share/it-triage
```

## Multiple Databases

You can maintain separate incident logs for different purposes:

```bash
# Production incidents
it-triage --db ~/.local/share/it-triage/production.jsonl list

# Test/staging incidents
it-triage --db ~/.local/share/it-triage/staging.jsonl list

# Security incidents
it-triage --db ~/.local/share/it-triage/security.jsonl list --category security
```

## Backup Configuration

The notes file is a plain JSON Lines text file, so you can back it up with standard tools:

```bash
# Copy to backup location
cp ~/.local/share/it-triage/notes.jsonl ~/.local/share/it-triage/notes.jsonl.backup

# Restore from backup
cp ~/.local/share/it-triage/notes.jsonl.backup ~/.local/share/it-triage/notes.jsonl

# Sync to external drive
rsync -av ~/.local/share/it-triage/ /mnt/backup/it-triage/
```

## File Format

The notes file is JSON Lines format (one JSON object per line):

```jsonl
{"id":"abc1234567","title":"Incident 1","body":"Details","category":"azure","severity":"high","status":"open","tags":["tag1"],"created_at":"2026-06-22T10:00:00Z","updated_at":"2026-06-22T10:00:00Z"}
{"id":"def5678901","title":"Incident 2","body":"More details","category":"m365","severity":"medium","status":"in-progress","tags":[],"created_at":"2026-06-22T11:00:00Z","updated_at":"2026-06-22T12:00:00Z"}
```

Each line is independent and can be processed by standard tools:

```bash
# Count total notes
wc -l ~/.local/share/it-triage/notes.jsonl

# View recent incidents (last 5 lines)
tail -5 ~/.local/share/it-triage/notes.jsonl

# Search for a keyword
grep -i "database" ~/.local/share/it-triage/notes.jsonl

# Process with jq
cat ~/.local/share/it-triage/notes.jsonl | jq '.title'
```

## No Additional Configuration

The tool requires no additional configuration files or setup. All options are available via command-line flags. The database location and custom paths are the only configurations needed.
