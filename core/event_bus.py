"""
全局事件总线。

使用 Qt Signal 实现模块间解耦通信。
"""
from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal


class EventBus(QObject):
    """全局事件总线（单例）"""
    
    _instance = None
    
    # 任务相关事件
    task_created = pyqtSignal(str)  # task_id
    task_updated = pyqtSignal(str, str)  # task_id, status
    task_succeeded = pyqtSignal(str, str)  # task_id, video_url
    task_failed = pyqtSignal(str, str)  # task_id, error_msg
    
    # 设置相关事件
    settings_changed = pyqtSignal()
    
    # 错误事件
    error_occurred = pyqtSignal(str, str)  # error_code, message
    
    # 资产库相关事件（P4 阶段使用）
    asset_uploaded = pyqtSignal(str)  # asset_id
    asset_approved = pyqtSignal(str)  # asset_id
    asset_rejected = pyqtSignal(str, str)  # asset_id, reason

    # 主题相关事件
    theme_changed = pyqtSignal(str)  # theme_id (e.g. "default_light", "marathon")

    # 通知/Toast 事件 (P9)
    toast_requested = pyqtSignal(str, str, str)  # type, title, message
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def instance(cls) -> EventBus:
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
