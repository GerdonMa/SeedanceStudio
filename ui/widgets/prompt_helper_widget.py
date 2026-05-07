"""
提示词助手侧边面板。

提供 Seedance 2.0 提示词模板库、公式速查和素材引用格式说明。
"""
from __future__ import annotations

import json
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QGroupBox, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal


class PromptHelperWidget(QWidget):
    """提示词助手侧边面板"""

    template_selected = pyqtSignal(str)

    _TEMPLATES_PATH = Path(__file__).parent.parent.parent / "assets" / "templates" / "prompt_templates.json"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._templates: list[dict] = []
        self._load_templates()
        self._init_ui()

    def _load_templates(self):
        """加载提示词模板"""
        try:
            if self._TEMPLATES_PATH.exists():
                with open(self._TEMPLATES_PATH, "r", encoding="utf-8") as f:
                    self._templates = json.load(f)
        except (json.JSONDecodeError, OSError):
            self._templates = []

    def _init_ui(self):
        """初始化 UI"""
        self.setMinimumWidth(260)
        self.setMaximumWidth(320)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(10)

        title = QLabel("提示词助手")
        title.setStyleSheet("font-size: 14px; font-weight: bold; padding: 4px 0;")
        main_layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        content = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

        content_layout.addWidget(self._build_template_section())
        content_layout.addWidget(self._build_formula_section())
        content_layout.addWidget(self._build_reference_section())

        content_layout.addStretch()
        content.setLayout(content_layout)
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        self.setLayout(main_layout)

    def _build_template_section(self) -> QGroupBox:
        """构建模板列表区域"""
        group = QGroupBox("模板库")
        layout = QVBoxLayout()
        layout.setSpacing(4)

        categories: dict[str, list[dict]] = {}
        for t in self._templates:
            cat = t.get("category", "通用")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(t)

        for cat_name, templates in categories.items():
            cat_label = QLabel(cat_name)
            cat_label.setStyleSheet("font-weight: bold; color: #555; padding: 4px 0 2px 0;")
            layout.addWidget(cat_label)

            for t in templates:
                btn = QPushButton(t["name"])
                btn.setStyleSheet("""
                    QPushButton {
                        text-align: left;
                        padding: 6px 10px;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        background-color: #fafafa;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #e8f4fd;
                        border-color: #3498db;
                    }
                """)
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.clicked.connect(lambda checked, tmpl=t["template"]: self._on_template_clicked(tmpl))
                layout.addWidget(btn)

        if not self._templates:
            no_data = QLabel("暂无模板")
            no_data.setStyleSheet("color: #999; padding: 8px;")
            layout.addWidget(no_data)

        group.setLayout(layout)
        return group

    def _build_formula_section(self) -> QGroupBox:
        """构建提示词公式速查区域"""
        group = QGroupBox("提示词公式速查")
        group.setCheckable(True)
        group.setChecked(False)

        layout = QVBoxLayout()
        layout.setSpacing(6)

        formulas = [
            ("主体 + 动作 + 场景 + 风格", "一只猫 + 在花园奔跑 + 阳光明媚 + 油画风格"),
            ("镜头 + 主体 + 环境 + 氛围", "近景特写 + 人物面部 + 咖啡厅背景 + 温馨柔和光线"),
            ("[图片N] + 动作描述 + 场景", "[图片1]中的角色在雨中撑伞行走，背景为城市街道"),
            ("[视频N] + 风格转换 + 参数", "[视频1]转换为黑白电影风格，增强对比度"),
        ]

        for formula, example in formulas:
            row = QVBoxLayout()
            row.setSpacing(2)

            formula_label = QLabel(formula)
            formula_label.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 11px;")
            formula_label.setWordWrap(True)
            row.addWidget(formula_label)

            example_label = QLabel(f"示例: {example}")
            example_label.setStyleSheet("color: #7f8c8d; font-size: 10px; padding-left: 8px;")
            example_label.setWordWrap(True)
            row.addWidget(example_label)

            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setStyleSheet("color: #eee;")
            row.addWidget(sep)

            layout.addLayout(row)

        group.setLayout(layout)
        return group

    def _build_reference_section(self) -> QGroupBox:
        """构建素材引用格式说明区域"""
        group = QGroupBox("素材引用格式说明")
        group.setCheckable(True)
        group.setChecked(False)

        layout = QVBoxLayout()
        layout.setSpacing(6)

        rules = [
            ("[图片1] [图片2] ... [图片N]", "引用上传的第N张图片作为参考"),
            ("[视频1] [视频2] ... [视频N]", "引用上传的第N个视频作为参考"),
            ("[音频1] [音频2] ... [音频N]", "引用上传的第N个音频作为参考"),
            ("素材编号规则", "按上传顺序自动编号，从1开始"),
            ("混合引用", "提示词中可同时引用图片、视频和音频素材"),
            ("资产库模式", "资产库素材使用 asset://{id} 格式，在资产选择器中自动填入"),
        ]

        for title_text, desc in rules:
            row = QVBoxLayout()
            row.setSpacing(1)

            rule_title = QLabel(title_text)
            rule_title.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 11px;")
            rule_title.setWordWrap(True)
            row.addWidget(rule_title)

            rule_desc = QLabel(desc)
            rule_desc.setStyleSheet("color: #7f8c8d; font-size: 10px; padding-left: 8px;")
            rule_desc.setWordWrap(True)
            row.addWidget(rule_desc)

            layout.addLayout(row)

        group.setLayout(layout)
        return group

    def _on_template_clicked(self, template: str):
        """模板被点击，通知填入提示词"""
        self.template_selected.emit(template)
