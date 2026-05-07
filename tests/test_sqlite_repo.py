"""
SQLite 任务仓储单元测试。

使用临时数据库测试 SqliteTaskRepository 的 CRUD 操作。
"""
from __future__ import annotations

import logging
import os
import unittest
import tempfile
from datetime import datetime
from unittest.mock import patch

from domain.entities import Task
from domain.enums import TaskStatus
from infrastructure.sqlite_task_repo import SqliteTaskRepository


class TestSqliteTaskRepository(unittest.TestCase):
    """SQLite 任务仓储测试"""

    @classmethod
    def setUpClass(cls):
        cls.tmp_dir = tempfile.mkdtemp()
        cls.original_env = os.environ.get("APPDATA", "")
        os.environ["APPDATA"] = cls.tmp_dir

    @classmethod
    def tearDownClass(cls):
        os.environ["APPDATA"] = cls.original_env
        import shutil
        shutil.rmtree(cls.tmp_dir, ignore_errors=True)

    def setUp(self):
        self.logger = logging.getLogger("test")
        self.logger.setLevel(logging.CRITICAL)
        self.repo = SqliteTaskRepository(self.logger)

    def _make_task(self, task_id="t1", status=TaskStatus.PENDING, video_url=None):
        return Task(
            task_id=task_id,
            model="doubao-seedance-2-0-260128",
            task_type="text_to_video",
            prompt="test prompt",
            status=status,
            created_at=datetime.now(),
            video_url=video_url,
        )

    def test_save_and_find_by_id(self):
        task = self._make_task()
        self.repo.save(task)

        found = self.repo.find_by_id("t1")
        self.assertIsNotNone(found)
        self.assertEqual(found.task_id, "t1")
        self.assertEqual(found.model, "doubao-seedance-2-0-260128")
        self.assertEqual(found.status, TaskStatus.PENDING)

    def test_find_by_id_not_found(self):
        found = self.repo.find_by_id("nonexistent")
        self.assertIsNone(found)

    def test_find_all(self):
        self.repo.save(self._make_task("t1"))
        self.repo.save(self._make_task("t2", TaskStatus.SUCCEEDED))

        tasks = self.repo.find_all()
        self.assertGreaterEqual(len(tasks), 2)

    def test_update_status(self):
        self.repo.save(self._make_task("t1"))
        self.repo.update_status("t1", TaskStatus.SUCCEEDED.value, video_url="http://example.com/v.mp4")

        updated = self.repo.find_by_id("t1")
        self.assertEqual(updated.status, TaskStatus.SUCCEEDED)
        self.assertEqual(updated.video_url, "http://example.com/v.mp4")

    def test_update_status_bulk(self):
        self.repo.save(self._make_task("t_bulk"))
        self.repo.update_status(
            "t_bulk", TaskStatus.FAILED.value,
            error_message="Something broke",
            token_usage=500,
            generation_time=12.5,
        )
        updated = self.repo.find_by_id("t_bulk")
        self.assertEqual(updated.status, TaskStatus.FAILED)
        self.assertEqual(updated.error_message, "Something broke")
        self.assertEqual(updated.token_usage, 500)
        self.assertEqual(updated.generation_time, 12.5)

    def test_delete(self):
        self.repo.save(self._make_task("to_delete"))
        self.repo.delete("to_delete")
        self.assertIsNone(self.repo.find_by_id("to_delete"))

    def test_save_overwrites(self):
        """INSERT OR REPLACE: 重复保存应覆盖旧记录"""
        task1 = self._make_task("t_overwrite", TaskStatus.PENDING)
        self.repo.save(task1)
        found = self.repo.find_by_id("t_overwrite")
        self.assertEqual(found.status, TaskStatus.PENDING)

        task2 = self._make_task("t_overwrite", TaskStatus.SUCCEEDED, video_url="http://v.mp4")
        self.repo.save(task2)
        found = self.repo.find_by_id("t_overwrite")
        self.assertEqual(found.status, TaskStatus.SUCCEEDED)
        self.assertEqual(found.video_url, "http://v.mp4")

    def test_empty_find_all(self):
        repo = SqliteTaskRepository(self.logger)
        tasks = repo.find_all()
        self.assertIsInstance(tasks, list)


if __name__ == "__main__":
    unittest.main()
