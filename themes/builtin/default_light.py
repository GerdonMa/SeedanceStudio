"""默认浅色主题。"""
from __future__ import annotations

THEME_MANIFEST = {
    "manifest_version": 1,
    "id": "default_light",
    "name": "默认浅色",
    "version": "1.0.0",
    "author": "Seedance Studio",
    "description": "默认浅色主题。白色背景 + 蓝色强调色。",
    "is_dark": False,
}

THEME_QSS = """/* ===== 浅色主题 ===== */

/* 全局 */
QWidget {
    background-color: #f5f6fa;
    color: #2c3e50;
    font-size: 13px;
}

/* 输入框 */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #ffffff;
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    padding: 6px 10px;
    color: #2c3e50;
    selection-background-color: #3498db;
    selection-color: #ffffff;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #3498db;
}

/* 下拉框 */
QComboBox {
    background-color: #ffffff;
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    padding: 6px 10px;
    color: #2c3e50;
}
QComboBox:hover {
    border-color: #3498db;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: 1px solid #dcdfe6;
}
QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #dcdfe6;
    selection-background-color: #3498db;
    selection-color: #ffffff;
    color: #2c3e50;
}

/* 滑块 */
QSlider::groove:horizontal {
    background: #dcdfe6;
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
    background: #f5f6fa;
    width: 10px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #bdc3c7;
    border-radius: 5px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background: #95a5a6;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar:horizontal {
    background: #f5f6fa;
    height: 10px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal {
    background: #bdc3c7;
    border-radius: 5px;
    min-width: 20px;
}
QScrollBar::handle:horizontal:hover {
    background: #95a5a6;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

/* 表格 */
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #dcdfe6;
    gridline-color: #ebeef5;
    selection-background-color: #3498db;
    selection-color: #ffffff;
    color: #2c3e50;
}
QTableWidget QHeaderView::section {
    background-color: #f5f6fa;
    color: #2c3e50;
    padding: 8px 12px;
    border: none;
    border-bottom: 2px solid #dcdfe6;
    font-weight: bold;
}

/* 复选框 */
QCheckBox {
    color: #2c3e50;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #dcdfe6;
    border-radius: 3px;
    background-color: #ffffff;
}
QCheckBox::indicator:checked {
    background-color: #3498db;
    border-color: #3498db;
}

/* 分组框 */
QGroupBox {
    font-weight: bold;
    color: #2c3e50;
    border: 1px solid #dcdfe6;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 16px;
    background-color: #ffffff;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #2c3e50;
}

/* 普通按钮 */
QPushButton {
    background-color: #ffffff;
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    padding: 6px 16px;
    color: #2c3e50;
}
QPushButton:hover {
    border-color: #3498db;
    color: #3498db;
}
QPushButton:pressed {
    background-color: #ecf0f1;
}

/* 标签页 */
QTabWidget::pane {
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    background-color: #ffffff;
}
QTabBar::tab {
    background-color: #f5f6fa;
    color: #2c3e50;
    padding: 8px 20px;
    border: 1px solid #dcdfe6;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}
QTabBar::tab:selected {
    background-color: #ffffff;
    color: #3498db;
    border-bottom: 2px solid #3498db;
}

/* 工具提示 */
QToolTip {
    background-color: #2c3e50;
    color: #ffffff;
    border: none;
    padding: 6px 10px;
    border-radius: 4px;
}"""

SIDEBAR_QSS = """QWidget {
        background-color: #2c3e50;
    }
    QPushButton {
        background-color: transparent;
        color: white;
        text-align: left;
        padding: 15px 20px;
        border: none;
        font-size: 14px;
    }
    QPushButton:hover {
        background-color: #34495e;
    }
    QPushButton:checked {
        background-color: #3498db;
    }"""
