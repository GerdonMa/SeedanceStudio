"""
分段选择控件。

一组互斥的可选中按钮（类似分段控制器），用于任务类型等
少量互斥选项的选择，替代下拉框以提升可读性与专业感。
"""
from __future__ import annotations

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal


class SegmentedControl(QWidget):
    """互斥分段选择控件（支持水平/垂直两种形态）。

    通过 property("segValue") 存储每段的用户数据；
    选中变化时发射 selectionChanged(value: str)。
    水平形态为拼接式分段条；垂直形态为全宽独立按钮列表。
    """

    selectionChanged = pyqtSignal(str)

    def __init__(self, items: list[tuple[str, str]], vertical: bool = False,
                 parent: QWidget | None = None):
        """
        Args:
            items: (显示文本, 用户数据) 列表
            vertical: True 时垂直按钮列表形态
        """
        super().__init__(parent)
        self._buttons: list[QPushButton] = []
        self._current: str | None = None

        if vertical:
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(6)
        else:
            layout = QHBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
        self._vertical = vertical

        n = len(items)
        for i, (text, value) in enumerate(items):
            btn = QPushButton(text)
            btn.setProperty("seg", True)
            if vertical:
                btn.setProperty("segPos", "solo")
            elif n == 1:
                btn.setProperty("segPos", "solo")
            elif i == 0:
                btn.setProperty("segPos", "first")
            elif i == n - 1:
                btn.setProperty("segPos", "last")
            else:
                btn.setProperty("segPos", "mid")
            btn.setProperty("segValue", value)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, v=value, b=btn: self._on_clicked(v, b))
            self._buttons.append(btn)
            if vertical:
                layout.addWidget(btn)
            else:
                layout.addWidget(btn, 1)

    def _on_clicked(self, value: str, btn: QPushButton):
        if self._current == value:
            btn.setChecked(True)  # 不允许取消选中
            return
        self.select(value, emit=True)

    def select(self, value: str, emit: bool = False):
        """程序化选中某段（不触发动画，可选发射信号）"""
        for btn in self._buttons:
            checked = btn.property("segValue") == value
            btn.blockSignals(True)
            btn.setChecked(checked)
            btn.blockSignals(False)
            if checked:
                self._current = value
        if emit:
            self.selectionChanged.emit(value)

    def current_value(self) -> str | None:
        """当前选中的用户数据"""
        return self._current

    def set_enabled_value(self, value: str, enabled: bool):
        """启用/禁用某一段"""
        for btn in self._buttons:
            if btn.property("segValue") == value:
                btn.setEnabled(enabled)
