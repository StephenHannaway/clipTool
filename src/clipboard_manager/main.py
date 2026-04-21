from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from clipboard_manager.column_select import ColumnSelectHelper
from clipboard_manager.history import ClipboardHistory
from clipboard_manager.hotkeys import HotkeyManager
from clipboard_manager.monitor import ClipboardMonitor
from clipboard_manager.ocr import OCRCapture
from clipboard_manager.picker import PickerWindow
from clipboard_manager.settings import Settings
from clipboard_manager.tray import SystemTrayIcon


def main() -> int:
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    settings = Settings.load()
    history = ClipboardHistory(
        Path.home() / ".clipboard-manager" / "history.db",
        settings.history_limit,
    )

    monitor = ClipboardMonitor(history)
    tray = SystemTrayIcon()
    picker = PickerWindow(history, settings)
    ocr = OCRCapture()
    column_select = ColumnSelectHelper()
    hotkeys = HotkeyManager(settings)

    tray.on_open_picker = picker.show_near_cursor
    tray.on_open_ocr = ocr.activate
    tray.on_open_column_select = column_select.activate
    tray.on_secure_mode_changed = monitor.set_paused

    hotkeys.picker_triggered.connect(picker.show_near_cursor)
    hotkeys.ocr_triggered.connect(ocr.activate)
    hotkeys.column_select_triggered.connect(column_select.activate)
    hotkeys.register()

    if not SystemTrayIcon.isSystemTrayAvailable():
        print("ERROR: system tray not available", file=sys.stderr)
        return 1

    monitor.start()
    tray.show()
    settings.apply_start_with_windows()

    return app.exec()
