"""
文件存储实现。

处理视频下载、本地缓存管理。
"""
from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path
from urllib.request import urlretrieve

from core.exceptions import StorageError


class FileStorage:
    """文件存储管理器"""
    
    def __init__(self, logger: logging.Logger):
        self._logger = logger
    
    def download_video(self, url: str, save_path: str) -> str:
        """
        下载视频文件。
        
        Args:
            url: 视频 URL
            save_path: 保存路径（目录或完整文件路径）
        Returns:
            实际保存的文件路径
        Raises:
            StorageError: 下载失败
        """
        try:
            # 如果 save_path 是目录，则自动生成文件名
            if os.path.isdir(save_path):
                filename = self._generate_filename(url)
                full_path = os.path.join(save_path, filename)
            else:
                full_path = save_path
            
            # 确保目录存在
            dir_part = os.path.dirname(full_path)
            if dir_part:
                os.makedirs(dir_part, exist_ok=True)
            
            self._logger.info(f"Downloading video: url={url}, path={full_path}")
            
            # 下载文件
            urlretrieve(url, full_path)
            
            self._logger.info(f"Video downloaded successfully: {full_path}")
            return full_path
            
        except Exception as e:
            self._logger.error(f"Failed to download video: {e}", exc_info=True)
            raise StorageError(f"视频下载失败: {e}") from e
    
    def _generate_filename(self, url: str) -> str:
        """从 URL 生成文件名"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 尝试从 URL 提取扩展名
        ext = ".mp4"
        if "." in url:
            url_ext = url.split(".")[-1].split("?")[0]
            if url_ext in ["mp4", "mov", "avi", "mkv"]:
                ext = f".{url_ext}"
        
        return f"seedance_{timestamp}{ext}"
