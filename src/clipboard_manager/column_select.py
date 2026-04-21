from __future__ import annotations

import pytesseract
from PIL import ImageGrab
from PyQt6.QtCore import QObject, QRect, pyqtSignal
from PyQt6.QtWidgets import QApplication

from clipboard_manager.overlay import SelectionOverlay

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


class ColumnSelectHelper(QObject):
    text_captured: pyqtSignal = pyqtSignal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._overlay = SelectionOverlay()
        self._overlay.selection_complete.connect(self._on_selection)

    def activate(self) -> None:
        self._overlay.activate()

    def _on_selection(self, rect: QRect) -> None:
        screen = QApplication.primaryScreen()
        ratio = screen.devicePixelRatio() if screen else 1.0
        x, y = rect.x(), rect.y()
        w, h = rect.width(), rect.height()
        img = ImageGrab.grab(
            bbox=(
                int(x * ratio),
                int(y * ratio),
                int((x + w) * ratio),
                int((y + h) * ratio),
            )
        )
        # PSM 6: "Assume a single uniform block of text" — good for columns
        text: str = pytesseract.image_to_string(img, config="--psm 6").strip()
        if text:
            clipboard = QApplication.clipboard()
            if clipboard is not None:
                clipboard.setText(text)
            self.text_captured.emit(text)
