"""
火山引擎资产管理 API 客户端实现。

基于 requests 实现 IAssetRepository 接口，调用资产管理 REST API。
"""
from __future__ import annotations

import logging
from pathlib import Path

import requests

from domain.interfaces import IAssetRepository
from core.exceptions import ApiError
from infrastructure.config_store import ConfigStore


class ArkAssetClient(IAssetRepository):
    """Ark 资产管理客户端"""

    def __init__(self, config: ConfigStore, logger: logging.Logger):
        self._config = config
        self._logger = logger
        self._base_url = config.get("base_url", "https://ark.cn-beijing.volces.com/api/v3")
        self._session: requests.Session | None = None

    def _get_session(self) -> requests.Session:
        if self._session is None:
            api_key = self._config.get("api_key")
            if not api_key:
                raise ApiError("CONFIG_ERROR", "API Key 未配置")
            self._session = requests.Session()
            self._session.headers.update({
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            })
        return self._session

    def _has_api_key(self) -> bool:
        return bool(self._config.get("api_key"))

    def list_assets(self) -> list[dict]:
        self._logger.info("Listing assets")
        if not self._has_api_key():
            self._logger.warning("API Key not configured, returning empty asset list")
            return []
        try:
            session = self._get_session()
            url = f"{self._base_url}/assets"
            resp = session.get(url, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            assets = data.get("assets", [])
            self._logger.info(f"Listed {len(assets)} assets")
            return assets
        except ApiError:
            raise
        except Exception as e:
            self._logger.error(f"Failed to list assets: {e}")
            raise ApiError(code="ASSET_LIST_ERROR", message=f"获取资产列表失败: {e}") from e

    def upload_asset(self, file_path: str) -> str:
        self._logger.info(f"Uploading asset: {file_path}")
        try:
            path = Path(file_path)
            if not path.exists():
                raise ApiError("FILE_NOT_FOUND", f"文件不存在: {file_path}")

            session = self._get_session()
            headers = {k: v for k, v in session.headers.items() if k != "Content-Type"}
            url = f"{self._base_url}/assets/upload"

            with open(file_path, "rb") as f:
                files = {"file": (path.name, f, self._get_content_type(path.suffix))}
                resp = requests.post(url, headers=headers, files=files, timeout=300)

            resp.raise_for_status()
            data = resp.json()
            asset_id = data.get("asset_id", "")
            self._logger.info(f"Asset uploaded: asset_id={asset_id}")
            return asset_id
        except ApiError:
            raise
        except Exception as e:
            self._logger.error(f"Failed to upload asset: {e}")
            raise ApiError(code="ASSET_UPLOAD_ERROR", message=str(e)) from e

    def get_asset_status(self, asset_id: str) -> str:
        self._logger.info(f"Querying asset status: asset_id={asset_id}")
        if not self._has_api_key():
            self._logger.warning("API Key not configured, returning unknown status")
            return "unknown"
        try:
            session = self._get_session()
            url = f"{self._base_url}/assets/{asset_id}"
            resp = session.get(url, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            status = data.get("status", "unknown")
            self._logger.info(f"Asset status: asset_id={asset_id}, status={status}")
            return status
        except ApiError:
            raise
        except Exception as e:
            self._logger.error(f"Failed to query asset {asset_id}: {e}")
            raise ApiError(code="ASSET_QUERY_ERROR", message=f"查询资产状态失败: {e}") from e

    def get_reject_reason(self, asset_id: str) -> str:
        """获取资产审核被拒原因"""
        self._logger.info(f"Querying asset reject reason: asset_id={asset_id}")
        if not self._has_api_key():
            return "未知原因"
        try:
            session = self._get_session()
            url = f"{self._base_url}/assets/{asset_id}"
            resp = session.get(url, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            reason = data.get("reject_reason") or data.get("status_message") or "未知原因"
            return reason
        except ApiError:
            raise
        except Exception as e:
            self._logger.warning(f"Failed to query reject reason for {asset_id}: {e}")
            return "未知原因"

    @staticmethod
    def _get_content_type(suffix: str) -> str:
        mapping = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".mp4": "video/mp4",
            ".mov": "video/quicktime",
            ".avi": "video/x-msvideo",
            ".mkv": "video/x-matroska",
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".aac": "audio/aac",
            ".ogg": "audio/ogg",
        }
        return mapping.get(suffix.lower(), "application/octet-stream")
