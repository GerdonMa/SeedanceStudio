"""
任务构建器基类。

定义任务构建的通用流程和校验逻辑。
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from domain.entities import TaskRequest
from core.exceptions import ValidationError


class TaskBuilder(ABC):
    """任务构建器基类"""
    
    def __init__(self):
        self._errors: list[str] = []
    
    @abstractmethod
    def build(self, **kwargs) -> TaskRequest:
        """
        构建任务请求对象。
        
        Args:
            **kwargs: 任务参数
        Returns:
            TaskRequest: 任务请求对象
        Raises:
            ValidationError: 参数校验失败
        """
        pass
    
    def _validate_prompt(self, prompt: str) -> None:
        """校验提示词"""
        if not prompt or not prompt.strip():
            self._errors.append("提示词不能为空")
        elif len(prompt) > 2000:
            self._errors.append("提示词长度不能超过 2000 字符")
    
    def _validate_resolution(self, resolution: str) -> None:
        """校验分辨率"""
        valid_resolutions = ["480p", "720p", "1080p"]
        if resolution not in valid_resolutions:
            self._errors.append(f"分辨率必须是 {', '.join(valid_resolutions)} 之一")
    
    def _validate_aspect_ratio(self, aspect_ratio: str) -> None:
        """校验宽高比"""
        valid_ratios = ["16:9", "9:16", "1:1", "4:3", "3:4", "21:9"]
        if aspect_ratio not in valid_ratios:
            self._errors.append(f"宽高比必须是 {', '.join(valid_ratios)} 之一")
    
    def _validate_duration(self, duration: int) -> None:
        """校验时长"""
        if duration < 4 or duration > 15:
            self._errors.append("视频时长必须在 4-15 秒之间")
    
    def _raise_if_errors(self) -> None:
        """如果有校验错误则抛出异常"""
        if self._errors:
            raise ValidationError(self._errors)
    
    def _reset_errors(self) -> None:
        """重置错误列表"""
        self._errors = []


class TaskBuilderFactory:
    """任务构建器工厂（插件式注册）"""
    
    _builders: dict[str, type[TaskBuilder]] = {}
    
    @classmethod
    def register(cls, task_type: str, builder_cls: type[TaskBuilder]) -> None:
        """
        注册任务构建器。
        
        Args:
            task_type: 任务类型标识（如 "text_to_video"）
            builder_cls: 构建器类
        """
        cls._builders[task_type] = builder_cls
    
    @classmethod
    def get(cls, task_type: str) -> TaskBuilder:
        """
        获取任务构建器实例。
        
        Args:
            task_type: 任务类型标识
        Returns:
            TaskBuilder 实例
        Raises:
            ValueError: 未注册的任务类型
        """
        if task_type not in cls._builders:
            raise ValueError(f"未注册的任务类型: {task_type}")
        return cls._builders[task_type]()
    
    @classmethod
    def registered_types(cls) -> list[str]:
        """返回所有已注册的任务类型列表"""
        return list(cls._builders.keys())
