"""
素材上传组件。

支持图片/视频/音频拖拽上传、公网 URL 输入、资产库模式切换。
"""
from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QCheckBox, QScrollArea,
    QFrame, QFileDialog, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QPixmap, QFont

from core.di_container import Container
from domain.entities import MediaItem
from domain.enums import MediaType
from themes.theme_context import ThemeContext
from ui.widgets.asset_picker_widget import AssetPickerWidget

_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}
_VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}
_AUDIO_EXTENSIONS = {'.mp3', '.wav', '.aac', '.ogg', '.wma', '.flac'}

_MAX_COUNTS = {
    MediaType.IMAGE: 9,
    MediaType.VIDEO: 3,
    MediaType.AUDIO: 3,
}

_TYPE_LABELS = {
    MediaType.IMAGE: "图片",
    MediaType.VIDEO: "视频",
    MediaType.AUDIO: "音频",
}

_TYPE_COLORS = {
    MediaType.IMAGE: "#3498db",
    MediaType.VIDEO: "#e67e22",
    MediaType.AUDIO: "#2ecc71",
}


def _detect_media_type(path_or_url: str) -> MediaType | None:
    """根据文件扩展名检测媒体类型"""
    parsed = urlparse(path_or_url)
    path_part = parsed.path if parsed.scheme else path_or_url
    ext = Path(path_part).suffix.lower()
    if ext in _IMAGE_EXTENSIONS:
        return MediaType.IMAGE
    if ext in _VIDEO_EXTENSIONS:
        return MediaType.VIDEO
    if ext in _AUDIO_EXTENSIONS:
        return MediaType.AUDIO
    return None


def _count_by_type(items: list[MediaItem], media_type: MediaType) -> int:
    """统计指定类型的素材数量"""
    return sum(1 for item in items if item.type == media_type)


class _DropZone(QLabel):
    """拖拽区域"""

    files_dropped = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("拖拽文件到此处\n或点击按钮选择文件")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setAcceptDrops(True)
        self.setMinimumHeight(80)
        self.setObjectName("dropZone")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        files = [url.toLocalFile() for url in urls if url.isLocalFile()]
        if files:
            self.files_dropped.emit(files)
        event.acceptProposedAction()


