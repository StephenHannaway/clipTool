from __future__ import annotations

from collections.abc import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QColor, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon


def _make_icon() -> QIcon:
    px = QPixmap(16, 16)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QColor(100, 150, 255))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(1, 1, 14, 14, 3, 3)
    p.end()
    return QIcon(px)


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, parent: QSystemTrayIcon | None = None) -> None:
        super().__init__(_make_icon(), parent)
        self.on_open_picker: Callable[[], None] | None = None
        self.on_open_ocr: Callable[[], None] | None = None
        self.on_open_column_select: Callable[[], None] | None = None
        self.on_secure_mode_changed: Callable[[bool], None] | None = None
        self._build_menu()
        self.activated.connect(self._on_activate)

    def _build_menu(self) -> None:
        menu = QMenu()
        picker_action = QAction("Open Picker\tCtrl+Alt+V")
        picker_action.triggered.connect(self._emit_open_picker)
        menu.addAction(picker_action)
        ocr_action = QAction("OCR Grab\tCtrl+Alt+G")
        ocr_action.triggered.connect(self._emit_open_ocr)
        menu.addAction(ocr_action)
        col_action = QAction("Column Select\tCtrl+Alt+K")
        col_action.triggered.connect(self._emit_open_column_select)
        menu.addAction(col_action)
        menu.addSeparator()
        self._secure_action = QAction("Secure Mode")
        self._secure_action.setCheckable(True)
        self._secure_action.toggled.connect(self._on_secure_toggled)
        menu.addAction(self._secure_action)
        menu.addSeparator()
        quit_action = QAction("Quit")
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(quit_action)
        self.setContextMenu(menu)

    def _emit_open_picker(self) -> None:
        if self.on_open_picker:
            self.on_open_picker()

    def _emit_open_ocr(self) -> None:
        if self.on_open_ocr:
            self.on_open_ocr()

    def _emit_open_column_select(self) -> None:
        if self.on_open_column_select:
            self.on_open_column_select()

    def _on_secure_toggled(self, checked: bool) -> None:
        if self.on_secure_mode_changed:
            self.on_secure_mode_changed(checked)

    def _on_activate(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._emit_open_picker()
