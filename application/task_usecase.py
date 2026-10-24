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
            # （save 失败降级为 warning：API 已成功创建，不能因本地持久化失败丢失任务）
            if self._task_repo is not None:
                try:
                    self._task_repo.save(task)
                except Exception as e:
                    self._logger.warning(
                        f"Failed to persist task {task_id} locally, continue: {e}"
                    )
            
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
            
            # 持久化最新状态（失败仅 warning，不影响返回）
            if self._task_repo is not None:
                try:
                    self._task_repo.update_status(
                        task_id,
                        result.status.value,
                        video_url=result.video_url,
                        error_message=result.error_message,
                        token_usage=result.token_usage,
                        generation_time=result.generation_time,
                    )
                except Exception as e:
                    self._logger.warning(
                        f"Failed to persist status for task {task_id}: {e}"
                    )
            
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
    
    def sync_recent_tasks(self) -> int:
        """
        从平台同步最近 7 天内的任务到本地仓储。

        调用 list_tasks 获取平台任务列表，对本地不存在的任务新建实体保存，
        已存在的任务若状态有变化则同步更新。

        注意：内部为同步 API 调用，应在 UI 主线程之外或调用方自行负责线程。

        Returns:
            int: 本次新增的本地任务数量
        Raises:
            ApiError: list_tasks 调用失败（由调用方处理）
        """
        self._logger.info("Syncing recent tasks from platform")
        
        if self._task_repo is None:
            self._logger.warning("TaskRepo not injected, skip sync_recent_tasks")
            return 0
        
        results = self._api_client.list_tasks(page_num=1, page_size=50)
        
        new_count = 0
        for result in results:
            existing = self._task_repo.find_by_id(result.task_id)
            if existing is None:
                # 本地不存在：构造 Task 实体保存（prompt 平台不回传，留空）
                created_at = (
                    datetime.fromtimestamp(result.created_at)
                    if result.created_at
                    else datetime.now()
                )
                task = Task(
                    task_id=result.task_id,
                    model=result.model or "",
                    task_type="multimodal_ref",  # 平台列表不回传任务类型，占位
                    prompt="",
                    status=result.status,
                    created_at=created_at,
                    video_url=result.video_url,
                    error_message=result.error_message,
                    token_usage=result.token_usage,
                    generation_time=result.generation_time,
                )
                try:
                    self._task_repo.save(task)
                    new_count += 1
                except Exception as e:
                    self._logger.warning(
                        f"Failed to save synced task {result.task_id}: {e}"
                    )
            elif existing.status != result.status:
                # 状态有变化：同步更新
                try:
                    self._task_repo.update_status(
                        result.task_id,
                        result.status.value,
                        video_url=result.video_url,
                        error_message=result.error_message,
                        token_usage=result.token_usage,
                        generation_time=result.generation_time,
                    )
                except Exception as e:
                    self._logger.warning(
                        f"Failed to update synced task {result.task_id}: {e}"
                    )
        
        self._logger.info(
            f"Sync recent tasks finished: fetched={len(results)}, new={new_count}"
        )
        return new_count
    
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
