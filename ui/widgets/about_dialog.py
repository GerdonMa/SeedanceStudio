"""
关于对话框。

显示版权归属、技术栈和使用说明。
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame,
)
from PyQt6.QtCore import Qt


APP_VERSION = "1.1.0"

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
        "font-family: 'Eurostile Extended', 'Microgramma', 'Share Tech', sans-serif;"
        "font-size: 20px; font-weight: 700; color: #C8FF00;"
    )
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(title)

    version = QLabel(f"版本 {APP_VERSION}")
    version.setStyleSheet("font-size: 12px; color: #717171;")
    version.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(version)

    layout.addSpacing(4)

    copyright_label = QLabel(_COPYRIGHT)
    copyright_label.setStyleSheet("font-size: 11px; color: #717171;")
    copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(copyright_label)

    layout.addSpacing(8)

    sep1 = QFrame()
    sep1.setFrameShape(QFrame.Shape.HLine)
    sep1.setStyleSheet("background-color: #333333; max-height: 1px;")
    layout.addWidget(sep1)

    tech_title = QLabel("技术栈")
    tech_title.setStyleSheet(
        "font-size: 10px; font-weight: 700; color: #444444; letter-spacing: 2px;"
    )
    tech_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(tech_title)

    tech_content = QLabel(_TECH_STACK)
    tech_content.setStyleSheet("font-size: 12px; color: #FFFFFF;")
    tech_content.setAlignment(Qt.AlignmentFlag.AlignCenter)
    tech_content.setWordWrap(True)
    layout.addWidget(tech_content)

    layout.addSpacing(4)

    sep2 = QFrame()
    sep2.setFrameShape(QFrame.Shape.HLine)
    sep2.setStyleSheet("background-color: #333333; max-height: 1px;")
    layout.addWidget(sep2)

    usage_title = QLabel("使用说明")
    usage_title.setStyleSheet(
        "font-size: 10px; font-weight: 700; color: #444444; letter-spacing: 2px;"
    )
    usage_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(usage_title)

    usage_content = QLabel(_USAGE)
    usage_content.setStyleSheet("font-size: 12px; color: #FFFFFF;")
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
