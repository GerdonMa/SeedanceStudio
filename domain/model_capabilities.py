"""
Seedance 模型能力表。

集中定义各模型支持的输出参数取值范围与素材上限，
供 TaskBuilder 校验和 UI 参数联动使用（P10：适配 Seedance 2.5）。

数据来源（官方文档，2026-10）：
- Doubao Seedance 2.5 教程「能力概述」表
- 创建视频生成任务 API（docs/api/create-task.md 快照 + 官方在线版）
"""
from __future__ import annotations

from dataclasses import dataclass

_ALL_RATIOS = ("adaptive", "16:9", "4:3", "1:1", "3:4", "9:16", "21:9")


@dataclass(frozen=True)
class ModelCapability:
    """单个模型的能力描述"""

    model_id: str
    display_name: str
    resolutions: tuple[str, ...]        # 支持的输出分辨率
    ratios: tuple[str, ...]             # 支持的输出宽高比
    duration_min: int                   # 时长下限（秒）
    duration_max: int                   # 时长上限（秒）
    duration_auto: bool                 # 是否支持 duration=-1 智能时长
    max_images: int                     # 参考图数量上限
    max_videos: int                     # 参考视频数量上限
    max_audios: int                     # 参考音频数量上限
    supports_audio_only: bool           # 是否支持纯音频参考（无图/视频）
    supports_web_search: bool           # 是否支持联网搜索工具
    supports_flex: bool                 # 是否支持离线推理 service_tier=flex
    supports_mov: bool                  # 是否支持 output_format=mov
    supports_first_last_frame: bool     # 是否支持首帧/首尾帧 role
    locks_ratio_on_edit_extend: bool    # 编辑/延长/首尾帧任务是否强制 ratio=adaptive
    locks_duration_on_edit: bool        # 编辑任务是否强制 duration=-1


MODEL_CAPABILITIES: dict[str, ModelCapability] = {
    "doubao-seedance-2-5-260628": ModelCapability(
        model_id="doubao-seedance-2-5-260628",
        display_name="Seedance 2.5（旗舰·最长30秒）",
        resolutions=("480p", "720p", "1080p"),
        ratios=_ALL_RATIOS,
        duration_min=4,
        duration_max=30,
        duration_auto=True,
        max_images=30,
        max_videos=10,
        max_audios=10,
        supports_audio_only=True,
        supports_web_search=True,
        supports_flex=False,
        supports_mov=True,
        supports_first_last_frame=True,
        locks_ratio_on_edit_extend=True,
        locks_duration_on_edit=True,
    ),
    "doubao-seedance-2-0-260128": ModelCapability(
        model_id="doubao-seedance-2-0-260128",
        display_name="Seedance 2.0（高质量）",
        resolutions=("480p", "720p", "1080p", "4k"),
        ratios=_ALL_RATIOS,
        duration_min=4,
        duration_max=15,
        duration_auto=True,
        max_images=9,
        max_videos=3,
        max_audios=3,
        supports_audio_only=False,
        supports_web_search=True,
        supports_flex=False,
        supports_mov=False,
        supports_first_last_frame=True,
        locks_ratio_on_edit_extend=False,
        locks_duration_on_edit=False,
    ),
    "doubao-seedance-2-0-fast-260128": ModelCapability(
        model_id="doubao-seedance-2-0-fast-260128",
        display_name="Seedance 2.0 Fast（快速）",
        resolutions=("480p", "720p"),
        ratios=_ALL_RATIOS,
        duration_min=4,
        duration_max=15,
        duration_auto=True,
        max_images=9,
        max_videos=3,
        max_audios=3,
        supports_audio_only=False,
        supports_web_search=True,
        supports_flex=False,
        supports_mov=False,
        supports_first_last_frame=True,
        locks_ratio_on_edit_extend=False,
        locks_duration_on_edit=False,
    ),
    "doubao-seedance-2-0-mini-260615": ModelCapability(
        model_id="doubao-seedance-2-0-mini-260615",
        display_name="Seedance 2.0 Mini（低成本）",
        resolutions=("480p", "720p"),
        ratios=_ALL_RATIOS,
        duration_min=4,
        duration_max=15,
        duration_auto=True,
        max_images=9,
        max_videos=3,
        max_audios=3,
        supports_audio_only=False,
        supports_web_search=True,
        supports_flex=False,
        supports_mov=False,
        supports_first_last_frame=True,
        locks_ratio_on_edit_extend=False,
        locks_duration_on_edit=False,
    ),
}

# UI 模型下拉框顺序（新模型在前）
MODEL_ORDER: list[str] = [
    "doubao-seedance-2-5-260628",
    "doubao-seedance-2-0-260128",
    "doubao-seedance-2-0-fast-260128",
    "doubao-seedance-2-0-mini-260615",
]


def get_capability(model_id: str) -> ModelCapability:
    """
    查询模型能力。未知模型返回基于官方全集的宽松能力，
    避免新模型上线后校验层直接拦截（由 API 端强校验兜底）。
    """
    cap = MODEL_CAPABILITIES.get(model_id)
    if cap is not None:
        return cap
    return ModelCapability(
        model_id=model_id,
        display_name=model_id,
        resolutions=("480p", "720p", "1080p"),
        ratios=_ALL_RATIOS,
        duration_min=4,
        duration_max=15,
        duration_auto=True,
        max_images=9,
        max_videos=3,
        max_audios=3,
        supports_audio_only=False,
        supports_web_search=True,
        supports_flex=False,
        supports_mov=False,
        supports_first_last_frame=True,
        locks_ratio_on_edit_extend=False,
        locks_duration_on_edit=False,
    )
