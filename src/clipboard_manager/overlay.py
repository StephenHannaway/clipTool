from __future__ import annotations

from PyQt6.QtCore import QPoint, QRect, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QKeyEvent, QMouseEvent, QPainter, QPaintEvent, QPen
from PyQt6.QtWidgets import QApplication, QWidget


class SelectionOverlay(QWidget):
    selection_complete: pyqtSignal = pyqtSignal(QRect)
    cancelled: pyqtSignal = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(
            parent,
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setMouseTracking(True)
        self._start: QPoint | None = None
        self._current: QPoint | None = None
        self._selecting = False

    def activate(self) -> None:
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        self.setGeometry(screen.geometry())
        self.showFullScreen()
        self.raise_()
        self.activateWindow()

    def mousePressEvent(self, event: QMouseEvent | None) -> None:
        if event is not None and event.button() == Qt.MouseButton.LeftButton:
            self._start = event.pos()
            self._selecting = True

    def mouseMoveEvent(self, event: QMouseEvent | None) -> None:
        if self._selecting and event is not None:
            self._current = event.pos()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent | None) -> None:
        if (
            event is not None
            and event.button() == Qt.MouseButton.LeftButton
            and self._selecting
        ):
            self._selecting = False
            if self._start is not None and self._current is not None:
                rect = QRect(self._start, self._current).normalized()
                self.hide()
                if rect.width() > 5 and rect.height() > 5:
                    self.selection_complete.emit(rect)
            self._start = None
            self._current = None

    def keyPressEvent(self, event: QKeyEvent | None) -> None:
        if event is not None and event.key() == Qt.Key.Key_Escape:
            self._start = None
            self._current = None
            self._selecting = False
            self.hide()
            self.cancelled.emit()

    def paintEvent(self, event: QPaintEvent | None) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 80))
        if self._start is not None and self._current is not None:
            rect = QRect(self._start, self._current).normalized()
            painter.fillRect(rect, QColor(255, 255, 255, 20))
            painter.setPen(QPen(QColor(100, 150, 255, 220), 2))
            painter.drawRect(rect)
