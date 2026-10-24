"""
统一页头组件。

眉题（ eyebrow 小标）+ 大标题 + 副标题 + 右侧动作区，
三个页面复用，保证信息层级一致。
"""
from __future__ import annotations

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy


class PageHeader(QWidget):
    """页面头部：眉题 + 标题 + 右侧动作容器"""

    def __init__(self, eyebrow: str, title: str, subtitle: str = "", parent: QWidget | None = None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(16)

        left = QVBoxLayout()
        left.setContentsMargins(0, 0, 0, 0)
        left.setSpacing(2)

        self._eyebrow = QLabel(eyebrow.upper())
        self._eyebrow.setObjectName("pageEyebrow")
        left.addWidget(self._eyebrow)

        self._title = QLabel(title)
        self._title.setObjectName("pageTitle")
        left.addWidget(self._title)

        if subtitle:
            self._subtitle = QLabel(subtitle)
            self._subtitle.setObjectName("pageSub")
            left.addWidget(self._subtitle)

        outer.addLayout(left)
        outer.addStretch()

        # 右侧动作容器：调用方 add_widget() 放按钮等
        self._actions = QHBoxLayout()
        self._actions.setSpacing(8)
        outer.addLayout(self._actions)

    def add_widget(self, widget: QWidget) -> None:
        """向右侧动作区追加控件"""
        self._actions.addWidget(widget)

    def set_title(self, title: str) -> None:
        self._title.setText(title)
