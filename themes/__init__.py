"""
主题系统核心模块。

提供 ThemeInfo 数据结构、ThemeRegistry 注册表。
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import ClassVar, Any


@dataclass(frozen=True)
class ThemeInfo:
    """主题元数据"""
    id: str                                    # 唯一标识，如 "default_light"
    name: str                                  # 显示名称，如 "默认浅色"
    qss: str                                   # 全局 QSS 样式表
    sidebar_qss: str                           # 侧边栏 QSS 样式表
    is_dark: bool                              # 是否为深色主题
    manifest: dict = field(default_factory=dict)  # 原始 manifest 数据
    fx_module: Any | None = None               # 动效模块引用（可选）


class ThemeRegistry:
    """
    主题注册表（类方法模式，一致性对齐 TaskBuilderFactory）。

    内置主题在 themes/builtin/ 中，第三方主题在 themes/community/ 中。
    通过 ThemeLoader.discover_all() 扫描后注册。
    """

    _themes: ClassVar[dict[str, ThemeInfo]] = {}
    _default_id: ClassVar[str] = "graphite"

    @classmethod
    def register(cls, theme: ThemeInfo) -> None:
        """注册一个主题。同名 ID 会被覆盖（后加载优先）"""
        if theme.id in cls._themes:
            existing = cls._themes[theme.id]
            # 优先使用后加载的主题
            cls._themes[theme.id] = theme
        else:
            cls._themes[theme.id] = theme

    @classmethod
    def get(cls, theme_id: str) -> ThemeInfo:
        """获取指定主题。不存在时安全回退到默认主题"""
        return cls._themes.get(theme_id, cls._themes[cls._default_id])

    @classmethod
    def list_all(cls) -> list[ThemeInfo]:
        """列出所有已注册的主题"""
        return list(cls._themes.values())

    @classmethod
    def registered_ids(cls) -> list[str]:
        """列出所有已注册的主题 ID"""
        return list(cls._themes.keys())

    @classmethod
    def unregister(cls, theme_id: str) -> bool:
        """卸载主题。内置默认主题不可卸载"""
        if theme_id == cls._default_id:
            return False
        if theme_id in cls._themes:
            del cls._themes[theme_id]
            return True
        return False

    @classmethod
    def default_id(cls) -> str:
        """默认主题 ID"""
        return cls._default_id
