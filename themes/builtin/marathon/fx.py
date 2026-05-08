"""
Marathon 深空终端主题 v3 — 色彩令牌 & 动效工具。

提供 MarathonColors 颜色类和 MarathonFX 动效静态方法集合。
参考：Bungie Marathon 深空作战终端 UI 风格规范 v3（docs/reference/marathon_style_v2.md）
"""
from __future__ import annotations

from PyQt6.QtWidgets import QWidget, QGraphicsOpacityEffect, QGraphicsDropShadowEffect
from PyQt6.QtCore import (
    QPropertyAnimation, QEasingCurve, QParallelAnimationGroup,
    QPoint, QTimer
)
from PyQt6.QtGui import QColor


class MarathonColors:
    """Marathon UI 色彩系统 v3 — Flat Design 全直角无渐变"""

    # 背景层级
    BG_BASE    = "#000000"
    BG_SURFACE = "#1C1C1C"
    BG_OVERLAY = "#1C1C1C"
    BG_RAISED  = "#1C1C1C"

    # 边框
    BORDER_SUBTLE  = "#333333"
    BORDER_DEFAULT = "#333333"
    BORDER_FOCUS   = "#C8FF00"

    # 强调色
    ACCENT   = "#C8FF00"
    DANGER   = "#FF3333"
    WARNING  = "#E5FF00"
    SUCCESS  = "#00FF88"

    # 基础色
    WHITE = "#FFFFFF"
    BLACK = "#000000"

    # 文字色阶
    TEXT_PRIMARY   = "#FFFFFF"
    TEXT_SECONDARY = "#717171"
    TEXT_TERTIARY  = "#444444"


