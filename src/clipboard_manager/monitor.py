from __future__ import annotations

from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from PyQt6.QtWidgets import QApplication

from clipboard_manager.history import ClipboardHistory


class ClipboardMonitor(QObject):
    entry_added: pyqtSignal = pyqtSignal(object)  # ClipboardEntry

    def __init__(
        self, history: ClipboardHistory, parent: QObject | None = None
    ) -> None:
        super().__init__(parent)
        self._history = history
        self._paused = False
        self._last_text = ""
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._check)

    def start(self) -> None:
        clipboard = QApplication.clipboard()
        self._last_text = clipboard.text() if clipboard else ""
        self._timer.start(500)

    def stop(self) -> None:
        self._timer.stop()

    def set_paused(self, paused: bool) -> None:
        self._paused = paused

    def _check(self) -> None:
        if self._paused:
            return
        clipboard = QApplication.clipboard()
        if clipboard is None:
            return
        text = clipboard.text()
        if not text or text == self._last_text:
            return
        self._last_text = text
        mime = clipboard.mimeData()
        raw: bytes | None = None
        if mime is not None:
            for fmt in ("text/rtf", "text/html"):
                data = mime.data(fmt)
                if data:
                    raw = bytes(data.data())
                    break
        entry = self._history.add(text, raw)
        if entry is not None:
            self.entry_added.emit(entry)
