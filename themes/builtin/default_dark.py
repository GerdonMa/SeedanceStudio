"""默认深色主题。"""
from __future__ import annotations

THEME_MANIFEST = {
    "manifest_version": 1,
    "id": "default_dark",
    "name": "默认深色",
    "version": "1.0.0",
    "author": "Seedance Studio",
    "description": "默认深色主题。深蓝背景 + 蓝色强调色。",
    "is_dark": True,
}

THEME_QSS = """/* ===== 深色主题 ===== */

/* 全局 */
QWidget {
    background-color: #1a1a2e;
    color: #e0e0e0;
    font-size: 13px;
}

/* 输入框 */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #16213e;
    border: 1px solid #2a2a4a;
    border-radius: 4px;
    padding: 6px 10px;
    color: #e0e0e0;
    selection-background-color: #3498db;
    selection-color: #ffffff;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #3498db;
}

/* 下拉框 */
QComboBox {
    background-color: #16213e;
    border: 1px solid #2a2a4a;
    border-radius: 4px;
    padding: 6px 10px;
    color: #e0e0e0;
}
QComboBox:hover {
    border-color: #3498db;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: 1px solid #2a2a4a;
}
QComboBox QAbstractItemView {
    background-color: #16213e;
    border: 1px solid #2a2a4a;
    selection-background-color: #3498db;
    selection-color: #ffffff;
    color: #e0e0e0;
}

/* 滑块 */
QSlider::groove:horizontal {
    background: #2a2a4a;
    height: 6px;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #3498db;
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}
QSlider::sub-page:horizontal {
    background: #3498db;
    border-radius: 3px;
}

/* 滚动条 */
QScrollBar:vertical {
    background: #1a1a2e;
    width: 10px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #2a2a4a;
    border-radius: 5px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background: #3a3a5a;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar:horizontal {
    background: #1a1a2e;
    height: 10px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal {
    background: #2a2a4a;
    border-radius: 5px;
    min-width: 20px;
}
QScrollBar::handle:horizontal:hover {
    background: #3a3a5a;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

/* 表格 */
QTableWidget {
    background-color: #16213e;
    border: 1px solid #2a2a4a;
    gridline-color: #2a2a4a;
    selection-background-color: #3498db;
    selection-color: #ffffff;
    color: #e0e0e0;
}
QTableWidget QHeaderView::section {
    background-color: #1a1a2e;
    color: #e0e0e0;
    padding: 8px 12px;
    border: none;
    border-bottom: 2px solid #2a2a4a;
    font-weight: bold;
}

/* 复选框 */
QCheckBox {
    color: #e0e0e0;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #2a2a4a;
    border-radius: 3px;
    background-color: #16213e;
}
QCheckBox::indicator:checked {
    background-color: #3498db;
    border-color: #3498db;
}

/* 分组框 */
QGroupBox {
    font-weight: bold;
    color: #e0e0e0;
    border: 1px solid #2a2a4a;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 16px;
    background-color: #16213e;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #e0e0e0;
}

/* 普通按钮 */
QPushButton {
    background-color: #16213e;
    border: 1px solid #2a2a4a;
    border-radius: 4px;
    padding: 6px 16px;
    color: #e0e0e0;
}
QPushButton:hover {
    border-color: #3498db;
    color: #3498db;
}
QPushButton:pressed {
    background-color: #0f3460;
}

/* 标签页 */
QTabWidget::pane {
    border: 1px solid #2a2a4a;
    border-radius: 4px;
    background-color: #16213e;
}
QTabBar::tab {
    background-color: #1a1a2e;
    color: #e0e0e0;
    padding: 8px 20px;
    border: 1px solid #2a2a4a;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}
QTabBar::tab:selected {
    background-color: #16213e;
    color: #3498db;
    border-bottom: 2px solid #3498db;
}

/* 工具提示 */
QToolTip {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #2a2a4a;
    padding: 6px 10px;
    border-radius: 4px;
}"""

SIDEBAR_QSS = """QWidget {
        background-color: #0f0f23;
    }
    QPushButton {
        background-color: transparent;
        color: #c0c0d0;
        text-align: left;
        padding: 15px 20px;
        border: none;
        font-size: 14px;
    }
    QPushButton:hover {
        background-color: #1a1a3e;
    }
    QPushButton:checked {
        background-color: #3498db;
        color: white;
    }"""
