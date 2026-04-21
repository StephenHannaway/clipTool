from __future__ import annotations

import pyautogui
from PyQt6.QtCore import QObject, QRect, pyqtSignal

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
        x1, y1 = rect.left(), rect.top()
        x2, y2 = rect.right(), rect.bottom()
        pyautogui.keyDown("alt")
        pyautogui.moveTo(x1, y1)
        pyautogui.mouseDown()
        pyautogui.moveTo(x2, y2, duration=0.1)
        pyautogui.mouseUp()
        pyautogui.keyUp("alt")
        self.selection_done.emit()
