"""
关于对话框。

显示应用名称、版本号、技术栈和作者信息。
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


APP_VERSION = "1.1.0"


def show_about_dialog(parent=None):
    dialog = QDialog(parent)
    dialog.setWindowTitle("关于 Seedance Studio")
    dialog.setFixedSize(380, 260)
    dialog.setWindowFlags(
        Qt.WindowType.Dialog
        | Qt.WindowType.CustomizeWindowHint
        | Qt.WindowType.WindowTitleHint
        | Qt.WindowType.WindowCloseButtonHint
    )

    layout = QVBoxLayout()
    layout.setContentsMargins(24, 20, 24, 20)
    layout.setSpacing(10)

    title = QLabel("Seedance Studio")
    title_font = title.font()
    title_font.setPointSize(16)
    title_font.setBold(True)
    title.setFont(title_font)
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(title)

    version = QLabel(f"版本 {APP_VERSION}")
    version.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(version)

    layout.addSpacing(6)

    info = QLabel(
        "基于火山引擎 Doubao Seedance 2.0 系列 API\n"
        "的桌面视频生成工具。\n\n"
        "<b>技术栈</b><br>"
        "Python 3.12 · PyQt6 · volcengine SDK<br>"
        "SQLite · Fernet 加密 · PyInstaller 打包"
    )
    info.setAlignment(Qt.AlignmentFlag.AlignCenter)
    info.setWordWrap(True)
    layout.addWidget(info)

    layout.addStretch()

    btn_layout = QHBoxLayout()
    btn_layout.addStretch()
    close_btn = QPushButton("确定")
    close_btn.setMinimumWidth(80)
    close_btn.clicked.connect(dialog.accept)
    btn_layout.addWidget(close_btn)
    btn_layout.addStretch()
    layout.addLayout(btn_layout)

    dialog.setLayout(layout)

    # 居中显示
    if parent:
        parent_center = parent.geometry().center()
        dialog.move(parent_center - dialog.rect().center())

    dialog.exec()
