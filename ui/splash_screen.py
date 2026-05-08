"""
启动画面。

居中无边框窗口，显示应用名称和版本号。
主窗口加载完成后自动关闭。
"""
from __future__ import annotations

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtGui import QFont

APP_NAME = "Seedance Studio"
APP_VERSION = "v1.2.1"


class SplashScreen(QWidget):
    """启动画面"""

    def __init__(self):
        super().__init__()
        self._close_anim = None

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.SplashScreen
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(360, 200)

        self._init_ui()

        # 居中
        screen = self.screen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 名称
        title = QLabel(APP_NAME)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("splashTitle")
        layout.addWidget(title)

        layout.addSpacing(8)

        # 版本号
        version = QLabel(APP_VERSION)
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setObjectName("splashVersion")
        layout.addWidget(version)

        layout.addSpacing(16)

        # 加载提示
        loading = QLabel("正在加载...")
        loading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading.setObjectName("splashLoading")
        layout.addWidget(loading)

        self.setLayout(layout)

        self.setObjectName("splashScreen")

    def close(self):
        """淡出后关闭（保持动画引用防止 GC 回收）"""
        if self._close_anim is not None:
            return  # 已经在关闭中

        self._opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity)

        self._close_anim = QPropertyAnimation(self._opacity, b"opacity")
        self._close_anim.setDuration(400)
        self._close_anim.setStartValue(1.0)
        self._close_anim.setEndValue(0.0)
        self._close_anim.setEasingCurve(QEasingCurve.Type.InCubic)
        self._close_anim.finished.connect(self._force_close)
        self._close_anim.start()

    def _force_close(self):
        """动画完成后强制关闭"""
        super().close()
