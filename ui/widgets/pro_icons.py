"""
专业线性图标集（Graphite 工作台配套）。

QPainter 绘制的 18px 线性图标：1.4px 描边、圆角端点、无填充。
颜色默认使用次级文字色，深浅主题下均可见。
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPainter, QPen, QColor, QIcon, QPixmap

_SIZE = 18
_STROKE = 1.4
_DEFAULT_COLOR = "#98A0B0"


def _canvas(size: int, color: str):
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(QColor(color), _STROKE)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.GlobalColor.transparent)
    return pixmap, painter


def _icon(draw_fn, color: str, size: int) -> QIcon:
    pixmap, painter = _canvas(size, color)
    draw_fn(painter, size)
    painter.end()
    return QIcon(pixmap)


def _line(p, x1, y1, x2, y2):
    p.drawLine(QPointF(x1, y1), QPointF(x2, y2))


# ── 各图标绘制函数 ──────────────────────────────────────────────

def _draw_create(p, s):
    """创建：胶片框 + 中央加号"""
    p.drawRoundedRect(QRectF(1.5, 3.5, s - 3, s - 7), 2, 2)
    _line(p, s / 2, 6.5, s / 2, s - 6.5)
    _line(p, s / 2 - 4, (6.5 + s - 6.5) / 2, s / 2 + 4, (6.5 + s - 6.5) / 2)


def _draw_tasks(p, s):
    """任务：三行列表 + 状态点"""
    for i, y in enumerate((4.5, s / 2, s - 4.5)):
        _line(p, 6, y, s - 3, y)
    p.drawEllipse(QPointF(3.2, 4.5), 1.4, 1.4)
    p.drawEllipse(QPointF(3.2, s / 2), 1.4, 1.4)
    p.drawEllipse(QPointF(3.2, s - 4.5), 1.4, 1.4)


def _draw_settings(p, s):
    """设置：齿轮（简化：圆 + 齿）"""
    c = QPointF(s / 2, s / 2)
    p.drawEllipse(c, 3.2, 3.2)
    import math
    for i in range(8):
        ang = math.pi / 4 * i
        x1 = c.x() + 4.6 * math.cos(ang)
        y1 = c.y() + 4.6 * math.sin(ang)
        x2 = c.x() + 6.6 * math.cos(ang)
        y2 = c.y() + 6.6 * math.sin(ang)
        _line(p, x1, y1, x2, y2)


def _draw_about(p, s):
    """关于：圆 + i"""
    p.drawEllipse(QPointF(s / 2, s / 2), s / 2 - 1.5, s / 2 - 1.5)
    _line(p, s / 2, 5.5, s / 2, 10.5)
    p.drawPoint(QPointF(s / 2, 13))


def _draw_refresh(p, s):
    """刷新：循环箭头"""
    p.drawArc(3, 3, s - 6, s - 6, 60 * 16, 260 * 16)
    _line(p, s - 4.5, 5.5, s - 4.5, 9.5)
    _line(p, s - 4.5, 5.5, s - 8.5, 5.5)


def _draw_sync(p, s):
    """同步：云 + 下载箭头"""
    p.drawArc(4, 5, 6, 6, 0, 180 * 16)
    _line(p, 7, 6, 11, 6)
    p.drawArc(8, 3, 7, 7, 90 * 16, 180 * 16)
    _line(p, s / 2 + 1, 8, s / 2 + 1, 13.5)
    _line(p, s / 2 - 2, 11, s / 2 + 1, 14)
    _line(p, s / 2 + 4, 11, s / 2 + 1, 14)


def _draw_sparkle(p, s):
    """提示词助手：四角星"""
    c = QPointF(s / 2, s / 2)
    pts = [
        (c.x(), 2), (c.x() + 2.2, c.y() - 2.2), (s - 2, c.y()),
        (c.x() + 2.2, c.y() + 2.2), (c.x(), s - 2), (c.x() - 2.2, c.y() + 2.2),
        (2, c.y()), (c.x() - 2.2, c.y() - 2.2),
    ]
    from PyQt6.QtGui import QPolygonF
    poly = QPolygonF([QPointF(x, y) for x, y in pts])
    p.drawPolygon(poly)


def _draw_layers(p, s):
    """多模态素材：三层叠加"""
    _line(p, s / 2, 2.5, s - 2.5, 6)
    _line(p, s / 2, 2.5, 2.5, 6)
    _line(p, 2.5, 6, s / 2, 9.5)
    _line(p, s / 2, 9.5, s - 2.5, 6)
    _line(p, 2.5, 10, s / 2, 13.5)
    _line(p, s / 2, 13.5, s - 2.5, 10)
    _line(p, 2.5, 13.8, s / 2, 16.8)
    _line(p, s / 2, 16.8, s - 2.5, 13.8)


def _draw_play(p, s):
    """播放：实心圆角三角"""
    from PyQt6.QtGui import QPolygonF
    pen = QPen(p.pen())
    pen.setWidthF(_STROKE * 2.6)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    old_pen = p.pen()
    p.setPen(pen)
    p.setBrush(pen.color())
    tri = QPolygonF([QPointF(6.5, 4), QPointF(6.5, 14), QPointF(15, 9)])
    p.drawPolygon(tri)
    p.setPen(old_pen)
    p.setBrush(Qt.GlobalColor.transparent)


def _draw_pause(p, s):
    """暂停：双竖条"""
    w = _STROKE * 2.2
    p.setBrush(p.pen().color())
    p.drawRoundedRect(QRectF(5, 4, w, 10), w / 2, w / 2)
    p.drawRoundedRect(QRectF(12 - w / 2 + 1, 4, w, 10), w / 2, w / 2)
    p.setBrush(Qt.GlobalColor.transparent)


# ── 对外接口 ────────────────────────────────────────────────────

def play_icon(color: str = _DEFAULT_COLOR, size: int = _SIZE) -> QIcon:
    return _icon(_draw_play, color, size)


def pause_icon(color: str = _DEFAULT_COLOR, size: int = _SIZE) -> QIcon:
    return _icon(_draw_pause, color, size)


def create_icon(color: str = _DEFAULT_COLOR, size: int = _SIZE) -> QIcon:
    return _icon(_draw_create, color, size)


def tasks_icon(color: str = _DEFAULT_COLOR, size: int = _SIZE) -> QIcon:
    return _icon(_draw_tasks, color, size)


def settings_icon(color: str = _DEFAULT_COLOR, size: int = _SIZE) -> QIcon:
    return _icon(_draw_settings, color, size)


def about_icon(color: str = _DEFAULT_COLOR, size: int = _SIZE) -> QIcon:
    return _icon(_draw_about, color, size)


def refresh_icon(color: str = _DEFAULT_COLOR, size: int = _SIZE) -> QIcon:
    return _icon(_draw_refresh, color, size)


def sync_icon(color: str = _DEFAULT_COLOR, size: int = _SIZE) -> QIcon:
    return _icon(_draw_sync, color, size)


def sparkle_icon(color: str = _DEFAULT_COLOR, size: int = _SIZE) -> QIcon:
    return _icon(_draw_sparkle, color, size)


def layers_icon(color: str = _DEFAULT_COLOR, size: int = _SIZE) -> QIcon:
    return _icon(_draw_layers, color, size)
