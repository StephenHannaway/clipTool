from __future__ import annotations

import pyautogui
from PyQt6.QtCore import QObject, QRect, QTimer, pyqtSignal
from PyQt6.QtWidgets import QApplication

from clipboard_manager.overlay import SelectionOverlay


class ColumnSelectHelper(QObject):
    selection_done: pyqtSignal = pyqtSignal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._overlay = SelectionOverlay()
        self._overlay.selection_complete.connect(self._on_selection)

    def activate(self) -> None:
        self._overlay.activate()

    def _on_selection(self, rect: QRect) -> None:
        screen = QApplication.primaryScreen()
        ratio = screen.devicePixelRatio() if screen else 1.0
        x1 = int(rect.left() * ratio)
        y1 = int(rect.top() * ratio)
        x2 = int(rect.right() * ratio)
        y2 = int(rect.bottom() * ratio)
        QTimer.singleShot(150, lambda: self._do_drag(x1, y1, x2, y2))

    def _do_drag(self, x1: int, y1: int, x2: int, y2: int) -> None:
        pyautogui.keyDown("alt")
        pyautogui.moveTo(x1, y1)
        pyautogui.mouseDown()
        pyautogui.moveTo(x2, y2, duration=0.1)
        pyautogui.mouseUp()
        pyautogui.keyUp("alt")
        pyautogui.hotkey("ctrl", "c")
        self.selection_done.emit()
