"""
Graphite Studio 专业控制台主题。

深灰蓝工作台配色：分层面板 + hairline 网格 + 专业蓝强调。
对标 Linear / DaVinci 一类正式桌面工具的视觉语言。
"""
from __future__ import annotations

from PyQt6.QtWidgets import QWidget, QGraphicsOpacityEffect
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve

THEME_MANIFEST = {
    "manifest_version": 1,
    "id": "graphite",
    "name": "Graphite 工作台",
    "version": "1.0.0",
    "author": "Seedance Studio",
    "description": "深灰蓝专业控制台：分层面板、hairline 网格、专业蓝强调。",
    "is_dark": True,
    "tags": ["graphite", "professional", "dark"],
    "colors": {
        "bg_base": "#14161C",
        "bg_surface": "#1B1E26",
        "bg_overlay": "#22262F",
        "bg_raised": "#2A2F3A",
        "primary": "#4D7CFE",
        "danger": "#E5484D",
        "warning": "#E8B339",
        "success": "#34C77B",
        "info": "#58A6FF",
        "text_primary": "#E8EBF2",
        "text_secondary": "#98A0B0",
        "text_tertiary": "#626B7E",
        "border_subtle": "#2C313C",
        "border_default": "#3A4050",
        "border_focus": "#4D7CFE",
        "toast_success": "#34C77B",
        "toast_warning": "#E8B339",
        "toast_error": "#E5484D",
        "toast_info": "#58A6FF",
        "media_image": "#58A6FF",
        "media_video": "#4D7CFE",
        "media_audio": "#34C77B",
    },
}

