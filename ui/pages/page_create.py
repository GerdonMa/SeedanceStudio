"""
创建任务页面。

提供视频生成任务创建界面，支持文生视频和多模态参考。
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QPushButton, QMessageBox, QComboBox,
    QSlider, QSpinBox, QCheckBox, QFormLayout, QGroupBox, QScrollArea
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve

from core.di_container import Container
from domain.task_builders.base import TaskBuilderFactory
from core.exceptions import ValidationError, ApiError
from ui.widgets.media_upload_widget import MediaUploadWidget
from ui.widgets.prompt_helper_widget import PromptHelperWidget


_RESOLUTIONS = ["480p", "720p", "1080p"]
_ASPECT_RATIOS = ["16:9", "9:16", "1:1", "4:3", "3:4", "21:9"]
_MODELS = [
    ("doubao-seedance-2-0-260128", "Seedance 2.0（高质量）"),
    ("doubao-seedance-2-0-fast-260128", "Seedance 2.0 Fast（快速）"),
]
_TASK_TYPES = [
    ("text_to_video", "文生视频"),
    ("multimodal_ref", "多模态参考"),
    ("edit_video", "编辑视频"),
    ("extend_video", "延长视频"),
]


class CreatePage(QWidget):
    """创建任务页面"""

    def __init__(self, container: Container):
        super().__init__()
        self._container = container
        self._helper_anim = None
        self._init_ui()
        self._restore_prefs()

    def _init_ui(self):
        """初始化 UI"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        content = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("创建视频")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # --- 基础设置 ---
        basic_group = QGroupBox("基础设置")
        basic_form = QFormLayout()
        basic_form.setSpacing(8)

        self._model_combo = QComboBox()
        for value, label in _MODELS:
            self._model_combo.addItem(label, value)
        basic_form.addRow("模型:", self._model_combo)

        self._task_type_combo = QComboBox()
        for value, label in _TASK_TYPES:
            self._task_type_combo.addItem(label, value)
        basic_form.addRow("任务类型:", self._task_type_combo)

        basic_group.setLayout(basic_form)
        layout.addWidget(basic_group)

        # --- 提示词 ---
        prompt_group = QGroupBox("提示词")
        prompt_layout = QVBoxLayout()

        prompt_toolbar = QHBoxLayout()
        self._helper_toggle_btn = QPushButton("▸ 提示词助手")
        self._helper_toggle_btn.setCheckable(True)
        self._helper_toggle_btn.clicked.connect(self._toggle_helper)
        prompt_toolbar.addStretch()
        prompt_toolbar.addWidget(self._helper_toggle_btn)
        prompt_layout.addLayout(prompt_toolbar)

        self._prompt_input = QTextEdit()
        self._prompt_input.setPlaceholderText("请输入视频描述，例如：一只可爱的小猫在草地上玩耍")
        self._prompt_input.setMaximumHeight(120)
        prompt_layout.addWidget(self._prompt_input)
        prompt_group.setLayout(prompt_layout)
        layout.addWidget(prompt_group)

        # --- 素材上传 ---
        media_group = QGroupBox("素材上传")
        media_layout = QVBoxLayout()
        self._media_upload = MediaUploadWidget(self._container)
        media_layout.addWidget(self._media_upload)
        media_group.setLayout(media_layout)
        layout.addWidget(media_group)
        self._media_group = media_group

        # --- 输出参数 ---
        output_group = QGroupBox("输出参数")
        output_form = QFormLayout()
        output_form.setSpacing(8)

        self._resolution_combo = QComboBox()
        self._resolution_combo.addItems(_RESOLUTIONS)
        output_form.addRow("分辨率:", self._resolution_combo)

        self._ratio_combo = QComboBox()
        self._ratio_combo.addItems(_ASPECT_RATIOS)
        output_form.addRow("宽高比:", self._ratio_combo)

        duration_row = QHBoxLayout()
        self._duration_slider = QSlider(Qt.Orientation.Horizontal)
        self._duration_slider.setRange(4, 15)
        self._duration_slider.setTickInterval(1)
        duration_row.addWidget(self._duration_slider)

        self._duration_spin = QSpinBox()
        self._duration_spin.setRange(4, 15)
        self._duration_spin.setSuffix(" 秒")
        self._duration_spin.setMinimumWidth(90)
        duration_row.addWidget(self._duration_spin)
        output_form.addRow("时长:", duration_row)

        self._duration_slider.valueChanged.connect(self._duration_spin.setValue)
        self._duration_spin.valueChanged.connect(self._duration_slider.setValue)

        self._audio_checkbox = QCheckBox("生成音频")
        self._audio_checkbox.setChecked(True)
        output_form.addRow("", self._audio_checkbox)

        self._watermark_checkbox = QCheckBox("添加水印")
        output_form.addRow("", self._watermark_checkbox)

        self._web_search_checkbox = QCheckBox("启用联网搜索")
        output_form.addRow("", self._web_search_checkbox)

        self._offline_checkbox = QCheckBox("离线推理（Flex 模式）")
        output_form.addRow("", self._offline_checkbox)

        output_group.setLayout(output_form)
        layout.addWidget(output_group)

        # --- 创建按钮 ---
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self._create_btn = QPushButton("创建任务")
        self._create_btn.setProperty("role", "primary")
        self._create_btn.clicked.connect(self._on_create)
        self._create_btn.setMinimumWidth(140)
        btn_layout.addWidget(self._create_btn)

        layout.addLayout(btn_layout)
        layout.addStretch()

        content.setLayout(layout)
        scroll.setWidget(content)

        # 提示词助手面板（用容器包裹以实现宽度动画）
        self._helper_panel = PromptHelperWidget()
        self._helper_panel.template_selected.connect(self._on_template_selected)
        self._helper_panel.hide()

        self._helper_container = QWidget()
        self._helper_container.setMaximumWidth(0)
        helper_ctn_layout = QVBoxLayout()
        helper_ctn_layout.setContentsMargins(0, 0, 0, 0)
        helper_ctn_layout.addWidget(self._helper_panel)
        self._helper_container.setLayout(helper_ctn_layout)

        outer = QHBoxLayout()
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll, 1)
        outer.addWidget(self._helper_container)
        self.setLayout(outer)

        self._connect_pref_signals()

    def _connect_pref_signals(self):
        """连接偏好持久化信号"""
        self._model_combo.currentIndexChanged.connect(
            lambda: self._container.settings_usecase.save_preference(
                "default_model", self._model_combo.currentData()
            )
        )
        self._task_type_combo.currentIndexChanged.connect(
            lambda: self._container.settings_usecase.save_preference(
                "default_task_type", self._task_type_combo.currentData()
            )
        )
        self._task_type_combo.currentIndexChanged.connect(self._on_task_type_changed)

        self._resolution_combo.currentTextChanged.connect(
            lambda v: self._container.settings_usecase.save_preference("default_resolution", v)
        )
        self._ratio_combo.currentTextChanged.connect(
            lambda v: self._container.settings_usecase.save_preference("default_aspect_ratio", v)
        )
        self._duration_slider.valueChanged.connect(
            lambda v: self._container.settings_usecase.save_preference("default_duration", v)
        )
        self._audio_checkbox.toggled.connect(
            lambda v: self._container.settings_usecase.save_preference("generate_audio", v)
        )
        self._watermark_checkbox.toggled.connect(
            lambda v: self._container.settings_usecase.save_preference("watermark", v)
        )
        self._web_search_checkbox.toggled.connect(
            lambda v: self._container.settings_usecase.save_preference("web_search", v)
        )
        self._offline_checkbox.toggled.connect(
            lambda v: self._container.settings_usecase.save_preference("offline_inference", v)
        )

    def _restore_prefs(self):
        """恢复偏好设置"""
        if self._container is None:
            return
        prefs = self._container.settings_usecase.load_preferences()

        model = prefs.get("default_model", "doubao-seedance-2-0-260128")
        idx = self._model_combo.findData(model)
        if idx >= 0:
            self._model_combo.setCurrentIndex(idx)

        task_type = prefs.get("default_task_type", "text_to_video")
        idx = self._task_type_combo.findData(task_type)
        if idx >= 0:
            self._task_type_combo.setCurrentIndex(idx)
        self._on_task_type_changed(self._task_type_combo.currentIndex())

        self._resolution_combo.setCurrentText(prefs.get("default_resolution", "720p"))
        self._ratio_combo.setCurrentText(prefs.get("default_aspect_ratio", "16:9"))

        duration = prefs.get("default_duration", 5)
        self._duration_slider.setValue(duration)

        self._audio_checkbox.setChecked(prefs.get("generate_audio", True))
        self._watermark_checkbox.setChecked(prefs.get("watermark", False))
        self._web_search_checkbox.setChecked(prefs.get("web_search", False))
        self._offline_checkbox.setChecked(prefs.get("offline_inference", False))

    def _on_task_type_changed(self, index: int):
        """任务类型切换"""
        task_type = self._task_type_combo.currentData()
        show_media = task_type in ("multimodal_ref", "edit_video", "extend_video")
        self._media_group.setVisible(show_media)

    def _toggle_helper(self, checked: bool):
        """切换提示词助手面板显示/隐藏（slide_in_right 动画）"""
        # 停止之前的动画防止冲突
        if self._helper_anim is not None and self._helper_anim.state() == QPropertyAnimation.State.Running:
            self._helper_anim.stop()

        if checked:
            self._helper_panel.show()
            self._helper_anim = QPropertyAnimation(self._helper_container, b"maximumWidth")
            self._helper_anim.setDuration(250)
            self._helper_anim.setStartValue(0)
            self._helper_anim.setEndValue(320)
            self._helper_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._helper_anim.start()
        else:
            self._helper_anim = QPropertyAnimation(self._helper_container, b"maximumWidth")
            self._helper_anim.setDuration(200)
            self._helper_anim.setStartValue(self._helper_container.width())
            self._helper_anim.setEndValue(0)
            self._helper_anim.setEasingCurve(QEasingCurve.Type.InCubic)
            self._helper_anim.finished.connect(self._helper_panel.hide)
            self._helper_anim.start()
        self._helper_toggle_btn.setText("▾ 提示词助手" if checked else "▸ 提示词助手")

    def _on_template_selected(self, template: str):
        """提示词模板被选中，填入输入框"""
        self._prompt_input.setPlainText(template)

    def _on_create(self):
        """创建任务"""
        prompt = self._prompt_input.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "警告", "请输入提示词")
            return

        try:
            model = self._model_combo.currentData()
            task_type = self._task_type_combo.currentData()

            # 构建参数
            builder_params = {
                "model": model,
                "prompt": prompt,
                "resolution": self._resolution_combo.currentText(),
                "aspect_ratio": self._ratio_combo.currentText(),
                "duration": self._duration_slider.value(),
                "generate_audio": self._audio_checkbox.isChecked(),
                "watermark": self._watermark_checkbox.isChecked(),
                "web_search": self._web_search_checkbox.isChecked(),
                "offline_inference": self._offline_checkbox.isChecked(),
            }

            # 需要素材的任务类型
            if task_type in ("multimodal_ref", "edit_video", "extend_video"):
                media_items = self._media_upload.get_media_items()
                if not media_items:
                    QMessageBox.warning(self, "警告", "请添加至少一个素材")
                    return
                builder_params["media_items"] = media_items

            # 获取构建器并构建请求
            builder = TaskBuilderFactory.get(task_type)
            request = builder.build(**builder_params)

            # 创建任务
            self._create_btn.setEnabled(False)
            self._create_btn.setText("创建中...")

            task = self._container.task_usecase.create_task(request)

            QMessageBox.information(
                self,
                "成功",
                f"任务已创建\n任务 ID: {task.task_id}\n\n请在任务列表中查看进度"
            )

            self._prompt_input.clear()
            if task_type in ("multimodal_ref", "edit_video", "extend_video"):
                self._media_upload.clear()

        except ValidationError as e:
            QMessageBox.warning(self, "校验失败", "\n".join(e.errors))
        except ApiError as e:
            QMessageBox.critical(self, "API 调用失败", f"[{e.code}] {e.message}\n\n请检查 API Key 配置是否正确以及网络连接是否正常。")
        except ValueError as e:
            QMessageBox.warning(self, "参数错误", str(e))
        except Exception as e:
            QMessageBox.critical(self, "创建失败", f"创建任务失败：{e}\n\n请检查网络连接和参数设置后重试。")
        finally:
            self._create_btn.setEnabled(True)
            self._create_btn.setText("创建任务")
