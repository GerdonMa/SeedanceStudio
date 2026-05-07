"""
Marathon 深空主题 — 色彩令牌 & 动效工具。

提供 MarathonColors 颜色类和 MarathonFX 动效静态方法集合。
"""
from __future__ import annotations

from PyQt6.QtWidgets import QWidget, QGraphicsOpacityEffect, QGraphicsDropShadowEffect
from PyQt6.QtCore import (
    QPropertyAnimation, QEasingCurve, QParallelAnimationGroup,
    QPoint, QTimer
)
from PyQt6.QtGui import QColor


class MarathonColors:
    """Marathon UI 色彩系统"""

    # 背景层级
    BG_ABYSS = "#06060B"
    BG_BASE = "#0A0B10"
    BG_SURFACE = "#101218"
    BG_OVERLAY = "#161A22"
    BG_RAISED = "#1C2029"

    # 边框
    BORDER_SUBTLE = "#1C2029"
    BORDER_DEFAULT = "#252A35"
    BORDER_FOCUS = "#00E5FF"

    # 强调色
    CYAN = "#00E5FF"
    CYAN_DIM = "#005F6B"
    CYAN_GLOW = "rgba(0, 229, 255, 0.15)"
    CYAN_GLOW_STRONG = "rgba(0, 229, 255, 0.35)"

    ORANGE = "#FF4D00"
    ORANGE_GLOW = "rgba(255, 77, 0, 0.12)"

    YELLOW = "#E5FF00"
    GREEN = "#00FF88"

    # 文字
    TEXT_PRIMARY = "#E8EAED"
    TEXT_SECONDARY = "#8B9099"
    TEXT_TERTIARY = "#4A5060"
    TEXT_INVERSE = "#0A0B10"


