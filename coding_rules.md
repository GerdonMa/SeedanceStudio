# Seedance Studio — AI 开发编码规范

> **每次开始新任务前必须阅读本文件。**  
> 本规范与 `plan.md`（架构设计）、`todo.md`（任务清单）、`testing_rules.md`（测试与验收）配合使用。

---

## 一、项目上下文速览

- 语言：Python 3.12，UI：PyQt6，API SDK：volcengine-python-sdk[ark]
- 四层架构：`domain` → `application` → `infrastructure` + `ui`，通过 `core` 共享基础设施
- 项目根目录：`seedance-studio/`
- 详细架构见 `plan.md` 第三章，目录结构见第六章

---

## 二、层间依赖规则（最重要）

```
允许的 import 方向：
  ui          -> application, domain, core
  application -> domain, core
  infrastructure -> domain, core
  domain      -> core（仅 exceptions）
  core        -> 无内部依赖

禁止的 import：
  domain      -> application / infrastructure / ui
  application -> infrastructure / ui
  ui          -> infrastructure（严禁直接 import ArkApiClient 等）
  任何层       -> ui（ui 只被 main.py 引用）
```

违反层间依赖是最严重的架构错误，发现时必须重构，不得绕过。

---

## 三、命名约定

| 类型 | 规范 | 示例 |
|------|------|------|
| 文件名 | `snake_case.py` | `ark_api_client.py` |
| 类名 | `PascalCase` | `ArkApiClient`, `TaskUseCase` |
| 接口/抽象类 | `I` 前缀 + PascalCase | `IApiClient`, `ITaskRepository` |
| 方法名 | `snake_case` | `create_task`, `save_preference` |
| 变量名 | `snake_case` | `task_id`, `video_url` |
| 常量 | `UPPER_SNAKE_CASE` | `DEFAULT_POLL_INTERVAL = 30` |
| Qt Signal | `snake_case` | `task_created`, `error_occurred` |
| 私有属性/方法 | 单下划线前缀 | `self._config`, `self._poll()` |
| 类型别名 | `PascalCase` | `TaskId = str` |

---

## 四、异常处理规范

### 各层职责

```
infrastructure 层：
  - 捕获所有外部异常（SDK 异常、sqlite3 异常、网络异常）
  - 转换为 core/exceptions.py 中定义的异常类型后向上抛出
  - 禁止吞掉异常（空 except 块）

application 层：
  - 捕获 infrastructure 抛出的异常
  - 通过 EventBus 广播错误，或向上抛出给 UI 层处理
  - 不直接操作 UI

ui 层：
  - 捕获 application 层异常，显示友好提示
  - 禁止将原始异常堆栈直接展示给用户
```

### 异常类型

```python
# core/exceptions.py 中定义
ApiError(code, message)      # API 调用失败、超时、认证错误
StorageError(message)        # 数据库读写失败、文件操作失败
ValidationError(errors: list[str])  # 表单校验失败，errors 为错误列表
```

### 示例

```python
# infrastructure 层 - 正确写法
def create_task(self, request: TaskRequest) -> str:
    try:
        resp = self._client.content_generation.tasks.create(...)
        return resp.id
    except ArkAPIError as e:
        raise ApiError(code=str(e.status_code), message=str(e)) from e
    except Exception as e:
        raise ApiError(code="UNKNOWN", message=str(e)) from e

# 错误写法 - 禁止
def create_task(self, request):
    try:
        ...
    except:  # 禁止空 except
        pass
```

---

## 五、Qt 线程规则

1. **子线程（QThread）中严禁直接操作任何 UI 控件**，包括 setText、setVisible、append 等
2. 子线程与主线程通信唯一方式：通过 `EventBus` 发射 Signal
3. `PollingWorker` 内部所有代码必须被 try/except 包裹，异常通过 Signal 广播，不能让线程崩溃
4. UI 层订阅 Signal 时使用 `connect`，槽函数在主线程执行，可以安全操作 UI

