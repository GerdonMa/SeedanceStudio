"""
文生视频任务构建器。

实现纯文本提示词生成视频的任务构建逻辑（P10：模型感知校验）。
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
        seed: int = -1,
        output_format: str = "mp4",
        return_last_frame: bool = False,
    ) -> TaskRequest:
        """
        构建文生视频任务请求。

        Args:
            model: 模型 ID
            prompt: 文本提示词
            resolution: 分辨率（按模型能力校验，2.0 含 4k）
            aspect_ratio: 宽高比（含 adaptive 自适应）
            duration: 视频时长（按模型能力 4~15/4~30 秒，-1 智能时长）
            generate_audio: 是否生成音频
            watermark: 是否添加水印
            web_search: 是否启用联网搜索
            offline_inference: 是否使用离线推理（当前 Seedance 2.x 均不支持）
            seed: 随机种子 [-1, 2^32-1]，-1 表示随机
            output_format: 输出格式（mp4/mov，mov 仅 2.5）
            return_last_frame: 是否返回尾帧图
        Returns:
            TaskRequest: 任务请求对象
        Raises:
            ValidationError: 参数校验失败
        """
        self._reset_errors()

        self._validate_prompt(prompt)
        self._validate_resolution(resolution, model)
        self._validate_aspect_ratio(aspect_ratio, model)
        self._validate_duration(duration, model)
        self._validate_seed(seed)
        self._validate_output_format(output_format, model)

        self._raise_if_errors()

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
            seed=seed,
            output_format=output_format,
            return_last_frame=return_last_frame,
        )
