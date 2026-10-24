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
    QFrame, QFileDialog, QMessageBox, QSizePolicy, QComboBox, QDialog,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QPixmap, QFont

from core.di_container import Container
from domain.entities import MediaItem
from domain.enums import MediaType
from domain.model_capabilities import get_capability
from themes.theme_context import ThemeContext
from ui.widgets.asset_picker_widget import AssetPickerWidget
from ui.widgets.flow_layout import FlowLayout

_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}
_VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}
_AUDIO_EXTENSIONS = {'.mp3', '.wav', '.aac', '.ogg', '.wma', '.flac'}

# 默认素材上限（未知模型的宽松兜底，实际以模型能力表为准）
_DEFAULT_MAX_COUNTS = {
    MediaType.IMAGE: 9,
    MediaType.VIDEO: 3,
    MediaType.AUDIO: 3,
}

# 图片素材角色选项：(userData, 显示文本)
_IMAGE_ROLES = [
    ("reference_image", "参考图"),
    ("first_frame", "首帧"),
    ("last_frame", "尾帧"),
]

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
    """拖拽区域（横条式，点击可选择文件）"""

    files_dropped = pyqtSignal(list)
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("⤒  拖拽文件到此处，或点击选择图片 / 视频 / 音频")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setAcceptDrops(True)
        self.setMinimumHeight(44)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("dropZone")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        files = [url.toLocalFile() for url in urls if url.isLocalFile()]
        if files:
            self.files_dropped.emit(files)
        event.acceptProposedAction()


class _ClickableThumb(QLabel):
    """可点击缩略图：点击弹出原图大图查看窗"""

    clicked = pyqtSignal()

    def __init__(self, pixmap: QPixmap | None, parent=None):
        super().__init__(parent)
        self._full_pixmap = pixmap
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        if pixmap is not None and not pixmap.isNull():
            self.setPixmap(pixmap.scaled(
                164, 116,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            ))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def show_full(self):
        """弹出原图查看窗（点击任意处关闭）"""
        if self._full_pixmap is None or self._full_pixmap.isNull():
            return
        dlg = QDialog(self)
        dlg.setWindowTitle("素材预览")
        dlg.setModal(False)
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(12, 12, 12, 12)
        viewer = QLabel()
        viewer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pm = self._full_pixmap
        # 大图限制在 1280×800 内展示
        if pm.width() > 1280 or pm.height() > 800:
            pm = pm.scaled(1280, 800, Qt.AspectRatioMode.KeepAspectRatio,
                           Qt.TransformationMode.SmoothTransformation)
        viewer.setPixmap(pm)
        layout.addWidget(viewer)
        hint = QLabel("点击任意处关闭")
        hint.setObjectName("mediaCountLabel")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)
        dlg.mousePressEvent = lambda _e: dlg.close()
        dlg.exec()


