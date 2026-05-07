"""
SQLite 任务仓储实现。

基于 sqlite3 实现 ITaskRepository 接口，持久化任务历史。
"""
from __future__ import annotations

import os
import sqlite3
import logging
from datetime import datetime
from pathlib import Path

from domain.interfaces import ITaskRepository
from domain.entities import Task
from domain.enums import TaskStatus
from core.exceptions import StorageError


class SqliteTaskRepository(ITaskRepository):
    """SQLite 任务仓储"""

    def __init__(self, logger: logging.Logger):
        self._logger = logger
        self._db_path = self._get_db_path()
        self._init_db()

    def _get_db_path(self) -> Path:
        db_dir = Path(os.getenv("APPDATA", Path.home())) / "SeedanceStudio"
        db_dir.mkdir(parents=True, exist_ok=True)
        return db_dir / "seedance_tasks.db"

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        try:
            conn = self._get_conn()
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    model TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT,
                    video_url TEXT,
                    error_message TEXT,
                    token_usage INTEGER,
                    generation_time REAL
                )
            """)
            conn.commit()
            conn.close()
            self._logger.info(f"Database initialized: {self._db_path}")
        except sqlite3.Error as e:
            self._logger.error(f"Database init failed: {e}")
            raise StorageError(f"数据库初始化失败: {e}") from e

    def save(self, task: Task) -> None:
        conn = None
        try:
            conn = self._get_conn()
            conn.execute(
                """INSERT OR REPLACE INTO tasks 
                   (task_id, model, task_type, prompt, status, created_at, updated_at,
                    video_url, error_message, token_usage, generation_time)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    task.task_id,
                    task.model,
                    task.task_type,
                    task.prompt,
                    task.status.value,
                    task.created_at.isoformat() if task.created_at else None,
                    task.updated_at.isoformat() if task.updated_at else None,
                    task.video_url,
                    task.error_message,
                    task.token_usage,
                    task.generation_time,
                ),
            )
            conn.commit()
            self._logger.info(f"Task saved: task_id={task.task_id}")
        except sqlite3.Error as e:
            self._logger.error(f"Failed to save task {task.task_id}: {e}")
            raise StorageError(f"任务保存失败: {e}") from e
        finally:
            if conn:
                conn.close()

    def find_all(self) -> list[Task]:
        conn = None
        try:
            conn = self._get_conn()
            rows = conn.execute(
                "SELECT * FROM tasks ORDER BY created_at DESC"
            ).fetchall()
            return [self._row_to_task(r) for r in rows]
        except sqlite3.Error as e:
            self._logger.error(f"Failed to query tasks: {e}")
            raise StorageError(f"查询任务列表失败: {e}") from e
        finally:
            if conn:
                conn.close()

    def find_by_id(self, task_id: str) -> Task | None:
        conn = None
        try:
            conn = self._get_conn()
            row = conn.execute(
                "SELECT * FROM tasks WHERE task_id = ?", (task_id,)
            ).fetchone()
            if row is None:
                return None
            return self._row_to_task(row)
        except sqlite3.Error as e:
            self._logger.error(f"Failed to query task {task_id}: {e}")
            raise StorageError(f"查询任务失败: {e}") from e
        finally:
            if conn:
                conn.close()

    def update_status(self, task_id: str, status: str, **kwargs) -> None:
        conn = None
        try:
            conn = self._get_conn()

            updates = ["status = ?", "updated_at = ?"]
            params = [status, datetime.now().isoformat()]

            if "video_url" in kwargs:
                updates.append("video_url = ?")
                params.append(kwargs["video_url"])
            if "error_message" in kwargs:
                updates.append("error_message = ?")
                params.append(kwargs["error_message"])
            if "token_usage" in kwargs:
                updates.append("token_usage = ?")
                params.append(kwargs["token_usage"])
            if "generation_time" in kwargs:
                updates.append("generation_time = ?")
                params.append(kwargs["generation_time"])

            params.append(task_id)
            sql = f"UPDATE tasks SET {', '.join(updates)} WHERE task_id = ?"
            conn.execute(sql, params)
            conn.commit()
            self._logger.info(f"Task status updated: task_id={task_id}, status={status}")
        except sqlite3.Error as e:
            self._logger.error(f"Failed to update task {task_id}: {e}")
            raise StorageError(f"更新任务状态失败: {e}") from e
        finally:
            if conn:
                conn.close()

    def delete(self, task_id: str) -> None:
        conn = None
        try:
            conn = self._get_conn()
            conn.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
            conn.commit()
            self._logger.info(f"Task deleted: task_id={task_id}")
        except sqlite3.Error as e:
            self._logger.error(f"Failed to delete task {task_id}: {e}")
            raise StorageError(f"删除任务失败: {e}") from e
        finally:
            if conn:
                conn.close()

    def _row_to_task(self, row: sqlite3.Row) -> Task:
        return Task(
            task_id=row["task_id"],
            model=row["model"],
            task_type=row["task_type"],
            prompt=row["prompt"],
            status=TaskStatus(row["status"]),
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.now(),
            updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None,
            video_url=row["video_url"],
            error_message=row["error_message"],
            token_usage=row["token_usage"],
            generation_time=row["generation_time"],
        )
