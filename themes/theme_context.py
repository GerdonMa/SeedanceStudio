"""
主题上下文管理器。

提供运行时主题变量访问，支持动态主题切换。
通过类变量存储当前主题状态，避免创建实例的开销。
"""
from __future__ import annotations

from typing import ClassVar


class ThemeContext:
    """
    主题上下文单例（类方法模式）。

    管理当前活跃主题的 ID，并提供颜色变量查询。
    MainWindow._apply_theme() 在切换主题时调用 set_current()，
    组件通过 get_color() 获取当前主题的颜色值。
    """

    _current_theme_id: ClassVar[str] = "graphite"

    @classmethod
    def set_current(cls, theme_id: str) -> None:
        """设置当前活跃主题 ID"""
        cls._current_theme_id = theme_id

    @classmethod
    def get_current(cls) -> str:
        """获取当前活跃主题 ID"""
        return cls._current_theme_id

    @classmethod
    def get_color(cls, key: str, fallback: str = "#000000") -> str:
        """
        从当前主题的 manifest.colors 字段获取颜色值。

        Args:
            key: 颜色变量名（如 "primary", "text_primary"）
            fallback: 主题不存在或缺少该颜色时的回退值

        Returns:
            颜色十六进制字符串（如 "#00E5FF"）
        """
        from themes import ThemeRegistry
        theme = ThemeRegistry.get(cls._current_theme_id)
        if theme is None:
            return fallback
        colors = theme.manifest.get("colors", {})
        return colors.get(key, fallback)

    @classmethod
    def is_dark(cls) -> bool:
        """判断当前主题是否为深色主题"""
        from themes import ThemeRegistry
        theme = ThemeRegistry.get(cls._current_theme_id)
        if theme is None:
            return False
        return theme.is_dark
