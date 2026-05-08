"""
任务卡片组件。

嵌入任务列表表格的操作列，提供取消/删除按钮。
"""
from __future__ import annotations

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton


class TaskCardWidget(QWidget):
    """任务卡片（操作列组件）"""

    def __init__(self, task_id: str, status: str, on_cancel, on_delete):
        super().__init__()
        self._task_id = task_id
        self._status = status

        layout = QHBoxLayout()
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)

        self._cancel_btn = QPushButton("取消")
        self._cancel_btn.setMinimumHeight(34)
        self._cancel_btn.setProperty("role", "ghost")
        self._cancel_btn.clicked.connect(on_cancel)
        layout.addWidget(self._cancel_btn)

        self._delete_btn = QPushButton("删除")
        self._delete_btn.setMinimumHeight(34)
        self._delete_btn.setProperty("role", "ghost")
        self._delete_btn.clicked.connect(on_delete)
        layout.addWidget(self._delete_btn)

        self.setLayout(layout)

    def set_status(self, status: str):
        self._status = status