class MarathonFX:
    """静态动效方法集合"""

    EASE_OUT = QEasingCurve.Type.OutQuad

    # ---- 淡入淡出 ----

    @staticmethod
    def fade_in(widget: QWidget, duration=300, start=0.0, end=1.0):
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
    def apply_glow(widget: QWidget, color="#C8FF00", radius=12, offset=(0, 0)):
        """给 widget 添加静态辉光阴影"""
        shadow = QGraphicsDropShadowEffect(widget)
        shadow.setColor(QColor(color))
        shadow.setBlurRadius(radius)
        shadow.setOffset(offset[0], offset[1])
        widget.setGraphicsEffect(shadow)
        return shadow

    @staticmethod
    def pulse_glow(widget: QWidget, color="#C8FF00",
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
        pos_anim.setEasingCurve(MarathonFX.EASE_OUT)

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
            MarathonFX.fade_in(pages, duration=300)

    @staticmethod
    def on_theme_deactivated(main_window) -> None:
        """主题被停用时调用（预留）"""
        pass


# 模块级包装函数，供 ThemeLoader 直接调用
def on_theme_activated(main_window) -> None:
    MarathonFX.on_theme_activated(main_window)


def on_theme_deactivated(main_window) -> None:
    MarathonFX.on_theme_deactivated(main_window)


# ---- 主题导出变量（PyInstaller 兼容：静态 import 替代文件 I/O） ----

THEME_MANIFEST = {
    "manifest_version": 1,
    "id": "marathon",
    "name": "Marathon 深空",
    "version": "3.0.0",
    "author": "Seedance Studio",
    "description": "Bungie Marathon 深空作战终端 UI 风格 v3。Flat Design 全直角 + Acid Green #C8FF00 强调 + JetBrains Mono 等宽正文 + Eurostile 几何标题 + 280px 侧边栏。",
    "is_dark": True,
    "tags": ["dark", "scifi", "terminal", "flat"],
    "colors": {
        "bg_base": "#000000",
        "bg_surface": "#1C1C1C",
        "bg_overlay": "#1C1C1C",
        "bg_raised": "#1C1C1C",
        "primary": "#C8FF00",
        "danger": "#FF3333",
        "warning": "#E5FF00",
        "success": "#00FF88",
        "info": "#C8FF00",
        "text_primary": "#FFFFFF",
        "text_secondary": "#717171",
        "text_tertiary": "#444444",
        "border_subtle": "#333333",
        "border_default": "#333333",
        "border_focus": "#C8FF00",
        "toast_success": "#00FF88",
        "toast_warning": "#E5FF00",
        "toast_error": "#FF3333",
        "toast_info": "#C8FF00",
        "media_image": "#3498db",
        "media_video": "#e67e22",
        "media_audio": "#2ecc71",
    },
}

MARATHON_QSS = """/* =========================================================
   MARATHON THEME v3 — Bungie Marathon 深空作战终端风格
   字体: Eurostile Extended / Microgramma (标题)
        JetBrains Mono / Cascadia Code / Consolas (正文)
   色彩: #000000 底 + #1C1C1C 面板 + Acid Green #C8FF00 强调
   Flat Design — 全直角 0px / 无渐变 / 无阴影
   ========================================================= */

/* ---- 全局 Reset ---- */
QWidget {
    background-color: transparent;
    font-family: "JetBrains Mono", "Cascadia Code", "Consolas", monospace;
    font-size: 14px;
    color: #FFFFFF;
    outline: none;
}

/* ---- 主窗口 ---- */
QMainWindow, QDialog {
    background-color: #000000;
    border: 1px solid #333333;
}

QWidget#centralWidget,
QWidget#mainRoot {
    background-color: #000000;
}

/* ---- 自定义标题栏（无边框模式保留，系统标题栏模式不生效） ---- */
QWidget#titleBar {
    background-color: #000000;
    border-bottom: 1px solid #333333;
    min-height: 36px;
    max-height: 36px;
}

QWidget#titleBar QLabel#titleLabel {
    font-family: "Eurostile Extended", "Microgramma", "Share Tech", sans-serif;
    font-size: 12px;
    font-weight: 600;
    color: #717171;
    padding-left: 12px;
    letter-spacing: 1px;
}

QWidget#titleBar QPushButton {
    background: transparent;
    border: none;
    color: #717171;
}

QWidget#titleBar QPushButton:hover {
    background-color: #1C1C1C;
    color: #FFFFFF;
}

QWidget#titleBar QPushButton#btnClose:hover {
    background-color: #FF3333;
    color: #FFFFFF;
}

/* ---- 侧边栏占位（详细样式在 SIDEBAR_QSS） ---- */
QWidget#sidebar {
    background-color: #000000;
    border-right: 1px solid #333333;
}

/* =========================================================
   标题层级
   ========================================================= */
QLabel#pageTitle {
    font-family: "Eurostile Extended", "Microgramma", "Share Tech", sans-serif;
    font-size: 20px;
    font-weight: 700;
    color: #FFFFFF;
    padding-bottom: 8px;
    letter-spacing: 1.5px;
}

QLabel#sectionTitle {
    font-size: 10px;
    font-weight: 700;
    color: #444444;
    letter-spacing: 2px;
    padding: 16px 0 8px 0;
}

/* =========================================================
   标签（通用）
   ========================================================= */
QLabel {
    color: #717171;
    font-size: 14px;
}

QLabel[role="fieldLabel"] {
    font-size: 10px;
    font-weight: 600;
    color: #717171;
    letter-spacing: 1.5px;
}

QLabel[role="hint"] {
    font-size: 12px;
    color: #444444;
    padding: 4px 0;
}

/* =========================================================
   输入框 & 文本编辑（仅底部 1px 边框，等宽字体）
   ========================================================= */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #1C1C1C;
    border: none;
    border-bottom: 1px solid #333333;
    border-radius: 0px;
    padding: 0 12px;
    min-height: 36px;
    color: #FFFFFF;
    font-size: 14px;
    selection-background-color: #C8FF00;
    selection-color: #000000;
}

QTextEdit, QPlainTextEdit {
    padding: 8px 12px;
    min-height: 80px;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border-bottom: 1px solid #C8FF00;
    background-color: #1C1C1C;
}

QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {
    background-color: #0D0D0D;
    border-bottom: 1px solid #333333;
    color: #444444;
}

QLineEdit::placeholder, QPlainTextEdit::placeholder {
    color: #444444;
}

/* =========================================================
   下拉框
   ========================================================= */
QComboBox {
    background-color: #1C1C1C;
    border: 1px solid #333333;
    border-radius: 0px;
    padding: 0 12px;
    min-height: 34px;
    color: #FFFFFF;
    font-size: 14px;
}

QComboBox:hover {
    border: 1px solid #717171;
}

QComboBox:focus, QComboBox:on {
    border: 1px solid #C8FF00;
}

QComboBox::drop-down {
    border: none;
    width: 28px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #717171;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #1C1C1C;
    border: 1px solid #333333;
    border-radius: 0px;
    selection-background-color: #C8FF00;
    selection-color: #000000;
    padding: 4px;
    outline: none;
}

QComboBox QAbstractItemView::item {
    padding: 6px 12px;
    min-height: 32px;
    border-radius: 0px;
    color: #FFFFFF;
}

QComboBox QAbstractItemView::item:hover {
    background-color: #333333;
}

/* =========================================================
   按钮 — Flat Design 全直角 / 无渐变 / 无阴影
   ========================================================= */
QPushButton {
    background-color: transparent;
    border: 1px solid #FFFFFF;
    border-radius: 0px;
    padding: 0 20px;
    font-size: 13px;
    font-weight: 600;
    color: #FFFFFF;
    min-height: 48px;
    min-width: 200px;
    letter-spacing: 1px;
}

QPushButton:hover {
    background-color: #C8FF00;
    border: 1px solid #C8FF00;
    color: #000000;
}

QPushButton:pressed {
    background-color: #C8FF00;
    border: 1px solid #C8FF00;
    color: #000000;
}

QPushButton:disabled {
    background-color: transparent;
    border: 1px solid #333333;
    color: #444444;
}

/* 主操作按钮 — accent 背景 + black 文字 */
QPushButton[role="primary"] {
    background-color: #C8FF00;
    border: none;
    color: #000000;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1px;
    min-height: 48px;
    min-width: 200px;
}

QPushButton[role="primary"]:hover {
    background-color: #000000;
    border: 1px solid #C8FF00;
    color: #C8FF00;
}

QPushButton[role="primary"]:pressed {
    background-color: #000000;
    border: 1px solid #C8FF00;
    color: #C8FF00;
}

QPushButton[role="primary"]:disabled {
    background-color: #1C1C1C;
    border: none;
    color: #444444;
}

/* 危险按钮 */
QPushButton[role="danger"] {
    background-color: transparent;
    border: 1px solid #FF3333;
    color: #FF3333;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 1px;
    min-height: 48px;
    min-width: 200px;
}

QPushButton[role="danger"]:hover {
    background-color: #FF3333;
    border: 1px solid #FF3333;
    color: #000000;
}

QPushButton[role="danger"]:pressed {
    background-color: #FF3333;
    border: 1px solid #FF3333;
    color: #000000;
}

QPushButton[role="danger"]:disabled {
    background-color: transparent;
    border: 1px solid #444444;
    color: #444444;
}

/* 小按钮（表格操作列 / Ghost） — min-height 32px */
QPushButton[role="ghost"] {
    min-height: 32px;
    min-width: 0px;
    background-color: transparent;
    border: 1px solid #333333;
    color: #FFFFFF;
    font-size: 12px;
    padding: 0 12px;
    letter-spacing: 0.5px;
}

QPushButton[role="ghost"]:hover {
    background-color: #C8FF00;
    border: 1px solid #C8FF00;
    color: #000000;
}

QPushButton[role="ghost"]:disabled {
    border: 1px solid #444444;
    color: #444444;
}

/* =========================================================
   复选框 & 单选框
   ========================================================= */
QCheckBox {
    spacing: 8px;
    color: #FFFFFF;
    font-size: 14px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #333333;
    border-radius: 0px;
    background-color: #1C1C1C;
}

QCheckBox::indicator:hover {
    border: 1px solid #717171;
}

QCheckBox::indicator:checked {
    background-color: #C8FF00;
    border: 1px solid #C8FF00;
}

QRadioButton {
    spacing: 8px;
    color: #FFFFFF;
    font-size: 14px;
}

QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #333333;
    border-radius: 0px;
    background-color: #1C1C1C;
}

QRadioButton::indicator:checked {
    background-color: #000000;
    border: 2px solid #C8FF00;
}

/* =========================================================
   滑块
   ========================================================= */
QSlider::groove:horizontal {
    height: 3px;
    background: #333333;
    border-radius: 0px;
}

QSlider::handle:horizontal {
    width: 14px;
    height: 14px;
    margin: -6px 0;
    background: #C8FF00;
    border-radius: 0px;
    border: none;
}

QSlider::handle:horizontal:hover {
    background: #C8FF00;
    width: 16px;
    height: 16px;
    margin: -7px 0;
}

QSlider::sub-page:horizontal {
    background: #C8FF00;
    border-radius: 0px;
}

/* =========================================================
   进度条（3px 轨道 + 纯色填充）
   ========================================================= */
QProgressBar {
    background-color: #333333;
    border: none;
    border-radius: 0px;
    max-height: 3px;
    min-height: 3px;
    text-align: center;
    font-size: 0px;
}

QProgressBar::chunk {
    background: #C8FF00;
    border-radius: 0px;
}

/* =========================================================
   滚动条（4px 细条，thumb #C8FF00，无圆角）
   ========================================================= */
QScrollBar:vertical {
    background: transparent;
    width: 4px;
    margin: 0;
    border: none;
}

QScrollBar::handle:vertical {
    background: #C8FF00;
    border-radius: 0px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #C8FF00;
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
    height: 4px;
    margin: 0;
    border: none;
}

QScrollBar::handle:horizontal {
    background: #C8FF00;
    border-radius: 0px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background: #C8FF00;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {
    background: transparent;
    width: 0px;
}

/* =========================================================
   标签页（底部 2px #C8FF00 指示条）
   ========================================================= */
QTabWidget::pane {
    border: none;
    background-color: #000000;
}

QTabBar {
    background: transparent;
}

QTabBar::tab {
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 10px 24px;
    font-size: 13px;
    font-weight: 600;
    color: #717171;
    letter-spacing: 1px;
    min-height: 40px;
}

QTabBar::tab:hover {
    color: #FFFFFF;
}

QTabBar::tab:selected {
    color: #C8FF00;
    border-bottom: 2px solid #C8FF00;
}

/* =========================================================
   分组框
   ========================================================= */
QGroupBox {
    background-color: #1C1C1C;
    border: 1px solid #333333;
    border-radius: 0px;
    margin-top: 16px;
    padding: 20px 16px 16px 16px;
    font-size: 10px;
    font-weight: 700;
    color: #444444;
    letter-spacing: 1.5px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: #444444;
    font-size: 10px;
    letter-spacing: 2px;
}

/* =========================================================
   表格（行高 44px，选中行左侧 3px #C8FF00 指示条）
   ========================================================= */
QTableView, QTreeView, QListView {
    background-color: #000000;
    alternate-background-color: #0D0D0D;
    border: 1px solid #333333;
    border-radius: 0px;
    gridline-color: #333333;
    selection-background-color: #1C1C1C;
    selection-color: #FFFFFF;
}

QHeaderView::section {
    background-color: #000000;
    border: none;
    border-bottom: 1px solid #333333;
    border-right: 1px solid #333333;
    padding: 8px 16px;
    font-size: 10px;
    font-weight: 700;
    color: #444444;
    letter-spacing: 2px;
    min-height: 36px;
}

QTableView::item {
    padding: 0 16px;
    border-bottom: 1px solid #333333;
    min-height: 44px;
}

QTableView::item:hover {
    background-color: #1C1C1C;
}

QTableView::item:selected {
    background-color: #1C1C1C;
    border-left: 3px solid #C8FF00;
}

/* QTableWidget 继承 */
QTableWidget {
    background-color: #000000;
    alternate-background-color: #0D0D0D;
    border: 1px solid #333333;
    gridline-color: #333333;
    selection-background-color: #1C1C1C;
    selection-color: #FFFFFF;
    color: #FFFFFF;
}

QTableWidget QHeaderView::section {
    background-color: #000000;
    color: #444444;
    padding: 8px 16px;
    border: none;
    border-bottom: 1px solid #333333;
    border-right: 1px solid #333333;
    font-weight: 700;
    font-size: 10px;
    letter-spacing: 2px;
    min-height: 36px;
}

QTableWidget::item {
    padding: 0 16px;
    border-bottom: 1px solid #333333;
    min-height: 44px;
}

QTableWidget::item:hover {
    background-color: #1C1C1C;
}

QTableWidget::item:selected {
    background-color: #1C1C1C;
    border-left: 3px solid #C8FF00;
}

/* =========================================================
   工具提示
   ========================================================= */
QToolTip {
    background-color: #1C1C1C;
    border: 1px solid #333333;
    border-radius: 0px;
    color: #FFFFFF;
    font-size: 12px;
    padding: 6px 10px;
}

/* =========================================================
   菜单
   ========================================================= */
QMenu {
    background-color: #1C1C1C;
    border: 1px solid #333333;
    border-radius: 0px;
    padding: 4px;
}

QMenu::item {
    padding: 8px 24px 8px 12px;
    border-radius: 0px;
    color: #FFFFFF;
    font-size: 14px;
}

QMenu::item:selected {
    background-color: #C8FF00;
    color: #000000;
}

QMenu::separator {
    height: 1px;
    background: #333333;
    margin: 4px 8px;
}

/* =========================================================
   拖放区域
   ========================================================= */
QWidget#dropZone {
    background-color: #1C1C1C;
    border: 1px dashed #333333;
    border-radius: 0px;
    min-height: 100px;
}

QWidget#dropZone:hover {
    border-color: #C8FF00;
    background-color: #1C1C1C;
}

/* =========================================================
   右侧面板
   ========================================================= */
QWidget#rightPanel {
    background-color: #1C1C1C;
    border-left: 1px solid #333333;
    min-width: 240px;
}

QWidget#rightPanel QLabel#panelTitle {
    font-family: "Eurostile Extended", "Microgramma", "Share Tech", sans-serif;
    font-size: 14px;
    font-weight: 700;
    color: #FFFFFF;
    padding: 16px 16px 12px 16px;
    letter-spacing: 1px;
}

/* =========================================================
   分割线（纯色 1px 线，无渐变）
   ========================================================= */
QFrame#separator {
    background-color: #333333;
    max-height: 1px;
    min-height: 1px;
    border: none;
}

QFrame#separatorSubtle {
    background-color: #333333;
    max-height: 1px;
    min-height: 1px;
    border: none;
}

/* =========================================================
   SpinBox
   ========================================================= */
QSpinBox, QDoubleSpinBox {
    background-color: #1C1C1C;
    border: 1px solid #333333;
    border-radius: 0px;
    padding: 0 8px;
    min-height: 34px;
    color: #FFFFFF;
    font-size: 14px;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #C8FF00;
}

QSpinBox::up-button, QDoubleSpinBox::up-button,
QSpinBox::down-button, QDoubleSpinBox::down-button {
    background: transparent;
    border: none;
    width: 20px;
}

/* =========================================================
   启动画面 (SplashScreen)
   ========================================================= */
QWidget#splashScreen {
    background-color: #000000;
    border: 1px solid #333333;
    border-radius: 0px;
}

QLabel#splashTitle {
    font-family: "Eurostile Extended", "Microgramma", "Share Tech", sans-serif;
    color: #FFFFFF;
    font-size: 24px;
    font-weight: 700;
    letter-spacing: 2px;
}

QLabel#splashVersion {
    color: #444444;
    font-size: 12px;
    letter-spacing: 1px;
}

QLabel#splashLoading {
    color: #C8FF00;
    font-size: 11px;
    letter-spacing: 1.5px;
}

/* =========================================================
   Toast 通知（左侧 3px 色条 + 深色背景，无圆角）
   ========================================================= */
QFrame#toastItem {
    background-color: #1C1C1C;
    border: 1px solid #333333;
    border-radius: 0px;
}

QFrame#toastItem[type="success"] {
    border-left: 3px solid #00FF88;
}

QFrame#toastItem[type="warning"] {
    border-left: 3px solid #E5FF00;
}

QFrame#toastItem[type="error"] {
    border-left: 3px solid #FF3333;
}

QFrame#toastItem[type="info"] {
    border-left: 3px solid #C8FF00;
}

QLabel#toastTitle {
    font-weight: 700;
    font-size: 13px;
    background: transparent;
    color: #FFFFFF;
    letter-spacing: 0.5px;
}

QLabel#toastMessage {
    color: #717171;
    font-size: 12px;
    background: transparent;
}

/* =========================================================
   提示词助手 (PromptHelperWidget)
   ========================================================= */
QLabel#helperTitle {
    font-family: "Eurostile Extended", "Microgramma", "Share Tech", sans-serif;
    font-size: 15px;
    font-weight: 700;
    padding: 4px 0;
    color: #FFFFFF;
    letter-spacing: 1px;
}

QLabel#helperCategory {
    font-size: 10px;
    font-weight: 700;
    color: #444444;
    padding: 4px 0 2px 0;
    letter-spacing: 2px;
}

QPushButton#helperButton {
    background: transparent;
    border: 1px solid #333333;
    border-radius: 0px;
    padding: 4px 10px;
    text-align: left;
    color: #717171;
    font-size: 13px;
    min-height: 28px;
    min-width: 0px;
}

QPushButton#helperButton:hover {
    background-color: #1C1C1C;
    border-color: #C8FF00;
    color: #FFFFFF;
}

QLabel#helperFormula {
    font-weight: 700;
    color: #FFFFFF;
    font-size: 12px;
}

QLabel#helperExample {
    color: #444444;
    font-size: 11px;
    padding-left: 8px;
}

QLabel#helperNoData {
    color: #444444;
    font-size: 13px;
    padding: 8px;
}

QFrame#helperSeparator {
    background-color: #333333;
    max-height: 1px;
}

QLabel#helperRuleTitle {
    font-weight: 700;
    color: #FFFFFF;
    font-size: 13px;
}

QLabel#helperRuleDesc {
    color: #717171;
    font-size: 12px;
}

/* =========================================================
   素材上传 (MediaUploadWidget)
   ========================================================= */
QLabel#dropZone {
    border: 1px dashed #333333;
    border-radius: 0px;
    color: #444444;
    font-size: 13px;
    background-color: #1C1C1C;
}

QLabel#dropZone:hover {
    border-color: #C8FF00;
    background-color: #1C1C1C;
    color: #717171;
}

QLabel#mediaSectionLabel {
    font-size: 10px;
    font-weight: 700;
    color: #444444;
    letter-spacing: 2px;
    margin-top: 8px;
}

QLabel#mediaCountLabel {
    color: #717171;
    font-size: 12px;
}

QFrame#mediaItemWidget {
    border: 1px solid #333333;
    border-radius: 0px;
    background-color: #1C1C1C;
}

QLabel#mediaNameLabel {
    font-size: 11px;
    color: #717171;
    border: none;
    background: transparent;
}

QPushButton#mediaRemoveButton {
    background: transparent;
    border: 1px solid #333333;
    color: #444444;
    font-size: 11px;
    padding: 0 8px;
    min-height: 24px;
    min-width: 0px;
}

QPushButton#mediaRemoveButton:hover {
    background-color: #FF3333;
    border-color: #FF3333;
    color: #FFFFFF;
}

/* =========================================================
   视频播放器 (VideoPlayerWidget)
   ========================================================= */
QLabel#expiryLabel {
    color: #E5FF00;
    font-size: 11px;
    letter-spacing: 0.5px;
}

/* =========================================================
   资产选择器 (AssetPickerWidget)
   ========================================================= */
QLabel#pickerTitle {
    font-family: "Eurostile Extended", "Microgramma", "Share Tech", sans-serif;
    font-size: 16px;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: 1px;
}

QLabel#pickerStatus {
    color: #717171;
    font-size: 13px;
}"""

SIDEBAR_QSS = """/* =========================================================
   MARATHON SIDEBAR v3 — 深空终端导航栏
   宽度 280px（固定展开），导航项 40px，全直角 Flat Design
   ========================================================= */

QWidget#sidebar {
    background-color: #000000;
    border-right: 1px solid #333333;
}

/* 应用标题（几何宽体字体，机械感） */
QWidget#sidebar QLabel#appTitle {
    font-family: "Eurostile Extended", "Microgramma", "Share Tech", sans-serif;
    font-size: 16px;
    font-weight: 700;
    color: #FFFFFF;
    padding: 20px 16px 8px 16px;
    letter-spacing: 1.5px;
}

/* NAVIGATION Overline 标签 */
QWidget#sidebar QLabel#navLabel {
    font-size: 10px;
    font-weight: 700;
    color: #444444;
    padding: 16px 16px 6px 16px;
    letter-spacing: 2px;
}

/* 导航按钮 */
QWidget#sidebar QPushButton {
    background: transparent;
    border: none;
    border-left: 3px solid transparent;
    border-radius: 0px;
    text-align: left;
    padding: 0 16px;
    font-size: 14px;
    font-weight: 500;
    color: #717171;
    min-height: 40px;
    max-height: 40px;
    min-width: 0px;
}

QWidget#sidebar QPushButton:hover {
    background-color: #1C1C1C;
    color: #FFFFFF;
    border-left: 3px solid transparent;
}

QWidget#sidebar QPushButton:checked {
    background-color: #1C1C1C;
    border-left: 3px solid #C8FF00;
    color: #C8FF00;
    font-weight: 600;
}"""
