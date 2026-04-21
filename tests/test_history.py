from pathlib import Path

import pytest

from clipboard_manager.history import ClipboardHistory


@pytest.fixture
def history(tmp_path: Path) -> ClipboardHistory:
    return ClipboardHistory(tmp_path / "test.db", limit=5)


def test_add_returns_entry(history: ClipboardHistory) -> None:
    entry = history.add("hello world")
    assert entry is not None
    assert entry.content == "hello world"
    assert entry.id > 0
    assert entry.content_type == "text"


def test_entries_newest_first(history: ClipboardHistory) -> None:
    history.add("first")
    history.add("second")
    entries = history.entries()
    assert entries[0].content == "second"
    assert entries[1].content == "first"


def test_dedupe_consecutive(history: ClipboardHistory) -> None:
    history.add("same")
    result = history.add("same")
    assert result is None
    assert len(history.entries()) == 1


def test_dedupe_allows_non_consecutive(history: ClipboardHistory) -> None:
    history.add("a")
    history.add("b")
    history.add("a")
    assert len(history.entries()) == 3


def test_expire_oldest_unpinned(history: ClipboardHistory) -> None:
    for i in range(5):
        history.add(f"item {i}")
    history.add("item 5")
    contents = [e.content for e in history.entries()]
    assert "item 0" not in contents
    assert "item 5" in contents


def test_pin_prevents_expire(history: ClipboardHistory) -> None:
    history.add("pinned")
    entry = history.entries()[0]
    history.pin(entry.id, True)
    for i in range(5):
        history.add(f"filler {i}")
    contents = [e.content for e in history.entries()]
    assert "pinned" in contents


def test_persist_and_reload(tmp_path: Path) -> None:
    h1 = ClipboardHistory(tmp_path / "test.db", limit=10)
    h1.add("persisted")
    h2 = ClipboardHistory(tmp_path / "test.db", limit=10)
    assert h2.entries()[0].content == "persisted"


def test_remove(history: ClipboardHistory) -> None:
    history.add("to remove")
    entry = history.entries()[0]
    history.remove(entry.id)
    assert len(history.entries()) == 0


def test_search_filters(history: ClipboardHistory) -> None:
    history.add("hello world")
    history.add("foo bar")
    results = history.search("hello")
    assert len(results) == 1
    assert results[0].content == "hello world"


def test_search_empty_query_returns_all(history: ClipboardHistory) -> None:
    history.add("a")
    history.add("b")
    assert len(history.search("")) == 2


def test_raw_stored_and_retrieved(history: ClipboardHistory) -> None:
    raw = b"<b>bold</b>"
    entry = history.add("bold", raw=raw)
    assert entry is not None
    loaded = history.entries()[0]
    assert loaded.raw == raw
