"""
多模态参考任务构建器。

实现基于图片/视频/音频参考的视频生成任务构建逻辑（P10：模型感知校验）。
支持图生视频-首帧/首尾帧（通过 MediaItem.role 指定）与纯音频参考（仅 2.5）。
"""
from __future__ import annotations

from domain.entities import TaskRequest, MediaItem
from domain.enums import TaskType, MediaType
from domain.model_capabilities import get_capability
from domain.task_builders.base import TaskBuilder

_IMAGE_ROLES = ("reference_image", "first_frame", "last_frame")


class MultimodalRefBuilder(TaskBuilder):
    """多模态参考任务构建器"""

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
        构建多模态参考任务请求。

        官方规则（Seedance 2.5 教程）：
        - 首尾帧任务 ratio 仅支持 adaptive，此处自动纠正
        - 2.5 支持纯音频参考；2.0 系列必须至少包含一张图片或一个视频
        - 首帧/首尾帧场景与参考图/视频/音频场景互斥，不可混用

        Args:
            model: 模型 ID
            prompt: 文本提示词（多模态场景可选）
            media_items: 参考素材列表（图片可带 role）
            resolution: 分辨率（按模型能力校验）
            aspect_ratio: 宽高比（含 adaptive）
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

        # 首尾帧任务（Seedance 2.5）仅支持 adaptive 宽高比，自动纠正
        has_frame_role = any(
            m.type == MediaType.IMAGE and m.role in ("first_frame", "last_frame")
            for m in media_items
        )
        if has_frame_role and cap.locks_ratio_on_edit_extend:
            aspect_ratio = "adaptive"

        self._validate_prompt(prompt, optional=True)
        self._validate_resolution(resolution, model)
        self._validate_aspect_ratio(aspect_ratio, model)
        self._validate_duration(duration, model)
        self._validate_seed(seed)
        self._validate_output_format(output_format, model)
        self._validate_media_items(media_items, model)

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
        if prompt and len(prompt) > 2000:
            errors.append("提示词长度不能超过 2000 字符")

        resolution = kwargs.get("resolution", "720p")
        if resolution not in cap.resolutions:
            errors.append(f"分辨率无效: {resolution}，应为 {', '.join(cap.resolutions)}")

        aspect_ratio = kwargs.get("aspect_ratio", "16:9")
        if aspect_ratio not in cap.ratios:
            errors.append(f"宽高比无效: {aspect_ratio}，应为 {', '.join(cap.ratios)}")

        duration = kwargs.get("duration", 5)
        if duration != -1 and not (cap.duration_min <= duration <= cap.duration_max):
            errors.append(
                f"视频时长必须在 {cap.duration_min}-{cap.duration_max} 秒之间或为 -1"
            )

        errors.extend(self._check_media(kwargs.get("media_items", []), model))
        return errors

    def _validate_media_items(self, media_items: list[MediaItem], model: str) -> None:
        """校验素材列表（内部使用，错误累积到 self._errors）"""
        for err in self._check_media(media_items, model):
            self._errors.append(err)

    def _check_media(self, media_items: list[MediaItem], model: str) -> list[str]:
        """按模型能力校验素材数量、组合与图片 role"""
        errors: list[str] = []
        cap = get_capability(model)

        if not media_items:
            errors.append("多模态参考任务需要至少一个素材")
            return errors

        image_count = sum(1 for m in media_items if m.type == MediaType.IMAGE)
        video_count = sum(1 for m in media_items if m.type == MediaType.VIDEO)
        audio_count = sum(1 for m in media_items if m.type == MediaType.AUDIO)

        first_count = sum(
            1 for m in media_items
            if m.type == MediaType.IMAGE and m.role == "first_frame"
        )
        last_count = sum(
            1 for m in media_items
            if m.type == MediaType.IMAGE and m.role == "last_frame"
        )
        ref_image_count = sum(
            1 for m in media_items
            if m.type == MediaType.IMAGE and m.role == "reference_image"
        )
        frame_mode = first_count > 0 or last_count > 0

        # 图片 role 合法性
        for m in media_items:
            if m.type == MediaType.IMAGE and m.role not in _IMAGE_ROLES:
                errors.append(f"图片角色无效: {m.role}，应为 {'/'.join(_IMAGE_ROLES)}")

        if frame_mode:
            # 首帧/首尾帧场景与多模态参考互斥
            if ref_image_count > 0:
                errors.append("首帧/尾帧图片不能与参考图混用（官方互斥场景）")
            if video_count > 0 or audio_count > 0:
                errors.append("首帧/首尾帧任务不支持搭配视频或音频素材")
            if first_count > 1:
                errors.append("首帧图片最多 1 张")
            if last_count > 1:
                errors.append("尾帧图片最多 1 张")
            # Seedance 2.0 系列要求尾帧必须与首帧成对；2.5 允许尾帧单独使用
            if last_count > 0 and first_count == 0 and not cap.supports_audio_only:
                errors.append("当前模型要求尾帧图片必须与首帧图片成对使用（2.5 才支持仅尾帧）")
        else:
            if image_count + video_count == 0 and not cap.supports_audio_only:
                errors.append("当前模型不支持纯音频输入，请添加至少一张图片或一个视频")
            if image_count > cap.max_images:
                errors.append(f"图片最多 {cap.max_images} 张，当前 {image_count} 张")
            if video_count > cap.max_videos:
                errors.append(f"视频最多 {cap.max_videos} 个，当前 {video_count} 个")
            if audio_count > cap.max_audios:
                errors.append(f"音频最多 {cap.max_audios} 个，当前 {audio_count} 个")

        return errors
