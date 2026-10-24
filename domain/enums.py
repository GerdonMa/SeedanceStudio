"""
领域层枚举定义。

定义任务状态、媒体类型、模型类型、任务类型等枚举。
"""
from __future__ import annotations

from enum import Enum


class TaskStatus(str, Enum):
    """任务状态枚举"""
    QUEUED = "queued"
    PENDING = "pending"
    RUNNING = "running"
    CANCELLED = "cancelled"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    EXPIRED = "expired"


class MediaType(str, Enum):
    """媒体类型枚举"""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"


class ModelType(str, Enum):
    """模型类型枚举"""
    SEEDANCE_25 = "doubao-seedance-2-5-260628"
    STANDARD = "doubao-seedance-2-0-260128"
    FAST = "doubao-seedance-2-0-fast-260128"
    MINI = "doubao-seedance-2-0-mini-260615"


class TaskType(str, Enum):
    """任务类型枚举"""
    TEXT_TO_VIDEO = "text_to_video"
    MULTIMODAL_REF = "multimodal_ref"
    EDIT_VIDEO = "edit_video"
    EXTEND_VIDEO = "extend_video"
