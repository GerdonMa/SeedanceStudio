"""
多模态参考任务构建器。

实现基于图片/视频/音频参考的视频生成任务构建逻辑。
"""
from __future__ import annotations

from domain.entities import TaskRequest, MediaItem
from domain.enums import TaskType, MediaType
from domain.task_builders.base import TaskBuilder


class MultimodalRefBuilder(TaskBuilder):
    """多模态参考任务构建器"""

    _MAX_IMAGES = 9
    _MAX_VIDEOS = 3
    _MAX_AUDIOS = 3

    def build(
        self,
        model: str,
        prompt: str,
        media_items: list[MediaItem],
        resolution: str = "720p",
        aspect_ratio: str = "16:9",
        duration: int = 5,
        generate_audio: bool = True,
        watermark: bool = False,
        web_search: bool = False,
        offline_inference: bool = False,
    ) -> TaskRequest:
        """
        构建多模态参考任务请求。

        Args:
            model: 模型名称
            prompt: 文本提示词
            media_items: 参考素材列表
            resolution: 分辨率
            aspect_ratio: 宽高比
            duration: 视频时长（4-15秒）
            generate_audio: 是否生成音频
            watermark: 是否添加水印
            web_search: 是否启用联网搜索
            offline_inference: 是否使用离线推理
        Returns:
            TaskRequest: 任务请求对象
        Raises:
            ValidationError: 参数校验失败
        """
        self._reset_errors()

        self._validate_prompt(prompt)
        self._validate_resolution(resolution)
        self._validate_aspect_ratio(aspect_ratio)
        self._validate_duration(duration)
        self._validate_media_items(media_items)

        self._raise_if_errors()

        return TaskRequest(
            model=model,
            task_type=TaskType.MULTIMODAL_REF.value,
            prompt=prompt.strip(),
            media_items=media_items,
            resolution=resolution,
            aspect_ratio=aspect_ratio,
            duration=duration,
            generate_audio=generate_audio,
            watermark=watermark,
            web_search=web_search,
            offline_inference=offline_inference,
        )

    def validate(self, **kwargs) -> list[str]:
        """
        独立校验参数，不抛出异常，返回错误列表。

        Args:
            **kwargs: 与 build 相同的参数
        Returns:
            错误信息列表，空列表表示通过
        """
        errors: list[str] = []

        prompt = kwargs.get("prompt", "")
        if not prompt or not prompt.strip():
            errors.append("提示词不能为空")

        resolution = kwargs.get("resolution", "720p")
        if resolution not in ("480p", "720p", "1080p"):
            errors.append(f"分辨率无效: {resolution}")

        aspect_ratio = kwargs.get("aspect_ratio", "16:9")
        if aspect_ratio not in ("16:9", "9:16", "1:1", "4:3", "3:4", "21:9"):
            errors.append(f"宽高比无效: {aspect_ratio}")

        duration = kwargs.get("duration", 5)
        if duration < 4 or duration > 15:
            errors.append("视频时长必须在 4-15 秒之间")

        media_items = kwargs.get("media_items", [])
        image_count = sum(1 for m in media_items if m.type == MediaType.IMAGE)
        video_count = sum(1 for m in media_items if m.type == MediaType.VIDEO)
        audio_count = sum(1 for m in media_items if m.type == MediaType.AUDIO)

        if not media_items:
            errors.append("多模态参考任务需要至少一个素材")
        else:
            if image_count + video_count == 0:
                errors.append("不支持纯音频输入，请添加至少一张图片或一个视频")
            if image_count > self._MAX_IMAGES:
                errors.append(f"图片最多 {self._MAX_IMAGES} 张，当前 {image_count} 张")
            if video_count > self._MAX_VIDEOS:
                errors.append(f"视频最多 {self._MAX_VIDEOS} 个，当前 {video_count} 个")
            if audio_count > self._MAX_AUDIOS:
                errors.append(f"音频最多 {self._MAX_AUDIOS} 个，当前 {audio_count} 个")

        return errors

    def _validate_media_items(self, media_items: list[MediaItem]) -> None:
        """校验素材列表（内部使用，错误累积到 self._errors）"""
        image_count = sum(1 for m in media_items if m.type == MediaType.IMAGE)
        video_count = sum(1 for m in media_items if m.type == MediaType.VIDEO)
        audio_count = sum(1 for m in media_items if m.type == MediaType.AUDIO)

        if not media_items:
            self._errors.append("多模态参考任务需要至少一个素材")
            return

        if image_count + video_count == 0:
            self._errors.append("不支持纯音频输入，请添加至少一张图片或一个视频")

        if image_count > self._MAX_IMAGES:
            self._errors.append(f"图片最多 {self._MAX_IMAGES} 张，当前 {image_count} 张")
        if video_count > self._MAX_VIDEOS:
            self._errors.append(f"视频最多 {self._MAX_VIDEOS} 个，当前 {video_count} 个")
        if audio_count > self._MAX_AUDIOS:
            self._errors.append(f"音频最多 {self._MAX_AUDIOS} 个，当前 {audio_count} 个")