THEME_QSS = """/* =========================================================
   GRAPHITE STUDIO — 专业控制台
   深灰蓝分层面板 · hairline 网格 · 专业蓝强调
   ========================================================= */

/* ---- 全局（深色主题：全局透明，容器着色） ---- */
QWidget {
    background-color: transparent;
    color: #E8EBF2;
    font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
    font-size: 13px;
}
QMainWindow, QWidget#mainRoot {
    background-color: #14161C;
}
QWidget#centralWidget, QWidget#contentArea {
    background-color: #14161C;
}
QLabel { background: transparent; }

/* ---- 页头 ---- */
QLabel#pageEyebrow {
    color: #4D7CFE;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    background: transparent;
}
QLabel#pageTitle {
    font-size: 21px;
    font-weight: 700;
    color: #E8EBF2;
    letter-spacing: 0.2px;
    background: transparent;
}
QLabel#pageSub {
    color: #98A0B0;
    font-size: 12px;
    background: transparent;
}

/* ---- 卡片（QGroupBox 即面板） ---- */
QGroupBox {
    background-color: #1B1E26;
    border: 1px solid #2C313C;
    border-radius: 8px;
    margin-top: 16px;
    padding: 14px 14px 12px 14px;
    font-weight: 600;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    background-color: #1B1E26;
    color: #98A0B0;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1px;
}

/* ---- 输入框 ---- */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #14161C;
    border: 1px solid #2C313C;
    border-radius: 6px;
    padding: 7px 10px;
    color: #E8EBF2;
    selection-background-color: #4D7CFE;
    selection-color: #FFFFFF;
}
QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {
    border: 1px solid #23262E;
    color: #626B7E;
    background-color: #181B21;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #4D7CFE;
}
QLineEdit::placeholder { color: #626B7E; }

/* ---- 下拉框 ---- */
QComboBox {
    background-color: #14161C;
    border: 1px solid #2C313C;
    border-radius: 6px;
    padding: 6px 10px;
    color: #E8EBF2;
    min-height: 18px;
}
QComboBox:disabled {
    border: 1px solid #23262E;
    color: #626B7E;
    background-color: #181B21;
}
QComboBox:hover { border: 1px solid #3A4050; background-color: #181B21; }
QComboBox:focus { border: 1px solid #4D7CFE; }
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 24px;
    border: none;
    background: transparent;
}
QComboBox::down-arrow {
    width: 0; height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #98A0B0;
    margin-right: 8px;
}
QComboBox QAbstractItemView {
    background-color: #22262F;
    border: 1px solid #3A4050;
    border-radius: 6px;
    outline: none;
    selection-background-color: #4D7CFE;
    selection-color: #FFFFFF;
    color: #E8EBF2;
    padding: 4px;
}

/* ---- 数字输入框 ---- */
QSpinBox, QDoubleSpinBox {
    background-color: #14161C;
    border: 1px solid #2C313C;
    border-radius: 6px;
    padding: 6px 8px;
    color: #E8EBF2;
}
QSpinBox:disabled, QDoubleSpinBox:disabled {
    border: 1px solid #23262E;
    color: #626B7E;
}
QSpinBox:focus, QDoubleSpinBox:focus { border: 1px solid #4D7CFE; }
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background: transparent;
    border: none;
    width: 18px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover { background: #2A2F3A; }
QSpinBox::up-arrow {
    width: 0; height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 5px solid #98A0B0;
}
QSpinBox::down-arrow {
    width: 0; height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #98A0B0;
}

/* ---- 按钮 ---- */
QPushButton {
    background-color: #22262F;
    border: 1px solid #2C313C;
    border-radius: 6px;
    padding: 7px 14px;
    color: #E8EBF2;
    font-weight: 600;
}
QPushButton:hover { background-color: #2A2F3A; border-color: #3A4050; }
QPushButton:pressed { background-color: #14161C; }
QPushButton:disabled { color: #626B7E; background-color: #1B1E26; border-color: #23262E; }
QPushButton:focus { border: 1px solid #4D7CFE; }

QPushButton[role="primary"] {
    background-color: #4D7CFE;
    border: 1px solid #4D7CFE;
    color: #FFFFFF;
    font-weight: 700;
    padding: 8px 18px;
}
QPushButton[role="primary"]:hover { background-color: #6B93FF; border-color: #6B93FF; }
QPushButton[role="primary"]:pressed { background-color: #3D68D8; }
QPushButton[role="primary"]:disabled { background-color: #2A3550; border-color: #2A3550; color: #626B7E; }

QPushButton[role="ghost"] {
    background-color: transparent;
    border: 1px solid #3A4050;
    color: #E8EBF2;
}
QPushButton[role="ghost"]:hover { background-color: #22262F; border-color: #4D7CFE; }

QPushButton[role="danger"] {
    background-color: transparent;
    border: 1px solid #5A3034;
    color: #E5484D;
}
QPushButton[role="danger"]:hover { background-color: #E5484D; border-color: #E5484D; color: #FFFFFF; }

/* ---- 分段控件（任务类型等） ---- */
QPushButton[seg="true"] {
    background-color: #181B21;
    border: 1px solid #2C313C;
    border-left: 3px solid transparent;
    color: #98A0B0;
    border-radius: 6px;
    padding: 8px 6px 8px 9px;
    font-weight: 600;
}
QPushButton[seg="true"]:hover { color: #E8EBF2; background-color: #22262F; }
QPushButton[seg="true"]:checked {
    background-color: #31437A;
    border: 1px solid #4D7CFE;
    border-left: 3px solid #6B93FF;
    color: #FFFFFF;
    font-weight: 700;
}
QPushButton[segPos="solo"] { border-radius: 6px; }
QPushButton[segPos="first"] { border-radius: 6px 0 0 6px; }
QPushButton[segPos="last"] { border-radius: 0 6px 6px 0; }

/* ---- 复选/单选 ---- */
QCheckBox, QRadioButton {
    background: transparent;
    spacing: 8px;
    color: #E8EBF2;
}
QCheckBox:disabled, QRadioButton:disabled { color: #626B7E; }
QCheckBox::indicator, QRadioButton::indicator {
    width: 15px;
    height: 15px;
    border: 1px solid #3A4050;
    background: #14161C;
}
QCheckBox::indicator { border-radius: 4px; }
QRadioButton::indicator { border-radius: 8px; }
QCheckBox::indicator:hover, QRadioButton::indicator:hover { border: 1px solid #4D7CFE; }
QCheckBox::indicator:checked {
    background: #4D7CFE;
    border: 1px solid #4D7CFE;
}
QRadioButton::indicator:checked {
    background: qradialgradient(cx:0.5, cy:0.5, radius:0.4, fx:0.5, fy:0.5,
        stop:0 #4D7CFE, stop:0.4 #4D7CFE, stop:0.5 #14161C, stop:1 #14161C);
    border: 1px solid #4D7CFE;
}
QCheckBox::indicator:disabled, QRadioButton::indicator:disabled {
    border: 1px solid #23262E; background: #181B21;
}

/* ---- 滑块 ---- */
QSlider::groove:horizontal {
    background: #2C313C;
    height: 4px;
    border-radius: 2px;
}
QSlider::sub-page:horizontal {
    background: #4D7CFE;
    height: 4px;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #E8EBF2;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider::handle:horizontal:hover { background: #FFFFFF; }
QSlider::handle:horizontal:disabled { background: #626B7E; }

/* ---- 表格 ---- */
QTableView, QTableWidget {
    background-color: #1B1E26;
    border: 1px solid #2C313C;
    border-radius: 8px;
    gridline-color: #23262E;
    color: #E8EBF2;
    selection-background-color: #2A3A66;
    selection-color: #FFFFFF;
    alternate-background-color: #1E222A;
}
QTableView::item, QTableWidget::item {
    padding: 8px 10px;
    border-bottom: 1px solid #23262E;
}
QTableView::item:selected, QTableWidget::item:selected {
    background-color: #2A3A66;
    color: #FFFFFF;
}
QHeaderView::section {
    background-color: #181B21;
    color: #98A0B0;
    border: none;
    border-bottom: 1px solid #2C313C;
    border-right: 1px solid #23262E;
    padding: 9px 10px;
    font-weight: 700;
    font-size: 12px;
}

/* ---- 标签页 ---- */
QTabWidget::pane { border: none; border-top: 1px solid #2C313C; }
QTabBar::tab {
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 8px 14px;
    color: #98A0B0;
    font-weight: 600;
}
QTabBar::tab:hover { color: #E8EBF2; }
QTabBar::tab:selected { color: #E8EBF2; border-bottom: 2px solid #4D7CFE; }

/* ---- 滚动条 ---- */
QScrollBar:vertical { background: transparent; width: 10px; margin: 0; }
QScrollBar::handle:vertical {
    background: #2C313C;
    min-height: 28px;
    border-radius: 5px;
    margin: 2px;
}
QScrollBar::handle:vertical:hover { background: #3A4050; }
QScrollBar:horizontal { background: transparent; height: 10px; }
QScrollBar::handle:horizontal {
    background: #2C313C;
    min-width: 28px;
    border-radius: 5px;
    margin: 2px;
}
QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; }
QScrollBar::add-page, QScrollBar::sub-page { background: none; }

/* ---- 进度条 ---- */
QProgressBar {
    background-color: #14161C;
    border: 1px solid #2C313C;
    border-radius: 6px;
    text-align: center;
    color: #E8EBF2;
    min-height: 16px;
}
QProgressBar::chunk { background-color: #4D7CFE; border-radius: 5px; }

/* ---- 菜单 ---- */
QMenu {
    background-color: #22262F;
    border: 1px solid #3A4050;
    border-radius: 8px;
    padding: 6px;
}
QMenu::item { padding: 7px 22px 7px 12px; color: #E8EBF2; border-radius: 4px; }
QMenu::item:selected { background-color: #4D7CFE; color: #FFFFFF; }
QMenu::separator { height: 1px; background: #2C313C; margin: 4px 8px; }

/* ---- 提示 ---- */
QToolTip {
    background-color: #22262F;
    color: #E8EBF2;
    border: 1px solid #3A4050;
    border-radius: 4px;
    padding: 5px 8px;
}

/* ---- Toast ---- */
QWidget#toastContainer { background: transparent; }
QWidget#toastItem {
    background-color: #1B1E26;
    border: 1px solid #3A4050;
    border-left: 3px solid #4D7CFE;
    border-radius: 8px;
}
QLabel#toastTitle { font-weight: 700; color: #E8EBF2; background: transparent; }
QLabel#toastMessage { color: #98A0B0; background: transparent; }

/* ---- 标题栏 ---- */
QWidget#titleBar {
    background-color: #14161C;
    border-bottom: 1px solid #23262E;
}
QLabel#titleLabel { color: #98A0B0; font-weight: 600; background: transparent; }
QPushButton#btnMin, QPushButton#btnMax {
    background: transparent; border: none; color: #98A0B0; border-radius: 4px;
}
QPushButton#btnMin:hover, QPushButton#btnMax:hover { background-color: #22262F; color: #E8EBF2; }
QPushButton#btnClose { background: transparent; border: none; color: #98A0B0; border-radius: 4px; }
QPushButton#btnClose:hover { background-color: #E5484D; color: #FFFFFF; }

/* ---- 素材上传卡片 ---- */
QFrame#mediaItemWidget {
    background-color: #14161C;
    border: 1px solid #2C313C;
    border-radius: 8px;
}
QWidget#mediaThumbBox {
    background-color: #181B21;
    border: 1px solid #23262E;
    border-radius: 6px;
}
QLabel#mediaNameLabel {
    color: #E8EBF2;
    font-size: 12px;
    background: transparent;
}
QLabel#mediaCountLabel {
    color: #98A0B0;
    font-size: 11px;
    background: transparent;
}
QLabel#dropZone {
    background-color: #181B21;
    border: 1px dashed #3A4050;
    border-radius: 8px;
    color: #626B7E;
}
QLabel#dropZone:hover { border: 1px dashed #4D7CFE; color: #98A0B0; }
QLabel#mediaSectionLabel {
    color: #98A0B0;
    font-size: 12px;
    font-weight: 700;
    background: transparent;
}
QPushButton#mediaRemoveButton {
    padding: 2px 10px;
    font-size: 12px;
}

/* ---- 消息框 ---- */
QMessageBox { background-color: #1B1E26; }
QMessageBox QLabel { color: #E8EBF2; background: transparent; }

/* ---- 统计徽章（任务页） ---- */
QLabel#statValue {
    font-size: 20px;
    font-weight: 800;
    color: #E8EBF2;
    background: transparent;
}
QLabel#statValue[accent="running"] { color: #58A6FF; }
QLabel#statValue[accent="succeeded"] { color: #34C77B; }
QLabel#statValue[accent="failed"] { color: #E5484D; }
QLabel#statLabel {
    font-size: 11px;
    color: #98A0B0;
    background: transparent;
}
QWidget#statCard {
    background-color: #1B1E26;
    border: 1px solid #2C313C;
    border-radius: 8px;
}

/* ---- 模型能力徽章（创建页） ---- */
QLabel#capBadge {
    background-color: #22262F;
    color: #98A0B0;
    border: 1px solid #2C313C;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
}
"""

