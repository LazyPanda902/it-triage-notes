"""Tests for it_triage CLI and core notes logic."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from it_triage.cli import build_parser, cmd_add, cmd_delete, cmd_list, cmd_show, cmd_stats, cmd_update, main
from it_triage.notes import Note, NoteStore


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def store(tmp_path: Path) -> NoteStore:
    return NoteStore(tmp_path / "notes.jsonl")


@pytest.fixture()
def populated_store(store: NoteStore) -> NoteStore:
    store.add(Note(title="Azure login fail", body="User cannot sign in", category="azure", severity="high", tags=["azure-ad", "login"]))
    store.add(Note(title="M365 license issue", body="License not assigned", category="m365", severity="medium"))
    store.add(Note(title="Disk alert", body="Disk usage above 90%", category="monitoring", severity="critical"))
    return store


# ---------------------------------------------------------------------------
# Note dataclass
# ---------------------------------------------------------------------------


def test_note_defaults():
    note = Note(title="Test", body="Body", category="other", severity="low")
    assert note.status == "open"
    assert note.tags == []
    assert len(note.id) == 10
    assert note.created_at
    assert note.updated_at


def test_note_to_dict_roundtrip():
    note = Note(title="Roundtrip", body="Some body", category="security", severity="critical", tags=["tag1"])
    recovered = Note.from_dict(note.to_dict())
    assert recovered.id == note.id
    assert recovered.title == note.title
    assert recovered.tags == ["tag1"]


def test_note_summary_line_badges():
    for severity, badge in [("low", "[ ]"), ("medium", "[~]"), ("high", "[!]"), ("critical", "[X]")]:
        note = Note(title="T", body="B", category="other", severity=severity)
        line = note.summary_line()
        assert badge in line
        assert note.id in line


# ---------------------------------------------------------------------------
# NoteStore CRUD
# ---------------------------------------------------------------------------


def test_store_add_and_get(store: NoteStore):
    note = Note(title="Add test", body="Body", category="network", severity="low")
    store.add(note)
    retrieved = store.get(note.id)
    assert retrieved is not None
    assert retrieved.title == "Add test"


def test_store_list_all(populated_store: NoteStore):
    notes = populated_store.list()
    assert len(notes) == 3


def test_store_list_filter_status(populated_store: NoteStore):
    note_id = populated_store.list()[0].id
    populated_store.update(note_id, status="resolved")
    resolved = populated_store.list(status="resolved")
    assert len(resolved) == 1


def test_store_list_filter_category(populated_store: NoteStore):
    notes = populated_store.list(category="azure")
    assert len(notes) == 1
    assert notes[0].category == "azure"


def test_store_list_filter_severity(populated_store: NoteStore):
    notes = populated_store.list(severity="critical")
    assert len(notes) == 1
    assert notes[0].severity == "critical"


def test_store_list_filter_tag(populated_store: NoteStore):
    notes = populated_store.list(tag="azure-ad")
    assert len(notes) == 1


def test_store_get_missing(store: NoteStore):
    assert store.get("nonexistent") is None


def test_store_update_fields(populated_store: NoteStore):
    note = populated_store.list()[0]
    updated = populated_store.update(note.id, title="New Title", status="in-progress")
    assert updated is not None
    assert updated.title == "New Title"
    assert updated.status == "in-progress"
    assert populated_store.get(note.id).title == "New Title"


def test_store_update_missing(store: NoteStore):
    result = store.update("doesnotexist", title="X")
    assert result is None


def test_store_delete(populated_store: NoteStore):
    note = populated_store.list()[0]
    deleted = populated_store.delete(note.id)
    assert deleted is True
    assert populated_store.get(note.id) is None
    assert len(populated_store.list()) == 2


def test_store_delete_missing(store: NoteStore):
    assert store.delete("nosuchid") is False


def test_store_stats(populated_store: NoteStore):
    data = populated_store.stats()
    assert data["total"] == 3
    assert "by_status" in data
    assert "by_severity" in data
    assert "by_category" in data
    assert data["by_status"]["open"] == 3


def test_store_stats_empty(store: NoteStore):
    data = store.stats()
    assert data["total"] == 0
    assert data["by_status"] == {}


def test_store_ignores_corrupt_lines(tmp_path: Path):
    db = tmp_path / "notes.jsonl"
    db.write_text('{"bad": true}\n{"also": "bad", "missing_fields": 1}\n', encoding="utf-8")
    store = NoteStore(db)
    assert store.list() == []


def test_store_creates_parent_dirs(tmp_path: Path):
    db = tmp_path / "deep" / "nested" / "notes.jsonl"
    NoteStore(db)
    assert db.exists()


# ---------------------------------------------------------------------------
# Parser construction
# ---------------------------------------------------------------------------


def test_build_parser_constructs():
    parser = build_parser()
    assert parser is not None
    assert parser.prog == "it-triage"


def test_parser_add_defaults(tmp_path):
    parser = build_parser()
    args = parser.parse_args(["--db", str(tmp_path / "n.jsonl"), "add", "Title", "Body"])
    assert args.command == "add"
    assert args.title == "Title"
    assert args.body == "Body"
    assert args.category == "other"
    assert args.severity == "medium"
    assert args.tags == ""


def test_parser_add_all_options(tmp_path):
    parser = build_parser()
    args = parser.parse_args([
        "--db", str(tmp_path / "n.jsonl"),
        "add", "Incident", "Details",
        "--category=azure", "--severity=high", "--tags=vpn,mfa",
    ])
    assert args.category == "azure"
    assert args.severity == "high"
    assert args.tags == "vpn,mfa"


def test_parser_list_defaults(tmp_path):
    parser = build_parser()
    args = parser.parse_args(["--db", str(tmp_path / "n.jsonl"), "list"])
    assert args.status is None
    assert args.category is None
    assert args.severity is None
    assert args.tag is None


def test_parser_list_filters(tmp_path):
    parser = build_parser()
    args = parser.parse_args([
        "--db", str(tmp_path / "n.jsonl"),
        "list", "--status=open", "--category=security", "--severity=low", "--tag=vpn",
    ])
    assert args.status == "open"
    assert args.category == "security"
    assert args.severity == "low"
    assert args.tag == "vpn"


def test_parser_show(tmp_path):
    parser = build_parser()
    args = parser.parse_args(["--db", str(tmp_path / "n.jsonl"), "show", "abc123"])
    assert args.command == "show"
    assert args.id == "abc123"


def test_parser_update(tmp_path):
    parser = build_parser()
    args = parser.parse_args([
        "--db", str(tmp_path / "n.jsonl"),
        "update", "abc123", "--title=New", "--status=resolved",
    ])
    assert args.id == "abc123"
    assert args.title == "New"
    assert args.status == "resolved"


def test_parser_delete(tmp_path):
    parser = build_parser()
    args = parser.parse_args(["--db", str(tmp_path / "n.jsonl"), "delete", "abc123"])
    assert args.command == "delete"
    assert args.id == "abc123"


def test_parser_stats_json_flag(tmp_path):
    parser = build_parser()
    args = parser.parse_args(["--db", str(tmp_path / "n.jsonl"), "stats", "--json"])
    assert args.json is True


def test_parser_stats_no_json_flag(tmp_path):
    parser = build_parser()
    args = parser.parse_args(["--db", str(tmp_path / "n.jsonl"), "stats"])
    assert args.json is False


def test_parser_unknown_subcommand_exits():
    parser = build_parser()
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["notacommand"])
    assert exc_info.value.code == 2


def test_parser_invalid_category_exits():
    parser = build_parser()
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["add", "T", "B", "--category=invalid"])
    assert exc_info.value.code == 2


def test_parser_invalid_severity_exits():
    parser = build_parser()
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["add", "T", "B", "--severity=extreme"])
    assert exc_info.value.code == 2


def test_parser_invalid_status_exits():
    parser = build_parser()
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["list", "--status=pending"])
    assert exc_info.value.code == 2


# ---------------------------------------------------------------------------
# cmd_* handlers via Namespace
# ---------------------------------------------------------------------------


def _ns(tmp_path, **kwargs):
    defaults = dict(db=str(tmp_path / "notes.jsonl"))
    defaults.update(kwargs)
    import argparse
    return argparse.Namespace(**defaults)


def test_cmd_add_returns_zero(tmp_path, capsys):
    ns = _ns(tmp_path, title="Incident", body="Details", category="azure", severity="high", tags="")
    rc = cmd_add(ns)
    assert rc == 0
    out = capsys.readouterr().out
    assert "Added note" in out


def test_cmd_add_persists_note(tmp_path):
    ns = _ns(tmp_path, title="Persist test", body="Body", category="security", severity="low", tags="tag1,tag2")
    cmd_add(ns)
    store = NoteStore(Path(tmp_path / "notes.jsonl"))
    notes = store.list()
    assert len(notes) == 1
    assert notes[0].title == "Persist test"
    assert notes[0].tags == ["tag1", "tag2"]


def test_cmd_list_empty(tmp_path, capsys):
    ns = _ns(tmp_path, status=None, category=None, severity=None, tag=None)
    rc = cmd_list(ns)
    assert rc == 0
    assert "No notes found" in capsys.readouterr().out


def test_cmd_list_shows_notes(tmp_path, capsys):
    store = NoteStore(tmp_path / "notes.jsonl")
    store.add(Note(title="Azure incident", body="Body", category="azure", severity="high"))
    ns = _ns(tmp_path, status=None, category=None, severity=None, tag=None)
    rc = cmd_list(ns)
    assert rc == 0
    assert "Azure incident" in capsys.readouterr().out


def test_cmd_show_existing(tmp_path, capsys):
    store = NoteStore(tmp_path / "notes.jsonl")
    note = Note(title="Show me", body="Body", category="m365", severity="medium")
    store.add(note)
    ns = _ns(tmp_path, id=note.id)
    rc = cmd_show(ns)
    assert rc == 0
    assert "Show me" in capsys.readouterr().out


def test_cmd_show_missing(tmp_path, capsys):
    ns = _ns(tmp_path, id="badid12345")
    rc = cmd_show(ns)
    assert rc == 1
    assert "not found" in capsys.readouterr().err


def test_cmd_update_no_fields_returns_one(tmp_path, capsys):
    store = NoteStore(tmp_path / "notes.jsonl")
    note = Note(title="Upd test", body="B", category="other", severity="low")
    store.add(note)
    ns = _ns(tmp_path, id=note.id, title=None, body=None, category=None, severity=None, status=None, tags=None)
    rc = cmd_update(ns)
    assert rc == 1


def test_cmd_update_changes_title(tmp_path, capsys):
    store = NoteStore(tmp_path / "notes.jsonl")
    note = Note(title="Old title", body="B", category="other", severity="low")
    store.add(note)
    ns = _ns(tmp_path, id=note.id, title="New title", body=None, category=None, severity=None, status=None, tags=None)
    rc = cmd_update(ns)
    assert rc == 0
    assert store.get(note.id).title == "New title"


def test_cmd_update_missing_note(tmp_path, capsys):
    ns = _ns(tmp_path, id="missing1234", title="X", body=None, category=None, severity=None, status=None, tags=None)
    rc = cmd_update(ns)
    assert rc == 1


def test_cmd_delete_existing(tmp_path, capsys):
    store = NoteStore(tmp_path / "notes.jsonl")
    note = Note(title="Del me", body="B", category="hardware", severity="low")
    store.add(note)
    ns = _ns(tmp_path, id=note.id)
    rc = cmd_delete(ns)
    assert rc == 0
    assert store.get(note.id) is None


def test_cmd_delete_missing(tmp_path, capsys):
    ns = _ns(tmp_path, id="nosuchid12")
    rc = cmd_delete(ns)
    assert rc == 1


def test_cmd_stats_text(tmp_path, capsys):
    store = NoteStore(tmp_path / "notes.jsonl")
    store.add(Note(title="A", body="B", category="azure", severity="high"))
    ns = _ns(tmp_path, json=False)
    rc = cmd_stats(ns)
    assert rc == 0
    out = capsys.readouterr().out
    assert "Total notes" in out


def test_cmd_stats_json_output(tmp_path, capsys):
    store = NoteStore(tmp_path / "notes.jsonl")
    store.add(Note(title="A", body="B", category="azure", severity="high"))
    ns = _ns(tmp_path, json=True)
    rc = cmd_stats(ns)
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["total"] == 1
    assert "by_status" in data


# ---------------------------------------------------------------------------
# main() integration
# ---------------------------------------------------------------------------


def test_main_add_and_list(tmp_path):
    db = str(tmp_path / "notes.jsonl")
    with pytest.raises(SystemExit) as exc_info:
        main(["--db", db, "add", "Integration note", "Body text", "--category=monitoring", "--severity=low"])
    assert exc_info.value.code == 0

    with pytest.raises(SystemExit) as exc_info:
        main(["--db", db, "list"])
    assert exc_info.value.code == 0


def test_main_stats(tmp_path):
    db = str(tmp_path / "notes.jsonl")
    with pytest.raises(SystemExit):
        main(["--db", db, "add", "Note", "Body", "--category=security", "--severity=critical"])
    with pytest.raises(SystemExit) as exc_info:
        main(["--db", db, "stats"])
    assert exc_info.value.code == 0


def test_main_show_missing_exits_one(tmp_path):
    db = str(tmp_path / "notes.jsonl")
    with pytest.raises(SystemExit) as exc_info:
        main(["--db", db, "show", "notexist12"])
    assert exc_info.value.code == 1


def test_main_no_subcommand_exits_two():
    with pytest.raises(SystemExit) as exc_info:
        main([])
    assert exc_info.value.code == 2
