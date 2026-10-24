"""
Seedance Studio 程序入口。

初始化 DI 容器，启动 Qt 应用程序。
P9: 支持 --no-frameless 回退参数、启动画面。
"""
from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from core.di_container import Container
from themes import ThemeRegistry
from themes.theme_loader import ThemeLoader
from ui.main_window import MainWindow
from ui.splash_screen import SplashScreen


def main():
    """程序入口函数"""
    try:
        use_frameless = False  # 使用系统默认标题栏

        # 1. 先创建 QApplication（必须在任何 QObject 之前）
        app = QApplication(sys.argv)
        app.setApplicationName("Seedance Studio")
        app.setOrganizationName("SeedanceStudio")

        # 2. 启动画面（第一时间显示）
        splash = SplashScreen()
        splash.show()
        app.processEvents()

        # 3. 初始化依赖注入容器（QApplication 已就绪）
        container = Container()

        # 4. 初始化主题系统
        loader = ThemeLoader(container.logger)
        for theme in loader.discover_all():
            ThemeRegistry.register(theme)
        container.logger.info(
            f"Theme system: {len(ThemeRegistry.list_all())} themes loaded"
        )

        # 5. 设置应用图标（程序化品牌图标，与主题品牌区同语言；打包环境回退 app.ico）
        from ui.widgets.app_icon import create_app_icon
        icon = create_app_icon()
        app.setWindowIcon(icon)

        # 6. 创建主窗口
        window = MainWindow(container, use_frameless=use_frameless)

        # 7. 恢复窗口状态
        prefs = container.settings_usecase.load_preferences()
        width = prefs.get("window_width", 1200)
        height = prefs.get("window_height", 800)
        x = prefs.get("window_x", -1)
        y = prefs.get("window_y", -1)
        maximized = prefs.get("window_maximized", False)

        window.resize(width, height)
        if x >= 0 and y >= 0:
            window.move(x, y)

        # 8. 主窗口就绪，延迟显示以完成 splash 过渡动画
        QTimer.singleShot(300, lambda: _show_main_window(splash, window, icon, maximized))

        container.logger.info("Application started successfully")

        # 9. 事件循环
        sys.exit(app.exec())

    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        # 确保启动画面被关闭（如果已创建）
        try:
            if 'splash' in locals() and splash is not None:
                splash._force_close()
        except Exception:
            pass
        sys.exit(1)


def _show_main_window(splash: SplashScreen, window: MainWindow, icon, maximized: bool):
    """显示主窗口并关闭启动画面"""
    if maximized:
        window.showMaximized()
    else:
        window.show()

    # 设置标题栏图标
    if window._title_bar is not None and icon is not None:
        for size in [16, 24, 32]:
            window._title_bar.set_icon(icon.pixmap(size, size))

    splash.close()


if __name__ == "__main__":
    main()
