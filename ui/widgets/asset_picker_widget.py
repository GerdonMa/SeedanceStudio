"""
资产库选择器弹窗。

显示资产列表，支持上传新素材，订阅 EventBus 自动更新审核状态。
"""
from __future__ import annotations

import logging

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QFileDialog, QProgressDialog,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from core.event_bus import EventBus
from core.exceptions import ApiError


class AssetPickerWidget(QDialog):
    """资产库选择器弹窗"""

    def __init__(
        self,
        asset_usecase,
        event_bus: EventBus,
        logger: logging.Logger,
        parent=None,
    ):
        super().__init__(parent)
        self._asset_usecase = asset_usecase
        self._event_bus = event_bus
        self._logger = logger
        self._selected_asset_id: str | None = None
        self._init_ui()
        self._connect_signals()
        self._load_assets()

    def _init_ui(self):
        """初始化 UI"""
        self.setWindowTitle("从资产库选择")
        self.setMinimumSize(640, 420)
        self.setModal(True)

        layout = QVBoxLayout()
        layout.setSpacing(12)

        title = QLabel("资产库列表")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        self._table = QTableWidget()
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["资产 ID", "名称", "类型", "审核状态"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self._table)

        self._status_label = QLabel()
        self._status_label.setStyleSheet("color: #888;")
        layout.addWidget(self._status_label)

        btn_layout = QHBoxLayout()

        self._refresh_btn = QPushButton("刷新")
        self._refresh_btn.clicked.connect(self._load_assets)
        btn_layout.addWidget(self._refresh_btn)

        self._upload_btn = QPushButton("上传新素材")
        self._upload_btn.clicked.connect(self._on_upload)
        btn_layout.addWidget(self._upload_btn)

        btn_layout.addStretch()

        self._select_btn = QPushButton("选择")
        self._select_btn.clicked.connect(self._on_select)
        self._select_btn.setEnabled(False)
        btn_layout.addWidget(self._select_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _connect_signals(self):
        """连接信号"""
        self._event_bus.asset_approved.connect(self._on_asset_approved)
        self._event_bus.asset_rejected.connect(self._on_asset_rejected)
        self._table.itemSelectionChanged.connect(self._on_selection_changed)

    def _load_assets(self):
        """加载资产列表"""
        self._status_label.setText("加载中...")
        self._refresh_btn.setEnabled(False)
        try:
            assets = self._asset_usecase.list_assets()
            self._populate_table(assets)
            self._status_label.setText(f"共 {len(assets)} 个资产")
        except ApiError as e:
            self._status_label.setText(f"加载失败: {e.message}")
        except Exception as e:
            self._status_label.setText(f"加载失败: {str(e)}")
        finally:
            self._refresh_btn.setEnabled(True)

    def _populate_table(self, assets: list[dict]):
        """填充表格数据"""
        self._table.setRowCount(len(assets))
        for row, asset in enumerate(assets):
            asset_id = asset.get("id", "")
            name = asset.get("name", "未命名")
            asset_type = asset.get("type", "")
            status = asset.get("status", "unknown")

            self._table.setItem(row, 0, QTableWidgetItem(asset_id))
            self._table.setItem(row, 1, QTableWidgetItem(name))
            self._table.setItem(row, 2, QTableWidgetItem(asset_type))

            status_text = self._format_status(status)
            status_item = QTableWidgetItem(status_text)
            if status == "approved":
                status_item.setForeground(QColor("green"))
            elif status == "rejected":
                status_item.setForeground(QColor("red"))
            else:
                status_item.setForeground(QColor("orange"))
            self._table.setItem(row, 3, status_item)

    @staticmethod
    def _format_status(status: str) -> str:
        mapping = {
            "pending": "审核中",
            "queued": "排队中",
            "approved": "已通过",
            "rejected": "已拒绝",
        }
        return mapping.get(status, status)

    def _on_selection_changed(self):
        """选中项变化"""
        self._select_btn.setEnabled(len(self._table.selectedItems()) > 0)

    def _on_select(self):
        """确认选择"""
        row = self._table.currentRow()
        if row >= 0:
            asset_id = self._table.item(row, 0).text()
            self._selected_asset_id = asset_id
            self.accept()

    def _on_upload(self):
        """上传新素材"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择素材文件",
            "",
            "素材文件 (*.jpg *.jpeg *.png *.gif *.bmp *.webp *.mp4 *.mov *.mp3 *.wav)"
        )
        if not file_path:
            return

        progress = QProgressDialog("正在上传...", None, 0, 0, self)
        progress.setWindowTitle("上传中")
        progress.setModal(True)
        progress.show()

        try:
            asset_id = self._asset_usecase.upload_asset(file_path)
            progress.close()
            QMessageBox.information(
                self,
                "上传成功",
                f"素材已上传，资产 ID: {asset_id}\n\n审核可能需要一些时间，请稍后查看状态。"
            )
            self._load_assets()
        except ApiError as e:
            progress.close()
            QMessageBox.critical(self, "上传失败", f"上传失败 [{e.code}]：{e.message}\n\n请检查素材格式是否支持并重试。")
        except Exception as e:
            progress.close()
            QMessageBox.critical(self, "上传失败", f"上传失败：{e}\n\n请检查网络连接并重试。")
        else:
            if progress is not None:
                progress.close()

    def _on_asset_approved(self, asset_id: str):
        """资产审核通过（主线程）"""
        self._update_asset_status_in_row(asset_id, "已通过", QColor("green"))

    def _on_asset_rejected(self, asset_id: str, reason: str):
        """资产审核被拒（主线程）"""
        self._update_asset_status_in_row(asset_id, f"已拒绝: {reason}", QColor("red"))

    def _update_asset_status_in_row(self, asset_id: str, status_text: str, color: QColor):
        """更新表格中指定资产行的状态"""
        for row in range(self._table.rowCount()):
            item = self._table.item(row, 0)
            if item and item.text() == asset_id:
                status_item = self._table.item(row, 3)
                if status_item:
                    status_item.setText(status_text)
                    status_item.setForeground(color)
                break

    def get_selected_asset_id(self) -> str | None:
        """获取选中的资产 ID"""
        return self._selected_asset_id
