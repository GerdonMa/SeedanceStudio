"""
任务列表页面。

显示所有任务历史，支持状态查看、取消、删除和视频预览。
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QMessageBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from core.di_container import Container
from domain.enums import TaskStatus
from ui.widgets.video_player_widget import VideoPlayerWidget
from ui.widgets.task_card_widget import TaskCardWidget


_STATUS_COLORS = {
    "queued": ("#95a5a6", "排队中"),
    "pending": ("#95a5a6", "等待中"),
    "running": ("#3498db", "运行中"),
    "succeeded": ("#27ae60", "已完成"),
    "failed": ("#e74c3c", "失败"),
    "cancelled": ("#e74c3c", "已取消"),
    "expired": ("#e74c3c", "已过期"),
}

_COLUMNS = ["任务 ID", "模型", "任务类型", "状态", "创建时间", "操作"]


class TaskListPage(QWidget):
    """任务列表页面"""

    def __init__(self, container: Container):
        super().__init__()
        self._container = container
        self._init_ui()
        if self._container is not None:
            self._subscribe_events()
            self._refresh()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # 标题栏
        header = QHBoxLayout()
        title = QLabel("任务列表")
        title.setObjectName("pageTitle")
        header.addWidget(title)
        header.addStretch()

        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self._refresh)
        header.addWidget(refresh_btn)

        layout.addLayout(header)

        # 表格
        self._table = QTableWidget()
        self._table.setColumnCount(len(_COLUMNS))
        self._table.setHorizontalHeaderLabels(_COLUMNS)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)

        header_view = self._table.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header_view.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header_view.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        header_view.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        header_view.setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)
        header_view.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(5, 120)

        self._table.doubleClicked.connect(self._on_row_double_clicked)

        layout.addWidget(self._table)
        self.setLayout(layout)

    def _subscribe_events(self):
        eb = self._container.event_bus
        eb.task_created.connect(self._on_task_created)
        eb.task_updated.connect(self._on_task_updated)
        eb.task_succeeded.connect(self._on_task_succeeded)
        eb.task_failed.connect(self._on_task_failed)

    def _refresh(self):
        self._table.setRowCount(0)
        try:
            tasks = self._container.task_repo.find_all()
            for task in tasks:
                self._add_task_row(task)
        except Exception as e:
            QMessageBox.warning(self, "加载失败", f"无法加载任务列表: {e}")

    def _add_task_row(self, task):
        row = self._table.rowCount()
        self._table.insertRow(row)

        # 任务 ID（截断显示）
        display_id = task.task_id[:16] + "..." if len(task.task_id) > 19 else task.task_id
        id_item = QTableWidgetItem(display_id)
        id_item.setData(Qt.ItemDataRole.UserRole, task.task_id)
        self._table.setItem(row, 0, id_item)

        # 模型
        self._table.setItem(row, 1, QTableWidgetItem(task.model))

        # 任务类型
        type_map = {
            "text_to_video": "文生视频",
            "multimodal_ref": "多模态参考",
            "edit_video": "编辑视频",
            "extend_video": "延长视频",
        }
        type_text = type_map.get(task.task_type, task.task_type)
        self._table.setItem(row, 2, QTableWidgetItem(type_text))

        # 状态
        status_value = task.status.value
        color, label = _STATUS_COLORS.get(status_value, ("#95a5a6", status_value))
        status_item = QTableWidgetItem(label)
        status_item.setForeground(QColor(color))
        status_item.setData(Qt.ItemDataRole.UserRole, status_value)
        self._table.setItem(row, 3, status_item)

        # 创建时间
        time_text = task.created_at.strftime("%Y-%m-%d %H:%M") if task.created_at else ""
        self._table.setItem(row, 4, QTableWidgetItem(time_text))

        # 操作列
        card = TaskCardWidget(
            task.task_id,
            status_value,
            on_cancel=lambda tid=task.task_id: self._on_cancel(tid),
            on_delete=lambda tid=task.task_id: self._on_delete(tid),
        )
        self._table.setCellWidget(row, 5, card)

    def _find_row_by_task_id(self, task_id: str) -> int:
        for row in range(self._table.rowCount()):
            item = self._table.item(row, 0)
            if item and item.data(Qt.ItemDataRole.UserRole) == task_id:
                return row
        return -1

    def _on_task_created(self, task_id: str):
        try:
            task = self._container.task_repo.find_by_id(task_id)
            if task:
                self._table.insertRow(0)
                self._add_task_row(task)
        except Exception:
            self._refresh()

    def _on_task_updated(self, task_id: str, status: str):
        row = self._find_row_by_task_id(task_id)
        if row < 0:
            return
        color, label = _STATUS_COLORS.get(status, ("#95a5a6", status))
        status_item = QTableWidgetItem(label)
        status_item.setForeground(QColor(color))
        status_item.setData(Qt.ItemDataRole.UserRole, status)
        self._table.setItem(row, 3, status_item)

    def _on_task_succeeded(self, task_id: str, video_url: str):
        self._on_task_updated(task_id, "succeeded")
        if task_id:
            self._show_video_player(task_id, video_url)

    def _on_task_failed(self, task_id: str, error_msg: str):
        self._on_task_updated(task_id, "failed")

    def _on_row_double_clicked(self, index):
        row = index.row()
        id_item = self._table.item(row, 0)
        if id_item is None:
            return
        task_id = id_item.data(Qt.ItemDataRole.UserRole)
        status_item = self._table.item(row, 3)
        if status_item and status_item.data(Qt.ItemDataRole.UserRole) == "succeeded":
            try:
                task = self._container.task_repo.find_by_id(task_id)
                if task and task.video_url:
                    self._show_video_player(task_id, task.video_url)
            except Exception as e:
                self._container.logger.warning(f"Failed to load video for task {task_id}: {e}")
                QMessageBox.warning(self, "加载失败", f"无法加载视频: {e}")

    def _show_video_player(self, task_id: str, video_url: str):
        player = VideoPlayerWidget(self._container, task_id, video_url)
        player.setWindowTitle(f"视频预览 - {task_id[:16]}...")
        player.resize(640, 480)
        player.show()
        self._player_window = player

    def _on_cancel(self, task_id: str):
        try:
            from core.exceptions import ApiError
            self._container.task_usecase.cancel_task(task_id)
            self._on_task_updated(task_id, "cancelled")
            QMessageBox.information(self, "取消成功", f"任务 {task_id[:16]} 已取消")
        except ApiError as e:
            QMessageBox.warning(self, "取消失败", f"取消失败 [{e.code}]：{e.message}\n\n任务可能已结束，请刷新列表查看最新状态。")
        except Exception as e:
            QMessageBox.warning(self, "取消失败", f"取消失败：{e}\n\n任务可能已结束或网络异常，请刷新列表确认。")

    def _on_delete(self, task_id: str):
        reply = QMessageBox.question(
            self, "确认删除", f"确定要删除任务 {task_id[:16]}... 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            self._container.task_usecase.delete_task(task_id)
            row = self._find_row_by_task_id(task_id)
            if row >= 0:
                self._table.removeRow(row)
        except Exception as e:
            QMessageBox.warning(self, "删除失败", f"删除失败：{e}\n\n请确认任务存在且未被锁定。")
