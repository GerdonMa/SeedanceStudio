"""
Seedance Studio 程序入口。

初始化 DI 容器，启动 Qt 应用程序。
"""
from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from core.di_container import Container
from themes import ThemeRegistry
from themes.theme_loader import ThemeLoader
from ui.main_window import MainWindow


def main():
    """程序入口函数"""
    try:
        # 初始化依赖注入容器
        container = Container()
        
        # 初始化主题系统（必须在创建 MainWindow 之前）
        loader = ThemeLoader(container.logger)
        for theme in loader.discover_all():
            ThemeRegistry.register(theme)
        container.logger.info(f"Theme system: {len(ThemeRegistry.list_all())} themes loaded")
        
        # 创建 Qt 应用
        app = QApplication(sys.argv)
        app.setApplicationName("Seedance Studio")
        app.setOrganizationName("SeedanceStudio")

        # 设置应用图标
        icon_path = Path(__file__).parent / "assets" / "icons" / "app.ico"
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))

        # 创建主窗口
        window = MainWindow(container)
        
        # 恢复窗口状态
        prefs = container.settings_usecase.load_preferences()
        width = prefs.get("window_width", 1200)
        height = prefs.get("window_height", 800)
        x = prefs.get("window_x", -1)
        y = prefs.get("window_y", -1)
        
        window.resize(width, height)
        if x >= 0 and y >= 0:
            window.move(x, y)
        
        window.show()
        
        container.logger.info("Application started successfully")
        
        # 运行应用
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
