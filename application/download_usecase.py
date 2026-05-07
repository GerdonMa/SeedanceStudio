"""
下载用例。

处理视频下载业务逻辑。
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from core.exceptions import StorageError

if TYPE_CHECKING:
    from infrastructure.file_storage import FileStorage


class DownloadUseCase:
    """下载用例"""
    
    def __init__(self, storage: FileStorage, logger: logging.Logger):
        self._storage = storage
        self._logger = logger
    
    def download_video(self, url: str, save_path: str) -> str:
        """
        下载视频到指定路径。
        
        自动检测 URL 过期（HTTP 404/410），过期时提示用户重新生成。
        
        Args:
            url: 视频 URL
            save_path: 保存路径
        Returns:
            实际保存的文件路径
        Raises:
            StorageError: 下载失败或 URL 过期
        """
        self._logger.info(f"Downloading video: url={url[:60]}..., save_path={save_path}")
        try:
            result = self._storage.download_video(url, save_path)
            self._logger.info(f"Video downloaded successfully: {result}")
            return result
        except StorageError:
            raise
        except Exception as e:
            self._logger.error(f"Download failed: {e}")
            raise StorageError(f"视频下载失败: {e}") from e