```python
# 子线程中 - 正确
self.event_bus.error_occurred.emit("POLL_ERROR", str(e))

# 子线程中 - 禁止
self.some_label.setText("error")  # 直接操作 UI 控件
```

---

## 六、偏好持久化接入模板

每个需要记忆状态的控件，按以下模板接入，两行代码完成：

```python
# 在页面/组件的 __init__ 或 _setup_ui 末尾，恢复上次的值
prefs = self._settings_usecase.load_preferences()
self.model_combo.setCurrentText(prefs.get("default_model", "doubao-seedance-2-0-260128"))
self.resolution_combo.setCurrentText(prefs.get("default_resolution", "720p"))
self.asset_mode_checkbox.setChecked(prefs.get("asset_mode_enabled", False))
# ... 其他控件

# 在控件的信号连接处，值变化时立即保存
self.model_combo.currentTextChanged.connect(
    lambda v: self._settings_usecase.save_preference("default_model", v)
)
self.asset_mode_checkbox.toggled.connect(
    lambda v: self._settings_usecase.save_preference("asset_mode_enabled", v)
)
```

所有偏好 key 见 `plan.md` 第五章 5.1 节表格，不得自造新 key 名。

---

## 七、代码注释要求

```python
# 公共接口（接口类、use case 方法、widget 公共方法）必须有 docstring
class TaskUseCase:
    def create_task(self, request: TaskRequest) -> str:
        """
        提交视频生成任务。
        
        Args:
            request: 由 TaskBuilder 构建的任务请求对象
        Returns:
            task_id: 平台返回的任务 ID
        Raises:
            ApiError: API 调用失败
            ValidationError: 请求参数不合法
        """

# 复杂逻辑需要行内注释，说明"为什么"而不是"做什么"
# 密钥派生自机器 ID，确保同一台机器的配置文件可解密，换机器后需重新输入 API Key
key = self._derive_key(machine_id)
```

私有方法和简单赋值不需要注释。

---

## 八、文件头部模板

每个新建的 `.py` 文件顶部统一格式：

```python
"""
模块简短描述（一行）。

详细说明（可选，多行）。
"""
from __future__ import annotations

# 标准库
import os
from abc import ABC, abstractmethod

# 第三方库
from PyQt6.QtCore import QObject, pyqtSignal

# 项目内部（按层级顺序）
from domain.entities import Task
from core.exceptions import ApiError
```

import 顺序：标准库 → 第三方库 → 项目内部，组间空一行。

---

## 九、每次任务开始前的检查清单

AI 在开始编写代码前，必须确认以下几点：

- [ ] 已阅读 `plan.md` 中与本任务相关的章节
- [ ] 已确认本任务涉及的文件路径（对照 plan.md 第六章目录结构）
- [ ] 已确认 import 方向不违反第二章层间依赖规则
- [ ] 已确认异常处理符合第四章规范
- [ ] 如果涉及 UI 控件，已确认偏好持久化接入（第六章模板）
- [ ] 如果涉及子线程，已确认不直接操作 UI（第五章）

---

## 十、禁止事项速查

| 禁止 | 原因 |
|------|------|
| `ui` 层直接 `import ArkApiClient` | 违反层间依赖 |
| `domain` 层 `import PyQt6` | 领域层不得依赖框架 |
| 子线程直接调用 `widget.setText()` | 线程安全问题，会导致崩溃 |
| 空 `except` 块或 `except: pass` | 吞掉异常，难以调试 |
| 明文存储 API Key | 安全问题，必须经 Fernet 加解密 |
| 自造偏好 key 名 | 与 plan.md 5.1 节表格不一致会导致恢复失败 |
| 在 `application` 层直接 `import sqlite3` | 应通过 `ITaskRepository` 接口访问 |
| 单个文件超过 500 行 | 拆分为多个模块 |

---

## 十一、日志使用规范

所有模块通过依赖注入获取 `logger` 实例，统一记录关键操作和异常。

### 日志级别使用指南

