"""
设置用例。

处理配置管理、偏好持久化、API 连通性测试等业务逻辑。
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from domain.interfaces import IApiClient
from core.event_bus import EventBus

if TYPE_CHECKING:
    from infrastructure.config_store import ConfigStore


class SettingsUseCase:
    """设置用例"""
    
    def __init__(self, config: ConfigStore, event_bus: EventBus, logger: logging.Logger, api_client: IApiClient | None = None):
        self._config = config
        self._event_bus = event_bus
        self._logger = logger
        self._api_client = api_client
    
    def save_preference(self, key: str, value) -> None:
        """
        保存偏好设置。
        
        Args:
            key: 配置项键名
            value: 配置项值
        Raises:
            StorageError: 保存失败
        """
        self._config.set(key, value)
        self._event_bus.settings_changed.emit()
    
    def load_preferences(self) -> dict:
        """
        加载所有偏好设置。
        
        Returns:
            配置字典
        """
        return self._config.get_all()
    
    def get_preference(self, key: str, default=None):
        """
        获取单个偏好设置。
        
        Args:
            key: 配置项键名
            default: 默认值
        Returns:
            配置项值
        """
        return self._config.get(key, default)
    
    def test_connection(self) -> tuple[bool, str]:
        """
        测试 API 连通性。
        
        Returns:
            (是否成功, 消息)
        """
        if self._api_client is None:
            api_key = self._config.get("api_key")
            if not api_key:
                return False, "API Key 未配置"
            return False, "API 客户端未初始化"
        
        return self._api_client.test_connection()
