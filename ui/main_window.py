"""
主窗口。

整合所有页面，提供导航和全局功能。
P9: 支持无边框窗口、Toast 通知、快捷键。
"""
from __future__ import annotations

import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QPushButton, QLabel, QApplication,
)
from PyQt6.QtCore import Qt, QEvent, QPoint, QSize
from PyQt6.QtGui import QShortcut, QKeySequence

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

from core.di_container import Container
from ui.pages.page_create import CreatePage
from ui.pages.page_settings import SettingsPage
from ui.pages.page_task_list import TaskListPage
from ui.title_bar import TitleBar
from ui.widgets.toast_widget import ToastWidget
from ui.widgets.about_dialog import show_about_dialog
from ui.widgets import pro_icons
from themes import ThemeRegistry
from themes.theme_context import ThemeContext
from themes.theme_loader import ThemeLoader


class MainWindow(QMainWindow):
    """主窗口"""

    SIDEBAR_EXPANDED = 232

    def __init__(self, container: Container, use_frameless: bool = True):
        super().__init__()
        self._container = container
        self._sidebar: QWidget | None = None
        self._title_bar: TitleBar | None = None
        self._use_frameless = use_frameless
        self._task_badge: QLabel | None = None

        # 主题系统初始化
        if not ThemeRegistry.list_all():
            loader = ThemeLoader(container.logger)
            for theme in loader.discover_all():
                ThemeRegistry.register(theme)

        if self._use_frameless:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self._init_ui()
        self._setup_shortcuts()
        self._subscribe_events()
        self._apply_theme_from_prefs()
        self._refresh_task_badge()

    # ---- UI 初始化 ----

    def _init_ui(self):
        self.setWindowTitle("Seedance Studio")
        self.setMinimumSize(1000, 640)

        # 根容器：标题栏（overlay）+ 中心部件
        root = QWidget()
        root.setObjectName("mainRoot")
        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 自定义标题栏（无边框模式下 overlay 到顶部）
        if self._use_frameless:
            self._title_bar = TitleBar(self, "Seedance Studio")
            root_layout.addWidget(self._title_bar)

        # 中心部件
        central = QWidget()
        central.setObjectName("centralWidget")
        central_layout = QHBoxLayout()
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)

        self._sidebar = self._create_sidebar()
        central_layout.addWidget(self._sidebar)

        self._pages = QStackedWidget()
        self._pages.setObjectName("contentArea")
        self._pages.addWidget(CreatePage(self._container))     # 索引 0：创建工作台
        self._pages.addWidget(TaskListPage(self._container))   # 索引 1：任务中心
        self._pages.addWidget(SettingsPage(self._container))   # 索引 2：设置
        central_layout.addWidget(self._pages, 1)

        central.setLayout(central_layout)
        root_layout.addWidget(central, 1)
        root.setLayout(root_layout)
        self.setCentralWidget(root)

        # Toast 容器
        self._toast_widget = ToastWidget(self._container, self)
        self._toast_widget.hide()

        self._switch_page(0)

    def _create_sidebar(self) -> QWidget:
        """专业导航侧边栏：品牌区 + 分组导航 + 任务计数徽章"""
        sidebar = QWidget()
        sidebar.setFixedWidth(self.SIDEBAR_EXPANDED)
        sidebar.setObjectName("sidebar")

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 12, 10, 10)
        layout.setSpacing(0)

        # --- 品牌区：标识方块 + 产品名 ---
        brand_row = QHBoxLayout()
        brand_row.setSpacing(10)

        mark = QWidget()
        mark.setObjectName("brandMark")
        mark.setFixedSize(30, 30)
        mark_text = QLabel("S")
        mark_text.setObjectName("brandMarkText")
        mark_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mark_layout = QVBoxLayout(mark)
        mark_layout.setContentsMargins(0, 0, 0, 0)
        mark_layout.addWidget(mark_text)
        brand_row.addWidget(mark)

        brand_texts = QVBoxLayout()
        brand_texts.setContentsMargins(0, 0, 0, 0)
        brand_texts.setSpacing(0)
        brand_name = QLabel("Seedance Studio")
        brand_name.setObjectName("brandName")
        brand_sub = QLabel("VIDEO GENERATION")
        brand_sub.setObjectName("brandSub")
        brand_texts.addWidget(brand_name)
        brand_texts.addWidget(brand_sub)
        brand_row.addLayout(brand_texts)
        brand_row.addStretch()

        layout.addLayout(brand_row)

        # --- 导航按钮 ---
        # 顺序必须与 _pages.addWidget 一致（pitfall #14）
        self._nav_buttons = []

        nav_label_1 = QLabel("工作区")
        nav_label_1.setObjectName("navLabel")
        layout.addWidget(nav_label_1)

        create_btn = QPushButton("  创建工作台")
        create_btn.setIcon(pro_icons.create_icon())
        create_btn.setIconSize(QSize(18, 18))
        create_btn.setCheckable(True)
        create_btn.clicked.connect(lambda checked: self._switch_page(0))
        self._nav_buttons.append(create_btn)
        layout.addWidget(create_btn)

        # 任务行：按钮 + 运行中计数徽章
        task_row = QHBoxLayout()
        task_row.setContentsMargins(0, 0, 6, 0)
        task_row.setSpacing(6)
        tasks_btn = QPushButton("  任务中心")
        tasks_btn.setIcon(pro_icons.tasks_icon())
        tasks_btn.setIconSize(QSize(18, 18))
        tasks_btn.setCheckable(True)
        tasks_btn.clicked.connect(lambda checked: self._switch_page(1))
        self._nav_buttons.append(tasks_btn)
        task_row.addWidget(tasks_btn, 1)

        self._task_badge = QLabel("")
        self._task_badge.setObjectName("navBadge")
        self._task_badge.setProperty("active", True)
        self._task_badge.hide()
        task_row.addWidget(self._task_badge)
        layout.addLayout(task_row)

        nav_label_2 = QLabel("系统")
        nav_label_2.setObjectName("navLabel")
        layout.addWidget(nav_label_2)

        settings_btn = QPushButton("  设置")
        settings_btn.setIcon(pro_icons.settings_icon())
        settings_btn.setIconSize(QSize(18, 18))
        settings_btn.setCheckable(True)
        settings_btn.clicked.connect(lambda checked: self._switch_page(2))
        self._nav_buttons.append(settings_btn)
        layout.addWidget(settings_btn)

        layout.addStretch()

        # --- 底部：关于 ---
        about_btn = QPushButton("  关于 Seedance")
        about_btn.setObjectName("aboutBtn")
        about_btn.setIcon(pro_icons.about_icon())
        about_btn.setIconSize(QSize(16, 16))
        about_btn.clicked.connect(lambda: show_about_dialog(self))
        layout.addWidget(about_btn)

        sidebar.setLayout(layout)
        return sidebar

    def _refresh_task_badge(self):
        """刷新侧边栏运行中任务计数徽章"""
        if self._task_badge is None:
            return
        try:
            tasks = self._container.task_usecase.find_all_tasks()
            active = sum(
                1 for t in tasks
                if t.status.value in ("queued", "pending", "running")
            )
            if active > 0:
                self._task_badge.setText(str(active))
                self._task_badge.show()
            else:
                self._task_badge.hide()
        except Exception as e:
            self._container.logger.warning(f"Failed to refresh task badge: {e}")
            self._task_badge.hide()

    def _setup_shortcuts(self):
        # Ctrl+1/2/3 切换页面 (setAutoRepeat(False) 防止重复触发，pitfall #28)
        for i in range(3):
            sc = QShortcut(QKeySequence(f"Ctrl+{i+1}"), self)
            sc.setAutoRepeat(False)
            sc.activated.connect(lambda idx=i: self._switch_page(idx))

        # Escape 关闭 Toast
        esc = QShortcut(QKeySequence("Escape"), self)
        esc.activated.connect(self._on_escape)

    # ---- 事件订阅 ----

    def _subscribe_events(self):
        eb = self._container.event_bus
        eb.theme_changed.connect(self._on_theme_changed)
        eb.toast_requested.connect(self._on_toast_requested)
        eb.page_switch_requested.connect(self._switch_page)
        # 任务状态变化时刷新侧边栏运行中计数
        eb.task_created.connect(lambda _id: self._refresh_task_badge())
        eb.task_updated.connect(lambda _id, _s: self._refresh_task_badge())
        eb.task_succeeded.connect(lambda _id, _u: self._refresh_task_badge())
        eb.task_failed.connect(lambda _id, _e: self._refresh_task_badge())

    # ---- 主题 ----

    def _apply_theme_from_prefs(self):
        prefs = self._container.settings_usecase.load_preferences()
        theme_id = prefs.get("ui_theme")
        if theme_id not in ThemeRegistry.registered_ids():
            # 未配置 / 旧版本已删除的主题（default_*/marathon）→ 迁移到默认主题
            theme_id = ThemeRegistry.default_id()
            self._container.settings_usecase.save_preference("ui_theme", theme_id)
        self._apply_theme(theme_id)

    def _apply_theme(self, theme_id: str):
        try:
            if theme_id not in ThemeRegistry.registered_ids():
                raise ValueError(f"Theme '{theme_id}' not found")

            theme = ThemeRegistry.get(theme_id)
            ThemeContext.set_current(theme_id)

            app = QApplication.instance()
            if app:
                app.setStyleSheet(theme.qss)
            if self._sidebar is not None:
                self._sidebar.setStyleSheet(theme.sidebar_qss)

            for i in range(self._pages.count()):
                page = self._pages.widget(i)
                if hasattr(page, 'on_theme_changed'):
                    page.on_theme_changed()

            if hasattr(self, '_toast_widget') and hasattr(self._toast_widget, 'on_theme_changed'):
                self._toast_widget.on_theme_changed()

            if theme.fx_module is not None:
                try:
                    theme.fx_module.on_theme_activated(self)
                except Exception as e:
                    self._container.logger.warning(f"Theme activation hook failed: {e}")

            self._container.logger.info(f"Theme switched to: {theme_id}")

        except Exception as e:
            self._container.logger.error(f"Failed to apply theme '{theme_id}': {e}")
            fallback = ThemeRegistry.default_id()
            if theme_id != fallback:
                self._container.logger.info(f"Falling back to {fallback} theme")
                self._apply_theme(fallback)
            else:
                self._container.logger.critical(f"Failed to load {fallback} theme, UI may be broken")

    def _on_theme_changed(self, theme_id: str):
        try:
            self._apply_theme(theme_id)
            theme = ThemeRegistry.get(theme_id)
            theme_name = theme.name if theme else theme_id
            self._container.event_bus.toast_requested.emit(
                "success", "主题已切换", f"当前主题：{theme_name}"
            )
        except Exception as e:
            self._container.event_bus.toast_requested.emit(
                "error", "主题切换失败", str(e)
            )

    # ---- 页面切换 ----

    def _switch_page(self, index: int):
        self._pages.setCurrentIndex(index)
        for i, btn in enumerate(self._nav_buttons):
            btn.setChecked(i == index)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, '_toast_widget') and self._toast_widget.isVisible():
            self._toast_widget._layout_toasts()

    # ---- Toast 通知 ----

    def _on_toast_requested(self, type_: str, title: str, message: str):
        self._toast_widget.show_toast(type_, title, message)

    def _on_escape(self):
        """Escape 键关闭当前 Toast/弹窗"""
        if self._toast_widget.isVisible():
            self._toast_widget.dismiss_all()

    # ---- 生命周期 ----

    def closeEvent(self, event):
        prefs = self._container.settings_usecase
        maximized = self.isMaximized()
        prefs.save_preference("window_maximized", maximized)
        # 最大化时用 normalGeometry 保存恢复后的尺寸
        if maximized:
            geo = self.normalGeometry()
            prefs.save_preference("window_width", geo.width())
            prefs.save_preference("window_height", geo.height())
            prefs.save_preference("window_x", geo.x())
            prefs.save_preference("window_y", geo.y())
        else:
            prefs.save_preference("window_width", self.width())
            prefs.save_preference("window_height", self.height())
            prefs.save_preference("window_x", self.x())
            prefs.save_preference("window_y", self.y())
        super().closeEvent(event)

    def changeEvent(self, event):
        """窗口状态变更（最大化/还原）"""
        super().changeEvent(event)
        if event.type() == QEvent.Type.WindowStateChange and self._title_bar is not None:
            self._title_bar.set_maximized(self.isMaximized())

    def nativeEvent(self, eventType, message):
        """Windows 原生事件：启用无边框窗口的边缘拖拽缩放。

        仅对窗口边缘返回 resize hit code。
        标题栏区域交由 TitleBar 自身的 mousePressEvent/mouseMoveEvent 处理拖拽，
        避免 HTCAPTION 导致 Windows 接管 Qt 按钮渲染和鼠标事件。
        """
        if not self._use_frameless or sys.platform != "win32":
            return False, 0

        try:
            msg = wintypes.MSG.from_address(int(message))
        except Exception:
            return False, 0

        # WM_NCHITTEST
        if msg.message != 0x0084:
            return False, 0

        x = ctypes.c_int16(msg.lParam & 0xFFFF).value
        y = ctypes.c_int16(msg.lParam >> 16).value
        pt = self.mapFromGlobal(QPoint(x, y))

        # 边缘缩放检测（仅窗口边缘 border px 范围）
        border = 5
        left = pt.x() < border
        right = pt.x() > self.width() - border
        top = pt.y() < border
        bottom = pt.y() > self.height() - border

        if top and left:
            return True, 13  # HTTOPLEFT
        if top and right:
            return True, 14  # HTTOPRIGHT
        if bottom and left:
            return True, 16  # HTBOTTOMLEFT
        if bottom and right:
            return True, 17  # HTBOTTOMRIGHT
        if top:
            return True, 12  # HTTOP
        if bottom:
            return True, 15  # HTBOTTOM
        if left:
            return True, 10  # HTLEFT
        if right:
            return True, 11  # HTRIGHT

        return False, 0

