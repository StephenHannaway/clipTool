from __future__ import annotations

from collections.abc import Callable

import keyboard

from clipboard_manager.settings import Settings


class HotkeyManager:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._registered = False

    def register(
        self,
        on_picker: Callable[[], None],
        on_ocr: Callable[[], None],
        on_column_select: Callable[[], None],
    ) -> None:
        h = self._settings.hotkeys
        keyboard.add_hotkey(h.picker, on_picker)
        keyboard.add_hotkey(h.ocr, on_ocr)
        keyboard.add_hotkey(h.column_select, on_column_select)
        self._registered = True

    def unregister_all(self) -> None:
        if self._registered:
            keyboard.unhook_all_hotkeys()
            self._registered = False
