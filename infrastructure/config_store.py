"""
配置存储实现。

使用 Fernet 加密存储敏感配置，支持自动备份和恢复。
"""
from __future__ import annotations

import json
import logging
import os
import shutil
import uuid
from pathlib import Path

from cryptography.fernet import Fernet
import base64
import hashlib

from core.exceptions import StorageError


class ConfigStore:
    """配置存储管理器"""
    
    def __init__(self, logger: logging.Logger):
        self._logger = logger
        self._config_dir = Path(os.getenv("APPDATA", str(Path.home()))) / "SeedanceStudio"
        self._config_dir.mkdir(parents=True, exist_ok=True)
        self._config_path = self._config_dir / "config.json"
        
        # 密钥派生自机器 ID，确保同一台机器的配置文件可解密
        self._cipher = self._init_cipher()
        self._data = self._load()
    
    def _init_cipher(self) -> Fernet:
        """初始化加密器，密钥派生自机器 ID"""
        try:
            # 获取机器唯一标识
            machine_id = str(uuid.getnode())
            # 派生 32 字节密钥
            key_bytes = hashlib.sha256(machine_id.encode()).digest()
            key = base64.urlsafe_b64encode(key_bytes)
            return Fernet(key)
        except Exception as e:
            self._logger.critical(f"Failed to initialize cipher: {e}")
            raise StorageError(f"加密器初始化失败: {e}") from e
    
    def _load(self) -> dict:
        """加载配置，失败时尝试从备份恢复"""
        try:
            if not self._config_path.exists():
                self._logger.info("Config file not found, creating default")
                defaults = self._get_defaults()
                self._save_to_file(self._config_path, defaults)
                return defaults
            
            with open(self._config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._logger.info("Config loaded successfully")
                return data
        except json.JSONDecodeError as e:
            self._logger.warning(f"Config file corrupted: {e}, trying backup")
            return self._load_from_backup()
        except Exception as e:
            self._logger.error(f"Unexpected error loading config: {e}")
            return self._load_from_backup()
    
    def _load_from_backup(self) -> dict:
        """从备份文件恢复配置"""
        backup_path = self._config_path.with_suffix(".json.bak")
        try:
            with open(backup_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._logger.info("Config restored from backup")
                # 恢复成功后立即写回主配置文件
                self._save_to_file(self._config_path, data)
                return data
        except Exception as e:
            self._logger.error(f"Backup restore failed: {e}, using defaults")
            # 备份也失败，返回默认值并写入文件
            defaults = self._get_defaults()
            try:
                self._save_to_file(self._config_path, defaults)
            except Exception as save_error:
                self._logger.critical(f"Cannot write default config: {save_error}")
            return defaults
    
    def _get_defaults(self) -> dict:
        """返回默认配置，确保程序可启动"""
        return {
            "api_key": "",
            "base_url": "https://ark.cn-beijing.volces.com/api/v3",
            "default_model": "doubao-seedance-2-0-260128",
            "default_task_type": "text_to_video",
            "asset_mode_enabled": False,
            "default_resolution": "720p",
            "default_aspect_ratio": "16:9",
            "default_duration": 5,
            "generate_audio": True,
            "watermark": False,
            "offline_inference": False,
            "web_search": False,
            "download_path": str(Path.home() / "Desktop"),
            "window_width": 1200,
            "window_height": 800,
            "window_x": -1,  # -1 表示居中
            "window_y": -1,
            "ui_theme": "default_light"
        }
    
    def _save_to_file(self, path: Path, data: dict) -> None:
        """保存数据到文件"""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _create_backup(self) -> None:
        """创建配置文件备份"""
        try:
            backup_path = self._config_path.with_suffix(".json.bak")
            shutil.copy2(self._config_path, backup_path)
            self._logger.debug(f"Config backup created: {backup_path}")
        except Exception as e:
            # 备份失败不影响主流程，只记录警告
            self._logger.warning(f"Failed to create config backup: {e}")
    
    def get(self, key: str, default=None):
        """获取配置项"""
        value = self._data.get(key, default)
        
        # API Key 需要解密
        if key == "api_key" and value:
            try:
                return self._cipher.decrypt(value.encode()).decode()
            except Exception as e:
                self._logger.error(f"Failed to decrypt API key: {e}")
                return ""
        
        return value
    
    def get_all(self) -> dict:
        """获取所有配置项（API Key 已解密）"""
        result = self._data.copy()
        if result.get("api_key"):
            try:
                result["api_key"] = self._cipher.decrypt(result["api_key"].encode()).decode()
            except Exception as e:
                self._logger.error(f"Failed to decrypt API key: {e}")
                result["api_key"] = ""
        return result
    
    def set(self, key: str, value) -> None:
        """保存配置项，成功后自动备份"""
        try:
            # API Key 需要加密
            if key == "api_key" and value:
                value = self._cipher.encrypt(value.encode()).decode()
            
            self._data[key] = value
            self._save_to_file(self._config_path, self._data)
            self._create_backup()
            
            # 不记录敏感信息的完整值
            if key == "api_key":
                self._logger.info(f"Preference saved: {key} (encrypted)")
            else:
                self._logger.info(f"Preference saved: {key}={value}")
        except Exception as e:
            self._logger.error(f"Failed to save preference {key}: {e}")
            raise StorageError(f"配置保存失败: {e}") from e
