"""
关于对话框。

显示版权归属、技术栈和使用说明。
颜色通过 ThemeContext 动态获取，支持深色/浅色主题切换。
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame,
)
from PyQt6.QtCore import Qt

from themes.theme_context import ThemeContext


APP_VERSION = "1.3.0"

_COPYRIGHT = "© 2025 GerdonMa. All rights reserved."

_TECH_STACK = (
    "Python 3.12  ·  PyQt6  ·  volcengine SDK\n"
    "SQLite  ·  Fernet 加密  ·  PyInstaller 打包\n"
    "Marathon v3 主题  ·  Flat Design"
)

_USAGE = (
    "1. 在「设置」中配置火山引擎 API Key\n"
    "2. 在「创建视频」中输入提示词并生成\n"
    "3. 在「任务列表」中查看历史与任务管理\n"
    "4. 支持图片 / 视频 / 音频多模态素材上传"
)


def show_about_dialog(parent=None):
    c_accent = ThemeContext.get_color("primary", "#C8FF00")
    c_primary = ThemeContext.get_color("text_primary", "#FFFFFF")
    c_secondary = ThemeContext.get_color("text_secondary", "#717171")
    c_tertiary = ThemeContext.get_color("text_tertiary", "#444444")
    c_border = ThemeContext.get_color("border_default", "#333333")

    dialog = QDialog(parent)
    dialog.setWindowTitle("关于 Seedance Studio")
    dialog.setFixedSize(420, 370)
    dialog.setWindowFlags(
        Qt.WindowType.Dialog
        | Qt.WindowType.CustomizeWindowHint
        | Qt.WindowType.WindowTitleHint
        | Qt.WindowType.WindowCloseButtonHint
    )

    layout = QVBoxLayout()
    layout.setContentsMargins(28, 24, 28, 20)
    layout.setSpacing(8)

    title = QLabel("Seedance Studio")
    title.setObjectName("aboutTitle")
    title.setStyleSheet(
        f"font-family: 'Eurostile Extended', 'Microgramma', 'Share Tech', sans-serif;"
        f"font-size: 20px; font-weight: 700; color: {c_accent};"
    )
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(title)

    version = QLabel(f"版本 {APP_VERSION}")
    version.setStyleSheet(f"font-size: 12px; color: {c_secondary};")
    version.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(version)

    layout.addSpacing(4)

    copyright_label = QLabel(_COPYRIGHT)
    copyright_label.setStyleSheet(f"font-size: 11px; color: {c_secondary};")
    copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(copyright_label)

    layout.addSpacing(8)

    sep1 = QFrame()
    sep1.setFrameShape(QFrame.Shape.HLine)
    sep1.setStyleSheet(f"background-color: {c_border}; max-height: 1px;")
    layout.addWidget(sep1)

    tech_title = QLabel("技术栈")
    tech_title.setStyleSheet(
        f"font-size: 10px; font-weight: 700; color: {c_tertiary}; letter-spacing: 2px;"
    )
    tech_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(tech_title)

    tech_content = QLabel(_TECH_STACK)
    tech_content.setStyleSheet(f"font-size: 12px; color: {c_primary};")
    tech_content.setAlignment(Qt.AlignmentFlag.AlignCenter)
    tech_content.setWordWrap(True)
    layout.addWidget(tech_content)

    layout.addSpacing(4)

    sep2 = QFrame()
    sep2.setFrameShape(QFrame.Shape.HLine)
    sep2.setStyleSheet(f"background-color: {c_border}; max-height: 1px;")
    layout.addWidget(sep2)

    usage_title = QLabel("使用说明")
    usage_title.setStyleSheet(
        f"font-size: 10px; font-weight: 700; color: {c_tertiary}; letter-spacing: 2px;"
    )
    usage_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(usage_title)

    usage_content = QLabel(_USAGE)
    usage_content.setStyleSheet(f"font-size: 12px; color: {c_primary};")
    usage_content.setAlignment(Qt.AlignmentFlag.AlignCenter)
    usage_content.setWordWrap(True)
    layout.addWidget(usage_content)

    layout.addStretch()

    btn_layout = QHBoxLayout()
    btn_layout.addStretch()
    close_btn = QPushButton("确定")
    close_btn.setMinimumWidth(100)
    close_btn.clicked.connect(dialog.accept)
    btn_layout.addWidget(close_btn)
    btn_layout.addStretch()
    layout.addLayout(btn_layout)

    dialog.setLayout(layout)

    if parent:
        parent_center = parent.geometry().center()
        dialog.move(parent_center - dialog.rect().center())

    dialog.exec()