```python
# INFO - 关键操作记录
self._logger.info(f"Task created: task_id={task_id}, model={model}")
self._logger.info(f"Config saved: key={key}")
self._logger.info(f"Video downloaded: path={save_path}")

# WARNING - 可恢复的异常
self._logger.warning(f"Config file corrupted, trying backup: {e}")
self._logger.warning(f"API retry attempt {retry_count}/3")
self._logger.warning(f"Video URL expired, task_id={task_id}")

# ERROR - 需要关注的错误
self._logger.error(f"API call failed: {e.status_code} - {e.message}")
self._logger.error(f"Database write failed: {e}")
self._logger.error(f"Backup restore failed: {e}")

# CRITICAL - 致命错误（程序无法继续）
self._logger.critical(f"DI container initialization failed: {e}")
self._logger.critical(f"Logger setup failed: {e}")
```

### 日志记录时机

1. **API 调用前后**：记录请求参数和响应结果
2. **配置读写**：记录配置项变更、备份恢复
3. **异常捕获**：记录异常类型、错误信息、堆栈（ERROR 级别）
4. **关键状态变更**：任务状态变化、资产审核结果
5. **文件操作**：上传、下载、删除操作

### 日志格式规范

```python
# 正确 - 包含上下文信息
self._logger.info(f"Task created: task_id={task_id}, model={model}, type={task_type}")

# 错误 - 信息不足
self._logger.info("Task created")

# 正确 - 异常记录包含原始异常
self._logger.error(f"API call failed: {e}", exc_info=True)

# 错误 - 丢失异常堆栈
self._logger.error("API call failed")
```

### 敏感信息保护

```python
# 禁止 - 记录完整 API Key
self._logger.info(f"API Key: {api_key}")

# 正确 - 只记录前后缀
self._logger.info(f"API Key configured: {api_key[:8]}...{api_key[-4:]}")

# 禁止 - 记录用户密码
self._logger.info(f"Password: {password}")

# 正确 - 只记录操作
self._logger.info("Password updated")
```

---

## 十二、配置文件异常处理增强

`ConfigStore` 必须实现完整的备份恢复机制，确保配置损坏时程序仍可启动。

### 配置读取流程

```python
# infrastructure/config_store.py
def _load(self) -> dict:
    """加载配置，失败时尝试从备份恢复"""
    try:
        with open(self._config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self._logger.info("Config loaded successfully")
            return data
    except FileNotFoundError:
        self._logger.warning("Config file not found, creating default")
        return self._get_defaults()
    except json.JSONDecodeError as e:
        self._logger.warning(f"Config file corrupted: {e}, trying backup")
        return self._load_from_backup()
    except Exception as e:
        self._logger.error(f"Unexpected error loading config: {e}")
        return self._load_from_backup()

def _load_from_backup(self) -> dict:
    """从备份文件恢复配置"""
    backup_path = self._config_path.with_suffix(".json.bak")
    try:
        with open(backup_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self._logger.info("Config restored from backup")
            # 恢复成功后立即写回主配置文件
            self._save_to_file(self._config_path, data)
            return data
    except Exception as e:
        self._logger.error(f"Backup restore failed: {e}, using defaults")
        # 备份也失败，返回默认值并写入文件
        defaults = self._get_defaults()
        try:
            self._save_to_file(self._config_path, defaults)
        except Exception as save_error:
            self._logger.critical(f"Cannot write default config: {save_error}")
        return defaults
```

### 配置写入流程

```python
def set(self, key: str, value) -> None:
    """保存配置项，成功后自动备份"""
    try:
        self._data[key] = value
        self._save_to_file(self._config_path, self._data)
        self._create_backup()
        self._logger.info(f"Preference saved: {key}")
    except Exception as e:
        self._logger.error(f"Failed to save preference {key}: {e}")
        raise StorageError(f"配置保存失败: {e}") from e

def _create_backup(self) -> None:
    """创建配置文件备份"""
    try:
        backup_path = self._config_path.with_suffix(".json.bak")
        shutil.copy2(self._config_path, backup_path)
        self._logger.debug(f"Config backup created: {backup_path}")
    except Exception as e:
        # 备份失败不影响主流程，只记录警告
        self._logger.warning(f"Failed to create config backup: {e}")
```

