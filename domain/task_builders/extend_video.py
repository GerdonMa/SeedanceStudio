"""
延长视频任务构建器。

实现基于源视频 + 文本提示词进行视频延长的任务构建逻辑（P10：模型感知校验）。

Seedance 2.5 规则：延长视频任务 ratio 仅支持 adaptive，builder 自动纠正。
"""
from __future__ import annotations

from domain.entities import TaskRequest, MediaItem
from domain.enums import TaskType, MediaType
from domain.model_capabilities import get_capability
from domain.task_builders.base import TaskBuilder


class ExtendVideoBuilder(TaskBuilder):
    """延长视频任务构建器"""

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
        seed: int = -1,
        output_format: str = "mp4",
        return_last_frame: bool = False,
    ) -> TaskRequest:
        """
        构建延长视频任务请求。

        Args:
            model: 模型 ID
            prompt: 文本提示词（延续描述，必填）
            media_items: 素材列表（必须包含至少一个视频作为源视频）
            resolution: 分辨率（按模型能力校验）
            aspect_ratio: 宽高比（2.5 自动纠正为 adaptive）
            duration: 视频时长（-1 智能时长）
            generate_audio: 是否生成音频
            watermark: 是否添加水印
            web_search: 是否启用联网搜索
            offline_inference: 是否使用离线推理
            seed: 随机种子
            output_format: 输出格式（mp4/mov）
            return_last_frame: 是否返回尾帧图
        Returns:
            TaskRequest: 任务请求对象
        Raises:
            ValidationError: 参数校验失败
        """
        self._reset_errors()
        cap = get_capability(model)

        # Seedance 2.5：延长任务强制 adaptive
        if cap.locks_ratio_on_edit_extend:
            aspect_ratio = "adaptive"

        self._validate_prompt(prompt)
        self._validate_resolution(resolution, model)
        self._validate_aspect_ratio(aspect_ratio, model)
        self._validate_duration(duration, model)
        self._validate_seed(seed)
        self._validate_output_format(output_format, model)
        self._validate_media_items(media_items, model)

        self._raise_if_errors()

        return TaskRequest(
            model=model,
            task_type=TaskType.EXTEND_VIDEO.value,
            prompt=prompt.strip(),
            media_items=media_items,
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

    def validate(self, **kwargs) -> list[str]:
        """
        独立校验参数，不抛出异常，返回错误列表。

        Args:
            **kwargs: 与 build 相同的参数（model 必传）
        Returns:
            错误信息列表，空列表表示通过
        """
        errors: list[str] = []
        model = kwargs.get("model", "")
        cap = get_capability(model)

        prompt = kwargs.get("prompt", "")
        if not prompt or not prompt.strip():
            errors.append("提示词不能为空")

        resolution = kwargs.get("resolution", "720p")
        if resolution not in cap.resolutions:
            errors.append(f"分辨率无效: {resolution}，应为 {', '.join(cap.resolutions)}")

        duration = kwargs.get("duration", 5)
        if duration != -1 and not (cap.duration_min <= duration <= cap.duration_max):
            errors.append(
                f"视频时长必须在 {cap.duration_min}-{cap.duration_max} 秒之间或为 -1"
            )

        media_items = kwargs.get("media_items", [])
        video_count = sum(1 for m in media_items if m.type == MediaType.VIDEO)
        image_count = sum(1 for m in media_items if m.type == MediaType.IMAGE)
        audio_count = sum(1 for m in media_items if m.type == MediaType.AUDIO)

        if not media_items:
            errors.append("延长视频任务需要至少一个视频作为源素材")
        else:
            if video_count == 0:
                errors.append("延长视频任务至少需要一个视频素材作为源视频")
            if video_count > cap.max_videos:
                errors.append(f"视频最多 {cap.max_videos} 个，当前 {video_count} 个")
            if image_count > 0:
                errors.append("延长视频任务不支持图片素材")
            if audio_count > cap.max_audios:
                errors.append(f"音频最多 {cap.max_audios} 个，当前 {audio_count} 个")

        return errors

    def _validate_media_items(self, media_items: list[MediaItem], model: str) -> None:
        """校验素材列表（内部使用，错误累积到 self._errors）"""
        cap = get_capability(model)

        if not media_items:
            self._errors.append("延长视频任务需要至少一个视频作为源素材")
            return

        video_count = sum(1 for m in media_items if m.type == MediaType.VIDEO)
        image_count = sum(1 for m in media_items if m.type == MediaType.IMAGE)
        audio_count = sum(1 for m in media_items if m.type == MediaType.AUDIO)

        if video_count == 0:
            self._errors.append("延长视频任务至少需要一个视频素材作为源视频")
        if video_count > cap.max_videos:
            self._errors.append(f"视频最多 {cap.max_videos} 个，当前 {video_count} 个")
        if image_count > 0:
            self._errors.append("延长视频任务不支持图片素材")
        if audio_count > cap.max_audios:
            self._errors.append(f"音频最多 {cap.max_audios} 个，当前 {audio_count} 个")