class MarathonFX:
    """静态动效方法集合"""

    EASE_OUT = QEasingCurve.Type.OutCubic
    EASE_IN_OUT = QEasingCurve.Type.InOutCubic
    EASE_SPRING = QEasingCurve.Type.OutBack

    # ---- 淡入淡出 ----

    @staticmethod
    def fade_in(widget: QWidget, duration=200, start=0.0, end=1.0):
        """淡入动画"""
        effect = widget.graphicsEffect()
        if not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)

        effect.setOpacity(start)
        anim = QPropertyAnimation(effect, b"opacity", widget)
        anim.setDuration(duration)
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.setEasingCurve(MarathonFX.EASE_OUT)
        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        return anim

    @staticmethod
    def fade_out(widget: QWidget, duration=150, start=1.0, end=0.0):
        """淡出动画"""
        return MarathonFX.fade_in(widget, duration, start, end)

    # ---- 滑入 ----

    @staticmethod
    def slide_in_right(widget: QWidget, duration=300, offset=30):
        """从右侧滑入 + 淡入"""
        start_pos = widget.pos() + QPoint(offset, 0)
        end_pos = widget.pos()

        pos_anim = QPropertyAnimation(widget, b"pos", widget)
        pos_anim.setDuration(duration)
        pos_anim.setStartValue(start_pos)
        pos_anim.setEndValue(end_pos)
        pos_anim.setEasingCurve(MarathonFX.EASE_OUT)

        effect = QGraphicsOpacityEffect(widget)
        effect.setOpacity(0.0)
        widget.setGraphicsEffect(effect)
        opacity_anim = QPropertyAnimation(effect, b"opacity", widget)
        opacity_anim.setDuration(duration)
        opacity_anim.setStartValue(0.0)
        opacity_anim.setEndValue(1.0)
        opacity_anim.setEasingCurve(MarathonFX.EASE_OUT)

        group = QParallelAnimationGroup(widget)
        group.addAnimation(pos_anim)
        group.addAnimation(opacity_anim)
        group.start(QParallelAnimationGroup.DeletionPolicy.DeleteWhenStopped)
        return group

    @staticmethod
    def slide_in_up(widget: QWidget, duration=250, offset=12):
        """从下方滑入 + 淡入"""
        start_pos = widget.pos() + QPoint(0, offset)
        end_pos = widget.pos()

        pos_anim = QPropertyAnimation(widget, b"pos", widget)
        pos_anim.setDuration(duration)
        pos_anim.setStartValue(start_pos)
        pos_anim.setEndValue(end_pos)
        pos_anim.setEasingCurve(MarathonFX.EASE_OUT)

        effect = QGraphicsOpacityEffect(widget)
        effect.setOpacity(0.0)
        widget.setGraphicsEffect(effect)
        opacity_anim = QPropertyAnimation(effect, b"opacity", widget)
        opacity_anim.setDuration(duration)
        opacity_anim.setStartValue(0.0)
        opacity_anim.setEndValue(1.0)
        opacity_anim.setEasingCurve(MarathonFX.EASE_OUT)

        group = QParallelAnimationGroup(widget)
        group.addAnimation(pos_anim)
        group.addAnimation(opacity_anim)
        group.start(QParallelAnimationGroup.DeletionPolicy.DeleteWhenStopped)
        return group

    # ---- 辉光 ----

    @staticmethod
    def apply_glow(widget: QWidget, color="#00E5FF", radius=12, offset=(0, 0)):
        """给 widget 添加静态辉光阴影"""
        shadow = QGraphicsDropShadowEffect(widget)
        shadow.setColor(QColor(color))
        shadow.setBlurRadius(radius)
        shadow.setOffset(offset[0], offset[1])
        widget.setGraphicsEffect(shadow)
        return shadow

    @staticmethod
    def pulse_glow(widget: QWidget, color="#00E5FF",
                   min_radius=4, max_radius=16, duration=1500):
        """脉冲辉光动画（无限循环）"""
        shadow = QGraphicsDropShadowEffect(widget)
        shadow.setColor(QColor(color))
        shadow.setBlurRadius(min_radius)
        shadow.setOffset(0, 0)
        widget.setGraphicsEffect(shadow)

        anim = QPropertyAnimation(shadow, b"blurRadius", widget)
        anim.setDuration(duration)
        anim.setStartValue(min_radius)
        anim.setKeyValueAt(0.5, max_radius)
        anim.setEndValue(min_radius)
        anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        anim.setLoopCount(-1)
        anim.start()
        return anim

    # ---- 列表依次进入 ----

    @staticmethod
    def stagger_children(parent: QWidget, duration=200,
                         delay_per_item=40, offset_y=8):
        """让 parent 的子 widget 依次淡入滑入"""
        children = [c for c in parent.children()
                    if isinstance(c, QWidget) and c.isVisible()]
        animations = []

        for i, child in enumerate(children):
            effect = QGraphicsOpacityEffect(child)
            effect.setOpacity(0.0)
            child.setGraphicsEffect(effect)

            delay = i * delay_per_item

            def _start(w=child, eff=effect, d=delay):
                QTimer.singleShot(d, lambda: MarathonFX._animate_child(
                    w, eff, duration, offset_y
                ))

            _start()
            animations.append(effect)

        return animations

    @staticmethod
    def _animate_child(widget, effect, duration, offset_y):
        start_pos = widget.pos() + QPoint(0, offset_y)
        end_pos = widget.pos()

        pos_anim = QPropertyAnimation(widget, b"pos", widget)
        pos_anim.setDuration(duration)
        pos_anim.setStartValue(start_pos)
        pos_anim.setEndValue(end_pos)
        pos_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        opacity_anim = QPropertyAnimation(effect, b"opacity", widget)
        opacity_anim.setDuration(duration)
        opacity_anim.setStartValue(0.0)
        opacity_anim.setEndValue(1.0)

        group = QParallelAnimationGroup(widget)
        group.addAnimation(pos_anim)
        group.addAnimation(opacity_anim)
        group.start(QParallelAnimationGroup.DeletionPolicy.DeleteWhenStopped)

    # ---- 主题激活/停用 ----

    @staticmethod
    def on_theme_activated(main_window) -> None:
        """主题被激活时调用，对主内容区执行淡入"""
        pages = getattr(main_window, "_pages", None)
        if pages is not None:
            MarathonFX.fade_in(pages, duration=200)

    @staticmethod
    def on_theme_deactivated(main_window) -> None:
        """主题被停用时调用（预留）"""
        pass

# ---- 主题导出变量（PyInstaller 兼容：静态 import 替代文件 I/O） ----

THEME_MANIFEST = {
    "manifest_version": 1,
    "id": "marathon",
    "name": "Marathon 深空",
    "version": "1.0.0",
    "author": "Seedance Studio",
    "description": "Bungie Marathon 深空作战终端 UI 风格。大面积暗色背景 + Cyan #00E5FF 强调色 + 精准网格排版。",
    "is_dark": True,
    "tags": ["dark", "scifi", "terminal"],
}

