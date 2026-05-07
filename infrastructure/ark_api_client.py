"""
火山引擎 Ark API 客户端实现。

基于 volcengine-python-sdk 实现 IApiClient 接口。
"""
from __future__ import annotations

import logging

from volcenginesdkarkruntime import Ark

from domain.interfaces import IApiClient
from domain.entities import TaskRequest, TaskResult
from domain.enums import TaskStatus
from core.exceptions import ApiError
from infrastructure.config_store import ConfigStore


class ArkApiClient(IApiClient):
    """Ark API 客户端"""
    
    def __init__(self, config: ConfigStore, logger: logging.Logger):
        self._config = config
        self._logger = logger
        self._client = None
    
    def _get_client(self) -> Ark:
        """获取或创建 Ark 客户端实例"""
        api_key = self._config.get("api_key")
        base_url = self._config.get("base_url")
        
        if not api_key:
            raise ApiError("CONFIG_ERROR", "API Key 未配置")
        
        if self._client is None:
            self._client = Ark(api_key=api_key, base_url=base_url)
            self._logger.info(f"Ark client initialized: base_url={base_url}")
        
        return self._client
    
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
        self._logger.info(
            f"Creating task: model={request.model}, type={request.task_type}, "
            f"prompt_length={len(request.prompt)}"
        )
        
        try:
            client = self._get_client()
            
            # 构建 content 数组（官方 API 格式）
            content = []
            
            # 文本提示词
            text_entry = {"type": "text", "text": request.prompt}
            content.append(text_entry)
            
            # 添加媒体素材
            if request.media_items:
                for item in request.media_items:
                    media_url = item.url if not item.asset_id else f"asset://{item.asset_id}"
                    if item.type.value == "image":
                        content.append({
                            "type": "image_url",
                            "image_url": {"url": media_url},
                            "role": "reference_image",
                        })
                    elif item.type.value == "video":
                        content.append({
                            "type": "video_url",
                            "video_url": {"url": media_url},
                            "role": "reference_video",
                        })
                    elif item.type.value == "audio":
                        content.append({
                            "type": "audio_url",
                            "audio_url": {"url": media_url},
                            "role": "reference_audio",
                        })
            
            # 构建请求参数
            params = {
                "model": request.model,
                "content": content,
            }
            
            extra_body = {}
            
            if request.resolution:
                extra_body["resolution"] = request.resolution
            
            extra_body["generate_audio"] = request.generate_audio
            extra_body["ratio"] = request.aspect_ratio
            extra_body["duration"] = request.duration
            extra_body["watermark"] = request.watermark
            
            if request.web_search:
                extra_body["tools"] = [{"type": "web_search"}]
            
            if request.offline_inference:
                extra_body["service_tier"] = "flex"
            
            if extra_body:
                params["extra_body"] = extra_body
            
            # 调用 API
            response = client.content_generation.tasks.create(**params)
            
            task_id = response.id
            self._logger.info(f"Task created successfully: task_id={task_id}")
            return task_id
            
        except Exception as e:
            error_msg = str(e)
            self._logger.error(f"API call failed: {error_msg}", exc_info=True)
            
            # 尝试提取错误码
            error_code = "API_ERROR"
            if hasattr(e, "status_code"):
                error_code = str(e.status_code)
            
            raise ApiError(code=error_code, message=error_msg) from e
    
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
        self._logger.info(f"Querying task: task_id={task_id}")
        
        try:
            client = self._get_client()
            response = client.content_generation.tasks.get(task_id=task_id)
            
            # 解析状态
            status_map = {
                "queued": TaskStatus.QUEUED,
                "running": TaskStatus.RUNNING,
                "cancelled": TaskStatus.CANCELLED,
                "succeeded": TaskStatus.SUCCEEDED,
                "failed": TaskStatus.FAILED,
                "expired": TaskStatus.EXPIRED,
            }
            status = status_map.get(response.status, TaskStatus.FAILED)
            
            # 解析嵌套字段（官方 API 结构）
            video_url = None
            if hasattr(response, "content") and response.content:
                video_url = getattr(response.content, "video_url", None)
            
            error_message = None
            if hasattr(response, "error") and response.error:
                error_code = getattr(response.error, "code", "")
                error_msg = getattr(response.error, "message", "")
                if error_code or error_msg:
                    error_message = f"[{error_code}] {error_msg}" if error_code else error_msg
            
            token_usage = None
            if hasattr(response, "usage") and response.usage:
                token_usage = getattr(response.usage, "completion_tokens", None)
            
            generation_time = None
            if hasattr(response, "updated_at") and hasattr(response, "created_at"):
                generation_time = response.updated_at - response.created_at
            
            # 构建结果对象
            result = TaskResult(
                task_id=task_id,
                status=status,
                video_url=video_url,
                error_message=error_message,
                token_usage=token_usage,
                generation_time=generation_time,
            )
            
            self._logger.info(f"Task query result: task_id={task_id}, status={status.value}")
            return result
            
        except Exception as e:
            error_msg = str(e)
            self._logger.error(f"Failed to query task {task_id}: {error_msg}", exc_info=True)
            
            error_code = "API_ERROR"
            if hasattr(e, "status_code"):
                error_code = str(e.status_code)
            
            raise ApiError(code=error_code, message=error_msg) from e
    
    def test_connection(self) -> tuple[bool, str]:
        """
        测试 API 连通性。
        
        Returns:
            (是否成功, 消息)
        """
        api_key = self._config.get("api_key")
        if not api_key:
            return False, "API Key 未配置"
        
        base_url = self._config.get("base_url")
        self._logger.info(f"Testing API connection: base_url={base_url}")
        
        try:
            client = self._get_client()
            try:
                response = client.content_generation.tasks.get(task_id="__connection_test__")
            except Exception as api_error:
                error_msg = str(api_error).lower()
                if "not found" in error_msg or "invalid" in error_msg or "does not exist" in error_msg:
                    self._logger.info("API connection test passed (endpoint reachable)")
                    return True, "连接成功"
                raise api_error
            
            self._logger.info("API connection test passed")
            return True, "连接成功"
            
        except Exception as e:
            error_msg = str(e)
            self._logger.error(f"API connection test failed: {error_msg}")
            
            if "401" in error_msg or "403" in error_msg or "unauthorized" in error_msg.lower() or "invalid_api_key" in error_msg.lower():
                return False, f"API Key 无效: {error_msg[:200]}"
            elif "timeout" in error_msg.lower() or "connection" in error_msg.lower() or "refused" in error_msg.lower():
                return False, f"网络连接失败: {error_msg[:200]}"
            else:
                return False, f"连接测试失败: {error_msg[:200]}"
    
    def cancel_task(self, task_id: str) -> None:
        """
        取消任务。
        
        Args:
            task_id: 任务 ID
        Raises:
            ApiError: API 调用失败
        """
        self._logger.info(f"Cancelling task: task_id={task_id}")
        
        try:
            client = self._get_client()
            client.content_generation.tasks.delete(task_id)
            self._logger.info(f"Task deleted: task_id={task_id}")
            
        except Exception as e:
            error_msg = str(e)
            self._logger.error(f"Failed to cancel task {task_id}: {error_msg}", exc_info=True)
            
            error_code = "API_ERROR"
            if hasattr(e, "status_code"):
                error_code = str(e.status_code)
            
            raise ApiError(code=error_code, message=error_msg) from e
