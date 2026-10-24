"""
任务列表页面（任务中心）。

显示所有任务历史，支持状态查看、取消、删除和视频预览；
页头 + 统计卡片 + 任务表格三段式布局。
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QMessageBox, QSizePolicy,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QPixmap

from core.di_container import Container
from core.exceptions import ApiError
from domain.enums import TaskStatus
from ui.widgets.video_player_widget import VideoPlayerWidget
from ui.widgets.task_card_widget import TaskCardWidget
from ui.widgets.page_header import PageHeader
from ui.widgets.pro_icons import refresh_icon, sync_icon, layers_icon, create_icon
from ui.widgets.thumbnail_service import ThumbnailService


_STATUS_COLORS = {
    "queued": ("#95a5a6", "排队中"),
    "pending": ("#95a5a6", "等待中"),
    "running": ("#3498db", "运行中"),
    "succeeded": ("#27ae60", "已完成"),
    "failed": ("#e74c3c", "失败"),
    "cancelled": ("#e74c3c", "已取消"),
    "expired": ("#e74c3c", "已过期"),
}

_COLUMNS = ["预览", "任务 ID", "模型", "任务类型", "状态", "创建时间", "操作"]

# 列索引常量（预览列插入后避免魔法数字）
_COL_PREVIEW, _COL_ID, _COL_MODEL, _COL_TYPE, _COL_STATUS, _COL_TIME, _COL_ACTIONS = range(7)


class TaskListPage(QWidget):
    """任务列表页面"""

    def __init__(self, container: Container):
        super().__init__()
        self._container = container
        self._player_windows: set = set()
        self._init_ui()
        if self._container is not None:
            self._subscribe_events()
            self._refresh()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # 页头：眉题 + 标题 + 副标题 + 右侧动作
        header = PageHeader("Tasks", "任务中心", "追踪生成任务进度，同步平台最近记录")

        refresh_btn = QPushButton("刷新")
        refresh_btn.setIcon(refresh_icon())
        refresh_btn.setIconSize(QSize(16, 16))
        refresh_btn.clicked.connect(self._refresh)
        header.add_widget(refresh_btn)

        self._sync_btn = QPushButton("同步平台任务")
        self._sync_btn.setIcon(sync_icon())
        self._sync_btn.setIconSize(QSize(16, 16))
        self._sync_btn.clicked.connect(self._on_sync_recent)
        header.add_widget(self._sync_btn)

        layout.addWidget(header)

        # 统计卡片行：进行中 / 已完成 / 失败
        self._stat_values: dict[str, QLabel] = {}
        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)
        for key, label in (("running", "进行中"), ("succeeded", "已完成"), ("failed", "失败")):
            card = QWidget()
            card.setObjectName("statCard")
            card.setFixedHeight(64)
            card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(16, 8, 16, 8)
            card_layout.setSpacing(2)

            value_label = QLabel("0")
            value_label.setObjectName("statValue")
            label_label = QLabel(label)
            label_label.setObjectName("statLabel")

            card_layout.addWidget(value_label)
            card_layout.addWidget(label_label)
            stats_row.addWidget(card, 1)
            self._stat_values[key] = value_label
        layout.addLayout(stats_row)

        # 表格
        self._table = QTableWidget()
        self._table.setColumnCount(len(_COLUMNS))
        self._table.setHorizontalHeaderLabels(_COLUMNS)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.setShowGrid(False)
        self._table.verticalHeader().setVisible(False)
        self._table.verticalHeader().setDefaultSectionSize(62)

        header_view = self._table.horizontalHeader()
        header_view.setSectionResizeMode(_COL_PREVIEW, QHeaderView.ResizeMode.Fixed)
        header_view.setSectionResizeMode(_COL_ID, QHeaderView.ResizeMode.Interactive)
        header_view.setSectionResizeMode(_COL_MODEL, QHeaderView.ResizeMode.Stretch)
        header_view.setSectionResizeMode(_COL_TYPE, QHeaderView.ResizeMode.Interactive)
        header_view.setSectionResizeMode(_COL_STATUS, QHeaderView.ResizeMode.Interactive)
        header_view.setSectionResizeMode(_COL_TIME, QHeaderView.ResizeMode.Interactive)
        header_view.setSectionResizeMode(_COL_ACTIONS, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(_COL_PREVIEW, 112)
        self._table.setColumnWidth(_COL_ACTIONS, 170)

        self._table.doubleClicked.connect(self._on_row_double_clicked)

        layout.addWidget(self._table)

        # 空状态视图（无任务时替代表格显示）
        self._empty_view = QWidget()
        self._empty_view.setObjectName("statCard")
        empty_layout = QVBoxLayout(self._empty_view)
        empty_layout.setContentsMargins(0, 40, 0, 40)
        empty_layout.setSpacing(10)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        empty_icon = QLabel()
        empty_icon.setPixmap(layers_icon().pixmap(QSize(44, 44)))
        empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(empty_icon)

        empty_title = QLabel("暂无任务")
        empty_title.setObjectName("pageTitle")
        empty_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(empty_title)

        empty_sub = QLabel("在创建工作台发起第一个生成任务，或同步平台最近记录")
        empty_sub.setObjectName("pageSub")
        empty_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(empty_sub)

        create_btn = QPushButton("去创建任务")
        create_btn.setProperty("role", "primary")
        create_btn.clicked.connect(
            lambda: self._container.event_bus.page_switch_requested.emit(0)
        )
        empty_layout.addWidget(create_btn, 0, Qt.AlignmentFlag.AlignCenter)
        self._empty_view.hide()
        layout.addWidget(self._empty_view)

        self.setLayout(layout)

    def _subscribe_events(self):
        eb = self._container.event_bus
        eb.task_created.connect(self._on_task_created)
        eb.task_updated.connect(self._on_task_updated)
        eb.task_succeeded.connect(self._on_task_succeeded)
        eb.task_failed.connect(self._on_task_failed)
        # 缩略图抓取完成后更新预览列
        ThumbnailService.instance().thumbnail_ready.connect(self._on_thumbnail_ready)

    def _on_sync_recent(self):
        """同步平台最近任务（同步期间禁用按钮防连点）"""
        eb = self._container.event_bus
        self._sync_btn.setEnabled(False)
        try:
            n = self._container.task_usecase.sync_recent_tasks()
            self._refresh()
            eb.toast_requested.emit("success", "同步完成", f"新增 {n} 个平台任务")
        except ApiError as e:
            eb.toast_requested.emit("error", "同步失败", f"[{e.code}] {e.message}")
        except Exception as e:
            eb.toast_requested.emit("error", "同步失败", f"同步平台任务时出错：{e}")
        finally:
            self._sync_btn.setEnabled(True)

    def _refresh(self):
        self._table.setRowCount(0)
        try:
            tasks = self._container.task_usecase.find_all_tasks()
            self._update_stats(tasks)
            if not tasks:
                self._show_empty_state()
                return
            self._table.setVisible(True)
            self._empty_view.hide()
            for task in tasks:
                self._add_task_row(task)
        except Exception as e:
            QMessageBox.warning(self, "加载失败", f"无法加载任务列表: {e}")
            self._update_stats([])
            self._show_empty_state()

    def _update_stats(self, tasks) -> None:
        """统计任务状态并更新顶部三张统计卡片（>0 时数字着色）"""
        counts = {"running": 0, "succeeded": 0, "failed": 0}
        for task in tasks:
            status = task.status.value if hasattr(task.status, "value") else str(task.status)
            if status in ("queued", "pending", "running"):
                counts["running"] += 1
            elif status == "succeeded":
                counts["succeeded"] += 1
            elif status in ("failed", "cancelled", "expired"):
                counts["failed"] += 1
        for key, label in self._stat_values.items():
            count = counts.get(key, 0)
            label.setText(str(count))
            # 0 值弱化灰色，>0 按类型着色；改 property 后需 unpolish/polish 刷新 QSS
            label.setProperty("accent", key if count > 0 else "")
            label.style().unpolish(label)
            label.style().polish(label)

    def _show_empty_state(self):
        """显示空状态视图（隐藏表格）"""
        self._table.setVisible(False)
        self._empty_view.show()

    def _add_task_row(self, task):
        row = self._table.rowCount()
        self._table.insertRow(row)

        status_value = task.status.value

        # 预览列（缩略图 / 占位图标）
        preview = QLabel()
        preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._table.setCellWidget(row, _COL_PREVIEW, preview)
        self._set_preview_content(preview, task.task_id, task.video_url, status_value)

        # 任务 ID（截断显示）
        display_id = task.task_id[:16] + "..." if len(task.task_id) > 19 else task.task_id
        id_item = QTableWidgetItem(display_id)
        id_item.setData(Qt.ItemDataRole.UserRole, task.task_id)
        self._table.setItem(row, _COL_ID, id_item)

        # 模型
        self._table.setItem(row, _COL_MODEL, QTableWidgetItem(task.model))

        # 任务类型
        type_map = {
            "text_to_video": "文生视频",
            "multimodal_ref": "多模态参考",
            "edit_video": "编辑视频",
            "extend_video": "延长视频",
        }
        type_text = type_map.get(task.task_type, task.task_type)
        self._table.setItem(row, _COL_TYPE, QTableWidgetItem(type_text))

        # 状态（● 前缀圆点）
        color, label = _STATUS_COLORS.get(status_value, ("#95a5a6", status_value))
        status_item = QTableWidgetItem(f"● {label}")
        status_item.setForeground(QColor(color))
        status_item.setData(Qt.ItemDataRole.UserRole, status_value)
        self._table.setItem(row, _COL_STATUS, status_item)

        # 创建时间
        time_text = task.created_at.strftime("%Y-%m-%d %H:%M") if task.created_at else ""
        self._table.setItem(row, _COL_TIME, QTableWidgetItem(time_text))

        # 操作列
        card = TaskCardWidget(
            task.task_id,
            status_value,
            on_cancel=lambda tid=task.task_id: self._on_cancel(tid),
            on_delete=lambda tid=task.task_id: self._on_delete(tid),
        )
        self._table.setCellWidget(row, _COL_ACTIONS, card)

    def _set_preview_content(self, label: QLabel, task_id: str,
                             video_url: str | None, status_value: str) -> None:
        """填充预览单元格：已完成显示缩略图（缺失则异步抓帧），否则灰色占位"""
        if status_value == "succeeded":
            service = ThumbnailService.instance()
            path = service.thumbnail_path(task_id)
            if path is not None:
                label.setPixmap(QPixmap(str(path)).scaled(
                    96, 54, Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                ))
            else:
                label.setPixmap(create_icon(color="#626B7E").pixmap(QSize(28, 28)))
                if video_url:
                    service.request(task_id, video_url)
        else:
            label.setPixmap(create_icon(color="#3A4050").pixmap(QSize(28, 28)))

    def _find_row_by_task_id(self, task_id: str) -> int:
        for row in range(self._table.rowCount()):
            item = self._table.item(row, _COL_ID)
            if item and item.data(Qt.ItemDataRole.UserRole) == task_id:
                return row
        return -1

    def _on_thumbnail_ready(self, task_id: str):
        """缩略图抓取完成，更新对应行预览格"""
        row = self._find_row_by_task_id(task_id)
        if row < 0:
            return
        widget = self._table.cellWidget(row, _COL_PREVIEW)
        if isinstance(widget, QLabel):
            path = ThumbnailService.instance().thumbnail_path(task_id)
            if path is not None:
                widget.setPixmap(QPixmap(str(path)).scaled(
                    96, 54, Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                ))

    def _on_task_created(self, task_id: str):
        self._refresh()

    def _on_task_updated(self, task_id: str, status: str):
        row = self._find_row_by_task_id(task_id)
        if row >= 0:
            color, label = _STATUS_COLORS.get(status, ("#95a5a6", status))
            status_item = QTableWidgetItem(f"● {label}")
            status_item.setForeground(QColor(color))
            status_item.setData(Qt.ItemDataRole.UserRole, status)
            self._table.setItem(row, _COL_STATUS, status_item)
            # 成功后刷新该行预览格（触发缩略图抓取）
            preview = self._table.cellWidget(row, _COL_PREVIEW)
            if isinstance(preview, QLabel) and status == "succeeded":
                try:
                    task = next(
                        t for t in self._container.task_usecase.find_all_tasks()
                        if t.task_id == task_id
                    )
                    self._set_preview_content(preview, task_id, task.video_url, status)
                except StopIteration:
                    pass
        # 状态变化会影响统计，重新统计
        try:
            self._update_stats(self._container.task_usecase.find_all_tasks())
        except Exception:
            pass

    def _on_task_succeeded(self, task_id: str, video_url: str):
        self._on_task_updated(task_id, "succeeded")
        if task_id:
            self._show_video_player(task_id, video_url)

    def _on_task_failed(self, task_id: str, error_msg: str):
        self._on_task_updated(task_id, "failed")

    def _on_row_double_clicked(self, index):
        row = index.row()
        id_item = self._table.item(row, _COL_ID)
        if id_item is None:
            return
        task_id = id_item.data(Qt.ItemDataRole.UserRole)
        status_item = self._table.item(row, _COL_STATUS)
        if status_item and status_item.data(Qt.ItemDataRole.UserRole) == "succeeded":
            try:
                task = self._container.task_usecase.query_task(task_id)
                if task and task.video_url:
                    self._show_video_player(task_id, task.video_url)
            except Exception as e:
                self._container.logger.warning(f"Failed to load video for task {task_id}: {e}")
                QMessageBox.warning(self, "加载失败", f"无法加载视频: {e}")

    def _show_video_player(self, task_id: str, video_url: str):
        """打开预览窗口（多实例持有，关闭自动移除引用）"""
        player = VideoPlayerWidget(self._container, task_id, video_url)
        player.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        player.destroyed.connect(
            lambda obj, p=player: self._player_windows.discard(p)
        )
        player.show()
        player.raise_()
        player.activateWindow()
        self._player_windows.add(player)

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
            try:
                self._update_stats(self._container.task_usecase.find_all_tasks())
            except Exception:
                pass
        except Exception as e:
            QMessageBox.warning(self, "删除失败", f"删除失败：{e}\n\n请确认任务存在且未被锁定。")
