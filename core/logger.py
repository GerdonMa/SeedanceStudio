"""
日志系统初始化。

配置全局日志系统，支持文件轮转和多级别日志。
"""
from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger() -> logging.Logger:
    """
    初始化全局日志系统。
    
    日志级别：
    - DEBUG: 详细调试信息（仅开发环境）
    - INFO: 关键操作记录（任务创建、API 调用、配置变更）
    - WARNING: 可恢复的异常（网络重试、配置回退）
    - ERROR: 需要关注的错误（API 失败、数据库异常）
    - CRITICAL: 致命错误（程序无法继续运行）
    
    日志文件：
    - 路径: %APPDATA%/SeedanceStudio/logs/app.log
    - 轮转: 单文件最大 10MB，保留最近 5 个文件
    - 格式: [时间] [级别] [模块名] 消息内容
    
    Returns:
        配置好的 logger 实例
    """
    logger = logging.getLogger("SeedanceStudio")
    logger.setLevel(logging.INFO)
    
    # 避免重复添加 handler
    if logger.handlers:
        return logger
    
    # 文件处理器（轮转日志）
    log_dir = Path(os.getenv("APPDATA", str(Path.home()))) / "SeedanceStudio" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(
        logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s")
    )
    logger.addHandler(file_handler)
    
    # 控制台处理器（开发时可见）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # 控制台只显示警告及以上
    console_handler.setFormatter(
        logging.Formatter("[%(levelname)s] %(message)s")
    )
    logger.addHandler(console_handler)
    
    logger.info("Logger initialized successfully")
    return logger
