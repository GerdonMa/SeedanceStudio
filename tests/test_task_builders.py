"""
任务构建器单元测试。

测试所有四种 TaskBuilder 的构建和校验逻辑。
"""
from __future__ import annotations

import unittest

from domain.entities import MediaItem
from domain.enums import MediaType
from domain.task_builders.base import TaskBuilderFactory
from domain.task_builders.text_to_video import TextToVideoBuilder
from domain.task_builders.multimodal_ref import MultimodalRefBuilder
from domain.task_builders.edit_video import EditVideoBuilder
from domain.task_builders.extend_video import ExtendVideoBuilder
from core.exceptions import ValidationError


class TestTextToVideoBuilder(unittest.TestCase):
    """文生视频构建器测试"""

    def setUp(self):
        self.builder = TextToVideoBuilder()

    def test_build_valid(self):
        request = self.builder.build(
            model="doubao-seedance-2-0-260128",
            prompt="一只猫在草地上玩耍",
            resolution="720p",
            aspect_ratio="16:9",
            duration=5,
        )
        self.assertEqual(request.model, "doubao-seedance-2-0-260128")
        self.assertEqual(request.prompt, "一只猫在草地上玩耍")
        self.assertEqual(request.task_type, "text_to_video")
        self.assertEqual(request.duration, 5)
        self.assertEqual(request.generate_audio, True)
        self.assertEqual(request.media_items, [])

    def test_build_empty_prompt_raises(self):
        with self.assertRaises(ValidationError) as ctx:
            self.builder.build(
                model="test", prompt="", resolution="720p",
                aspect_ratio="16:9", duration=5,
            )
        self.assertIn("提示词", str(ctx.exception.errors))

    def test_build_invalid_duration_raises(self):
        for d in [3, 16, 0, -1]:
            with self.assertRaises(ValidationError):
                self.builder.build(
                    model="test", prompt="猫", resolution="720p",
                    aspect_ratio="16:9", duration=d,
                )

    def test_build_invalid_resolution_raises(self):
        with self.assertRaises(ValidationError):
            self.builder.build(
                model="test", prompt="猫", resolution="4k",
                aspect_ratio="16:9", duration=5,
            )

    def test_build_invalid_aspect_ratio_raises(self):
        with self.assertRaises(ValidationError):
            self.builder.build(
                model="test", prompt="猫", resolution="720p",
                aspect_ratio="32:9", duration=5,
            )

    def test_build_with_all_options(self):
        request = self.builder.build(
            model="doubao-seedance-2-0-fast-260128",
            prompt="测试",
            resolution="1080p",
            aspect_ratio="21:9",
            duration=15,
            generate_audio=False,
            watermark=True,
            web_search=True,
            offline_inference=True,
        )
        self.assertEqual(request.resolution, "1080p")
        self.assertEqual(request.aspect_ratio, "21:9")
        self.assertEqual(request.duration, 15)
        self.assertFalse(request.generate_audio)
        self.assertTrue(request.watermark)
        self.assertTrue(request.web_search)
        self.assertTrue(request.offline_inference)


class TestMultimodalRefBuilder(unittest.TestCase):
    """多模态参考构建器测试"""

    def setUp(self):
        self.builder = MultimodalRefBuilder()

    def test_build_with_image_valid(self):
        media = [MediaItem(type=MediaType.IMAGE, url="http://example.com/img.jpg")]
        request = self.builder.build(
            model="test", prompt="猫", media_items=media,
            resolution="720p", aspect_ratio="16:9", duration=5,
        )
        self.assertEqual(request.task_type, "multimodal_ref")
        self.assertEqual(len(request.media_items), 1)

    def test_build_no_media_raises(self):
        with self.assertRaises(ValidationError):
            self.builder.build(
                model="test", prompt="猫", media_items=[],
                resolution="720p", aspect_ratio="16:9", duration=5,
            )

    def test_build_audio_only_rejected(self):
        audio = [MediaItem(type=MediaType.AUDIO, url="http://example.com/audio.mp3")]
        with self.assertRaises(ValidationError) as ctx:
            self.builder.build(
                model="test", prompt="猫", media_items=audio,
                resolution="720p", aspect_ratio="16:9", duration=5,
            )
        self.assertIn("音频", str(ctx.exception.errors))

    def test_build_mixed_valid(self):
        media = [
            MediaItem(type=MediaType.IMAGE, url="http://example.com/img.jpg"),
            MediaItem(type=MediaType.VIDEO, url="http://example.com/vid.mp4"),
            MediaItem(type=MediaType.AUDIO, url="http://example.com/aud.mp3"),
        ]
        request = self.builder.build(
            model="test", prompt="猫", media_items=media,
            resolution="720p", aspect_ratio="16:9", duration=5,
        )
        self.assertEqual(len(request.media_items), 3)

    def test_validate_returns_errors(self):
        errors = self.builder.validate(prompt="", media_items=[], duration=3, resolution="8k")
        self.assertGreater(len(errors), 0)

    def test_image_count_limit(self):
        media = [MediaItem(type=MediaType.IMAGE, url=f"http://example.com/{i}.jpg") for i in range(10)]
        with self.assertRaises(ValidationError):
            self.builder.build(
                model="test", prompt="猫", media_items=media,
                resolution="720p", aspect_ratio="16:9", duration=5,
            )