class MediaUploadWidget(QWidget):
    """素材上传组件"""

    items_changed = pyqtSignal()

    def __init__(self, container: Container, parent=None):
        super().__init__(parent)
        self._container = container
        self._items: list[MediaItem] = []
        self._init_ui()
        self._restore_prefs()
        # 在恢复偏好后再连接保存信号，避免 startup 时冗余写入
        self._asset_mode_checkbox.toggled.connect(
            lambda v: self._container.settings_usecase.save_preference("asset_mode_enabled", v)
        )

    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # 资产库模式开关
        self._asset_mode_checkbox = QCheckBox("使用资产库模式")
        self._asset_mode_checkbox.toggled.connect(self._on_toggle_asset_mode)
        layout.addWidget(self._asset_mode_checkbox)

        # 资产库模式输入区（默认隐藏）
        self._asset_mode_widget = QWidget()
        asset_layout = QHBoxLayout()
        asset_layout.setContentsMargins(0, 0, 0, 0)
        self._asset_id_input = QLineEdit()
        self._asset_id_input.setPlaceholderText("输入资产 ID，如 asset://xxx")
        asset_layout.addWidget(self._asset_id_input)
        self._asset_picker_btn = QPushButton("从资产库选择")
        self._asset_picker_btn.clicked.connect(self._on_open_asset_picker)
        asset_layout.addWidget(self._asset_picker_btn)
        self._asset_mode_widget.setLayout(asset_layout)
        self._asset_mode_widget.setVisible(False)
        layout.addWidget(self._asset_mode_widget)

        # 普通模式上传区
        self._upload_area = QWidget()
        upload_layout = QVBoxLayout()
        upload_layout.setContentsMargins(0, 0, 0, 0)
        upload_layout.setSpacing(6)

        # 拖拽区
        self._drop_zone = _DropZone()
        upload_layout.addWidget(self._drop_zone)

        # 按钮行
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        btn_image = QPushButton("选择图片")
        btn_image.clicked.connect(lambda: self._on_browse_files(MediaType.IMAGE))
        btn_row.addWidget(btn_image)

        btn_video = QPushButton("选择视频")
        btn_video.clicked.connect(lambda: self._on_browse_files(MediaType.VIDEO))
        btn_row.addWidget(btn_video)

        btn_audio = QPushButton("选择音频")
        btn_audio.clicked.connect(lambda: self._on_browse_files(MediaType.AUDIO))
        btn_row.addWidget(btn_audio)

        btn_row.addStretch()
        upload_layout.addLayout(btn_row)

        # URL 输入行
        url_row = QHBoxLayout()
        url_row.setSpacing(4)
        self._url_input = QLineEdit()
        self._url_input.setPlaceholderText("输入公网 URL（图片/视频/音频）")
        url_row.addWidget(self._url_input)
        btn_add_url = QPushButton("添加")
        btn_add_url.clicked.connect(self._on_add_url)
        url_row.addWidget(btn_add_url)
        upload_layout.addLayout(url_row)

        self._upload_area.setLayout(upload_layout)
        layout.addWidget(self._upload_area)

        # 缩略图列表区
        thumb_label = QLabel("已添加素材:")
        thumb_label.setObjectName("mediaSectionLabel")
        layout.addWidget(thumb_label)

        self._thumbnail_scroll = QScrollArea()
        self._thumbnail_scroll.setWidgetResizable(True)
        self._thumbnail_scroll.setMaximumHeight(160)
        self._thumbnail_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._thumbnail_container = QWidget()
        self._thumbnail_layout = QHBoxLayout()
        self._thumbnail_layout.setContentsMargins(4, 4, 4, 4)
        self._thumbnail_layout.setSpacing(8)
        self._thumbnail_layout.addStretch()
        self._thumbnail_container.setLayout(self._thumbnail_layout)

        self._thumbnail_scroll.setWidget(self._thumbnail_container)
        layout.addWidget(self._thumbnail_scroll)

        # 数量提示
        self._count_label = QLabel()
        self._count_label.setObjectName("mediaCountLabel")
        self._update_count_label()
        layout.addWidget(self._count_label)

        self.setLayout(layout)

        # 连接拖拽信号
        self._drop_zone.files_dropped.connect(self._on_files_dropped)

    def _restore_prefs(self):
        """恢复偏好设置"""
        if self._container is None:
            return
        prefs = self._container.settings_usecase.load_preferences()
        asset_mode = prefs.get("asset_mode_enabled", False)
        self._asset_mode_checkbox.setChecked(asset_mode)

    def _on_toggle_asset_mode(self, checked: bool):
        """切换资产库模式"""
        self._asset_mode_widget.setVisible(checked)
        self._upload_area.setVisible(not checked)

    def _on_open_asset_picker(self):
        """打开资产库选择器"""
        picker = AssetPickerWidget(
            self._container.asset_usecase,
            self._container.event_bus,
            self._container.logger,
            self,
        )
        if picker.exec() == AssetPickerWidget.DialogCode.Accepted:
            asset_id = picker.get_selected_asset_id()
            if asset_id:
                self._asset_id_input.setText(f"asset://{asset_id}")

    def _on_files_dropped(self, files: list[str]):
        """处理拖拽的文件"""
        added = 0
        for file_path in files:
            if self._try_add_local_file(file_path):
                added += 1
        if added > 0:
            self.items_changed.emit()

    def _on_browse_files(self, media_type: MediaType):
        """浏览选择文件"""
        file_filter = self._get_file_filter(media_type)
        files, _ = QFileDialog.getOpenFileNames(
            self,
            f"选择{_TYPE_LABELS[media_type]}文件",
            "",
            file_filter
        )
        added = 0
        for file_path in files:
            if self._try_add_local_file(file_path):
                added += 1
        if added > 0:
            self.items_changed.emit()

    def _on_add_url(self):
        """添加 URL 素材"""
        url = self._url_input.text().strip()
        if not url:
            return

        media_type = _detect_media_type(url)
        if media_type is None:
            QMessageBox.warning(
                self,
                "无法识别",
                "无法识别该 URL 的文件类型，请确认 URL 包含图片/视频/音频扩展名"
            )
            return

        current_count = _count_by_type(self._items, media_type)
        max_count = _MAX_COUNTS[media_type]
        if current_count >= max_count:
            QMessageBox.warning(
                self,
                "超出限制",
                f"{_TYPE_LABELS[media_type]}最多 {max_count} 个，当前已有 {current_count} 个"
            )
            return

        item = MediaItem(type=media_type, url=url)
        self._items.append(item)
        self._add_thumbnail_widget(item, len(self._items) - 1)
        self._url_input.clear()
        self._update_count_label()
        self.items_changed.emit()

    def _try_add_local_file(self, file_path: str) -> bool:
        """尝试添加本地文件，返回是否成功"""
        media_type = _detect_media_type(file_path)
        if media_type is None:
            ext = Path(file_path).suffix.lower()
            if ext:
                QMessageBox.warning(self, "不支持的文件", f"不支持的文件格式 (.{ext})，请使用图片、视频或音频文件")
            return False

        current_count = _count_by_type(self._items, media_type)
        max_count = _MAX_COUNTS[media_type]
        if current_count >= max_count:
            QMessageBox.warning(
                self,
                "超出限制",
                f"{_TYPE_LABELS[media_type]}最多 {max_count} 个，当前已有 {current_count} 个"
            )
            return False

        item = MediaItem(type=media_type, url=file_path)
        self._items.append(item)
        self._add_thumbnail_widget(item, len(self._items) - 1)
        self._update_count_label()
        return True

    def _add_thumbnail_widget(self, item: MediaItem, index: int):
        """添加缩略图组件到布局"""
        widget = QFrame()
        widget.setFixedSize(130, 150)
        widget.setObjectName("mediaItemWidget")

        frame_layout = QVBoxLayout()
        frame_layout.setContentsMargins(4, 4, 4, 4)
        frame_layout.setSpacing(4)

        # 缩略图
        thumb_label = QLabel()
        thumb_label.setFixedSize(120, 90)
        thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if item.type == MediaType.IMAGE:
            pixmap = QPixmap(item.url)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(
                    120, 90,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                thumb_label.setPixmap(pixmap)
            else:
                thumb_label.setText("图片")
                color = ThemeContext.get_color("media_image", "#3498db")
                thumb_label.setStyleSheet(f"background-color: {color}; color: #fff; font-size: 13px; border-radius: 4px;")
        elif item.type == MediaType.VIDEO:
            thumb_label.setText("视频")
            color = ThemeContext.get_color("media_video", "#e67e22")
            thumb_label.setStyleSheet(f"background-color: {color}; color: #fff; font-size: 13px; border-radius: 4px;")
        else:
            thumb_label.setText("音频")
            color = ThemeContext.get_color("media_audio", "#2ecc71")
            thumb_label.setStyleSheet(f"background-color: {color}; color: #fff; font-size: 13px; border-radius: 4px;")

        frame_layout.addWidget(thumb_label)

        # 文件名标签
        name = os.path.basename(item.url) if os.path.sep in item.url else item.url
        name = name[:20] + "..." if len(name) > 20 else name
        name_label = QLabel(name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setObjectName("mediaNameLabel")
        name_label.setWordWrap(True)
        frame_layout.addWidget(name_label)

        # 删除按钮
        remove_btn = QPushButton("移除")
        remove_btn.setFixedHeight(22)
        remove_btn.setObjectName("mediaRemoveButton")
        remove_btn.clicked.connect(lambda: self._remove_item(index))
        frame_layout.addWidget(remove_btn)

        widget.setLayout(frame_layout)

        # 插入到 stretch 之前
        self._thumbnail_layout.insertWidget(
            self._thumbnail_layout.count() - 1,
            widget
        )

    def _remove_item(self, index: int):
        """移除指定位置的素材"""
        if 0 <= index < len(self._items):
            self._items.pop(index)
            self._rebuild_thumbnails()
            self._update_count_label()
            self.items_changed.emit()

    def _rebuild_thumbnails(self):
        """重建所有缩略图"""
        while self._thumbnail_layout.count() > 1:
            item_widget = self._thumbnail_layout.takeAt(0)
            if item_widget.widget():
                item_widget.widget().deleteLater()

        for i, item in enumerate(self._items):
            self._add_thumbnail_widget(item, i)

    def _update_count_label(self):
        """更新数量提示"""
        parts = []
        for mt in (MediaType.IMAGE, MediaType.VIDEO, MediaType.AUDIO):
            cnt = _count_by_type(self._items, mt)
            max_cnt = _MAX_COUNTS[mt]
            parts.append(f"{_TYPE_LABELS[mt]}: {cnt}/{max_cnt}")
        self._count_label.setText("  |  ".join(parts))

    def _get_file_filter(self, media_type: MediaType) -> str:
        """获取文件筛选器"""
        if media_type == MediaType.IMAGE:
            return "图片文件 (*.jpg *.jpeg *.png *.gif *.bmp *.webp *.tiff)"
        elif media_type == MediaType.VIDEO:
            return "视频文件 (*.mp4 *.mov *.avi *.mkv *.webm)"
        else:
            return "音频文件 (*.mp3 *.wav *.aac *.ogg *.wma *.flac)"

    def get_media_items(self) -> list[MediaItem]:
        """返回已添加的素材列表"""
        if self._asset_mode_checkbox.isChecked():
            asset_id = self._asset_id_input.text().strip()
            if asset_id:
                clean_id = asset_id.replace("asset://", "")
                return [MediaItem(type=MediaType.IMAGE, url=f"asset://{clean_id}", asset_id=clean_id)]
            return []
        return list(self._items)

    def clear(self):
        """清空所有素材"""
        self._items.clear()
        self._rebuild_thumbnails()
        self._update_count_label()
        self.items_changed.emit()

    def validate(self) -> list[str]:
        """
        校验当前素材列表。

        Returns:
            错误信息列表，空列表表示通过
        """
        errors = []
        image_count = _count_by_type(self._items, MediaType.IMAGE)
        video_count = _count_by_type(self._items, MediaType.VIDEO)
        audio_count = _count_by_type(self._items, MediaType.AUDIO)

        if image_count > _MAX_COUNTS[MediaType.IMAGE]:
            errors.append(f"图片最多 {_MAX_COUNTS[MediaType.IMAGE]} 张，当前 {image_count} 张")
        if video_count > _MAX_COUNTS[MediaType.VIDEO]:
            errors.append(f"视频最多 {_MAX_COUNTS[MediaType.VIDEO]} 个，当前 {video_count} 个")
        if audio_count > _MAX_COUNTS[MediaType.AUDIO]:
            errors.append(f"音频最多 {_MAX_COUNTS[MediaType.AUDIO]} 个，当前 {audio_count} 个")

        return errors

    def on_theme_changed(self):
        self._rebuild_thumbnails()
