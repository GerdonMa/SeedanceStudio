"""
资产管理用例。

处理资产列表查询、上传新素材、查询审核状态等业务逻辑。
"""
from __future__ import annotations

import logging

from domain.interfaces import IAssetRepository
from core.event_bus import EventBus


class AssetUseCase:
    """资产管理用例"""

    def __init__(
        self,
        asset_repo: IAssetRepository,
        event_bus: EventBus,
        logger: logging.Logger,
    ):
        self._asset_repo = asset_repo
        self._event_bus = event_bus
        self._logger = logger

    def list_assets(self) -> list[dict]:
        """
        查询资产列表。

        Returns:
            资产字典列表，每个字典包含 id/name/type/status 等字段
        """
        self._logger.info("Listing assets")
        return self._asset_repo.list_assets()

    def upload_asset(self, file_path: str) -> str:
        """
        上传新素材到资产库。

        上传成功后自动广播 asset_uploaded 事件，触发审核轮询。

        Args:
            file_path: 本地文件路径

        Returns:
            asset_id: 资产 ID
        """
        self._logger.info(f"Uploading asset: {file_path}")
        asset_id = self._asset_repo.upload_asset(file_path)
        self._event_bus.asset_uploaded.emit(asset_id)
        self._logger.info(f"Asset uploaded and event emitted: asset_id={asset_id}")
        return asset_id

    def get_asset_status(self, asset_id: str) -> str:
        """
        查询资产审核状态。

        Args:
            asset_id: 资产 ID

        Returns:
            状态值: pending / approved / rejected
        """
        return self._asset_repo.get_asset_status(asset_id)

    def get_reject_reason(self, asset_id: str) -> str:
        """
        获取资产审核被拒原因。

        Args:
            asset_id: 资产 ID

        Returns:
            拒绝原因描述文本
        """
        return self._asset_repo.get_reject_reason(asset_id)
