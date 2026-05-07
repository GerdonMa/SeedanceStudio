"""
主窗口。

整合所有页面，提供导航和全局功能。
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QPushButton, QLabel, QApplication
)
from PyQt6.QtCore import Qt

from core.di_container import Container
from ui.pages.page_create import CreatePage
from ui.pages.page_settings import SettingsPage
from ui.pages.page_task_list import TaskListPage
from themes import ThemeRegistry
from themes.theme_loader import ThemeLoader


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self, container: Container):
        super().__init__()
        self._container = container
        self._sidebar: QWidget | None = None
        
        # 初始化主题系统（确保运行时已有主题注册）
        if not ThemeRegistry.list_all():
            loader = ThemeLoader(container.logger)
            for theme in loader.discover_all():
                ThemeRegistry.register(theme)
        
        self._init_ui()
        self._subscribe_events()
        self._apply_theme_from_prefs()

    def _init_ui(self):
        """初始化 UI"""
        self.setWindowTitle("Seedance Studio")
        self.setMinimumSize(900, 600)

        # 中心部件
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 侧边栏
        self._sidebar = self._create_sidebar()
        layout.addWidget(self._sidebar)

        # 页面容器
        self._pages = QStackedWidget()
        self._pages.setObjectName("contentArea")
        self._pages.addWidget(CreatePage(self._container))  # 索引 0
        self._pages.addWidget(SettingsPage(self._container))  # 索引 1
        self._pages.addWidget(TaskListPage(self._container))  # 索引 2
        layout.addWidget(self._pages, 1)

        central.setLayout(layout)

        # 恢复窗口位置和大小
        self._restore_window_geometry()

        self._switch_page(0)

    def _create_sidebar(self) -> QWidget:
        """创建侧边栏"""
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setObjectName("sidebar")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 20, 0, 0)
        layout.setSpacing(0)

        # 标题
        title = QLabel("Seedance Studio")
        title.setObjectName("appTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # 导航按钮
        self._nav_buttons = []

        btn_create = QPushButton("创建视频")
        btn_create.setCheckable(True)
        btn_create.clicked.connect(lambda: self._switch_page(0))
        self._nav_buttons.append(btn_create)
        layout.addWidget(btn_create)

        btn_settings = QPushButton("设置")
        btn_settings.setCheckable(True)
        btn_settings.clicked.connect(lambda: self._switch_page(1))
        self._nav_buttons.append(btn_settings)
        layout.addWidget(btn_settings)

        btn_tasks = QPushButton("任务列表")
        btn_tasks.setCheckable(True)
        btn_tasks.clicked.connect(lambda: self._switch_page(2))
        self._nav_buttons.append(btn_tasks)
        layout.addWidget(btn_tasks)

        layout.addStretch()

        sidebar.setLayout(layout)
        return sidebar

    def _subscribe_events(self):
        """订阅事件总线"""
        eb = self._container.event_bus
        eb.theme_changed.connect(self._on_theme_changed)

    def _apply_theme_from_prefs(self):
        """从偏好设置恢复主题（含旧版 dark_mode 迁移）"""
        prefs = self._container.settings_usecase.load_preferences()
        theme_id = prefs.get("ui_theme")
        if not theme_id:
            dark = prefs.get("dark_mode", False)
            theme_id = "default_dark" if dark else "default_light"
            self._container.settings_usecase.save_preference("ui_theme", theme_id)
        self._apply_theme(theme_id)

    def _apply_theme(self, theme_id: str):
        """应用主题样式表"""
        theme = ThemeRegistry.get(theme_id)

        app = QApplication.instance()
        if app:
            app.setStyleSheet(theme.qss)
        if self._sidebar is not None:
            self._sidebar.setStyleSheet(theme.sidebar_qss)

    def _on_theme_changed(self, theme_id: str):
        """主题变更事件处理"""
        self._apply_theme(theme_id)
        # Marathon 主题切换时执行淡入动效
        theme = ThemeRegistry.get(theme_id)
        if theme.fx_module is not None:
            try:
                theme.fx_module.on_theme_activated(self)
            except Exception:
                pass

    def _switch_page(self, index: int):
        """切换页面"""
        self._pages.setCurrentIndex(index)
        for i, btn in enumerate(self._nav_buttons):
            btn.setChecked(i == index)

    def _restore_window_geometry(self):
        """从偏好设置恢复窗口位置和大小"""
        prefs = self._container.settings_usecase.load_preferences()
        width = prefs.get("window_width", 1200)
        height = prefs.get("window_height", 800)
        x = prefs.get("window_x", -1)
        y = prefs.get("window_y", -1)
        self.resize(width, height)
        if x >= 0 and y >= 0:
            self.move(x, y)

    def closeEvent(self, event):
        """关闭窗口时保存位置和大小"""
        prefs = self._container.settings_usecase
        prefs.save_preference("window_width", self.width())
        prefs.save_preference("window_height", self.height())
        prefs.save_preference("window_x", self.x())
        prefs.save_preference("window_y", self.y())
        super().closeEvent(event)
