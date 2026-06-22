"""Core data layer for IT triage notes stored as a local JSON journal."""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

CATEGORIES = ("azure", "m365", "monitoring", "security", "network", "hardware", "other")
SEVERITIES = ("low", "medium", "high", "critical")
STATUSES = ("open", "in-progress", "resolved", "closed")

Category = Literal["azure", "m365", "monitoring", "security", "network", "hardware", "other"]
Severity = Literal["low", "medium", "high", "critical"]
Status = Literal["open", "in-progress", "resolved", "closed"]


@dataclass
class Note:
    title: str
    body: str
    category: Category
    severity: Severity
    status: Status = "open"
    tags: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:10])
    created_at: str = field(default_factory=lambda: _now())
    updated_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Note":
        return cls(**data)

    def summary_line(self) -> str:
        sev_badge = {"low": "[ ]", "medium": "[~]", "high": "[!]", "critical": "[X]"}[self.severity]
        return f"{sev_badge} {self.id}  [{self.status:<11}]  [{self.category:<10}]  {self.title}"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class NoteStore:
    """Append-only JSON journal; each line is one serialized Note dict."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.touch()

    def _load_all(self) -> list[Note]:
        notes: list[Note] = []
        for raw in self.path.read_text(encoding="utf-8").splitlines():
            raw = raw.strip()
            if raw:
                try:
                    notes.append(Note.from_dict(json.loads(raw)))
                except (json.JSONDecodeError, TypeError):
                    pass
        return notes

    def _write_all(self, notes: list[Note]) -> None:
        self.path.write_text(
            "\n".join(json.dumps(n.to_dict()) for n in notes) + "\n",
            encoding="utf-8",
        )

    def add(self, note: Note) -> Note:
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(note.to_dict()) + "\n")
        return note

    def list(
        self,
        *,
        status: str | None = None,
        category: str | None = None,
        severity: str | None = None,
        tag: str | None = None,
    ) -> list[Note]:
        notes = self._load_all()
        if status:
            notes = [n for n in notes if n.status == status]
        if category:
            notes = [n for n in notes if n.category == category]
        if severity:
            notes = [n for n in notes if n.severity == severity]
        if tag:
            notes = [n for n in notes if tag in n.tags]
        return notes

    def get(self, note_id: str) -> Note | None:
        for note in self._load_all():
            if note.id == note_id:
                return note
        return None

    def update(self, note_id: str, **fields) -> Note | None:
        notes = self._load_all()
        target: Note | None = None
        for note in notes:
            if note.id == note_id:
                target = note
                break
        if target is None:
            return None
        allowed = {"title", "body", "category", "severity", "status", "tags"}
        for key, value in fields.items():
            if key in allowed:
                object.__setattr__(target, key, value)
        target.updated_at = _now()
        self._write_all(notes)
        return target

    def delete(self, note_id: str) -> bool:
        notes = self._load_all()
        filtered = [n for n in notes if n.id != note_id]
        if len(filtered) == len(notes):
            return False
        self._write_all(filtered)
        return True

    def stats(self) -> dict:
        notes = self._load_all()
        counts: dict = {
            "total": len(notes),
            "by_status": {},
            "by_severity": {},
            "by_category": {},
        }
        for note in notes:
            counts["by_status"][note.status] = counts["by_status"].get(note.status, 0) + 1
            counts["by_severity"][note.severity] = counts["by_severity"].get(note.severity, 0) + 1
            counts["by_category"][note.category] = counts["by_category"].get(note.category, 0) + 1
        return counts


def default_store_path() -> Path:
    import os

    xdg = os.environ.get("XDG_DATA_HOME", "")
    base = Path(xdg) if xdg else Path.home() / ".local" / "share"
    return base / "it-triage" / "notes.jsonl"
