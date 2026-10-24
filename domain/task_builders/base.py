"""
任务构建器基类。

定义任务构建的通用流程和模型感知的校验逻辑（P10：按能力表校验）。
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from domain.entities import TaskRequest
from domain.model_capabilities import get_capability
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

    def _validate_prompt(self, prompt: str, optional: bool = False) -> None:
        """
        校验提示词。

        Args:
            prompt: 提示词文本
            optional: True 时允许为空（多模态场景文本可选）
        """
        if not prompt or not prompt.strip():
            if not optional:
                self._errors.append("提示词不能为空")
        elif len(prompt) > 2000:
            self._errors.append("提示词长度不能超过 2000 字符")

    def _validate_resolution(self, resolution: str, model: str) -> None:
        """按模型能力校验分辨率"""
        cap = get_capability(model)
        if resolution not in cap.resolutions:
            self._errors.append(
                f"模型 {cap.display_name} 支持的分辨率为 {', '.join(cap.resolutions)}，"
                f"当前选择: {resolution}"
            )

    def _validate_aspect_ratio(self, aspect_ratio: str, model: str) -> None:
        """按模型能力校验宽高比"""
        cap = get_capability(model)
        if aspect_ratio not in cap.ratios:
            self._errors.append(
                f"模型 {cap.display_name} 支持的宽高比为 {', '.join(cap.ratios)}，"
                f"当前选择: {aspect_ratio}"
            )

    def _validate_duration(self, duration: int, model: str) -> None:
        """按模型能力校验时长（-1 表示智能时长）"""
        cap = get_capability(model)
        if duration == -1:
            if not cap.duration_auto:
                self._errors.append(f"模型 {cap.display_name} 不支持智能时长（-1）")
            return
        if duration < cap.duration_min or duration > cap.duration_max:
            self._errors.append(
                f"模型 {cap.display_name} 的视频时长必须在 "
                f"{cap.duration_min}-{cap.duration_max} 秒之间（或 -1 智能时长），"
                f"当前值: {duration}"
            )

    def _validate_seed(self, seed: int) -> None:
        """校验种子值，取值范围 [-1, 2^32-1]"""
        if seed < -1 or seed > 2**32 - 1:
            self._errors.append("种子值必须在 -1 到 4294967295 之间")

    def _validate_output_format(self, output_format: str, model: str) -> None:
        """按模型能力校验输出格式（mov 仅 2.5 支持）"""
        cap = get_capability(model)
        valid = ("mp4", "mov") if cap.supports_mov else ("mp4",)
        if output_format not in valid:
            self._errors.append(
                f"模型 {cap.display_name} 支持的输出格式为 {', '.join(valid)}，"
                f"当前选择: {output_format}"
            )

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