### 默认值表

```python
def _get_defaults(self) -> dict:
    """返回默认配置，确保程序可启动"""
    return {
        "api_key": "",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "default_model": "doubao-seedance-2-0-260128",
        "default_task_type": "text_to_video",
        "asset_mode_enabled": False,
        "default_resolution": "720p",
        "default_aspect_ratio": "16:9",
        "default_duration": 5,
        "generate_audio": True,
        "watermark": False,
        "offline_inference": False,
        "web_search": False,
        "download_path": str(Path.home() / "Desktop"),
        "window_width": 1200,
        "window_height": 800,
        "window_x": -1,  # -1 表示居中
        "window_y": -1,
        "dark_mode": False
    }
```

---

## 十三、资产审核轮询线程安全

`AssetPollingWorker` 与 `PollingWorker` 类似，必须遵守线程安全规则。

### 线程安全规则

```python
# core/asset_polling_worker.py
class AssetPollingWorker(QThread):
    def __init__(self, asset_usecase, event_bus, logger):
        super().__init__()
        self._asset_usecase = asset_usecase
        self._event_bus = event_bus
        self._logger = logger
        self._pending_assets = []  # 待审核资产 ID 列表
        self._running = True
    
    def run(self):
        """轮询线程主循环，内部全覆盖 try/except"""
        while self._running:
            try:
                self._poll_assets()
            except Exception as e:
                # 任何异常都不能让线程崩溃
                self._logger.error(f"Asset polling error: {e}", exc_info=True)
                self._event_bus.error_occurred.emit("ASSET_POLL_ERROR", str(e))
            
            # 每 10 秒轮询一次
            QThread.sleep(10)
    
    def _poll_assets(self):
        """轮询所有待审核资产"""
        for asset_id in self._pending_assets[:]:  # 复制列表避免迭代时修改
            try:
                status = self._asset_usecase.get_asset_status(asset_id)
                
                if status == "approved":
                    self._event_bus.asset_approved.emit(asset_id)
                    self._pending_assets.remove(asset_id)
                    self._logger.info(f"Asset approved: {asset_id}")
                
                elif status == "rejected":
                    reason = self._asset_usecase.get_reject_reason(asset_id)
                    self._event_bus.asset_rejected.emit(asset_id, reason)
                    self._pending_assets.remove(asset_id)
                    self._logger.warning(f"Asset rejected: {asset_id}, reason={reason}")
                
                # pending 状态继续轮询
            except Exception as e:
                # 单个资产查询失败不影响其他资产
                self._logger.error(f"Failed to poll asset {asset_id}: {e}")
    
    def add_asset(self, asset_id: str):
        """添加待审核资产到轮询队列（线程安全）"""
        if asset_id not in self._pending_assets:
            self._pending_assets.append(asset_id)
            self._logger.info(f"Asset added to polling queue: {asset_id}")
    
    def stop(self):
        """停止轮询线程"""
        self._running = False
        self.wait()
```

### UI 层订阅示例

```python
# ui/widgets/asset_picker_widget.py
class AssetPickerWidget(QWidget):
    def __init__(self, event_bus, ...):
        super().__init__()
        self._event_bus = event_bus
        
        # 订阅资产审核结果
        self._event_bus.asset_approved.connect(self._on_asset_approved)
        self._event_bus.asset_rejected.connect(self._on_asset_rejected)
    
    def _on_asset_approved(self, asset_id: str):
        """资产审核通过（主线程，可安全操作 UI）"""
        # 更新列表中的资产状态
        for i in range(self.asset_list.count()):
            item = self.asset_list.item(i)
            if item.data(Qt.UserRole) == asset_id:
                item.setText(f"{asset_id} - 已通过")
                item.setForeground(QColor("green"))
    
    def _on_asset_rejected(self, asset_id: str, reason: str):
        """资产审核被拒（主线程，可安全操作 UI）"""
        for i in range(self.asset_list.count()):
            item = self.asset_list.item(i)
            if item.data(Qt.UserRole) == asset_id:
                item.setText(f"{asset_id} - 已拒绝: {reason}")
                item.setForeground(QColor("red"))
```

