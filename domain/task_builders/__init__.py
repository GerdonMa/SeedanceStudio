"""任务构建器模块"""

from domain.task_builders.base import TaskBuilderFactory
from domain.task_builders.text_to_video import TextToVideoBuilder
from domain.task_builders.multimodal_ref import MultimodalRefBuilder
from domain.task_builders.edit_video import EditVideoBuilder
from domain.task_builders.extend_video import ExtendVideoBuilder

TaskBuilderFactory.register("text_to_video", TextToVideoBuilder)
TaskBuilderFactory.register("multimodal_ref", MultimodalRefBuilder)
TaskBuilderFactory.register("edit_video", EditVideoBuilder)
TaskBuilderFactory.register("extend_video", ExtendVideoBuilder)
