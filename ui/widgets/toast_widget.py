"""
Toast 通知组件。

右下角弹出通知，支持 success/warning/error/info 四种类型，
自动消失、最多 5 条堆积、进入/退出动画。
"""
from __future__ import annotations

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QFont

from core.di_container import Container
from themes.theme_context import ThemeContext
from ui.widgets.sidebar_icons import create_toast_icon

_TOAST_COLORS_FALLBACK = {
    "success": "#00FF88",
    "warning": "#E5FF00",
    "error":   "#FF3333",
    "info":    "#C8FF00",
}

_MAX_TOASTS = 5
_AUTO_DISMISS_MS = 5000
_TOAST_WIDTH = 320
_TOAST_MARGIN = 16


class ToastItem(QFrame):
    """单条 Toast"""

    def __init__(self, type_: str, title: str, message: str, parent: QWidget):
        super().__init__(parent)
        self._type = type_
        self._parent_container: ToastWidget = parent
        self.setObjectName("toastItem")
        self.setFixedWidth(_TOAST_WIDTH)
        self.setMinimumHeight(64)

        color = ThemeContext.get_color(f"toast_{type_}", _TOAST_COLORS_FALLBACK.get(type_, "#00E5FF"))

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(8)

        bar = QFrame()
        bar.setFixedWidth(3)
        bar.setStyleSheet(f"background-color: {color}; border-radius: 1px; border: none;")
        layout.addWidget(bar)

        icon_label = QLabel()
        icon_label.setFixedSize(20, 20)
        icon_label.setPixmap(create_toast_icon(type_, color))
        icon_label.setStyleSheet("background: transparent;")
        layout.addWidget(icon_label)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(1)

        title_label = QLabel(title)
        f = title_label.font()
        f.setBold(True)
        title_label.setFont(f)
        title_label.setObjectName("toastTitle")
        text_layout.addWidget(title_label)

        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setObjectName("toastMessage")
        text_layout.addWidget(msg_label)

        layout.addLayout(text_layout, 1)
        self.setLayout(layout)

    def slide_in(self):
        anim = QPropertyAnimation(self, b"pos")
        anim.setDuration(300)
        target = self.pos()
        start = QPoint(target.x() + 380, target.y())
        anim.setStartValue(start)
        anim.setEndValue(target)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
        self._slide_anim = anim
        return anim

    def fade_out(self):
        opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(opacity_effect)
        anim = QPropertyAnimation(opacity_effect, b"opacity")
        anim.setDuration(150)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.Type.InCubic)
        anim.finished.connect(self._on_fade_finished)
        anim.start()
        self._fade_anim = anim
        return anim

    def _on_fade_finished(self):
        self._parent_container._remove_toast(self)


class ToastWidget(QWidget):
    """Toast 通知容器（覆盖在主窗口上方）"""

    def __init__(self, container: Container, parent: QWidget):
        super().__init__(parent)
        self._container = container
        self._toasts: list[ToastItem] = []
        self._timers: dict[ToastItem, QTimer] = {}

        self.setObjectName("toastContainer")
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.hide()

    def show_toast(self, type_: str, title: str, message: str):
        if len(self._toasts) >= _MAX_TOASTS:
            self._remove_toast(self._toasts[0])

        # 确保容器覆盖父窗口整个区域
        self.setGeometry(0, 0, self.parent().width(), self.parent().height())

        toast = ToastItem(type_, title, message, self)
        toast.setParent(self)
        self._toasts.append(toast)
        toast.show()

        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(lambda t=toast: t.fade_out())
        timer.start(_AUTO_DISMISS_MS)
        self._timers[toast] = timer

        self._layout_toasts()

        QTimer.singleShot(10, toast.slide_in)

        self.show()
        self.raise_()

    def _remove_toast(self, toast: ToastItem):
        if toast in self._timers:
            self._timers[toast].stop()
            del self._timers[toast]
        if toast in self._toasts:
            self._toasts.remove(toast)
        toast.hide()
        toast.deleteLater()

        if not self._toasts:
            self.hide()
        else:
            self._layout_toasts()

    def _layout_toasts(self):
        parent = self.parent()
        if parent is None:
            return
        parent_w = parent.width()
        parent_h = parent.height()
        y = parent_h - _TOAST_MARGIN

        for i, toast in enumerate(reversed(self._toasts)):
            toast_h = toast.sizeHint().height()
            toast_x = parent_w - _TOAST_WIDTH - _TOAST_MARGIN
            toast_y = y - toast_h - (i * (toast_h + 6))
            toast.move(toast_x, toast_y)

    def dismiss_all(self):
        for toast in list(self._toasts):
            self._remove_toast(toast)

    def on_theme_changed(self):
        pass

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._layout_toasts()
