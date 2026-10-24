"""
火山引擎 Ark API 客户端实现。

基于 volcengine-python-sdk 实现 IApiClient 接口。
"""
from __future__ import annotations

import base64
import logging
import mimetypes
from pathlib import Path

from volcenginesdkarkruntime import Ark

from domain.interfaces import IApiClient
from domain.model_capabilities import get_capability
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
    
    def _resolve_media_url(self, url: str) -> str:
        if url.startswith(("http://", "https://", "asset://", "data:")):
            return url
        path = Path(url)
        if not path.is_file():
            raise ApiError("FILE_NOT_FOUND", f"文件不存在: {url}")
        mime, _ = mimetypes.guess_type(str(path))
        if mime is None:
            mime = "application/octet-stream"
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        return f"data:{mime};base64,{b64}"

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
            
            # 文本提示词（多模态场景下官方允许省略，仅非空时下发）
            if request.prompt and request.prompt.strip():
                content.append({"type": "text", "text": request.prompt})
            
            # 添加媒体素材
            if request.media_items:
                for item in request.media_items:
                    raw_url = item.url if not item.asset_id else f"asset://{item.asset_id}"
                    media_url = self._resolve_media_url(raw_url)
                    if item.type.value == "image":
                        content.append({
                            "type": "image_url",
                            "image_url": {"url": media_url},
                            "role": item.role or "reference_image",
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
            extra_body["duration"] = request.duration  # -1 原样下发（智能时长）
            extra_body["watermark"] = request.watermark
            
            # 随机种子（-1 表示随机，官方允许显式下发）
            if request.seed is not None:
                extra_body["seed"] = request.seed
            
            # 输出格式（mp4 为默认，仅支持 mov 的模型且显式要求 mov 时下发）
            capability = get_capability(request.model)
            if request.output_format == "mov" and capability.supports_mov:
                extra_body["output_format"] = "mov"
            
            # 尾帧图返回（连续生成用）
            if request.return_last_frame:
                extra_body["return_last_frame"] = True
            
            # Seedance 2.5 编辑/延长任务类型声明
            if request.model.startswith("doubao-seedance-2-5"):
                if request.task_type == "edit_video":
                    extra_body["omni_reference_task_type"] = "edit"
                elif request.task_type == "extend_video":
                    extra_body["omni_reference_task_type"] = "extend"
            
            if request.web_search:
                extra_body["tools"] = [{"type": "web_search"}]
            
            # 离线推理（仅支持 flex 的模型才下发，避免无效参数）
            if request.offline_inference and capability.supports_flex:
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
    
    def _parse_task_response(self, response, task_id: str) -> TaskResult:
        """
        将 SDK 任务响应对象解析为 TaskResult（get_task / list_tasks 共用）。

        Args:
            response: SDK 任务响应对象（单个任务）
            task_id: 任务 ID（list 场景取 response.id，此处由调用方传入）
        Returns:
            TaskResult: 任务结果对象
        """
        # 解析状态（未知状态记 warning 后按 FAILED 处理）
        status_map = {
            "queued": TaskStatus.QUEUED,
            "running": TaskStatus.RUNNING,
            "cancelled": TaskStatus.CANCELLED,
            "succeeded": TaskStatus.SUCCEEDED,
            "failed": TaskStatus.FAILED,
            "expired": TaskStatus.EXPIRED,
        }
        raw_status = getattr(response, "status", None)
        status = status_map.get(raw_status)
        if status is None:
            self._logger.warning(
                f"Unknown task status from API: task_id={task_id}, status={raw_status!r}, "
                f"mapped to FAILED"
            )
            status = TaskStatus.FAILED
        
        # 解析嵌套字段（官方 API 结构）
        video_url = None
        last_frame_url = None
        if hasattr(response, "content") and response.content:
            video_url = getattr(response.content, "video_url", None)
            last_frame_url = getattr(response.content, "last_frame_url", None)
        
        error_message = None
        if hasattr(response, "error") and response.error:
            error_code = getattr(response.error, "code", "")
            error_msg = getattr(response.error, "message", "")
            if error_code or error_msg:
                error_message = f"[{error_code}] {error_msg}" if error_code else error_msg
        
        token_usage = None
        total_tokens = None
        if hasattr(response, "usage") and response.usage:
            token_usage = getattr(response.usage, "completion_tokens", None)
            total_tokens = getattr(response.usage, "total_tokens", None)
        
        model = getattr(response, "model", None)
        created_at = getattr(response, "created_at", None)
        
        generation_time = None
        if hasattr(response, "updated_at") and hasattr(response, "created_at"):
            try:
                generation_time = response.updated_at - response.created_at
            except TypeError:
                generation_time = None
        
        # 构建结果对象
        return TaskResult(
            task_id=task_id,
            status=status,
            video_url=video_url,
            last_frame_url=last_frame_url,
            error_message=error_message,
            token_usage=token_usage,
            total_tokens=total_tokens,
            generation_time=generation_time,
            model=model,
            created_at=created_at,
        )
    
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
            
            result = self._parse_task_response(response, task_id)
            
            self._logger.info(f"Task query result: task_id={task_id}, status={result.status.value}")
            return result
            
        except Exception as e:
            error_msg = str(e)
            self._logger.error(f"Failed to query task {task_id}: {error_msg}", exc_info=True)
            
            error_code = "API_ERROR"
            if hasattr(e, "status_code"):
                error_code = str(e.status_code)
            
            raise ApiError(code=error_code, message=error_msg) from e
    
    def list_tasks(self, page_num: int = 1, page_size: int = 20) -> list[TaskResult]:
        """
        查询平台上最近 7 天内的视频生成任务列表。

        Args:
            page_num: 页码（1~500）
            page_size: 每页数量（1~500）
        Returns:
            list[TaskResult]: 任务结果列表
        Raises:
            ApiError: API 调用失败
        """
        self._logger.info(f"Listing tasks: page_num={page_num}, page_size={page_size}")
        
        try:
            client = self._get_client()
            response = client.content_generation.tasks.list(
                page_num=page_num, page_size=page_size
            )
            
            results: list[TaskResult] = []
            items = getattr(response, "items", None) or []
            for item in items:
                item_id = getattr(item, "id", None)
                if not item_id:
                    self._logger.warning("Skipped list item without id")
                    continue
                results.append(self._parse_task_response(item, item_id))
            
            self._logger.info(
                f"Task list fetched: total={getattr(response, 'total', None)}, "
                f"parsed={len(results)}"
            )
            return results
            
        except Exception as e:
            error_msg = str(e)
            self._logger.error(f"Failed to list tasks: {error_msg}", exc_info=True)
            
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
