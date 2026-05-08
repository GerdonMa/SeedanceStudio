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
    "colors": {
        "bg_base": "#ffffff",
        "bg_surface": "#f5f6fa",
        "bg_overlay": "#ecf0f1",
        "bg_raised": "#ffffff",
        "primary": "#3498db",
        "danger": "#e74c3c",
        "warning": "#f39c12",
        "success": "#27ae60",
        "info": "#3498db",
        "text_primary": "#2c3e50",
        "text_secondary": "#7f8c8d",
        "text_tertiary": "#95a5a6",
        "border_subtle": "#dcdfe6",
        "border_default": "#bdc3c7",
        "border_focus": "#3498db",
        "toast_success": "#27ae60",
        "toast_warning": "#f39c12",
        "toast_error": "#e74c3c",
        "toast_info": "#3498db",
        "media_image": "#3498db",
        "media_video": "#e67e22",
        "media_audio": "#2ecc71",
    },
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
}

/* =========================================================
   启动画面 (SplashScreen)
   ========================================================= */
QWidget#splashScreen {
    background-color: #ffffff;
    border: 1px solid #dcdfe6;
    border-radius: 8px;
}
QLabel#splashTitle {
    color: #2c3e50;
    font-size: 22px;
    font-weight: bold;
}
QLabel#splashVersion {
    color: #95a5a6;
    font-size: 13px;
}
QLabel#splashLoading {
    color: #3498db;
    font-size: 12px;
}

/* =========================================================
   Toast 通知 (ToastWidget)
   ========================================================= */
QFrame#toastItem {
    background-color: #ffffff;
    border: 1px solid #dcdfe6;
    border-radius: 6px;
}
QLabel#toastTitle {
    font-weight: bold;
    background: transparent;
    color: #2c3e50;
}
QLabel#toastMessage {
    color: #7f8c8d;
    font-size: 11px;
    background: transparent;
}

/* =========================================================
   提示词助手 (PromptHelperWidget)
   ========================================================= */
QLabel#helperTitle {
    font-size: 14px;
    font-weight: bold;
    padding: 4px 0;
    color: #2c3e50;
}
QLabel#helperCategory {
    font-weight: bold;
    color: #7f8c8d;
    padding: 4px 0 2px 0;
}
QPushButton#helperButton {
    background: #fafafa;
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    padding: 6px 10px;
    text-align: left;
    color: #7f8c8d;
    font-size: 12px;
}
QPushButton#helperButton:hover {
    background-color: #e8f4fd;
    border-color: #3498db;
    color: #2c3e50;
}
QLabel#helperFormula {
    font-weight: bold;
    color: #2c3e50;
    font-size: 11px;
}
QLabel#helperExample {
    color: #7f8c8d;
    font-size: 10px;
    padding-left: 8px;
}
QLabel#helperNoData {
    color: #95a5a6;
    font-size: 12px;
    padding: 8px;
}
QFrame#helperSeparator {
    background-color: #dcdfe6;
    max-height: 1px;
}
QLabel#helperRuleTitle {
    font-weight: bold;
    color: #2c3e50;
    font-size: 12px;
}
QLabel#helperRuleDesc {
    color: #7f8c8d;
    font-size: 11px;
}

/* =========================================================
   素材上传 (MediaUploadWidget)
   ========================================================= */
QLabel#dropZone {
    border: 2px dashed #bdc3c7;
    border-radius: 8px;
    color: #7f8c8d;
    font-size: 13px;
    background-color: #f5f6fa;
}
QLabel#dropZone:hover {
    border-color: #3498db;
    background-color: #ffffff;
}
QLabel#mediaSectionLabel {
    font-weight: bold;
    margin-top: 8px;
    color: #2c3e50;
}
QLabel#mediaCountLabel {
    color: #7f8c8d;
    font-size: 12px;
}
QFrame#mediaItemWidget {
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    background-color: #fafafa;
}
QLabel#mediaNameLabel {
    font-size: 10px;
    color: #7f8c8d;
    border: none;
    background: transparent;
}
QPushButton#mediaRemoveButton {
    background: transparent;
    border: 1px solid #dcdfe6;
    color: #7f8c8d;
    font-size: 11px;
    padding: 0 8px;
}
QPushButton#mediaRemoveButton:hover {
    background-color: #e74c3c;
    color: #ffffff;
}

/* =========================================================
   视频播放器 (VideoPlayerWidget)
   ========================================================= */
QLabel#expiryLabel {
    color: #f39c12;
    font-size: 12px;
}

/* =========================================================
   资产选择器 (AssetPickerWidget)
   ========================================================= */
QLabel#pickerTitle {
    font-size: 16px;
    font-weight: bold;
    color: #2c3e50;
}
QLabel#pickerStatus {
    color: #7f8c8d;
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
