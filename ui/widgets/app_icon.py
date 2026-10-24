"""
应用品牌图标（程序化绘制）。

与 Graphite 主题侧边栏品牌区同语言：蓝色渐变圆角方块 + 白色圆角播放三角。
程序化生成多尺寸 QIcon，运行时不依赖磁盘图标文件。
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, QPointF, QRectF, QSize
from PyQt6.QtGui import (
    QPainter, QPixmap, QIcon, QColor, QLinearGradient, QPolygonF, QPen,
)

_SIZES = (16, 20, 24, 32, 48, 64, 128, 256)


def _draw_mark(painter: QPainter, size: int) -> None:
    """在 size×size 画布上绘制品牌图形"""
    s = size

    # 蓝色对角渐变圆角方块
    gradient = QLinearGradient(0, 0, s, s)
    gradient.setColorAt(0.0, QColor("#5B8BFF"))
    gradient.setColorAt(1.0, QColor("#2E5BDC"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(gradient)
    radius = s * 0.22
    painter.drawRoundedRect(QRectF(0, 0, s, s), radius, radius)

    # 白色圆角播放三角：实心填充 + 同色圆角描边，使三个顶点圆润
    unit = s / 256.0
    tri = QPolygonF([
        QPointF(104 * unit, 74 * unit),
        QPointF(104 * unit, 182 * unit),
        QPointF(196 * unit, 128 * unit),
    ])
    pen_width = 22 * unit
    pen = QPen(QColor("#FFFFFF"), pen_width)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(QColor("#FFFFFF"))
    painter.drawPolygon(tri)


def app_pixmap(size: int) -> QPixmap:
    """生成指定尺寸的品牌 QPixmap"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    _draw_mark(painter, size)
    painter.end()
    return pixmap


def create_app_icon() -> QIcon:
    """生成多尺寸应用图标"""
    icon = QIcon()
    for size in _SIZES:
        icon.addPixmap(app_pixmap(size), QIcon.Mode.Normal, QIcon.State.Off)
    return icon


def brand_mark_pixmap(size: int = 30) -> QPixmap:
    """侧边栏品牌方块专用（含标识）"""
    return app_pixmap(size)
