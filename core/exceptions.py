"""
统一异常定义。

定义项目中使用的所有自定义异常类型。
"""
from __future__ import annotations


class ApiError(Exception):
    """API 调用失败异常"""
    
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")


class StorageError(Exception):
    """存储操作失败异常（数据库、文件系统）"""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ValidationError(Exception):
    """表单校验失败异常"""
    
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__(f"Validation failed: {', '.join(errors)}")