class TestEditVideoBuilder(unittest.TestCase):
    """编辑视频构建器测试"""

    def setUp(self):
        self.builder = EditVideoBuilder()

    def test_build_with_video_valid(self):
        media = [MediaItem(type=MediaType.VIDEO, url="http://example.com/video.mp4")]
        request = self.builder.build(
            model="test", prompt="添加特效", media_items=media,
            resolution="720p", aspect_ratio="16:9", duration=5,
        )
        self.assertEqual(request.task_type, "edit_video")
        self.assertEqual(len(request.media_items), 1)

    def test_build_no_media_raises(self):
        with self.assertRaises(ValidationError):
            self.builder.build(
                model="test", prompt="编辑视频", media_items=[],
                resolution="720p", aspect_ratio="16:9", duration=5,
            )

    def test_build_no_video_raises(self):
        img = [MediaItem(type=MediaType.IMAGE, url="http://example.com/img.jpg")]
        with self.assertRaises(ValidationError) as ctx:
            self.builder.build(
                model="test", prompt="编辑视频", media_items=img,
                resolution="720p", aspect_ratio="16:9", duration=5,
            )
        self.assertIn("视频", str(ctx.exception.errors))

    def test_build_audio_rejected(self):
        audio = [MediaItem(type=MediaType.AUDIO, url="http://example.com/audio.mp3")]
        with self.assertRaises(ValidationError):
            self.builder.build(
                model="test", prompt="编辑视频", media_items=audio,
                resolution="720p", aspect_ratio="16:9", duration=5,
            )

    def test_build_video_with_image_ok(self):
        media = [
            MediaItem(type=MediaType.VIDEO, url="http://example.com/v.mp4"),
            MediaItem(type=MediaType.IMAGE, url="http://example.com/i.jpg"),
        ]
        request = self.builder.build(
            model="test", prompt="编辑视频", media_items=media,
            resolution="720p", aspect_ratio="16:9", duration=5,
        )
        self.assertEqual(len(request.media_items), 2)

    def test_validate_returns_errors(self):
        errors = self.builder.validate(prompt="", media_items=[], duration=3, resolution="8k")
        self.assertGreater(len(errors), 0)


class TestExtendVideoBuilder(unittest.TestCase):
    """延长视频构建器测试"""

    def setUp(self):
        self.builder = ExtendVideoBuilder()

    def test_build_with_video_valid(self):
        media = [MediaItem(type=MediaType.VIDEO, url="http://example.com/video.mp4")]
        request = self.builder.build(
            model="test", prompt="延长视频", media_items=media,
            resolution="720p", aspect_ratio="16:9", duration=5,
        )
        self.assertEqual(request.task_type, "extend_video")

    def test_build_no_media_raises(self):
        with self.assertRaises(ValidationError):
            self.builder.build(
                model="test", prompt="延长视频", media_items=[],
                resolution="720p", aspect_ratio="16:9", duration=5,
            )

    def test_build_image_only_rejected(self):
        img = [MediaItem(type=MediaType.IMAGE, url="http://example.com/img.jpg")]
        with self.assertRaises(ValidationError) as ctx:
            self.builder.build(
                model="test", prompt="延长视频", media_items=img,
                resolution="720p", aspect_ratio="16:9", duration=5,
            )
        self.assertIn("视频", str(ctx.exception.errors))

    def test_build_video_with_audio_ok(self):
        media = [
            MediaItem(type=MediaType.VIDEO, url="http://example.com/v.mp4"),
            MediaItem(type=MediaType.AUDIO, url="http://example.com/a.mp3"),
        ]
        request = self.builder.build(
            model="test", prompt="延长视频", media_items=media,
            resolution="720p", aspect_ratio="16:9", duration=5,
        )
        self.assertEqual(len(request.media_items), 2)

    def test_validate_returns_errors(self):
        errors = self.builder.validate(prompt="", media_items=[], duration=16)
        self.assertGreater(len(errors), 0)


class TestTaskBuilderFactory(unittest.TestCase):
    """任务构建器工厂测试"""

    def test_register_and_get(self):
        TaskBuilderFactory.register("test_type", TextToVideoBuilder)
        self.assertIn("test_type", TaskBuilderFactory.registered_types())
        builder = TaskBuilderFactory.get("test_type")
        self.assertIsInstance(builder, TextToVideoBuilder)

    def test_get_unregistered_raises(self):
        with self.assertRaises(ValueError):
            TaskBuilderFactory.get("nonexistent")

    def test_registered_types_returns_all(self):
        TaskBuilderFactory.register("a", TextToVideoBuilder)
        TaskBuilderFactory.register("b", MultimodalRefBuilder)
        types = TaskBuilderFactory.registered_types()
        self.assertIn("a", types)
        self.assertIn("b", types)


if __name__ == "__main__":
    unittest.main()
