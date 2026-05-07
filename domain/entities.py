"""
领域层实体定义。

定义核心业务实体的数据类。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from domain.enums import TaskStatus, MediaType


@dataclass
class MediaItem:
    """媒体素材项"""
    type: MediaType
    url: str
    asset_id: str | None = None  # 资产库模式下的资产ID


@dataclass
class TaskRequest:
    """任务请求对象"""
    model: str
    task_type: str
    prompt: str
    media_items: list[MediaItem] = field(default_factory=list)
    resolution: str = "720p"
    aspect_ratio: str = "16:9"
    duration: int = 5
    generate_audio: bool = True
    watermark: bool = False
    web_search: bool = False
    offline_inference: bool = False


@dataclass
class TaskResult:
    """任务结果对象"""
    task_id: str
    status: TaskStatus
    video_url: str | None = None
    error_message: str | None = None
    token_usage: int | None = None
    generation_time: float | None = None


@dataclass
class Task:
    """任务实体"""
    task_id: str
    model: str
    task_type: str
    prompt: str
    status: TaskStatus
    created_at: datetime
    updated_at: datetime | None = None
    video_url: str | None = None
    error_message: str | None = None
    token_usage: int | None = None
    generation_time: float | None = None
