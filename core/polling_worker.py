"""
后台任务轮询 Worker。

使用 QThread 定期查询进行中的任务状态，通过 EventBus 广播变更。
"""
from __future__ import annotations

import logging

from PyQt6.QtCore import QThread, pyqtSignal

from domain.interfaces import IApiClient, ITaskRepository
from domain.enums import TaskStatus
from core.event_bus import EventBus


_POLLING_INTERVAL_SECONDS = 30
_POLLING_STATUSES = {TaskStatus.QUEUED, TaskStatus.PENDING, TaskStatus.RUNNING}


class PollingWorker(QThread):
    """后台任务轮询工作线程"""

    poll_completed = pyqtSignal()

    def __init__(
        self,
        api_client: IApiClient,
        task_repo: ITaskRepository,
        event_bus: EventBus,
        logger: logging.Logger,
    ):
        super().__init__()
        self._api_client = api_client
        self._task_repo = task_repo
        self._event_bus = event_bus
        self._logger = logger
        self._running = True

    def run(self):
        self._logger.info("PollingWorker started")
        while self._running:
            try:
                self._poll_all()
            except Exception as e:
                self._logger.error(f"Polling error: {e}", exc_info=True)
                self._event_bus.error_occurred.emit("POLL_ERROR", str(e))

            QThread.sleep(_POLLING_INTERVAL_SECONDS)

    def _poll_all(self):
        tasks = self._task_repo.find_all()
        active_tasks = [t for t in tasks if t.status in _POLLING_STATUSES]

        for task in active_tasks[:]:
            try:
                result = self._api_client.get_task(task.task_id)

                if result.status != task.status:
                    self._logger.info(
                        f"Task status changed: task_id={task.task_id}, "
                        f"{task.status.value} -> {result.status.value}"
                    )

                    kwargs = {}
                    if result.video_url:
                        kwargs["video_url"] = result.video_url
                    if result.error_message:
                        kwargs["error_message"] = result.error_message
                    if result.token_usage:
                        kwargs["token_usage"] = result.token_usage
                    if result.generation_time:
                        kwargs["generation_time"] = result.generation_time

                    self._task_repo.update_status(
                        task.task_id,
                        result.status.value,
                        **kwargs,
                    )

                    self._event_bus.task_updated.emit(
                        task.task_id, result.status.value
                    )

                    if result.status == TaskStatus.SUCCEEDED:
                        self._event_bus.task_succeeded.emit(
                            task.task_id, result.video_url or ""
                        )
                    elif result.status == TaskStatus.FAILED:
                        self._event_bus.task_failed.emit(
                            task.task_id, result.error_message or "未知错误"
                        )

            except Exception as e:
                self._logger.error(
                    f"Failed to poll task {task.task_id}: {e}", exc_info=True
                )

        self.poll_completed.emit()

    def stop(self):
        self._running = False
        self._logger.info("PollingWorker stopping")
        self.wait()
        self._logger.info("PollingWorker stopped")
