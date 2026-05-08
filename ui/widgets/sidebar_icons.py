"""
Marathon v3 程序化几何图标。

QPainter 绘制的扁平几何图标，用于侧边栏导航和 Toast 通知。
风格：全直角 / 1px 描边 / 无渐变 / accent green #C8FF00。
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QPen, QColor, QIcon, QPixmap, QPolygon


_SIDEBAR_SIZE = 16
_TOAST_SIZE = 14
_ACCENT = "#C8FF00"


def _make_painter(size: int, color: str):
    from PyQt6.QtWidgets import QApplication
    if QApplication.instance() is None:
        raise RuntimeError("sidebar_icons requires a running QApplication")
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QPen(QColor(color), 1))
    painter.setBrush(QColor(color))
    return pixmap, painter


# ── 侧边栏图标 (16×16, accent green) ──────────────────────────────

def create_video_icon(color: str = _ACCENT, size: int = _SIDEBAR_SIZE) -> QIcon:
    """播放三角 — 实心右指三角形"""
    pixmap, p = _make_painter(size, color)
    poly = QPolygon([QPoint(5, 3), QPoint(5, 13), QPoint(13, 8)])
    p.drawPolygon(poly)
    p.end()
    return QIcon(pixmap)


def create_settings_icon(color: str = _ACCENT, size: int = _SIDEBAR_SIZE) -> QIcon:
    """十字准星 — 方框 + 中心点"""
    pixmap, p = _make_painter(size, color)
    p.setBrush(Qt.GlobalColor.transparent)
    p.drawRect(2, 2, 12, 12)
    p.setBrush(QColor(color))
    p.drawRect(7, 7, 2, 2)
    p.end()
    return QIcon(pixmap)


def create_task_list_icon(color: str = _ACCENT, size: int = _SIDEBAR_SIZE) -> QIcon:
    """任务列表 — 三横线 + 左端方块标记"""
    pixmap, p = _make_painter(size, color)
    for i in range(3):
        y = 3 + i * 4
        p.drawRect(3, y, 2, 2)
        p.drawLine(7, y + 1, 14, y + 1)
    p.end()
    return QIcon(pixmap)


def create_about_icon(color: str = _ACCENT, size: int = _SIDEBAR_SIZE) -> QIcon:
    """关于 — 菱形框 + 叹号"""
    pixmap, p = _make_painter(size, color)
    p.setBrush(Qt.GlobalColor.transparent)
    poly = QPolygon([QPoint(8, 1), QPoint(15, 8), QPoint(8, 15), QPoint(1, 8)])
    p.drawPolygon(poly)
    p.setBrush(QColor(color))
    p.drawLine(8, 4, 8, 10)
    p.drawRect(7, 11, 2, 2)
    p.end()
    return QIcon(pixmap)


# ── Toast 图标 (14×14, 按类型着色) ─────────────────────────────────

def create_toast_icon(type_: str, color: str, size: int = _TOAST_SIZE) -> QPixmap:
    """返回对应 toast 类型的 QPainter 绘制 pixmap。

    type_ 取值: success, warning, error, info
    """
    pixmap, p = _make_painter(size, color)

    if type_ == "success":
        _draw_success(p, size)
    elif type_ == "warning":
        _draw_warning(p, size)
    elif type_ == "error":
        _draw_error(p, size)
    else:
        _draw_info(p, size)

    p.end()
    return pixmap


def _draw_success(p: QPainter, size: int):
    """圆圈 + 对勾"""
    p.setBrush(Qt.GlobalColor.transparent)
    r = size - 2
    p.drawEllipse(1, 1, r, r)
    mid = size // 2
    p.drawLine(mid - 3, mid + 1, mid - 1, mid + 3)
    p.drawLine(mid - 1, mid + 3, mid + 3, mid - 2)


def _draw_warning(p: QPainter, size: int):
    """三角形 + 叹号"""
    p.setBrush(Qt.GlobalColor.transparent)
    poly = QPolygon([QPoint(size // 2, 1), QPoint(size - 1, size - 1), QPoint(1, size - 1)])
    p.drawPolygon(poly)
    mid = size // 2
    p.setBrush(QColor(p.pen().color()))
    p.drawLine(mid, 5, mid, 9)
    p.drawRect(mid - 1, 10, 2, 2)


def _draw_error(p: QPainter, size: int):
    """圆圈 + X"""
    p.setBrush(Qt.GlobalColor.transparent)
    r = size - 2
    p.drawEllipse(1, 1, r, r)
    p.drawLine(4, 4, size - 4, size - 4)
    p.drawLine(size - 4, 4, 4, size - 4)


def _draw_info(p: QPainter, size: int):
    """菱形 + 叹号"""
    p.setBrush(Qt.GlobalColor.transparent)
    mid = size // 2
    poly = QPolygon([QPoint(mid, 1), QPoint(size - 1, mid), QPoint(mid, size - 1), QPoint(1, mid)])
    p.drawPolygon(poly)
    p.setBrush(QColor(p.pen().color()))
    p.drawLine(mid, 4, mid, 9)
    p.drawRect(mid - 1, 10, 2, 2)
