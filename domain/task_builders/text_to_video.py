"""
文生视频任务构建器。

实现纯文本提示词生成视频的任务构建逻辑。
"""
from __future__ import annotations

from domain.entities import TaskRequest
from domain.enums import TaskType
from domain.task_builders.base import TaskBuilder


class TextToVideoBuilder(TaskBuilder):
    """文生视频任务构建器"""
    
    def build(
        self,
        model: str,
        prompt: str,
        resolution: str = "720p",
        aspect_ratio: str = "16:9",
        duration: int = 5,
        generate_audio: bool = True,
        watermark: bool = False,
        web_search: bool = False,
        offline_inference: bool = False,
    ) -> TaskRequest:
        """
        构建文生视频任务请求。
        
        Args:
            model: 模型名称
            prompt: 文本提示词
            resolution: 分辨率（480p/720p/1080p）
            aspect_ratio: 宽高比（16:9/9:16/1:1/4:3/3:4）
            duration: 视频时长（1-10秒）
            generate_audio: 是否生成音频
            watermark: 是否添加水印
            web_search: 是否启用联网搜索
            offline_inference: 是否使用离线推理（flex 模式）
        Returns:
            TaskRequest: 任务请求对象
        Raises:
            ValidationError: 参数校验失败
        """
        self._reset_errors()
        
        # 校验参数
        self._validate_prompt(prompt)
        self._validate_resolution(resolution)
        self._validate_aspect_ratio(aspect_ratio)
        self._validate_duration(duration)
        
        # 如果有错误则抛出异常
        self._raise_if_errors()
        
        # 构建请求对象
        return TaskRequest(
            model=model,
            task_type=TaskType.TEXT_TO_VIDEO.value,
            prompt=prompt.strip(),
            media_items=[],  # 文生视频无需媒体素材
            resolution=resolution,
            aspect_ratio=aspect_ratio,
            duration=duration,
            generate_audio=generate_audio,
            watermark=watermark,
            web_search=web_search,
            offline_inference=offline_inference,
        )
