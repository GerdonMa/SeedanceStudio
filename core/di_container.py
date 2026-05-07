"""
依赖注入容器。

在程序入口统一组装各层依赖，避免模块间硬编码依赖关系。
"""
from __future__ import annotations

import logging

from PyQt6.QtCore import Qt

from core.logger import setup_logger
from core.event_bus import EventBus
from core.polling_worker import PollingWorker
from core.asset_polling_worker import AssetPollingWorker
from infrastructure.config_store import ConfigStore
from infrastructure.ark_api_client import ArkApiClient
from infrastructure.ark_asset_client import ArkAssetClient
from infrastructure.file_storage import FileStorage
from infrastructure.sqlite_task_repo import SqliteTaskRepository
from application.settings_usecase import SettingsUseCase
from application.task_usecase import TaskUseCase
from application.download_usecase import DownloadUseCase
from application.asset_usecase import AssetUseCase
from domain.task_builders.base import TaskBuilderFactory
from domain.task_builders.text_to_video import TextToVideoBuilder
from domain.task_builders.multimodal_ref import MultimodalRefBuilder
from domain.task_builders.edit_video import EditVideoBuilder
from domain.task_builders.extend_video import ExtendVideoBuilder


class Container:
    """依赖注入容器"""
    
    def __init__(self):
        # 初始化日志系统
        self.logger = setup_logger()
        
        # 初始化事件总线
        self.event_bus = EventBus.instance()
        
        # 初始化配置存储
        self.config = ConfigStore(self.logger)
        
        # 初始化基础设施层
        self.api_client = ArkApiClient(self.config, self.logger)
        self.asset_client = ArkAssetClient(self.config, self.logger)
        self.file_storage = FileStorage(self.logger)
        self.task_repo = SqliteTaskRepository(self.logger)
        
        # 初始化用例层
        self.settings_usecase = SettingsUseCase(self.config, self.event_bus, self.logger, self.api_client)
        self.task_usecase = TaskUseCase(self.api_client, self.event_bus, self.logger, self.task_repo)
        self.download_usecase = DownloadUseCase(self.file_storage, self.logger)
        self.asset_usecase = AssetUseCase(self.asset_client, self.event_bus, self.logger)
        
        # 初始化后台轮询（延迟启动，等待 API Key 配置后由 UI 层启动）
        self.polling_worker = PollingWorker(self.api_client, self.task_repo, self.event_bus, self.logger)
        self.asset_polling_worker = AssetPollingWorker(self.asset_usecase, self.event_bus, self.logger)

        # 将 asset_uploaded 信号连接到轮询队列，使用 QueuedConnection 确保跨线程安全
        self.event_bus.asset_uploaded.connect(
            self.asset_polling_worker.add_asset,
            Qt.ConnectionType.QueuedConnection,
        )

        # 如果 API Key 已配置，自动启动轮询 Worker
        self._auto_start_workers()

        # 注册任务构建器
        TaskBuilderFactory.register("text_to_video", TextToVideoBuilder)
        TaskBuilderFactory.register("multimodal_ref", MultimodalRefBuilder)
        TaskBuilderFactory.register("edit_video", EditVideoBuilder)
        TaskBuilderFactory.register("extend_video", ExtendVideoBuilder)

        self.logger.info("DI container initialized successfully")

    def _auto_start_workers(self):
        """如果 API Key 已配置，自动启动后台轮询"""
        if self.config.get("api_key"):
            self.logger.info("API Key configured, auto-starting workers")
            self.polling_worker.start()
            self.asset_polling_worker.start()

    def start_workers(self):
        """手动启动后台轮询 Worker（API Key 配置后由 UI 层调用）"""
        if not self.polling_worker.isRunning():
            self.polling_worker.start()
            self.logger.info("PollingWorker started")
        if not self.asset_polling_worker.isRunning():
            self.asset_polling_worker.start()
            self.logger.info("AssetPollingWorker started")
