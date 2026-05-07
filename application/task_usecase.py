"""
任务用例。

处理任务创建、查询、轮询等业务逻辑。
"""
from __future__ import annotations

import logging
from datetime import datetime

from domain.interfaces import IApiClient, ITaskRepository
from domain.entities import Task, TaskRequest
from domain.enums import TaskStatus
from core.event_bus import EventBus
from core.exceptions import ApiError


class TaskUseCase:
    """任务用例"""
    
    def __init__(self, api_client: IApiClient, event_bus: EventBus, logger: logging.Logger, task_repo: ITaskRepository | None = None):
        self._api_client = api_client
        self._event_bus = event_bus
        self._logger = logger
        self._task_repo = task_repo
    
    def create_task(self, request: TaskRequest) -> Task:
        """
        创建任务。
        
        Args:
            request: 任务请求对象
        Returns:
            Task: 任务实体
        Raises:
            ApiError: API 调用失败
            ValidationError: 参数校验失败
        """
        try:
            # 调用 API 创建任务
            task_id = self._api_client.create_task(request)
            
            # 构建任务实体
            task = Task(
                task_id=task_id,
                model=request.model,
                task_type=request.task_type,
                prompt=request.prompt,
                status=TaskStatus.PENDING,
                created_at=datetime.now(),
            )
            
            # 发送事件
            self._event_bus.task_created.emit(task_id)
            
            # 如果 task_repo 已注入，持久化到本地存储
            if self._task_repo is not None:
                self._task_repo.save(task)
            
            self._logger.info(f"Task created: task_id={task_id}")
            return task
            
        except ApiError as e:
            self._logger.error(f"Failed to create task: {e}")
            self._event_bus.error_occurred.emit(e.code, e.message)
            raise
    
    def query_task(self, task_id: str) -> Task:
        """
        查询任务状态。
        
        Args:
            task_id: 任务 ID
        Returns:
            Task: 任务实体
        Raises:
            ApiError: API 调用失败
        """
        try:
            result = self._api_client.get_task(task_id)
            
            # 构建任务实体
            task = Task(
                task_id=task_id,
                model="",  # 查询结果不包含模型信息
                task_type="",
                prompt="",
                status=result.status,
                created_at=datetime.now(),
                video_url=result.video_url,
                error_message=result.error_message,
                token_usage=result.token_usage,
                generation_time=result.generation_time,
            )
            
            # 发送状态更新事件
            self._event_bus.task_updated.emit(task_id, result.status.value)
            
            if result.status == TaskStatus.SUCCEEDED:
                self._event_bus.task_succeeded.emit(task_id, result.video_url or "")
            elif result.status == TaskStatus.FAILED:
                self._event_bus.task_failed.emit(task_id, result.error_message or "未知错误")
            
            return task
            
        except ApiError as e:
            self._logger.error(f"Failed to query task {task_id}: {e}")
            self._event_bus.error_occurred.emit(e.code, e.message)
            raise
    
    def find_all_tasks(self) -> list[Task]:
        """
        查询所有本地任务。
        
        Returns:
            任务列表
        Raises:
            StorageError: 查询失败
        """
        if self._task_repo is None:
            return []
        return self._task_repo.find_all()
    
    def delete_task(self, task_id: str) -> None:
        """
        删除本地任务记录。
        
        Args:
            task_id: 任务 ID
        Raises:
            StorageError: 删除失败
        """
        if self._task_repo is None:
            self._logger.warning("TaskRepo not injected, cannot delete task")
            return
        self._task_repo.delete(task_id)
        self._logger.info(f"Task deleted: task_id={task_id}")
    
    def cancel_task(self, task_id: str) -> None:
        """
        取消任务。
        
        Args:
            task_id: 任务 ID
        Raises:
            ApiError: API 调用失败
        """
        try:
            self._api_client.cancel_task(task_id)
            self._logger.info(f"Task cancelled: task_id={task_id}")
            
            if self._task_repo is not None:
                self._task_repo.update_status(task_id, TaskStatus.CANCELLED.value)
            
        except ApiError as e:
            self._logger.error(f"Failed to cancel task {task_id}: {e}")
            self._event_bus.error_occurred.emit(e.code, e.message)
            raise
