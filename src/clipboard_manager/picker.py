from __future__ import annotations

from PyQt6.QtCore import QMimeData, Qt, QTimer
from PyQt6.QtGui import QCursor, QFocusEvent, QKeyEvent
from PyQt6.QtWidgets import (
    QApplication,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from clipboard_manager.history import ClipboardHistory
from clipboard_manager.models import ClipboardEntry
from clipboard_manager.settings import Settings

_STYLE = """
QWidget {
    background: #1a1a2e;
    color: #e0e0e0;
    border-radius: 8px;
    font-family: "Segoe UI", sans-serif;
    font-size: 12px;
}
QLineEdit {
    background: #2a2a3e;
    border: none;
    padding: 6px 8px;
    border-radius: 4px;
    color: #e0e0e0;
}
QListWidget {
    background: transparent;
    border: none;
    outline: none;
}
QListWidget::item {
    padding: 6px 8px;
    border-radius: 4px;
}
QListWidget::item:selected {
    background: #2d2d4e;
}
QListWidget::item:hover {
    background: #222240;
}
"""

_TYPE_LABELS = {"url": "URL", "email": "EMAIL", "code": "CODE", "text": "TXT"}


class PickerWindow(QWidget):
    def __init__(
        self,
        history: ClipboardHistory,
        settings: Settings,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(
            parent,
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool,
        )
        self._history = history
        self._settings = settings
        self._displayed: list[ClipboardEntry] = []
        self._setup_ui()
        self.setStyleSheet(_STYLE)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        self._search = QLineEdit()
        self._search.setPlaceholderText("Search history...")
        self._search.textChanged.connect(self._filter)
        layout.addWidget(self._search)
        self._list = QListWidget()
        self._list.setFrameShape(QListWidget.Shape.NoFrame)
        self._list.itemActivated.connect(lambda _: self._paste_selected())
        layout.addWidget(self._list)
        self.setFixedWidth(320)
        self.setMinimumHeight(100)
        self.setMaximumHeight(480)

    def show_near_cursor(self) -> None:
        self._search.clear()
        self._populate(self._history.entries())
        pos = QCursor.pos()
        screen_geo = QApplication.primaryScreen().geometry()  # type: ignore[union-attr]
        x = min(pos.x(), screen_geo.right() - self.width() - 10)
        y = min(pos.y(), screen_geo.bottom() - self.height() - 10)
        self.move(x, y)
        self.show()
        self.raise_()
        self.activateWindow()
        self._search.setFocus()

    def _populate(self, entries: list[ClipboardEntry]) -> None:
        self._list.clear()
        self._displayed = entries
        for entry in entries:
            label = _TYPE_LABELS.get(entry.content_type, "TXT")
            pin = " \U0001f4cc" if entry.pinned else ""
            preview = entry.content[:60].replace("\n", " ")
            item = QListWidgetItem(f"[{label}]{pin} {preview}")
            item.setData(Qt.ItemDataRole.UserRole, entry.id)
            item.setToolTip(entry.content[:400])
            self._list.addItem(item)
        if self._list.count():
            self._list.setCurrentRow(0)
        self.adjustSize()

    def _filter(self, text: str) -> None:
        results = self._history.search(text) if text else self._history.entries()
        self._populate(results)

    def _entry_for_current(self) -> ClipboardEntry | None:
        item = self._list.currentItem()
        if item is None:
            return None
        entry_id: int = item.data(Qt.ItemDataRole.UserRole)
        return next((e for e in self._displayed if e.id == entry_id), None)

    def _paste_selected(self) -> None:
        entry = self._entry_for_current()
        if entry is None:
            return
        clipboard = QApplication.clipboard()
        if clipboard is None:
            return
        if self._settings.plain_text_strip or entry.raw is None:
            clipboard.setText(entry.content)
        else:
            mime = QMimeData()
            mime.setText(entry.content)
            if entry.raw[:4] == b"{\\rt":
                mime.setData("text/rtf", entry.raw)
            else:
                mime.setHtml(entry.raw.decode("utf-8", errors="replace"))
            clipboard.setMimeData(mime)
        self.hide()
        import keyboard as kb

        QTimer.singleShot(100, lambda: kb.press_and_release("ctrl+v"))

    def _toggle_pin(self) -> None:
        entry = self._entry_for_current()
        if entry is None:
            return
        self._history.pin(entry.id, not entry.pinned)
        self._populate(self._history.entries())

    def _delete_selected(self) -> None:
        entry = self._entry_for_current()
        if entry is None:
            return
        self._history.remove(entry.id)
        self._populate(self._history.entries())

    def _copy_without_paste(self) -> None:
        entry = self._entry_for_current()
        if entry is None:
            return
        clipboard = QApplication.clipboard()
        if clipboard is not None:
            clipboard.setText(entry.content)
        self.hide()

    def keyPressEvent(self, event: QKeyEvent | None) -> None:
        if event is None:
            return
        key = event.key()
        mod = event.modifiers()
        if key == Qt.Key.Key_Escape:
            self.hide()
        elif key == Qt.Key.Key_Return:
            self._paste_selected()
        elif key == Qt.Key.Key_Up:
            self._list.setCurrentRow(max(0, self._list.currentRow() - 1))
        elif key == Qt.Key.Key_Down:
            self._list.setCurrentRow(
                min(self._list.count() - 1, self._list.currentRow() + 1)
            )
        elif key == Qt.Key.Key_P:
            self._toggle_pin()
        elif key == Qt.Key.Key_Delete:
            self._delete_selected()
        elif key == Qt.Key.Key_C and mod & Qt.KeyboardModifier.ControlModifier:
            self._copy_without_paste()
        else:
            super().keyPressEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:  # type: ignore[override]
        self.hide()
        super().focusOutEvent(event)
