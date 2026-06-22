"""Argparse CLI entry point for it-triage-notes."""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
from pathlib import Path

from .notes import (
    CATEGORIES,
    SEVERITIES,
    STATUSES,
    Note,
    NoteStore,
    default_store_path,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _store(args: argparse.Namespace) -> NoteStore:
    path = Path(args.db) if getattr(args, "db", None) else default_store_path()
    return NoteStore(path)


def _print_note(note: Note) -> None:
    print(f"  id       : {note.id}")
    print(f"  title    : {note.title}")
    print(f"  category : {note.category}")
    print(f"  severity : {note.severity}")
    print(f"  status   : {note.status}")
    print(f"  tags     : {', '.join(note.tags) if note.tags else '—'}")
    print(f"  created  : {note.created_at}")
    print(f"  updated  : {note.updated_at}")
    print(f"  body     :")
    for line in textwrap.wrap(note.body, width=72):
        print(f"    {line}")


# ---------------------------------------------------------------------------
# Sub-command handlers
# ---------------------------------------------------------------------------


def cmd_add(args: argparse.Namespace) -> int:
    store = _store(args)
    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []
    note = Note(
        title=args.title,
        body=args.body,
        category=args.category,
        severity=args.severity,
        tags=tags,
    )
    store.add(note)
    print(f"Added note {note.id}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    store = _store(args)
    notes = store.list(
        status=args.status,
        category=args.category,
        severity=args.severity,
        tag=args.tag,
    )
    if not notes:
        print("No notes found.")
        return 0
    for note in notes:
        print(note.summary_line())
    print(f"\n{len(notes)} note(s)")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    store = _store(args)
    note = store.get(args.id)
    if note is None:
        print(f"Note '{args.id}' not found.", file=sys.stderr)
        return 1
    _print_note(note)
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    store = _store(args)
    fields: dict = {}
    if args.title:
        fields["title"] = args.title
    if args.body:
        fields["body"] = args.body
    if args.category:
        fields["category"] = args.category
    if args.severity:
        fields["severity"] = args.severity
    if args.status:
        fields["status"] = args.status
    if args.tags is not None:
        fields["tags"] = [t.strip() for t in args.tags.split(",") if t.strip()]
    if not fields:
        print("Nothing to update.", file=sys.stderr)
        return 1
    note = store.update(args.id, **fields)
    if note is None:
        print(f"Note '{args.id}' not found.", file=sys.stderr)
        return 1
    print(f"Updated note {note.id}")
    return 0


def cmd_delete(args: argparse.Namespace) -> int:
    store = _store(args)
    if not store.delete(args.id):
        print(f"Note '{args.id}' not found.", file=sys.stderr)
        return 1
    print(f"Deleted note {args.id}")
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    store = _store(args)
    data = store.stats()
    if args.json:
        print(json.dumps(data, indent=2))
        return 0
    print(f"Total notes : {data['total']}")
    if data["by_status"]:
        print("\nBy status:")
        for k, v in sorted(data["by_status"].items()):
            print(f"  {k:<12} {v}")
    if data["by_severity"]:
        print("\nBy severity:")
        for k, v in sorted(data["by_severity"].items()):
            print(f"  {k:<12} {v}")
    if data["by_category"]:
        print("\nBy category:")
        for k, v in sorted(data["by_category"].items()):
            print(f"  {k:<12} {v}")
    return 0


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        prog="it-triage",
        description="Log and triage IT support incidents from the terminal.",
    )
    root.add_argument(
        "--db",
        metavar="PATH",
        default=None,
        help="Path to the notes journal file (default: ~/.local/share/it-triage/notes.jsonl)",
    )

    sub = root.add_subparsers(dest="command", metavar="<command>")
    sub.required = True

    # --- add ---
    p_add = sub.add_parser("add", help="Create a new triage note")
    p_add.add_argument("title", help="Short incident title")
    p_add.add_argument("body", help="Detailed description or steps taken")
    p_add.add_argument(
        "-c", "--category",
        choices=CATEGORIES, default="other",
        help="Incident category (default: other)",
    )
    p_add.add_argument(
        "-s", "--severity",
        choices=SEVERITIES, default="medium",
        help="Severity level (default: medium)",
    )
    p_add.add_argument(
        "-t", "--tags",
        metavar="TAG[,TAG]",
        default="",
        help="Comma-separated tags",
    )
    p_add.set_defaults(func=cmd_add)

    # --- list ---
    p_list = sub.add_parser("list", help="List notes with optional filters")
    p_list.add_argument("--status", choices=STATUSES, default=None)
    p_list.add_argument("--category", choices=CATEGORIES, default=None)
    p_list.add_argument("--severity", choices=SEVERITIES, default=None)
    p_list.add_argument("--tag", metavar="TAG", default=None)
    p_list.set_defaults(func=cmd_list)

    # --- show ---
    p_show = sub.add_parser("show", help="Show full details for a note")
    p_show.add_argument("id", help="Note ID (first 10 hex chars)")
    p_show.set_defaults(func=cmd_show)

    # --- update ---
    p_upd = sub.add_parser("update", help="Update fields on an existing note")
    p_upd.add_argument("id", help="Note ID to update")
    p_upd.add_argument("--title", default=None)
    p_upd.add_argument("--body", default=None)
    p_upd.add_argument("--category", choices=CATEGORIES, default=None)
    p_upd.add_argument("--severity", choices=SEVERITIES, default=None)
    p_upd.add_argument("--status", choices=STATUSES, default=None)
    p_upd.add_argument("--tags", metavar="TAG[,TAG]", default=None)
    p_upd.set_defaults(func=cmd_update)

    # --- delete ---
    p_del = sub.add_parser("delete", help="Remove a note permanently")
    p_del.add_argument("id", help="Note ID to delete")
    p_del.set_defaults(func=cmd_delete)

    # --- stats ---
    p_stats = sub.add_parser("stats", help="Show aggregate counts")
    p_stats.add_argument("--json", action="store_true", help="Output as JSON")
    p_stats.set_defaults(func=cmd_stats)

    return root


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
