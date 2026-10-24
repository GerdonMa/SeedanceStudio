"""
创建工作台页面（两栏工作台布局）。

左栏：模型 / 任务类型 / 画面 / 高级 参数面板；
右栏：提示词编辑器 + 素材上传 + 动作条。
模型参数联动基于 domain.model_capabilities 能力表驱动。
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout,
    QTextEdit, QPushButton, QMessageBox, QComboBox,
    QSlider, QSpinBox, QCheckBox, QFormLayout, QGroupBox, QScrollArea,
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve

from core.di_container import Container
from domain.task_builders.base import TaskBuilderFactory
from domain.model_capabilities import MODEL_ORDER, get_capability
from core.exceptions import ValidationError, ApiError
from ui.widgets.media_upload_widget import MediaUploadWidget
from ui.widgets.prompt_helper_widget import PromptHelperWidget
from ui.widgets.page_header import PageHeader
from ui.widgets.segmented_control import SegmentedControl


_DEFAULT_MODEL = "doubao-seedance-2-5-260628"
_TASK_TYPES = [
    ("text_to_video", "文生视频"),
    ("multimodal_ref", "多模态参考"),
    ("edit_video", "编辑视频"),
    ("extend_video", "延长视频"),
]
_ADAPTIVE_LABEL = "adaptive（自适应）"
_MEDIA_TASK_TYPES = ("multimodal_ref", "edit_video", "extend_video")


class CreatePage(QWidget):
    """创建工作台页面"""

    def __init__(self, container: Container):
        super().__init__()
        self._container = container
        self._helper_anim = None
        self._duration_auto_before_lock = False
        self._init_ui()
        self._restore_prefs()
        self._update_summary()

    # ---- UI 构建 ----

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)

        root.addWidget(PageHeader("Workspace", "创建工作台", "选择模型与参数，输入提示词生成视频"))

        workspace = QHBoxLayout()
        workspace.setSpacing(16)
        root.addLayout(workspace, 1)

        workspace.addWidget(self._build_side_panel())
        workspace.addLayout(self._build_main_area(), 1)
        workspace.addWidget(self._build_helper_container())

        self._connect_signals()

    def _build_side_panel(self) -> QScrollArea:
        """左栏：生成配置面板"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setFixedWidth(320)

        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 6, 0)
        layout.setSpacing(4)

        # --- 模型 ---
        model_group = QGroupBox("模 型")
        model_form = QFormLayout(model_group)
        model_form.setSpacing(8)

        self._model_combo = QComboBox()
        for mid in MODEL_ORDER:
            cap = get_capability(mid)
            self._model_combo.addItem(cap.display_name, mid)
        model_form.addRow("模型版本", self._model_combo)

        # 能力徽章行（模型切换时更新）
        self._cap_badges_layout = QHBoxLayout()
        self._cap_badges_layout.setSpacing(6)
        model_form.addRow("", self._cap_badges_layout)

        layout.addWidget(model_group)

        # --- 任务类型 ---
        type_group = QGroupBox("任务类型")
        type_layout = QVBoxLayout(type_group)
        type_layout.setContentsMargins(10, 22, 10, 10)
        # _TASK_TYPES 为 (value, label)，SegmentedControl 需要 (label, value)
        self._task_type_seg = SegmentedControl(
            [(label, value) for value, label in _TASK_TYPES], vertical=True
        )
        type_layout.addWidget(self._task_type_seg)
        layout.addWidget(type_group)

        # --- 画面 ---
        visual_group = QGroupBox("画 面")
        visual_form = QFormLayout(visual_group)
        visual_form.setSpacing(8)

        self._resolution_combo = QComboBox()
        visual_form.addRow("分辨率", self._resolution_combo)

        self._ratio_combo = QComboBox()
        visual_form.addRow("宽高比", self._ratio_combo)

        duration_row = QHBoxLayout()
        self._duration_slider = QSlider(Qt.Orientation.Horizontal)
        self._duration_slider.setRange(4, 15)
        self._duration_slider.setTickInterval(1)
        duration_row.addWidget(self._duration_slider, 1)
        self._duration_spin = QSpinBox()
        self._duration_spin.setRange(4, 15)
        self._duration_spin.setSuffix(" 秒")
        self._duration_spin.setFixedWidth(84)
        duration_row.addWidget(self._duration_spin)
        visual_form.addRow("时长", duration_row)
        self._duration_slider.valueChanged.connect(self._duration_spin.setValue)
        self._duration_spin.valueChanged.connect(self._duration_slider.setValue)

        self._duration_auto_checkbox = QCheckBox("智能时长（模型自动决定）")
        self._duration_auto_checkbox.toggled.connect(self._on_duration_auto_toggled)
        visual_form.addRow("", self._duration_auto_checkbox)

        layout.addWidget(visual_group)

        # --- 高级 ---
        adv_group = QGroupBox("高 级")
        adv_layout = QVBoxLayout(adv_group)
        adv_layout.setContentsMargins(10, 22, 10, 10)
        adv_layout.setSpacing(8)

        adv_form = QFormLayout()
        adv_form.setSpacing(8)
        self._seed_spin = QSpinBox()
        self._seed_spin.setRange(-1, 2147483647)
        self._seed_spin.setValue(-1)
        self._seed_spin.setToolTip("-1 表示随机")
        adv_form.addRow("随机种子", self._seed_spin)

        self._format_combo = QComboBox()
        adv_form.addRow("输出格式", self._format_combo)
        adv_layout.addLayout(adv_form)

        toggles = QGridLayout()
        toggles.setHorizontalSpacing(16)
        toggles.setVerticalSpacing(6)
        self._audio_checkbox = QCheckBox("生成音频")
        self._audio_checkbox.setChecked(True)
        self._watermark_checkbox = QCheckBox("添加水印")
        self._web_search_checkbox = QCheckBox("联网搜索")
        self._last_frame_checkbox = QCheckBox("返回尾帧图")
        toggles.addWidget(self._audio_checkbox, 0, 0)
        toggles.addWidget(self._watermark_checkbox, 0, 1)
        toggles.addWidget(self._web_search_checkbox, 1, 0)
        toggles.addWidget(self._last_frame_checkbox, 1, 1)
        adv_layout.addLayout(toggles)

        self._offline_checkbox = QCheckBox("离线推理（Flex 模式）")
        adv_layout.addWidget(self._offline_checkbox)

        layout.addWidget(adv_group)
        layout.addStretch()

        scroll.setWidget(panel)
        return scroll

    def _build_main_area(self) -> QVBoxLayout:
        """右栏：提示词 + 素材 + 动作条"""
        main = QVBoxLayout()
        main.setSpacing(14)

        # --- 提示词 ---
        prompt_group = QGroupBox("提 示 词")
        prompt_layout = QVBoxLayout(prompt_group)
        prompt_layout.setContentsMargins(12, 24, 12, 12)
        prompt_layout.setSpacing(8)

        toolbar = QHBoxLayout()
        self._prompt_count_label = QLabel("0 字")
        self._prompt_count_label.setObjectName("pageSub")
        toolbar.addWidget(self._prompt_count_label)
        toolbar.addStretch()

        self._helper_toggle_btn = QPushButton("提示词助手")
        self._helper_toggle_btn.setProperty("role", "ghost")
        self._helper_toggle_btn.setCheckable(True)
        self._helper_toggle_btn.clicked.connect(self._toggle_helper)
        toolbar.addWidget(self._helper_toggle_btn)
        prompt_layout.addLayout(toolbar)

        self._prompt_input = QTextEdit()
        self._prompt_input.setPlaceholderText(
            "描述你想要生成的视频，例如：黄昏的城市天台，一位穿风衣的旅人望向远方，镜头缓缓推近，电影感光效"
        )
        self._prompt_input.setMinimumHeight(160)
        self._prompt_input.textChanged.connect(self._on_prompt_changed)
        prompt_layout.addWidget(self._prompt_input, 4)

        main.addWidget(prompt_group, 4)
        self._prompt_group = prompt_group

        # --- 素材 ---
        media_group = QGroupBox("参考素材")
        media_layout = QVBoxLayout(media_group)
        media_layout.setContentsMargins(12, 24, 12, 12)
        self._media_upload = MediaUploadWidget(self._container)
        media_layout.addWidget(self._media_upload)
        main.addWidget(media_group, 2)
        self._media_group = media_group
        self._main_layout = main

        # --- 动作条 ---
        action_bar = QHBoxLayout()
        action_bar.setSpacing(12)

        self._summary_label = QLabel("")
        self._summary_label.setObjectName("pageSub")
        action_bar.addWidget(self._summary_label)
        action_bar.addStretch()

        self._create_btn = QPushButton("创建任务")
        self._create_btn.setProperty("role", "primary")
        self._create_btn.clicked.connect(self._on_create)
        self._create_btn.setMinimumWidth(160)
        self._create_btn.setMinimumHeight(38)
        action_bar.addWidget(self._create_btn)

        main.addLayout(action_bar)
        return main

    def _build_helper_container(self) -> QWidget:
        """右侧可展开的提示词助手容器（宽度动画）"""
        self._helper_panel = PromptHelperWidget()
        self._helper_panel.template_selected.connect(self._on_template_selected)
        self._helper_panel.hide()

        container = QWidget()
        container.setMaximumWidth(0)
        ctn_layout = QVBoxLayout(container)
        ctn_layout.setContentsMargins(0, 0, 0, 0)
        ctn_layout.addWidget(self._helper_panel)
        self._helper_container = container
        return container

    # ---- 联动与偏好 ----

    def _connect_signals(self):
        """连接联动与偏好持久化信号"""
        self._model_combo.currentIndexChanged.connect(self._on_model_changed)
        self._model_combo.currentIndexChanged.connect(
            lambda: self._container.settings_usecase.save_preference(
                "default_model", self._model_combo.currentData()
            )
        )
        self._task_type_seg.selectionChanged.connect(self._on_task_type_changed)
        self._task_type_seg.selectionChanged.connect(
            lambda v: self._container.settings_usecase.save_preference("default_task_type", v)
        )

        self._resolution_combo.currentTextChanged.connect(
            lambda v: self._container.settings_usecase.save_preference("default_resolution", v)
        )
        self._resolution_combo.currentTextChanged.connect(lambda _v: self._update_summary())
        self._ratio_combo.currentTextChanged.connect(
            lambda v: self._container.settings_usecase.save_preference("default_aspect_ratio", v)
        )
        self._ratio_combo.currentTextChanged.connect(lambda _v: self._update_summary())
        self._duration_slider.valueChanged.connect(
            lambda v: self._container.settings_usecase.save_preference("default_duration", v)
        )
        self._duration_slider.valueChanged.connect(lambda _v: self._update_summary())
        self._duration_auto_checkbox.toggled.connect(
            lambda v: self._container.settings_usecase.save_preference("duration_auto", v)
        )
        self._duration_auto_checkbox.toggled.connect(lambda _v: self._update_summary())

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
        self._seed_spin.valueChanged.connect(
            lambda v: self._container.settings_usecase.save_preference("default_seed", v)
        )
        self._format_combo.currentTextChanged.connect(
            lambda v: self._container.settings_usecase.save_preference("output_format", v)
        )
        self._last_frame_checkbox.toggled.connect(
            lambda v: self._container.settings_usecase.save_preference("return_last_frame", v)
        )

    def _on_model_changed(self, index: int):
        """模型切换：按能力表联动各输出参数控件"""
        model_id = self._model_combo.currentData()
        cap = get_capability(model_id)

        # 分辨率：保留当前选择若仍合法，否则回落到首个 ≤720p 项或首项
        current_res = self._resolution_combo.currentText()
        self._rebuild_combo(self._resolution_combo, list(cap.resolutions), list(cap.resolutions))
        if current_res in cap.resolutions:
            self._resolution_combo.setCurrentText(current_res)
        else:
            fallback = next((r for r in cap.resolutions if r in ("480p", "720p")), cap.resolutions[0])
            self._resolution_combo.setCurrentText(fallback)

        # 宽高比（含 adaptive）
        ratios = list(cap.ratios)
        labels = [_ADAPTIVE_LABEL if r == "adaptive" else r for r in ratios]
        self._rebuild_combo(self._ratio_combo, labels, ratios)
        if self._ratio_combo.count() > 0:
            self._ratio_combo.setCurrentIndex(0)

        # 时长范围
        self._duration_slider.setRange(cap.duration_min, cap.duration_max)
        self._duration_spin.setRange(cap.duration_min, cap.duration_max)

        # 输出格式
        formats = ["mp4", "mov"] if cap.supports_mov else ["mp4"]
        self._rebuild_combo(self._format_combo, formats, formats)

        # 离线推理（Flex）按能力显示/隐藏
        self._offline_checkbox.setVisible(cap.supports_flex)

        # 能力徽章
        self._update_cap_badges(cap)

        # 素材上限同步
        self._media_upload.set_model(model_id)

        self._apply_task_type_locks()
        self._update_summary()

    def _update_cap_badges(self, cap) -> None:
        """更新模型能力徽章行"""
        while self._cap_badges_layout.count():
            item = self._cap_badges_layout.takeAt(0)
            if item.widget() is not None:
                item.widget().deleteLater()
        badges = [f"{cap.resolutions[-1]}", f"{cap.duration_min}–{cap.duration_max}s"]
        if cap.supports_mov:
            badges.append("MOV")
        if cap.supports_audio_only:
            badges.append("纯音频")
        for text in badges:
            label = QLabel(text)
            label.setObjectName("capBadge")
            self._cap_badges_layout.addWidget(label)
        self._cap_badges_layout.addStretch()

    def _rebuild_combo(self, combo: QComboBox, labels: list[str], data: list[str]):
        """重建下拉框选项（阻断信号避免误存偏好）"""
        combo.blockSignals(True)
        combo.clear()
        for label, value in zip(labels, data):
            combo.addItem(label, value)
        combo.blockSignals(False)

    def _apply_task_type_locks(self):
        """按模型能力与任务类型锁定参数控件"""
        cap = get_capability(self._model_combo.currentData())
        task_type = self._task_type_seg.current_value()

        lock_ratio = (
            cap.locks_ratio_on_edit_extend
            and task_type in ("edit_video", "extend_video")
        )
        if lock_ratio:
            idx = self._ratio_combo.findData("adaptive")
            if idx >= 0:
                self._ratio_combo.setCurrentIndex(idx)
            self._ratio_combo.setEnabled(False)
        else:
            self._ratio_combo.setEnabled(True)

        lock_duration = cap.locks_duration_on_edit and task_type == "edit_video"
        if lock_duration:
            self._duration_auto_before_lock = self._duration_auto_checkbox.isChecked()
            self._duration_auto_checkbox.setChecked(True)
            self._duration_auto_checkbox.setEnabled(False)
        else:
            self._duration_auto_checkbox.setEnabled(True)
            self._duration_auto_checkbox.setChecked(self._duration_auto_before_lock)

    def _on_duration_auto_toggled(self, checked: bool):
        """智能时长勾选时禁用时长滑块与输入框"""
        self._duration_slider.setEnabled(not checked)
        self._duration_spin.setEnabled(not checked)

    def _on_task_type_changed(self, value: str):
        """任务类型切换：显隐素材区并动态调整右栏比例（素材浏览优先）"""
        show_media = value in _MEDIA_TASK_TYPES
        self._media_group.setVisible(show_media)
        if show_media:
            # 素材任务：提示词 2 / 素材 3，给参考图更大浏览空间
            self._main_layout.setStretchFactor(self._prompt_group, 2)
            self._main_layout.setStretchFactor(self._media_group, 3)
            self._prompt_input.setMinimumHeight(140)
        else:
            self._main_layout.setStretchFactor(self._prompt_group, 1)
            self._prompt_input.setMinimumHeight(200)
        self._apply_task_type_locks()

    def _on_prompt_changed(self):
        """提示词字数统计"""
        text = self._prompt_input.toPlainText()
        self._prompt_count_label.setText(f"{len(text)} 字")

    def _update_summary(self):
        """更新动作条左侧的参数摘要"""
        if not hasattr(self, "_summary_label"):
            return
        model = get_capability(self._model_combo.currentData())
        short_name = model.display_name.split("（")[0]
        ratio = self._ratio_combo.currentData() or self._ratio_combo.currentText()
        if self._duration_auto_checkbox.isChecked():
            duration = "智能时长"
        else:
            duration = f"{self._duration_slider.value()}s"
        parts = [short_name, self._resolution_combo.currentText(), ratio, duration]
        if self._format_combo.currentText() == "mov":
            parts.append("MOV")
        self._summary_label.setText("  ·  ".join(parts))

    def _restore_prefs(self):
        """恢复偏好设置"""
        if self._container is None:
            return
        prefs = self._container.settings_usecase.load_preferences()

        # 恢复模型并触发一次联动（setCurrentIndex 若未变化则不会发信号，需手动调）
        model = prefs.get("default_model", _DEFAULT_MODEL)
        idx = self._model_combo.findData(model)
        if idx >= 0 and idx != self._model_combo.currentIndex():
            self._model_combo.setCurrentIndex(idx)
        else:
            self._on_model_changed(self._model_combo.currentIndex())

        task_type = prefs.get("default_task_type", "text_to_video")
        if any(value == task_type for value, _ in _TASK_TYPES):
            self._task_type_seg.select(task_type)
        else:
            self._task_type_seg.select(_TASK_TYPES[0][0])
        self._on_task_type_changed(self._task_type_seg.current_value())

        # 旧配置的分辨率可能不被新模型支持，findData 回落
        res = prefs.get("default_resolution", "720p")
        if self._resolution_combo.findText(res) >= 0:
            self._resolution_combo.setCurrentText(res)

        ratio = prefs.get("default_aspect_ratio", "16:9")
        if self._ratio_combo.findData(ratio) >= 0:
            idx = self._ratio_combo.findData(ratio)
            self._ratio_combo.setCurrentIndex(idx)

        duration = prefs.get("default_duration", 5)
        self._duration_slider.setValue(duration)

        self._audio_checkbox.setChecked(prefs.get("generate_audio", True))
        self._watermark_checkbox.setChecked(prefs.get("watermark", False))
        self._web_search_checkbox.setChecked(prefs.get("web_search", False))
        self._offline_checkbox.setChecked(prefs.get("offline_inference", False))

        # 新增偏好
        duration_auto = bool(prefs.get("duration_auto", False))
        self._duration_auto_before_lock = duration_auto
        self._duration_auto_checkbox.setChecked(duration_auto)

        seed = prefs.get("default_seed", -1)
        self._seed_spin.setValue(int(seed))

        fmt = prefs.get("output_format", "mp4")
        if self._format_combo.findText(fmt) >= 0:
            self._format_combo.setCurrentText(fmt)

        self._last_frame_checkbox.setChecked(prefs.get("return_last_frame", False))

        # 恢复完成后兜底执行一次锁定联动
        self._apply_task_type_locks()

    # ---- 提示词助手 ----

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
        self._helper_toggle_btn.setText("收起助手" if checked else "提示词助手")

    def _on_template_selected(self, template: str):
        """提示词模板被选中，填入输入框"""
        self._prompt_input.setPlainText(template)

    # ---- 创建任务 ----

    def _on_create(self):
        """创建任务"""
        prompt = self._prompt_input.toPlainText().strip()
        task_type = self._task_type_seg.current_value()
        # 多模态参考任务的提示词可留空（builder 已支持 optional）
        if not prompt and task_type != "multimodal_ref":
            QMessageBox.warning(self, "警告", "请输入提示词")
            return

        try:
            model = self._model_combo.currentData()

            # 构建参数
            duration = -1 if self._duration_auto_checkbox.isChecked() else self._duration_slider.value()
            builder_params = {
                "model": model,
                "prompt": prompt,
                "resolution": self._resolution_combo.currentText(),
                "aspect_ratio": self._ratio_combo.currentData() or self._ratio_combo.currentText(),
                "duration": duration,
                "seed": self._seed_spin.value(),
                "output_format": self._format_combo.currentData() or self._format_combo.currentText(),
                "return_last_frame": self._last_frame_checkbox.isChecked(),
                "generate_audio": self._audio_checkbox.isChecked(),
                "watermark": self._watermark_checkbox.isChecked(),
                "web_search": self._web_search_checkbox.isChecked(),
                "offline_inference": self._offline_checkbox.isChecked(),
            }

            # 需要素材的任务类型
            if task_type in _MEDIA_TASK_TYPES:
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

            self._container.event_bus.toast_requested.emit(
                "success", "任务已创建", f"任务 ID: {task.task_id[:20]}..."
            )

            self._prompt_input.clear()
            if task_type in _MEDIA_TASK_TYPES:
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