---

## 十四、代码提交前自查清单

> AI 在结束**每一次**代码修改任务前（包括标记 todo 完成、提交 commit、结束对话），必须逐项检查。

- [ ] 1. 本次修改是否涉及新增/修改 import？确认不违反第二章层间依赖规则
- [ ] 2. 新增的类/方法是否遵循第三章命名约定（接口 I 前缀、方法 snake_case 等）？
- [ ] 3. 异常处理是否符合第四章规范（infrastructure 层捕获 SDK 异常转为 ApiError，禁止空 except）？
- [ ] 4. 如果涉及子线程（QThread），是否确保不直接操作 UI 控件？
- [ ] 5. 如果涉及 UI 控件，是否已接入偏好持久化（第六章模板）？
- [ ] 6. 日志记录是否符合第十一章规范（敏感信息保护、关键操作 INFO、异常 ERROR）？
- [ ] 7. 文件头部模板是否符合第八章格式？
- [ ] 8. 单文件是否超过 500 行？（超过需拆分为多个模块）
- [ ] 9. 是否运行了 `testing_rules.md` 规定的强制测试流程？
- [ ] 10. 对照 `testing_rules.md` 第五章的自查清单确认无误？

---

## 十五、已知踩坑记录（AI 必须阅读，避免重复犯错）

> 以下是在本项目中 AI 曾犯过的具体错误，**每次开始任务前必须浏览一遍**。

