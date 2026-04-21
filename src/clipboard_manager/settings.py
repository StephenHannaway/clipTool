from __future__ import annotations

import contextlib
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class HotkeySettings:
    picker: str = "ctrl+alt+v"
    ocr: str = "ctrl+alt+g"
    column_select: str = "ctrl+alt+k"


@dataclass
class Settings:
    history_limit: int = 500
    hotkeys: HotkeySettings = field(default_factory=HotkeySettings)
    plain_text_strip: bool = True
    start_with_windows: bool = False

    @staticmethod
    def default_path() -> Path:
        return Path.home() / ".clipboard-manager" / "settings.json"

    @classmethod
    def load(cls, path: Path | None = None) -> Settings:
        p = path or cls.default_path()
        if not p.exists():
            return cls()
        data = json.loads(p.read_text(encoding="utf-8"))
        defaults = cls()
        hotkeys_data = data.get("hotkeys", {})
        return cls(
            history_limit=data.get("history_limit", defaults.history_limit),
            hotkeys=HotkeySettings(
                picker=hotkeys_data.get("picker", defaults.hotkeys.picker),
                ocr=hotkeys_data.get("ocr", defaults.hotkeys.ocr),
                column_select=hotkeys_data.get(
                    "column_select", defaults.hotkeys.column_select
                ),
            ),
            plain_text_strip=data.get("plain_text_strip", defaults.plain_text_strip),
            start_with_windows=data.get(
                "start_with_windows", defaults.start_with_windows
            ),
        )

    def save(self, path: Path | None = None) -> None:
        p = path or self.default_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")

    def apply_start_with_windows(self) -> None:
        if sys.platform != "win32":
            return
        import winreg

        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "ClipboardManager"
        exe = str(Path(sys.executable).parent / "clipboard-manager.exe")
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE
        ) as key:
            if self.start_with_windows:
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe)
            else:
                with contextlib.suppress(FileNotFoundError):
                    winreg.DeleteValue(key, app_name)
