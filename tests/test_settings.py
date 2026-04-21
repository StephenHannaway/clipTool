import json
from pathlib import Path

from clipboard_manager.settings import HotkeySettings, Settings


def test_defaults():
    s = Settings()
    assert s.history_limit == 500
    assert s.plain_text_strip is True
    assert s.start_with_windows is False
    assert s.hotkeys.picker == "ctrl+win+v"
    assert s.hotkeys.ocr == "ctrl+win+o"
    assert s.hotkeys.column_select == "ctrl+win+b"


def test_save_creates_file(tmp_path: Path):
    path = tmp_path / "settings.json"
    Settings().save(path)
    assert path.exists()


def test_save_and_load_roundtrip(tmp_path: Path):
    path = tmp_path / "settings.json"
    s = Settings(history_limit=200, plain_text_strip=False)
    s.save(path)
    loaded = Settings.load(path)
    assert loaded.history_limit == 200
    assert loaded.plain_text_strip is False


def test_load_missing_file_returns_defaults(tmp_path: Path):
    path = tmp_path / "does_not_exist.json"
    s = Settings.load(path)
    assert s.history_limit == 500


def test_load_partial_file_fills_defaults(tmp_path: Path):
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({"history_limit": 100}))
    s = Settings.load(path)
    assert s.history_limit == 100
    assert s.plain_text_strip is True
    assert s.hotkeys.picker == "ctrl+win+v"


def test_save_creates_parent_dirs(tmp_path: Path):
    path = tmp_path / "deep" / "nested" / "settings.json"
    Settings().save(path)
    assert path.exists()


def test_hotkey_roundtrip(tmp_path: Path):
    path = tmp_path / "settings.json"
    s = Settings(hotkeys=HotkeySettings(picker="ctrl+alt+v"))
    s.save(path)
    loaded = Settings.load(path)
    assert loaded.hotkeys.picker == "ctrl+alt+v"
    assert loaded.hotkeys.ocr == "ctrl+win+o"
