"""
瑞士风格主题（Swiss / International Typographic Style）.

设计语言：暖纸灰底 + 深炭文字（柔和版） + 瑞士红单一强调色；全直角、无阴影、无渐变；
粗黑顶线与 hairline 细线构建网格节奏；大字重标题、左对齐、克制的留白。
"""
from __future__ import annotations

from PyQt6.QtWidgets import QWidget, QGraphicsOpacityEffect
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve

SWISS_RED = "#CE1124"
SWISS_BLACK = "#2E2F36"
SWISS_PAPER = "#F6F5F1"
SWISS_SURFACE = "#DDDCD6"
SWISS_HAIRLINE = "#C9C8C1"

THEME_MANIFEST = {
    "manifest_version": 1,
    "id": "swiss",
    "name": "瑞士风格",
    "version": "1.0.0",
    "author": "Seedance Studio",
    "description": "瑞士国际主义平面风格：纸白 + 瑞士红 + 全直角网格排版。",
    "is_dark": False,
    "tags": ["swiss", "minimal", "light"],
    "colors": {
        "bg_base": "#EAE9E4",
        "bg_surface": "#F6F5F1",
        "bg_overlay": "#DDDCD6",
        "bg_raised": "#F6F5F1",
        "primary": "#CE1124",
        "danger": "#C8102E",
        "warning": "#E8A33D",
        "success": "#1D7A3D",
        "info": "#1F4FC4",
        "text_primary": "#2A2B31",
        "text_secondary": "#5C5D66",
        "text_tertiary": "#8E8D87",
        "border_subtle": "#C9C8C1",
        "border_default": "#34353C",
        "border_focus": "#CE1124",
        "toast_success": "#1D7A3D",
        "toast_warning": "#E8A33D",
        "toast_error": "#C8102E",
        "toast_info": "#1F4FC4",
        "media_image": "#1F4FC4",
        "media_video": "#CE1124",
        "media_audio": "#1D7A3D",
    },
}

