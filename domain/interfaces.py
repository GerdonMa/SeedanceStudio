"""
领域层接口定义。

定义各层之间的抽象接口，实现依赖倒置。
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from domain.entities import TaskRequest, TaskResult, Task


class IApiClient(ABC):
    """API 客户端接口"""
    
    @abstractmethod
    def create_task(self, request: TaskRequest) -> str:
        """
        创建视频生成任务。
        
        Args:
            request: 任务请求对象
        Returns:
            task_id: 平台返回的任务 ID
        Raises:
            ApiError: API 调用失败
        """
        pass
    
    @abstractmethod
    def get_task(self, task_id: str) -> TaskResult:
        """
        查询任务状态和结果。
        
        Args:
            task_id: 任务 ID
        Returns:
            TaskResult: 任务结果对象
        Raises:
            ApiError: API 调用失败
        """
        pass
    
    @abstractmethod
    def list_tasks(self, page_num: int = 1, page_size: int = 20) -> list[TaskResult]:
        """
        查询平台上最近 7 天内的视频生成任务列表（用于本地任务恢复/同步）。

        Args:
            page_num: 页码（1~500）
            page_size: 每页数量（1~500）
        Returns:
            list[TaskResult]: 任务结果列表（含 model / created_at）
        Raises:
            ApiError: API 调用失败
        """
        pass

    @abstractmethod
    def cancel_task(self, task_id: str) -> None:
        """
        取消任务。
        
        Args:
            task_id: 任务 ID
        Raises:
            ApiError: API 调用失败
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> tuple[bool, str]:
        """
        测试 API 连通性。
        
        Returns:
            (是否成功, 消息)
        """
        pass


class ITaskRepository(ABC):
    """任务仓储接口"""
    
    @abstractmethod
    def save(self, task: Task) -> None:
        """
        保存任务到本地存储。
        
        Args:
            task: 任务实体
        Raises:
            StorageError: 存储失败
        """
        pass
    
    @abstractmethod
    def find_all(self) -> list[Task]:
        """
        查询所有任务。
        
        Returns:
            任务列表
        Raises:
            StorageError: 查询失败
        """
        pass
    
    @abstractmethod
    def find_by_id(self, task_id: str) -> Task | None:
        """
        根据 ID 查询任务。
        
        Args:
            task_id: 任务 ID
        Returns:
            任务实体，不存在则返回 None
        Raises:
            StorageError: 查询失败
        """
        pass
    
    @abstractmethod
    def update_status(self, task_id: str, status: str, **kwargs) -> None:
        """
        更新任务状态。
        
        Args:
            task_id: 任务 ID
            status: 新状态
            **kwargs: 其他需要更新的字段（video_url, error_message 等）
        Raises:
            StorageError: 更新失败
        """
        pass
    
    @abstractmethod
    def delete(self, task_id: str) -> None:
        """
        删除任务。
        
        Args:
            task_id: 任务 ID
        Raises:
            StorageError: 删除失败
        """
        pass


class IAssetRepository(ABC):
    """资产库接口（P4 阶段实现）"""
    
    @abstractmethod
    def list_assets(self) -> list[dict]:
        """列出所有资产"""
        pass
    
    @abstractmethod
    def upload_asset(self, file_path: str) -> str:
        """上传资产，返回 asset_id"""
        pass
    
    @abstractmethod
    def get_asset_status(self, asset_id: str) -> str:
        """查询资产审核状态"""
        pass
    
    @abstractmethod
    def get_reject_reason(self, asset_id: str) -> str:
        """获取资产审核被拒原因"""
        pass