SIDEBAR_QSS = """/* =========================================================
   GRAPHITE SIDEBAR — 专业导航栏
   品牌区 · 分组标签 · 计数徽章
   ========================================================= */

QWidget#sidebar {
    background-color: #101218;
    border-right: 1px solid #23262E;
}

/* 品牌区 */
QLabel#brandName {
    font-size: 14px;
    font-weight: 800;
    color: #E8EBF2;
    letter-spacing: 0.8px;
    background: transparent;
}
QLabel#brandSub {
    font-size: 10px;
    color: #626B7E;
    letter-spacing: 1.5px;
    background: transparent;
}
QWidget#brandMark {
    background-color: #4D7CFE;
    border-radius: 6px;
}
QLabel#brandMarkText {
    color: #FFFFFF;
    font-size: 13px;
    font-weight: 800;
    background: transparent;
}

/* 分组标签 */
QLabel#navLabel {
    font-size: 10px;
    font-weight: 700;
    color: #626B7E;
    padding: 16px 14px 4px 14px;
    letter-spacing: 2px;
    background: transparent;
}

/* 导航按钮 */
QWidget#sidebar QPushButton {
    background: transparent;
    border: none;
    border-left: 3px solid transparent;
    border-radius: 6px;
    text-align: left;
    padding: 0 9px 0 12px;
    font-size: 13px;
    font-weight: 500;
    color: #98A0B0;
    min-height: 36px;
    max-height: 36px;
}
QWidget#sidebar QPushButton:hover {
    background-color: #1B1E26;
    color: #E8EBF2;
}
QWidget#sidebar QPushButton:checked {
    background-color: #22262F;
    border-left: 3px solid #4D7CFE;
    color: #FFFFFF;
    font-weight: 700;
}

/* 导航徽章（运行中任务计数） */
QLabel#navBadge {
    background-color: #4D7CFE;
    color: #FFFFFF;
    border-radius: 8px;
    padding: 1px 7px;
    font-size: 11px;
    font-weight: 700;
    background: transparent;
}
QLabel#navBadge[active="true"] { background-color: #4D7CFE; }

/* 底部关于按钮 */
QWidget#sidebar QPushButton#aboutBtn {
    color: #626B7E;
    min-height: 32px;
    max-height: 32px;
}
QWidget#sidebar QPushButton#aboutBtn:hover { color: #98A0B0; background-color: #1B1E26; }
"""


def fade_in(widget: QWidget, duration=260, start=0.0, end=1.0):
    """透明度淡入"""
    effect = widget.graphicsEffect()
    if not isinstance(effect, QGraphicsOpacityEffect):
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
    effect.setOpacity(start)
    anim = QPropertyAnimation(effect, b"opacity", widget)
    anim.setDuration(duration)
    anim.setStartValue(start)
    anim.setEndValue(end)
    anim.setEasingCurve(QEasingCurve.Type.OutQuad)
    anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
    return anim


def on_theme_activated(main_window) -> None:
    """主题激活：整窗快速淡入"""
    if main_window is not None:
        fade_in(main_window, duration=260)