| # | 错误描述 | 发生文件 | 正确做法 |
|---|---------|---------|---------|
| 1 | import `volcengine.ark` 而非 `volcenginesdkarkruntime` | `infrastructure/ark_api_client.py:10` | 火山引擎新版 SDK 的 import 路径为 `from volcenginesdkarkruntime import Ark` |
| 2 | `create_task` 使用扁平 params（`{"model":..., "prompt":...}`）而非 `content` 数组格式 | `infrastructure/ark_api_client.py:61-90` | 官方 API 使用 `content=[{type:"text", text:"..."}, {type:"image_url", image_url:{url:"..."}, role:"reference_image"}]` |
| 3 | `get_task` 调用了 `.retrieve()` 而非 `.get()` | `infrastructure/ark_api_client.py:139` | 新版 SDK 使用 `client.content_generation.tasks.get(task_id=...)` |
| 4 | 时长校验范围写成了 1-10 秒 | `domain/task_builders/base.py:55-56` | Seedance API 支持 4-15 秒 |
| 5 | 窗口标题拼写为 "SeeDance" 而非 "Seedance" | `ui/main_window.py:29,84` | 产品名称统一为 "Seedance Studio" |
| 6 | `TaskBuilderFactory` 未实现，导致直接 import 具体 Builder 类 | 未实现，所有子类 import | 应通过 `TaskBuilderFactory.register()` 注册，`TaskBuilderFactory.get()` 获取 |
| 7 | `settings_usecase.test_connection()` 是空桩函数，始终返回 `True` | `application/settings_usecase.py:72-76` | 应调用一个轻量 API 端点验证 Key 有效性 |
| 8 | `TaskUseCase` 缺少 `ITaskRepository` 注入 | `application/task_usecase.py:21` | 任务创建后应通过 `ITaskRepository.save()` 持久化到 SQLite |
| 9 | `page_create.py` 直接实例化 `TextToVideoBuilder()` | `ui/pages/page_create.py:73` | 应先注册到 `TaskBuilderFactory`，再通过 `TaskBuilderFactory.get(task_type)` 获取 |
| 10 | `get_task` 响应解析顶层取值（`response.video_url`）而非嵌套结构 | `infrastructure/ark_api_client.py:151-158` | 官方 API 返回 `response.content.video_url`（嵌套）、`response.error.code`/`error.message`、`response.usage.completion_tokens` |
| 11 | `web_search` 作为独立 boolean 参数传入 API | `infrastructure/ark_api_client.py:100-101` | API 要求 `tools: [{type: "web_search"}]` 格式，非扁平字段 |
| 12 | `create_task` 未传入 `resolution` 参数 | `infrastructure/ark_api_client.py:91-98` | 参数列表需包含 `params["resolution"] = request.resolution` |
| 13 | `TaskStatus` 枚举用 `PENDING` 映射 API 的 `"pending"`，但 API 实际返回 `"queued"` | `infrastructure/ark_api_client.py:143`、`domain/enums.py` | 状态枚举需包含 `queued`、`running`、`cancelled`、`succeeded`、`failed`、`expired` 六个值 |
| 14 | `_nav_buttons` 列表添加顺序与 `_pages` 堆栈索引不一致，导致 `_switch_page` 高亮错位 | `ui/main_window.py:92-115` | `QStackedWidget.addWidget` 的添加顺序就是页面索引；`_nav_buttons` 必须按相同顺序 append，否则 `enumerate` 导航按钮时高亮错位。每次新增页面时：先在 `_pages.addWidget()` 末尾追加，再在 `_nav_buttons.append()` 末尾追加对应的按钮，且 `_switch_page` 传参索引必须等于新增顺序索引。 |
| 15 | SDK `Tasks.create()` 只接受 `model`/`content`/`callback_url`/`return_last_frame`，`generate_audio`/`ratio`/`duration`/`watermark`/`tools`/`service_tier` 必须通过 `extra_body` 传入 | `infrastructure/ark_api_client.py:90-116` | 先用 `inspect.getsource(Tasks.create)` 查看 SDK 真实签名，参数不在签名内的全部放进 `extra_body` 字典 |
| 16 | SDK `Tasks` 类取消任务的方法是 `.delete(task_id)`（位置参数），非 `.cancel(task_id=...)` | `infrastructure/ark_api_client.py:238-239` | 先用 `dir(client.content_generation.tasks)` 确认方法名，再 `inspect.getsource` 确认签名 |
| 17 | plan.md 5.1 节定义的偏好项 `download_path`，todo 中遗漏了对应的 UI 实现任务 | `ui/pages/page_settings.py` | plan 中每个偏好项都应在 todo 中有对应的 UI 控件任务，按 coding_rules.md 第六章模板接入持久化 |
| 18 | SQLite CRUD 方法中异常时 `conn.close()` 被跳过，导致连接泄漏 | `infrastructure/sqlite_task_repo.py:63-157` | 所有数据库操作使用 `try/finally` 或 context manager，确保 `conn.close()` 无论成功失败都会执行 |
| 19 | `AssetPollingWorker._pending_assets` list 被工作线程和主线程并发修改，无锁保护 | `core/asset_polling_worker.py:31-75` | 用 `threading.Lock` 保护共享列表的读写操作，`add_asset` 和 `_poll_all` 均通过 `with self._lock:` 访问 |
| 20 | 新增 TaskBuilder 后未在 `__init__.py` 同步注册，`Factory.get()` 会抛 `ValueError` | `domain/task_builders/__init__.py:3-8` | 每次新增 Builder 时，必须同时更新 `__init__.py` 和 `di_container.py` 的 `TaskBuilderFactory.register()` 调用 |
| 21 | `IAssetRepository` / `AssetUseCase` 缺少 `get_reject_reason` 方法，`AssetPollingWorker` 调用失败 | `domain/interfaces.py` + `application/asset_usecase.py` | 新增接口方法需三层联动：在接口定义 → infrastructure 实现 → application 代理，缺一不可 |
| 22 | infrastructure 层在 API 错误时静默返回空值/"unknown"，调用方无法区分失败和空数据 | `infrastructure/ark_asset_client.py:59-60, 105-106` | API 调用失败应转为 `ApiError` 抛出，不可静默吞异常。仅 API Key 未配置时可安全降级返回默认值 |
| 23 | `window_width/height/x/y` 四个偏好项未接入持久化，启动时无法恢复窗口位置/大小 | `ui/main_window.py` | 在 `_init_ui` 末尾从 prefs 恢复窗口几何，在 `closeEvent` 中保存当前值，参考 plan.md 5.1 表 |
| 24 | `dark_mode: bool` 改为 `ui_theme: str` 后，旧配置文件中的 `dark_mode` 会被忽略导致主题未恢复 | `infrastructure/config_store.py:108`, `ui/main_window.py` | `_get_defaults()` 用 `ui_theme: "default_light"` 替换 `dark_mode: False`；`MainWindow._apply_theme_from_prefs()` 检测缺少 `ui_theme` 时从 `dark_mode` 自动迁移 |
| 25 | 在全局 QSS 中设置 `QWidget { background-color: #xxx; }` 导致所有子部件背景染色，覆盖区域混乱 | `themes/builtin/marathon/theme.qss` | Marathon 主题全局 QWidget 设为 `background-color: transparent`，容器背景通过 `QMainWindow` 或 `#objectName` 选择器单独设置。浅色/深色主题可保持原写法（`QWidget` 级联是刻意为之的简单方案） |
| 26 | 内联 `setStyleSheet()` 优先级高于 `app.setStyleSheet()`，切换主题后部分组件颜色不变 | `ui/pages/page_create.py:170-186`, `ui/main_window.py:75` | 凡颜色/字体/背景相关的内联 styleSheet 必须删除，改用 objectName + 主题 QSS 控制。仅布局类属性（padding、margin、min-width）可保留内联 |
| 27 | 使用 `FramelessWindowHint` 后 `QMainWindow` 的 `centralWidget` 布局区域会收缩，部分子部件不可见 | `ui/main_window.py` | 使用 Frameless 窗口时，必须将 `centralWidget` 的 `layout.setContentsMargins(0, title_bar_height, 0, 0)` 偏移到标题栏下方，同时确保标题栏不在 centralWidget 布局内（作为独立 overlay widget） |
| 28 | `QShortcut` 在 Windows 上 `setAutoRepeat(True)` 时按住快捷键会重复触发`Ctrl+1`等页面切换动作 | `ui/main_window.py` | 页面切换类快捷键必须 `setAutoRepeat(False)`；仅连续操作（如微调值）才允许 auto-repeat |