class MediaUploadWidget(QWidget):
    """素材上传组件"""

    items_changed = pyqtSignal()

    def __init__(self, container: Container, parent=None):
        super().__init__(parent)
        self._container = container
        self._items: list[MediaItem] = []
        self._max_counts: dict[MediaType, int] = dict(_DEFAULT_MAX_COUNTS)
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

        # 拖拽横条（点击选择文件）
        self._drop_zone = _DropZone()
        self._drop_zone.clicked.connect(lambda: self._on_browse_files(MediaType.IMAGE))
        upload_layout.addWidget(self._drop_zone)

        # 操作行：类型按钮 + URL 输入合并，压缩垂直占用
        action_row = QHBoxLayout()
        action_row.setSpacing(8)

        for text, media_type in (("图片", MediaType.IMAGE), ("视频", MediaType.VIDEO), ("音频", MediaType.AUDIO)):
            btn = QPushButton(text)
            btn.setToolTip(f"选择{ {'IMAGE': '图片', 'VIDEO': '视频', 'AUDIO': '音频'}[media_type.name] }文件")
            btn.clicked.connect(lambda _c, mt=media_type: self._on_browse_files(mt))
            action_row.addWidget(btn)

        self._url_input = QLineEdit()
        self._url_input.setPlaceholderText("或输入公网 URL（图片/视频/音频）")
        self._url_input.setMinimumWidth(120)
        action_row.addWidget(self._url_input, 1)
        btn_add_url = QPushButton("添加")
        btn_add_url.clicked.connect(self._on_add_url)
        action_row.addWidget(btn_add_url)
        upload_layout.addLayout(action_row)

        self._upload_area.setLayout(upload_layout)
        layout.addWidget(self._upload_area)

        # 标题行：已添加素材 + 数量统计（合并为一行）
        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        thumb_label = QLabel("已添加素材")
        thumb_label.setObjectName("mediaSectionLabel")
        header_row.addWidget(thumb_label)
        header_row.addStretch()
        self._count_label = QLabel()
        self._count_label.setObjectName("mediaCountLabel")
        self._update_count_label()
        header_row.addWidget(self._count_label)
        layout.addLayout(header_row)

        # 素材浏览区：流式网格（自动换行），占满剩余高度，纵向滚动
        self._thumbnail_scroll = QScrollArea()
        self._thumbnail_scroll.setWidgetResizable(True)
        self._thumbnail_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._thumbnail_scroll.setMinimumHeight(240)
        self._thumbnail_scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._thumbnail_container = QWidget()
        self._thumbnail_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._thumbnail_layout = FlowLayout(self._thumbnail_container, margin=2, spacing=10)
        self._thumbnail_container.setLayout(self._thumbnail_layout)

        self._thumbnail_scroll.setWidget(self._thumbnail_container)
        layout.addWidget(self._thumbnail_scroll, 1)

        self.setLayout(layout)

        # 连接拖拽信号
        self._drop_zone.files_dropped.connect(self._on_files_dropped)

    def set_model(self, model_id: str):
        """
        按模型能力表更新素材上限（切换模型时由创建页调用）。

        已添加素材不做删除，仅新上传按新上限拦截。
        """
        cap = get_capability(model_id)
        self._max_counts = {
            MediaType.IMAGE: cap.max_images,
            MediaType.VIDEO: cap.max_videos,
            MediaType.AUDIO: cap.max_audios,
        }
        self._update_count_label()

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
        max_count = self._max_counts[media_type]
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
        max_count = self._max_counts[media_type]
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
        """添加素材卡片：编号徽章 + 大缩略图（点击查看）+ 文件名/尺寸 + 角色选择"""
        widget = QFrame()
        widget.setFixedSize(176, 208)
        widget.setObjectName("mediaItemWidget")

        frame_layout = QVBoxLayout()
        frame_layout.setContentsMargins(5, 5, 5, 5)
        frame_layout.setSpacing(3)

        # 缩略图区（含左上角编号/角色徽章）
        thumb_box = QWidget()
        thumb_box.setObjectName("mediaThumbBox")
        thumb_box.setFixedSize(166, 118)
        thumb_layout = QVBoxLayout(thumb_box)
        thumb_layout.setContentsMargins(0, 0, 0, 0)

        full_pixmap = None
        if item.type == MediaType.IMAGE:
            pm = QPixmap(item.url)
            if not pm.isNull():
                full_pixmap = pm
        thumb_label = _ClickableThumb(full_pixmap, thumb_box)
        if full_pixmap is None:
            # 非图片或加载失败：类型色块占位
            if item.type == MediaType.IMAGE:
                text, color_key = "图片", "media_image"
            elif item.type == MediaType.VIDEO:
                text, color_key = "视频", "media_video"
            else:
                text, color_key = "音频", "media_audio"
            thumb_label.setText(text)
            color = ThemeContext.get_color(color_key, "#3498db")
            thumb_label.setStyleSheet(f"background-color: {color}; color: #fff; font-size: 13px; border-radius: 4px;")
        thumb_label.clicked.connect(thumb_label.show_full)
        thumb_layout.addWidget(thumb_label)

        badge_text, badge_color = self._badge_for(index)
        if badge_text:
            badge = QLabel(badge_text, thumb_box)
            badge.setObjectName("mediaBadge")
            badge.setStyleSheet(
                f"background-color: {badge_color}; color: #FFFFFF;"
                f"border-radius: 8px; padding: 1px 7px; font-weight: 700; font-size: 12px;"
            )
            badge.setFixedSize(26 if len(badge_text) <= 2 else 34, 20)
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge.move(5, 5)
            badge.show()
        frame_layout.addWidget(thumb_box)

        # 文件名
        name = os.path.basename(item.url) if os.path.sep in item.url else item.url
        name = name[:18] + "…" if len(name) > 18 else name
        name_label = QLabel(name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setObjectName("mediaNameLabel")
        frame_layout.addWidget(name_label)

        # 元信息行：分辨率（图片）或类型说明
        if full_pixmap is not None:
            meta_text = f"{full_pixmap.width()}×{full_pixmap.height()}"
        elif item.url.startswith(("http://", "https://", "asset://")):
            meta_text = "URL"
        else:
            meta_text = _TYPE_LABELS[item.type]
        meta_label = QLabel(meta_text)
        meta_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        meta_label.setObjectName("mediaCountLabel")
        frame_layout.addWidget(meta_label)

        # 底部行：图片角色选择 + 删除按钮
        bottom_row = QHBoxLayout()
        bottom_row.setContentsMargins(0, 0, 0, 0)
        bottom_row.setSpacing(4)

        if item.type == MediaType.IMAGE:
            role_combo = QComboBox()
            for role_value, role_label in _IMAGE_ROLES:
                role_combo.addItem(role_label, role_value)
            role_idx = role_combo.findData(getattr(item, "role", "reference_image"))
            if role_idx >= 0:
                role_combo.setCurrentIndex(role_idx)
            role_combo.setFixedHeight(24)
            role_combo.setToolTip("该图片在任务中的角色（首帧/尾帧不参与 [图n] 编号）")
            role_combo.currentIndexChanged.connect(
                lambda _i, idx=index, cb=role_combo: self._on_role_changed(idx, cb.currentData())
            )
            bottom_row.addWidget(role_combo, 1)

        remove_btn = QPushButton("移除")
        remove_btn.setFixedHeight(24)
        remove_btn.setObjectName("mediaRemoveButton")
        remove_btn.clicked.connect(lambda: self._remove_item(index))
        bottom_row.addWidget(remove_btn)

        frame_layout.addLayout(bottom_row)

        # 缩略图尺寸同步放大
        if full_pixmap is not None:
            thumb_label.setPixmap(full_pixmap.scaled(
                164, 116,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            ))

        widget.setLayout(frame_layout)

        # 流式网格自动排列（超宽换行）
        self._thumbnail_layout.addWidget(widget)

    def _badge_for(self, index: int) -> tuple[str, str]:
        """
        计算素材条目徽章：参考图按图片顺序编号（对应提示词 [图n] 引用），
        首帧/尾帧显示角色徽章，非图片素材无徽章。
        Returns:
            (徽章文本, 颜色)，无徽章时 ("", "")
        """
        item = self._items[index]
        if item.type != MediaType.IMAGE:
            return "", ""
        if item.role == "first_frame":
            return "首", ThemeContext.get_color("info", "#1F4FC4")
        if item.role == "last_frame":
            return "尾", ThemeContext.get_color("warning", "#E8A33D")
        n = sum(
            1 for it in self._items[:index]
            if it.type == MediaType.IMAGE and it.role in (None, "", "reference_image")
        ) + 1
        return str(n), ThemeContext.get_color("primary", "#4D7CFE")

    def _on_role_changed(self, index: int, role: str):
        """图片角色变化，更新 role 并重建条目（编号徽章随角色联动）"""
        if 0 <= index < len(self._items):
            self._items[index].role = role or "reference_image"
            self._rebuild_thumbnails()

    def _remove_item(self, index: int):
        """移除指定位置的素材"""
        if 0 <= index < len(self._items):
            self._items.pop(index)
            self._rebuild_thumbnails()
            self._update_count_label()
            self.items_changed.emit()

    def _rebuild_thumbnails(self):
        """重建所有缩略图（流式网格）"""
        while self._thumbnail_layout.count():
            taken = self._thumbnail_layout.takeAt(0)
            if taken is not None and taken.widget() is not None:
                taken.widget().deleteLater()

        for i, item in enumerate(self._items):
            self._add_thumbnail_widget(item, i)

    def _update_count_label(self):
        """更新数量提示"""
        parts = []
        for mt in (MediaType.IMAGE, MediaType.VIDEO, MediaType.AUDIO):
            cnt = _count_by_type(self._items, mt)
            max_cnt = self._max_counts[mt]
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

        if image_count > self._max_counts[MediaType.IMAGE]:
            errors.append(f"图片最多 {self._max_counts[MediaType.IMAGE]} 张，当前 {image_count} 张")
        if video_count > self._max_counts[MediaType.VIDEO]:
            errors.append(f"视频最多 {self._max_counts[MediaType.VIDEO]} 个，当前 {video_count} 个")
        if audio_count > self._max_counts[MediaType.AUDIO]:
            errors.append(f"音频最多 {self._max_counts[MediaType.AUDIO]} 个，当前 {audio_count} 个")

        return errors

    def on_theme_changed(self):
        self._rebuild_thumbnails()
