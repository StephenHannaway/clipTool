from __future__ import annotations

import keyboard
from PyQt6.QtCore import QObject, pyqtSignal

from clipboard_manager.settings import Settings


class HotkeyManager(QObject):
    picker_triggered: pyqtSignal = pyqtSignal()
    ocr_triggered: pyqtSignal = pyqtSignal()

    def __init__(self, settings: Settings, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._settings = settings
        self._registered = False

    def register(self) -> None:
        h = self._settings.hotkeys
        keyboard.add_hotkey(h.picker, self.picker_triggered.emit)
        keyboard.add_hotkey(h.ocr, self.ocr_triggered.emit)
        self._registered = True

    def unregister_all(self) -> None:
        if self._registered:
            keyboard.unhook_all_hotkeys()
            self._registered = False