> **重要**：当 AI 发现新的错误时，必须在行 15 的记录表末尾追加一条新记录，确保后续 AI 会话不再重犯。修正已有错误的 commit 消息中标注 `(fixes pitfall #N)`。

---

## 十六、主题包开发规范（Phase 8 新增）

### 16.1 主题包文件结构

**目录型（推荐完整主题）：**

```
{theme_id}/
├── manifest.json         # 必选：主题元数据
├── theme.qss             # 必选：全局 QSS（通过 app.setStyleSheet() 应用）
├── sidebar.qss           # 必选：侧边栏 QSS（通过 sidebar.setStyleSheet() 应用）
└── fx.py                 # 可选：动效模块
```

**单文件型（快速开发）：**

```python
# {theme_id}.py
THEME_MANIFEST = {"id": "...", "name": "...", "is_dark": True, ...}
THEME_QSS = """..."""
SIDEBAR_QSS = """..."""
# 可选动效函数：on_theme_activated(main_window), fade_in(widget, ...)
```

### 16.2 QSS 编写规范

1. **全局透明**：Marathon 类深色主题必须 `QWidget { background-color: transparent; }`，容器背景通过 `QMainWindow` 或 `#objectName` 设置
2. **使用 objectName 选择器**：`#sidebar`、`#pageTitle`、`#appTitle` 等，不依赖类型选择器
3. **按钮角色属性**：`[role="primary"]`（主操作）、`[role="ghost"]`（次要）、`[role="danger"]`（破坏性操作）
4. **组件全覆盖**：自定义主题需覆盖 QLineEdit、QTextEdit、QComboBox、QPushButton、QCheckBox、QRadioButton、QSlider、QScrollBar、QProgressBar、QTabWidget、QGroupBox、QTableView、QTableWidget、QToolTip、QMenu、QSpinBox
5. **禁止在 QSS 中硬编码布局属性**（min-width、margin 等），布局由代码控制

