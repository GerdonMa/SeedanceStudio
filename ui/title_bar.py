"""
自定义标题栏组件。

无边框窗口模式下替换系统标题栏，提供窗口拖拽移动、
最小化/最大化/关闭按钮、双击最大化切换功能。
"""
from __future__ import annotations

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont


class TitleBar(QWidget):
    """自定义标题栏（36px 高）"""

    def __init__(self, parent: QWidget, app_name: str = "Seedance Studio"):
        super().__init__(parent)
        self._parent = parent
        self._drag_pos = None
        self._maximized = False

        self.setObjectName("titleBar")
        self.setFixedHeight(36)

        self._init_ui(app_name)

    def _init_ui(self, app_name: str):
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 0, 4, 0)
        layout.setSpacing(0)

        # 左侧：应用图标 + 名称
        self._icon_label = QLabel()
        self._icon_label.setFixedSize(20, 20)
        self._icon_label.setScaledContents(True)
        layout.addWidget(self._icon_label)

        layout.addSpacing(6)

        title_label = QLabel(app_name)
        title_label.setObjectName("titleLabel")
        layout.addWidget(title_label)

        layout.addStretch()

        # 右侧：窗口控制按钮（用 setFont 而非 setStyleSheet，避免覆盖主题 QSS）
        btn_min = QPushButton("\u2014")  # — em dash
        btn_min.setObjectName("btnMin")
        btn_min.setFixedSize(36, 28)
        btn_min.setFont(QFont("Segoe UI", 11))
        btn_min.clicked.connect(self._parent.showMinimized)
        layout.addWidget(btn_min)

        self._btn_max = QPushButton("\u25A1")  # □ white square
        self._btn_max.setObjectName("btnMax")
        self._btn_max.setFixedSize(36, 28)
        self._btn_max.setFont(QFont("Segoe UI", 11))
        self._btn_max.clicked.connect(self._toggle_maximize)
        layout.addWidget(self._btn_max)

        btn_close = QPushButton("\u00D7")  # × multiplication sign
        btn_close.setObjectName("btnClose")
        btn_close.setFixedSize(36, 28)
        btn_close.setFont(QFont("Segoe UI", 13))
        btn_close.clicked.connect(self._parent.close)
        layout.addWidget(btn_close)

        self.setLayout(layout)

    def set_icon(self, pixmap: QPixmap | None):
        if pixmap is not None:
            self._icon_label.setPixmap(pixmap)
        else:
            self._icon_label.clear()

    def set_maximized(self, maximized: bool):
        self._maximized = maximized
        self._btn_max.setText("\u29C9" if maximized else "\u25A1")  # ⧉ 或 □

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and not self._maximized:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self._parent.move(self._parent.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._toggle_maximize()

    def _toggle_maximize(self):
        if self._parent.isMaximized():
            self._parent.showNormal()
        else:
            self._parent.showMaximized()
