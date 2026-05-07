"""
任务用例单元测试。

使用 Mock 对象测试 TaskUseCase 的核心业务逻辑。
"""
from __future__ import annotations

import logging
import unittest
from unittest.mock import MagicMock, patch

from domain.entities import TaskRequest, TaskResult, Task
from domain.enums import TaskStatus
from domain.interfaces import IApiClient, ITaskRepository
from core.event_bus import EventBus
from core.exceptions import ApiError
from application.task_usecase import TaskUseCase


class TestTaskUseCase(unittest.TestCase):
    """任务用例测试"""

    def setUp(self):
        self.mock_api = MagicMock(spec=IApiClient)
        self.mock_repo = MagicMock(spec=ITaskRepository)
        self.event_bus = EventBus.instance()
        self.logger = logging.getLogger("test")
        self.logger.setLevel(logging.CRITICAL)
        self.usecase = TaskUseCase(self.mock_api, self.event_bus, self.logger, self.mock_repo)

    def test_create_task_success(self):
        self.mock_api.create_task.return_value = "task_123"

        request = TaskRequest(
            model="doubao-seedance-2-0-260128",
            task_type="text_to_video",
            prompt="一只猫",
            resolution="720p",
            aspect_ratio="16:9",
            duration=5,
        )
        task = self.usecase.create_task(request)

        self.assertEqual(task.task_id, "task_123")
        self.assertEqual(task.status, TaskStatus.PENDING)
        self.mock_api.create_task.assert_called_once_with(request)
        self.mock_repo.save.assert_called_once()

    def test_create_task_api_error(self):
        self.mock_api.create_task.side_effect = ApiError(code="401", message="Unauthorized")

        request = TaskRequest(model="test", task_type="text_to_video", prompt="猫")
        with self.assertRaises(ApiError):
            self.usecase.create_task(request)
        self.mock_repo.save.assert_not_called()

    def test_query_task_succeeded(self):
        result = TaskResult(
            task_id="task_123",
            status=TaskStatus.SUCCEEDED,
            video_url="http://example.com/video.mp4",
            token_usage=100,
        )
        self.mock_api.get_task.return_value = result

        task = self.usecase.query_task("task_123")

        self.assertEqual(task.status, TaskStatus.SUCCEEDED)
        self.assertEqual(task.video_url, "http://example.com/video.mp4")
        self.assertEqual(task.token_usage, 100)

    def test_query_task_failed(self):
        result = TaskResult(
            task_id="task_123",
            status=TaskStatus.FAILED,
            error_message="Generation error",
        )
        self.mock_api.get_task.return_value = result

        task = self.usecase.query_task("task_123")
        self.assertEqual(task.status, TaskStatus.FAILED)
        self.assertEqual(task.error_message, "Generation error")

    def test_query_task_api_error(self):
        self.mock_api.get_task.side_effect = ApiError(code="404", message="Not found")
        with self.assertRaises(ApiError):
            self.usecase.query_task("task_999")

    def test_cancel_task_success(self):
        self.usecase.cancel_task("task_123")
        self.mock_api.cancel_task.assert_called_once_with("task_123")
        self.mock_repo.update_status.assert_called_once_with("task_123", "cancelled")

    def test_cancel_task_api_error(self):
        self.mock_api.cancel_task.side_effect = ApiError(code="400", message="Bad request")
        with self.assertRaises(ApiError):
            self.usecase.cancel_task("task_123")

    def test_delete_task_success(self):
        self.usecase.delete_task("task_123")
        self.mock_repo.delete.assert_called_once_with("task_123")

    def test_delete_task_no_repo(self):
        usecase = TaskUseCase(self.mock_api, self.event_bus, self.logger, None)
        usecase.delete_task("task_123")

    def test_find_all_tasks(self):
        mock_tasks = [
            Task(
                task_id="t1", model="m", task_type="text_to_video",
                prompt="p", status=TaskStatus.SUCCEEDED,
                created_at=None,
            ),
        ]
        self.mock_repo.find_all.return_value = mock_tasks

        tasks = self.usecase.find_all_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].task_id, "t1")

    def test_find_all_tasks_no_repo(self):
        usecase = TaskUseCase(self.mock_api, self.event_bus, self.logger, None)
        tasks = usecase.find_all_tasks()
        self.assertEqual(tasks, [])


if __name__ == "__main__":
    unittest.main()