THEME_QSS = """/* =========================================================
   SWISS — International Typographic Style
   纸白 / 近黑 / 瑞士红 · 全直角 · 粗黑顶线 · hairline 网格
   ========================================================= */

/* ---- 全局基底 ---- */
QWidget {
    background-color: #EAE9E4;
    color: #2E2F36;
    font-family: "Segoe UI", "Arial", "Helvetica Neue", sans-serif;
    font-size: 13px;
}
QMainWindow, QWidget#mainRoot {
    background-color: #EAE9E4;
}
QWidget#centralWidget, QWidget#contentArea {
    background-color: #EAE9E4;
}

/* ---- 页面标题（大字重、紧字距） ---- */
QLabel#pageTitle {
    font-size: 22px;
    font-weight: 800;
    color: #2E2F36;
    letter-spacing: -0.5px;
    padding: 2px 0 10px 0;
    background: transparent;
}
QLabel {
    background: transparent;
    color: #2E2F36;
}

/* ---- 分组框：粗黑顶线 + 无边框（瑞士网格栏） ---- */
QGroupBox {
    background: transparent;
    border: none;
    border-top: 3px solid #2E2F36;
    margin-top: 14px;
    padding: 8px 2px 6px 2px;
    font-weight: 700;
    color: #2E2F36;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 0px;
    padding: 0 6px 0 0;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 1.5px;
    color: #2E2F36;
}

/* ---- 输入框：白底黑边，focus 红边 ---- */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #F6F5F1;
    border: 1px solid #2E2F36;
    border-radius: 0px;
    padding: 6px 10px;
    color: #2E2F36;
    selection-background-color: #2E2F36;
    selection-color: #F6F5F1;
    font-size: 13px;
}
QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {
    border: 1px solid #C9C8C1;
    color: #8E8D87;
    background-color: #DDDCD6;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #CE1124;
}
QLineEdit::placeholder {
    color: #8E8D87;
}

/* ---- 下拉框 ---- */
QComboBox {
    background-color: #F6F5F1;
    border: 1px solid #2E2F36;
    border-radius: 0px;
    padding: 5px 10px;
    color: #2E2F36;
    min-height: 18px;
}
QComboBox:disabled {
    border: 1px solid #C9C8C1;
    color: #8E8D87;
    background-color: #DDDCD6;
}
QComboBox:hover {
    background-color: #DDDCD6;
}
QComboBox:focus {
    border: 1px solid #CE1124;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 26px;
    border: none;
    border-left: 1px solid #2E2F36;
    background: transparent;
}
QComboBox::down-arrow {
    width: 0; height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid #2E2F36;
    margin-right: 8px;
}
QComboBox QAbstractItemView {
    background-color: #F6F5F1;
    border: 1px solid #2E2F36;
    outline: none;
    selection-background-color: #2E2F36;
    selection-color: #F6F5F1;
    color: #2E2F36;
    padding: 2px;
}

/* ---- 数字输入框 ---- */
QSpinBox, QDoubleSpinBox {
    background-color: #F6F5F1;
    border: 1px solid #2E2F36;
    border-radius: 0px;
    padding: 5px 8px;
    color: #2E2F36;
}
QSpinBox:disabled, QDoubleSpinBox:disabled {
    border: 1px solid #C9C8C1;
    color: #8E8D87;
    background-color: #DDDCD6;
}
QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #CE1124;
}
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background: #F6F5F1;
    border: none;
    border-left: 1px solid #C9C8C1;
    width: 18px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
    background: #2E2F36;
}
QSpinBox::up-arrow {
    width: 0; height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 5px solid #2E2F36;
}
QSpinBox::down-arrow {
    width: 0; height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #2E2F36;
}

/* ---- 按钮：默认黑边白底，hover 反色 ---- */
QPushButton {
    background-color: #F6F5F1;
    border: 1px solid #2E2F36;
    border-radius: 0px;
    padding: 7px 16px;
    color: #2E2F36;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #2E2F36;
    color: #F6F5F1;
}
QPushButton:pressed {
    background-color: #CE1124;
    border-color: #CE1124;
    color: #F6F5F1;
}
QPushButton:disabled {
    border: 1px solid #C9C8C1;
    color: #8E8D87;
    background-color: #DDDCD6;
}
QPushButton:focus {
    border: 1px solid #CE1124;
}

/* 主操作：瑞士红实底 */
QPushButton[role="primary"] {
    background-color: #CE1124;
    border: 1px solid #CE1124;
    color: #F6F5F1;
    font-weight: 700;
}
QPushButton[role="primary"]:hover {
    background-color: #2E2F36;
    border-color: #2E2F36;
}
QPushButton[role="primary"]:pressed {
    background-color: #F6F5F1;
    border-color: #2E2F36;
    color: #2E2F36;
}

/* 次要操作：透明底黑边 */
QPushButton[role="ghost"] {
    background-color: transparent;
    border: 1px solid #2E2F36;
    color: #2E2F36;
}
QPushButton[role="ghost"]:hover {
    background-color: #2E2F36;
    color: #F6F5F1;
}

/* 危险操作：黑边红字 */
QPushButton[role="danger"] {
    background-color: transparent;
    border: 1px solid #2E2F36;
    color: #C8102E;
}
QPushButton[role="danger"]:hover {
    background-color: #C8102E;
    border-color: #C8102E;
    color: #F6F5F1;
}

/* ---- 分段控件（任务类型等）：深炭底反白 + 左侧红条 ---- */
QPushButton[seg="true"] {
    background-color: #F6F5F1;
    border: 1px solid #34353C;
    border-left: 3px solid transparent;
    color: #5C5D66;
    border-radius: 0px;
    padding: 8px 6px 8px 9px;
    font-weight: 600;
}
QPushButton[seg="true"]:hover { color: #2E2F36; background-color: #EAE9E4; }
QPushButton[seg="true"]:checked {
    background-color: #2E2F36;
    border: 1px solid #2E2F36;
    border-left: 3px solid #CE1124;
    color: #F6F5F1;
    font-weight: 700;
}

/* ---- 复选/单选：黑边方框，选中红底 ---- */
QCheckBox, QRadioButton {
    background: transparent;
    spacing: 8px;
    color: #2E2F36;
}
QCheckBox:disabled, QRadioButton:disabled {
    color: #8E8D87;
}
QCheckBox::indicator, QRadioButton::indicator {
    width: 15px;
    height: 15px;
    border: 1px solid #2E2F36;
    background: #F6F5F1;
}
QCheckBox::indicator {
    border-radius: 0px;
}
QRadioButton::indicator {
    border-radius: 8px;
}
QCheckBox::indicator:hover, QRadioButton::indicator:hover {
    border: 1px solid #CE1124;
}
QCheckBox::indicator:checked {
    background: #CE1124;
    border: 1px solid #CE1124;
    image: none;
}
QRadioButton::indicator:checked {
    background: qradialgradient(cx:0.5, cy:0.5, radius:0.4, fx:0.5, fy:0.5,
        stop:0 #CE1124, stop:0.35 #CE1124, stop:0.45 #F6F5F1, stop:1 #F6F5F1);
    border: 1px solid #2E2F36;
}
QCheckBox::indicator:disabled, QRadioButton::indicator:disabled {
    border: 1px solid #C9C8C1;
    background: #DDDCD6;
}

/* ---- 滑块：红色方块 handle + 细灰轨道 ---- */
QSlider::groove:horizontal {
    background: #C9C8C1;
    height: 2px;
    border-radius: 0px;
}
QSlider::sub-page:horizontal {
    background: #2E2F36;
    height: 2px;
}
QSlider::handle:horizontal {
    background: #CE1124;
    width: 14px;
    height: 14px;
    margin: -6px 0;
    border-radius: 0px;
}
QSlider::handle:horizontal:hover {
    background: #2E2F36;
}
QSlider::handle:horizontal:disabled {
    background: #8E8D87;
}
QSlider::groove:vertical {
    background: #C9C8C1;
    width: 2px;
}
QSlider::sub-page:vertical {
    background: #2E2F36;
    width: 2px;
}
QSlider::handle:vertical {
    background: #CE1124;
    width: 14px;
    height: 14px;
    margin: 0 -6px;
    border-radius: 0px;
}

/* ---- 表格：无竖线 + hairline 横线 + 黑色表头字 ---- */
QTableView, QTableWidget {
    background-color: #F6F5F1;
    border: 1px solid #2E2F36;
    gridline-color: #C9C8C1;
    color: #2E2F36;
    selection-background-color: #2E2F36;
    selection-color: #F6F5F1;
    alternate-background-color: #F1F0EB;
}
QTableView::item, QTableWidget::item {
    padding: 6px 10px;
    border-bottom: 1px solid #C9C8C1;
}
QTableView::item:selected, QTableWidget::item:selected {
    background-color: #2E2F36;
    color: #F6F5F1;
}
QHeaderView::section {
    background-color: #F6F5F1;
    color: #2E2F36;
    border: none;
    border-bottom: 2px solid #2E2F36;
    padding: 8px 10px;
    font-weight: 800;
    font-size: 12px;
    letter-spacing: 1px;
}

/* ---- 标签页：红色下划线 ---- */
QTabWidget::pane {
    border: none;
    border-top: 2px solid #2E2F36;
}
QTabBar::tab {
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 8px 16px;
    color: #5C5D66;
    font-weight: 600;
    margin-right: 4px;
}
QTabBar::tab:hover {
    color: #2E2F36;
}
QTabBar::tab:selected {
    color: #2E2F36;
    border-bottom: 2px solid #CE1124;
    font-weight: 700;
}

/* ---- 滚动条：极简细条 ---- */
QScrollBar:vertical {
    background: #F6F5F1;
    width: 8px;
    border: none;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #C9C8C1;
    min-height: 24px;
    border: none;
}
QScrollBar::handle:vertical:hover {
    background: #2E2F36;
}
QScrollBar:horizontal {
    background: #F6F5F1;
    height: 8px;
    border: none;
}
QScrollBar::handle:horizontal {
    background: #C9C8C1;
    min-width: 24px;
    border: none;
}
QScrollBar::handle:horizontal:hover {
    background: #2E2F36;
}
QScrollBar::add-line, QScrollBar::sub-line {
    width: 0; height: 0;
}
QScrollBar::add-page, QScrollBar::sub-page {
    background: none;
}

/* ---- 进度条：红色方形进度 ---- */
QProgressBar {
    background-color: #DDDCD6;
    border: 1px solid #2E2F36;
    border-radius: 0px;
    text-align: center;
    color: #2E2F36;
    font-weight: 700;
    min-height: 14px;
}
QProgressBar::chunk {
    background-color: #CE1124;
}

/* ---- 菜单：白底 hairline，选中黑底反色 ---- */
QMenu {
    background-color: #F6F5F1;
    border: 1px solid #2E2F36;
    padding: 4px;
}
QMenu::item {
    padding: 7px 24px 7px 12px;
    color: #2E2F36;
}
QMenu::item:selected {
    background-color: #2E2F36;
    color: #F6F5F1;
}
QMenu::separator {
    height: 1px;
    background: #C9C8C1;
    margin: 4px 8px;
}

/* ---- 提示：黑底白字（海报式） ---- */
QToolTip {
    background-color: #2E2F36;
    color: #F6F5F1;
    border: 1px solid #2E2F36;
    padding: 5px 8px;
    font-size: 12px;
}

/* ---- Toast：白底黑边 + 左侧功能色条 ---- */
QWidget#toastContainer {
    background: transparent;
}
QWidget#toastItem {
    background-color: #F6F5F1;
    border: 1px solid #2E2F36;
    border-left: 4px solid #2E2F36;
}
QLabel#toastTitle {
    font-weight: 800;
    color: #2E2F36;
    background: transparent;
}
QLabel#toastMessage {
    color: #5C5D66;
    background: transparent;
}

/* ---- 标题栏：白底 + 底部黑线 ---- */
QWidget#titleBar {
    background-color: #E6E5E0;
    border-bottom: 1px solid #2E2F36;
}
QLabel#titleLabel {
    color: #2E2F36;
    font-weight: 800;
    letter-spacing: 0.5px;
    background: transparent;
}
QPushButton#btnMin, QPushButton#btnMax {
    background: transparent;
    border: none;
    color: #2E2F36;
}
QPushButton#btnMin:hover, QPushButton#btnMax:hover {
    background-color: #2E2F36;
    color: #F6F5F1;
}
QPushButton#btnClose {
    background: transparent;
    border: none;
    color: #2E2F36;
}
QPushButton#btnClose:hover {
    background-color: #CE1124;
    color: #F6F5F1;
}

/* ---- 素材上传卡片 ---- */
QFrame#mediaItemWidget {
    background-color: #F6F5F1;
    border: 1px solid #34353C;
    border-radius: 0px;
}
QWidget#mediaThumbBox {
    background-color: #EAE9E4;
    border: 1px solid #C9C8C1;
    border-radius: 0px;
}
QLabel#mediaNameLabel {
    color: #2A2B31;
    font-size: 12px;
    background: transparent;
}
QLabel#mediaCountLabel {
    color: #5C5D66;
    font-size: 11px;
    background: transparent;
}
QLabel#dropZone {
    background-color: #EAE9E4;
    border: 1px dashed #5C5D66;
    border-radius: 0px;
    color: #5C5D66;
}
QLabel#dropZone:hover { border: 1px dashed #CE1124; }
QLabel#mediaSectionLabel {
    color: #2A2B31;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 1px;
    background: transparent;
}
QPushButton#mediaRemoveButton {
    padding: 2px 10px;
    font-size: 12px;
}

/* ---- 消息框 ---- */
QMessageBox {
    background-color: #F6F5F1;
}
QMessageBox QLabel {
    color: #2E2F36;
    background: transparent;
}

/* ---- 拖拽/上传区提示文字 ---- */
QLabel[swissHint="true"] {
    color: #8E8D87;
}
"""