MARATHON_QSS = """/* =========================================================
   MARATHON THEME — Global Reset
   ========================================================= */
QWidget {
    background-color: transparent;
    font-family: "Segoe UI Variable", "Segoe UI", "Inter", sans-serif;
    font-size: 13px;
    color: #E8EAED;
    outline: none;
}

/* =========================================================
   主窗口 & 通用容器
   ========================================================= */
QMainWindow, QDialog {
    background-color: #0A0B10;
    border: 1px solid #1C2029;
}

QWidget#centralWidget {
    background-color: #0A0B10;
}

/* =========================================================
   自定义标题栏
   ========================================================= */
QWidget#titleBar {
    background-color: #06060B;
    border-bottom: 1px solid #1C2029;
    min-height: 36px;
    max-height: 36px;
}

QWidget#titleBar QLabel#titleLabel {
    font-size: 12px;
    font-weight: 600;
    color: #8B9099;
    padding-left: 12px;
}

QWidget#titleBar QPushButton {
    background: transparent;
    border: none;
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
    color: #8B9099;
    font-size: 14px;
}

QWidget#titleBar QPushButton:hover {
    background-color: #1C2029;
    color: #E8EAED;
}

QWidget#titleBar QPushButton#btnClose:hover {
    background-color: #FF4D00;
    color: #FFFFFF;
}

/* =========================================================
   侧边栏（全局样式，具体由 sidebar.qss 承载）
   ========================================================= */
QWidget#sidebar {
    background-color: #0A0B10;
    border-right: 1px solid #1C2029;
}

/* =========================================================
   主内容区标题
   ========================================================= */
QLabel#pageTitle {
    font-size: 18px;
    font-weight: 700;
    color: #E8EAED;
    padding-bottom: 8px;
    letter-spacing: 0.5px;
}

QLabel#sectionTitle {
    font-size: 11px;
    font-weight: 700;
    color: #4A5060;
    letter-spacing: 1.8px;
    padding: 16px 0 8px 0;
    text-transform: uppercase;
}

/* =========================================================
   标签（通用）
   ========================================================= */
QLabel {
    color: #8B9099;
    font-size: 13px;
}

QLabel[role="fieldLabel"] {
    font-size: 12px;
    font-weight: 600;
    color: #8B9099;
}

QLabel[role="hint"] {
    font-size: 11px;
    color: #4A5060;
    padding: 4px 0;
}

/* =========================================================
   输入框 & 文本编辑
   ========================================================= */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #1C2029;
    border: 1px solid #252A35;
    border-radius: 2px;
    padding: 8px 12px;
    color: #E8EAED;
    font-size: 13px;
    selection-background-color: rgba(0, 229, 255, 0.3);
    selection-color: #FFFFFF;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #00E5FF;
    background-color: #1C2029;
}

QLineEdit:disabled, QTextEdit:disabled {
    background-color: #101218;
    border: 1px solid #1C2029;
    color: #4A5060;
}

QLineEdit::placeholder {
    color: #4A5060;
}

/* =========================================================
   下拉框
   ========================================================= */
QComboBox {
    background-color: #1C2029;
    border: 1px solid #252A35;
    border-radius: 2px;
    padding: 6px 12px;
    min-height: 28px;
    color: #E8EAED;
}

QComboBox:hover {
    border: 1px solid #8B9099;
}

QComboBox:focus, QComboBox:on {
    border: 1px solid #00E5FF;
}

QComboBox::drop-down {
    border: none;
    width: 28px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #8B9099;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #161A22;
    border: 1px solid #252A35;
    selection-background-color: rgba(0, 229, 255, 0.12);
    selection-color: #00E5FF;
    padding: 4px;
    outline: none;
}

QComboBox QAbstractItemView::item {
    padding: 6px 12px;
    min-height: 28px;
    border-radius: 2px;
}

QComboBox QAbstractItemView::item:hover {
    background-color: rgba(0, 229, 255, 0.06);
}

/* =========================================================
   按钮 — 主按钮
   ========================================================= */
QPushButton {
    background-color: #1C2029;
    border: 1px solid #252A35;
    border-radius: 2px;
    padding: 7px 18px;
    font-size: 12px;
    font-weight: 600;
    color: #E8EAED;
    min-height: 30px;
    letter-spacing: 0.3px;
}

QPushButton:hover {
    background-color: #252A35;
    border: 1px solid #8B9099;
}

QPushButton:pressed {
    background-color: #101218;
}

QPushButton:disabled {
    background-color: #101218;
    border: 1px solid #1C2029;
    color: #4A5060;
}

/* 主操作按钮 */
QPushButton[role="primary"] {
    background-color: #00E5FF;
    border: none;
    color: #0A0B10;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}

QPushButton[role="primary"]:hover {
    background-color: #33ECFF;
}

QPushButton[role="primary"]:pressed {
    background-color: #00B8CC;
}

/* 幽灵按钮（边框型） */
QPushButton[role="ghost"] {
    background-color: transparent;
    border: 1px solid #00E5FF;
    color: #00E5FF;
}

QPushButton[role="ghost"]:hover {
    background-color: rgba(0, 229, 255, 0.08);
}

QPushButton[role="ghost"]:pressed {
    background-color: rgba(0, 229, 255, 0.15);
}

/* 危险按钮 */
QPushButton[role="danger"] {
    background-color: transparent;
    border: 1px solid #FF4D00;
    color: #FF4D00;
}

QPushButton[role="danger"]:hover {
    background-color: rgba(255, 77, 0, 0.1);
}

/* =========================================================
   复选框 & 单选框
   ========================================================= */
QCheckBox {
    spacing: 8px;
    color: #E8EAED;
    font-size: 13px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #252A35;
    border-radius: 2px;
    background-color: #1C2029;
}

QCheckBox::indicator:hover {
    border: 1px solid #8B9099;
}

QCheckBox::indicator:checked {
    background-color: #00E5FF;
    border: 1px solid #00E5FF;
}

QRadioButton {
    spacing: 8px;
    color: #E8EAED;
}

QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #252A35;
    border-radius: 8px;
    background-color: #1C2029;
}

QRadioButton::indicator:checked {
    background-color: #0A0B10;
    border: 5px solid #00E5FF;
}

/* =========================================================
   滑块
   ========================================================= */
QSlider::groove:horizontal {
    height: 3px;
    background: #1C2029;
    border-radius: 1px;
}

QSlider::handle:horizontal {
    width: 14px;
    height: 14px;
    margin: -6px 0;
    background: #00E5FF;
    border-radius: 7px;
    border: none;
}

QSlider::handle:horizontal:hover {
    background: #33ECFF;
    width: 16px;
    height: 16px;
    margin: -7px 0;
}

QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #00B8CC, stop:1 #00E5FF);
    border-radius: 1px;
}

/* =========================================================
   进度条
   ========================================================= */
QProgressBar {
    background-color: #1C2029;
    border: none;
    border-radius: 2px;
    height: 4px;
    text-align: center;
    font-size: 0px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #00B8CC, stop:1 #00E5FF);
    border-radius: 2px;
}

/* =========================================================
   滚动条
   ========================================================= */
QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 0;
    border: none;
}

QScrollBar::handle:vertical {
    background: #252A35;
    border-radius: 3px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #00E5FF;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: transparent;
    height: 0px;
}

QScrollBar:horizontal {
    background: transparent;
    height: 6px;
    margin: 0;
    border: none;
}

QScrollBar::handle:horizontal {
    background: #252A35;
    border-radius: 3px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background: #00E5FF;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {
    background: transparent;
    width: 0px;
}

/* =========================================================
   标签页 (QTabWidget)
   ========================================================= */
QTabWidget::pane {
    border: none;
    background-color: #0A0B10;
}

QTabBar {
    background: transparent;
}

QTabBar::tab {
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 10px 18px;
    font-size: 12px;
    font-weight: 600;
    color: #8B9099;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

QTabBar::tab:hover {
    color: #E8EAED;
}

QTabBar::tab:selected {
    color: #00E5FF;
    border-bottom: 2px solid #00E5FF;
}

/* =========================================================
   分组框
   ========================================================= */
QGroupBox {
    background-color: #101218;
    border: 1px solid #1C2029;
    border-radius: 3px;
    margin-top: 16px;
    padding: 20px 16px 16px 16px;
    font-size: 12px;
    font-weight: 700;
    color: #8B9099;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: #8B9099;
    font-size: 11px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

/* =========================================================
   表格
   ========================================================= */
QTableView, QTreeView, QListView {
    background-color: #0A0B10;
    alternate-background-color: #0D0F14;
    border: 1px solid #1C2029;
    border-radius: 2px;
    gridline-color: #1C2029;
    selection-background-color: rgba(0, 229, 255, 0.08);
    selection-color: #E8EAED;
}

QHeaderView::section {
    background-color: #0A0B10;
    border: none;
    border-bottom: 1px solid #1C2029;
    border-right: 1px solid #1C2029;
    padding: 8px 12px;
    font-size: 10px;
    font-weight: 700;
    color: #4A5060;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

QTableView::item {
    padding: 8px 12px;
    border-bottom: 1px solid #1C2029;
}

QTableView::item:selected {
    background-color: rgba(0, 229, 255, 0.08);
    border-left: 3px solid #00E5FF;
}

/* 兼容 QTableWidget（继承自 QTableView） */
QTableWidget {
    background-color: #0A0B10;
    alternate-background-color: #0D0F14;
    border: 1px solid #1C2029;
    gridline-color: #1C2029;
    selection-background-color: rgba(0, 229, 255, 0.08);
    selection-color: #E8EAED;
    color: #E8EAED;
}

QTableWidget QHeaderView::section {
    background-color: #0A0B10;
    color: #4A5060;
    padding: 8px 12px;
    border: none;
    border-bottom: 1px solid #1C2029;
    border-right: 1px solid #1C2029;
    font-weight: 700;
    font-size: 10px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

QTableWidget::item {
    padding: 8px 12px;
    border-bottom: 1px solid #1C2029;
}

QTableWidget::item:selected {
    background-color: rgba(0, 229, 255, 0.08);
    border-left: 3px solid #00E5FF;
}

/* =========================================================
   工具提示
   ========================================================= */
QToolTip {
    background-color: #1C2029;
    border: 1px solid #252A35;
    border-radius: 3px;
    color: #E8EAED;
    font-size: 12px;
    padding: 6px 10px;
}

/* =========================================================
   菜单
   ========================================================= */
QMenu {
    background-color: #161A22;
    border: 1px solid #252A35;
    border-radius: 3px;
    padding: 4px;
}

QMenu::item {
    padding: 8px 24px 8px 12px;
    border-radius: 2px;
    color: #E8EAED;
    font-size: 13px;
}

QMenu::item:selected {
    background-color: rgba(0, 229, 255, 0.1);
    color: #00E5FF;
}

QMenu::separator {
    height: 1px;
    background: #1C2029;
    margin: 4px 8px;
}

/* =========================================================
   拖放区域（自定义 widget）
   ========================================================= */
QWidget#dropZone {
    background-color: #101218;
    border: 1px dashed #252A35;
    border-radius: 3px;
    min-height: 100px;
}

QWidget#dropZone:hover {
    border-color: #00E5FF;
    background-color: rgba(0, 229, 255, 0.03);
}

/* =========================================================
   右侧面板
   ========================================================= */
QWidget#rightPanel {
    background-color: #101218;
    border-left: 1px solid #1C2029;
    min-width: 240px;
}

QWidget#rightPanel QLabel#panelTitle {
    font-size: 13px;
    font-weight: 700;
    color: #E8EAED;
    padding: 16px 16px 12px 16px;
}

/* =========================================================
   分割线装饰
   ========================================================= */
QFrame#separator {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #00E5FF, stop:0.6 #1C2029, stop:1 transparent);
    max-height: 1px;
    min-height: 1px;
    border: none;
}

QFrame#separatorSubtle {
    background-color: #1C2029;
    max-height: 1px;
    min-height: 1px;
    border: none;
}

/* =========================================================
   SpinBox
   ========================================================= */
QSpinBox, QDoubleSpinBox {
    background-color: #1C2029;
    border: 1px solid #252A35;
    border-radius: 2px;
    padding: 6px 8px;
    color: #E8EAED;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #00E5FF;
}

QSpinBox::up-button, QDoubleSpinBox::up-button,
QSpinBox::down-button, QDoubleSpinBox::down-button {
    background: transparent;
    border: none;
    width: 20px;
}"""

SIDEBAR_QSS = """/* =========================================================
   MARATHON SIDEBAR — 深空终端风格侧边栏
   ========================================================= */

QWidget#sidebar {
    background-color: #0A0B10;
    border-right: 1px solid #1C2029;
    min-width: 180px;
    max-width: 180px;
}

QWidget#sidebar QLabel#appTitle {
    font-size: 15px;
    font-weight: 700;
    color: #E8EAED;
    padding: 20px 16px 24px 16px;
    letter-spacing: 0.5px;
}

/* 侧边栏导航按钮 */
QWidget#sidebar QPushButton {
    background: transparent;
    border: none;
    border-left: 3px solid transparent;
    border-radius: 0px;
    text-align: left;
    padding: 10px 16px;
    font-size: 13px;
    font-weight: 500;
    color: #8B9099;
    min-height: 38px;
}

QWidget#sidebar QPushButton:hover {
    background-color: rgba(0, 229, 255, 0.04);
    color: #E8EAED;
}

QWidget#sidebar QPushButton:checked {
    background-color: rgba(0, 229, 255, 0.08);
    border-left: 3px solid #00E5FF;
    color: #00E5FF;
    font-weight: 600;
}"""
