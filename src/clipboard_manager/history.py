from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from clipboard_manager.models import ClipboardEntry, detect_content_type

_CREATE = """
    CREATE TABLE IF NOT EXISTS entries (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        content   TEXT    NOT NULL,
        content_type TEXT NOT NULL,
        raw       BLOB,
        timestamp TEXT    NOT NULL,
        pinned    INTEGER NOT NULL DEFAULT 0
    )
"""


class ClipboardHistory:
    def __init__(self, db_path: Path, limit: int = 500) -> None:
        self._limit = limit
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(db_path))
        self._conn.row_factory = sqlite3.Row
        self._conn.execute(_CREATE)
        self._conn.commit()
        self._entries: list[ClipboardEntry] = self._load_all()

    def add(self, content: str, raw: bytes | None = None) -> ClipboardEntry | None:
        if self._entries and self._entries[0].content == content:
            return None
        content_type = detect_content_type(content)
        now = datetime.now()
        sql = (
            "INSERT INTO entries (content, content_type, raw, timestamp, pinned)"
            " VALUES (?,?,?,?,0)"
        )
        cur = self._conn.execute(sql, (content, content_type, raw, now.isoformat()))
        self._conn.commit()
        entry = ClipboardEntry(
            id=cur.lastrowid,  # type: ignore[arg-type]
            content=content,
            content_type=content_type,
            raw=raw,
            timestamp=now,
            pinned=False,
        )
        self._entries.insert(0, entry)
        self._enforce_limit()
        return entry

    def remove(self, entry_id: int) -> None:
        self._conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
        self._conn.commit()
        self._entries = [e for e in self._entries if e.id != entry_id]

    def pin(self, entry_id: int, pinned: bool) -> None:
        self._conn.execute(
            "UPDATE entries SET pinned = ? WHERE id = ?", (int(pinned), entry_id)
        )
        self._conn.commit()
        for e in self._entries:
            if e.id == entry_id:
                e.pinned = pinned
                break

    def entries(self) -> list[ClipboardEntry]:
        return list(self._entries)

    def search(self, query: str) -> list[ClipboardEntry]:
        q = query.lower()
        return [e for e in self._entries if q in e.content.lower()]

    def _enforce_limit(self) -> None:
        while len(self._entries) > self._limit:
            unpinned = [e for e in self._entries if not e.pinned]
            if not unpinned:
                break
            self.remove(unpinned[-1].id)

    def _load_all(self) -> list[ClipboardEntry]:
        sql = (
            "SELECT id, content, content_type, raw, timestamp, pinned"
            " FROM entries ORDER BY id DESC"
        )
        rows = self._conn.execute(sql).fetchall()
        return [
            ClipboardEntry(
                id=row["id"],
                content=row["content"],
                content_type=row["content_type"],
                raw=bytes(row["raw"]) if row["raw"] is not None else None,
                timestamp=datetime.fromisoformat(row["timestamp"]),
                pinned=bool(row["pinned"]),
            )
            for row in rows
        ]
