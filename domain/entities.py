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
    # 图片角色：reference_image（默认）/ first_frame / last_frame；
    # 视频/音频角色固定为 reference_video / reference_audio，不使用此字段区分
    role: str = "reference_image"


@dataclass
class TaskRequest:
    """任务请求对象"""
    model: str
    task_type: str
    prompt: str
    media_items: list[MediaItem] = field(default_factory=list)
    resolution: str = "720p"
    aspect_ratio: str = "16:9"
    duration: int = 5  # -1 表示智能时长（模型自动决定）
    generate_audio: bool = True
    watermark: bool = False
    web_search: bool = False
    offline_inference: bool = False
    seed: int = -1  # [-1, 2^32-1]，-1 表示随机
    output_format: str = "mp4"  # 仅 2.5 支持 mov
    return_last_frame: bool = False  # 是否返回尾帧图（连续生成用）


@dataclass
class TaskResult:
    """任务结果对象"""
    task_id: str
    status: TaskStatus
    video_url: str | None = None
    last_frame_url: str | None = None  # return_last_frame=true 时返回
    error_message: str | None = None
    token_usage: int | None = None
    total_tokens: int | None = None
    generation_time: float | None = None
    model: str | None = None
    created_at: int | None = None  # Unix 时间戳（秒）


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