### 16.3 动效模块接口

主题包中的 `fx.py` 应导出以下可选函数：

```python
def on_theme_activated(main_window) -> None:  # 主题切换入场动画
def on_theme_deactivated(main_window) -> None:  # 主题切换离场
def fade_in(widget, duration=200) -> object: ...
def fade_out(widget, duration=150) -> object: ...
def apply_glow(widget, color="#00E5FF", radius=12) -> object: ...
```

### 16.4 新增主题检查清单

- [ ] manifest.json 所有必选字段完整且合法
- [ ] `id` 与已有主题不冲突
- [ ] theme.qss 遵守 16.2 规范（全局透明 + objectName 选择器）
- [ ] sidebar.qss 不破坏侧边栏导航按钮状态的视觉区分
- [ ] 在三种分辨率（900×600 / 1200×800 / 1920×1080）下测试
- [ ] 在默认浅色主题和 Marathon 主题之间切换，验证回退正常

---

## 十七、无边框窗口开发规范（Phase 9 新增）

### 17.1 FramelessWindowHint 前提条件

```python
# main_window.py
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self, ...):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
```

使用无边框窗口后，系统不再提供以下能力，必须手动实现：
- 窗口移动（通过标题栏拖拽）
- 窗口缩放（边缘/角落 resize handles）
- 最大化/还原/最小化/关闭按钮
- Aero Snap（Windows 11 窗口贴靠）

### 17.2 标题栏实现模板

```python
# ui/title_bar.py
class TitleBar(QWidget):
    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        self._parent = parent
        self._drag_pos = None
        self.setObjectName("titleBar")
        self.setFixedHeight(36)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self._parent.move(self._parent.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def mouseDoubleClickEvent(self, event):
        if self._parent.isMaximized():
            self._parent.showNormal()
        else:
            self._parent.showMaximized()
```

### 17.3 窗口控制按钮

| 按钮 | objectName | 功能 |
|------|-----------|------|
| 最小化 | `#btnMin` | `window().showMinimized()` |
| 最大化 | `#btnMax` | `window().showMaximized()` 或 `window().showNormal()` |
| 关闭 | `#btnClose` | `window().close()` |

关闭按钮 hover 态（Marathon QSS）：`QPushButton#btnClose:hover { background-color: #FF4D00; color: #FFFFFF; }`

### 17.4 回退机制

```python
# main.py
import sys
if "--no-frameless" in sys.argv:
    # 跳过 FramelessWindowHint，使用系统默认标题栏
    pass
```

---

## 十八、通知/Toast 系统规范（Phase 9 新增）

### 18.1 EventBus 信号

```python
# core/event_bus.py
toast_requested = pyqtSignal(str, str, str)  # type, title, message
# type 值: "success" / "warning" / "error" / "info"
```

### 18.2 Toast 组件规则

1. **不阻塞主线程**：Toast 使用 `QTimer.singleShot()` 管理自动消失
2. **最多 5 条堆积**：超过时自动关闭最早的消息
3. **通过 EventBus 触发**：UI 层和业务层都可发送 Toast（`event_bus.toast_requested.emit("info", "标题", "详情")`）
4. **类型与色条映射**：
   - `success` → `#00FF88`（绿色）
   - `warning` → `#E5FF00`（黄色）
   - `error` → `#FF4D00`（橙色）
   - `info` → `#00E5FF`（青色）

### 18.3 用法示例

```python
# 任何层（通过 EventBus 实例）
event_bus.toast_requested.emit("success", "任务创建成功", f"任务 ID: {task_id[:16]}...")
event_bus.toast_requested.emit("error", "API 调用失败", str(e))
```