SIDEBAR_QSS = """/* =========================================================
   SWISS SIDEBAR — 白底黑线导航，选中态黑底反色块
   ========================================================= */

QWidget#sidebar {
    background-color: #E6E5E0;
    border-right: 1px solid #2E2F36;
}

/* 应用标题：大字重紧字距，瑞士海报式 */
QWidget#sidebar QLabel#appTitle {
    font-family: "Segoe UI", "Arial", "Helvetica Neue", sans-serif;
    font-size: 17px;
    font-weight: 800;
    color: #2E2F36;
    padding: 18px 14px 6px 14px;
    letter-spacing: -0.3px;
}

/* 导航分组小标（大写 + 宽字距） */
QWidget#sidebar QLabel#navLabel {
    font-size: 10px;
    font-weight: 800;
    color: #8E8D87;
    padding: 14px 14px 4px 14px;
    letter-spacing: 2px;
}

/* 导航按钮：左对齐、hairline 底线、左侧红色选中指示条 */
QWidget#sidebar QPushButton {
    background: transparent;
    border: none;
    border-left: 3px solid transparent;
    border-bottom: 1px solid #E2E1DB;
    border-radius: 0px;
    text-align: left;
    padding: 0 11px 0 14px;
    font-size: 13px;
    font-weight: 500;
    color: #5C5D66;
    min-height: 38px;
    max-height: 38px;
}
QWidget#sidebar QPushButton:hover {
    background-color: #DDDCD6;
    color: #2E2F36;
}
QWidget#sidebar QPushButton:checked {
    background-color: #2E2F36;
    border-left: 3px solid #CE1124;
    color: #F6F5F1;
    font-weight: 700;
}
QWidget#sidebar QPushButton:checked:hover {
    background-color: #2E2F36;
    color: #F6F5F1;
}

/* 折叠按钮（侧边栏底部）：hairline 顶线 */
QWidget#sidebar QPushButton#sidebarToggle {
    border-top: 1px solid #2E2F36;
    border-bottom: none;
    color: #5C5D66;
    min-height: 30px;
    max-height: 30px;
    font-size: 12px;
}
QWidget#sidebar QPushButton#sidebarToggle:hover {
    background-color: #DDDCD6;
    color: #2E2F36;
}
"""


def fade_in(widget: QWidget, duration=240, start=0.0, end=1.0):
    """透明度淡入（瑞士风格：快速、无弹性）"""
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


def fade_out(widget: QWidget, duration=120, start=1.0, end=0.0):
    """透明度淡出"""
    return fade_in(widget, duration, start, end)


def on_theme_activated(main_window) -> None:
    """主题激活：整窗 240ms 快速淡入，干净利落"""
    if main_window is not None:
        fade_in(main_window, duration=240)
