# Seedance Studio — Windows 11 桌面软件规划文档（v3）

> **Version**: 1.0  |  **Last Updated**: 2026-05-08  |  **Status**: P0~P8 完成 ✅  P9 规划中

---

## 一、项目概述

**软件名称**：Seedance Studio  
**目标平台**：Windows 11  
**核心定位**：基于火山引擎 Doubao Seedance 2.0 系列 API 的桌面视频生成工具，让用户无需编写代码即可完成视频生成、编辑、延长等任务。

---

## 二、技术选型

| 层级 | 技术 | 理由 |
|------|------|------|
| 语言 | Python 3.12 | 官方 SDK 支持，生态丰富 |
| UI 框架 | PyQt6 | Windows 11 原生风格，支持 Fluent Design，控件完善 |
| API SDK | volcengine-python-sdk[ark] | 官方 SDK，异步任务封装完整 |
| 视频播放 | QtMultimedia | 内嵌视频预览，无需额外依赖 |
| 本地存储 | SQLite（via sqlite3） | 轻量任务历史持久化 |
| 日志系统 | Python logging | 标准库，支持文件轮转和多级别日志 |
| 打包 | PyInstaller | 打包为单文件 .exe，无需用户安装 Python |

---

## 三、架构设计（四层分离）

核心原则：**UI 不直接调用 API，模块间通过接口和事件总线通信，新增功能只需新增模块，不改动已有代码。**

```
Presentation Layer（表现层）
  UI 页面 / 组件，只负责展示和用户交互，不包含任何业务逻辑
        |
        | Qt Signals / EventBus
        v
Application Layer（应用层）
  用例编排：TaskUseCase / SettingsUseCase 等
  协调各 Service，不直接操作数据库或 API
        |
   _____|_____
  |           |
  v           v
Domain Layer  Infrastructure Layer
（领域层）      （基础设施层）
- Task 实体    - ArkApiClient
- MediaItem   - SqliteRepo
- TaskStatus  - FileStorage
- ITaskRepo   - ConfigStore
- IApiClient
```

### 3.1 依赖倒置原则

领域层定义接口，基础设施层实现接口。应用层只依赖接口，不依赖具体实现。将来换 API 提供商或数据库，只改基础设施层，其他层零改动。

```python
# domain/interfaces.py
from abc import ABC, abstractmethod

class IApiClient(ABC):
    @abstractmethod
    def create_task(self, request: TaskRequest) -> str: ...
    @abstractmethod
    def get_task(self, task_id: str) -> TaskResult: ...

class ITaskRepository(ABC):
    @abstractmethod
    def save(self, task: Task) -> None: ...
    @abstractmethod
    def find_all(self) -> list[Task]: ...
    @abstractmethod
    def update_status(self, task_id: str, status: TaskStatus) -> None: ...
```

### 3.2 事件总线（解耦 UI 与业务）

模块间通过全局事件总线通信，不直接调用对方方法。新增功能只需订阅/发布事件，不修改已有代码。

```python
# core/event_bus.py
class EventBus(QObject):
    task_created     = pyqtSignal(str)        # task_id
    task_updated     = pyqtSignal(str, str)   # task_id, status
    task_succeeded   = pyqtSignal(str, str)   # task_id, video_url
    task_failed      = pyqtSignal(str, str)   # task_id, error_msg
    settings_changed = pyqtSignal()
    error_occurred   = pyqtSignal(str, str)   # error_code, message
```

### 3.3 插件式任务类型（开闭原则）

每种任务类型封装为独立的 `TaskBuilder`，注册到工厂。新增任务类型只需新增一个类并注册，不改工厂以外的任何代码。

```python
# domain/task_builders/base.py
class ITaskBuilder(ABC):
    @abstractmethod
    def build(self, form_data: dict) -> TaskRequest: ...
    @abstractmethod
    def validate(self, form_data: dict) -> list[str]: ...  # 返回错误列表

# 注册示例
TaskBuilderFactory.register("text_to_video",   TextToVideoBuilder)
TaskBuilderFactory.register("multimodal_ref",  MultimodalRefBuilder)
TaskBuilderFactory.register("edit_video",      EditVideoBuilder)
TaskBuilderFactory.register("extend_video",    ExtendVideoBuilder)
```

### 3.4 依赖注入容器

在程序入口统一组装各层依赖，避免模块间硬编码依赖关系。

```python
# core/di_container.py
class Container:
    def __init__(self):
        logger      = setup_logger()             # 初始化日志系统
        config      = ConfigStore(logger)
        api_client  = ArkApiClient(config, logger)       # 实现 IApiClient
        task_repo   = SqliteTaskRepository(logger)       # 实现 ITaskRepository
        event_bus   = EventBus.instance()

        self.task_usecase     = TaskUseCase(api_client, task_repo, event_bus, logger)
        self.settings_usecase = SettingsUseCase(config, api_client, event_bus, logger)
        self.download_usecase = DownloadUseCase(logger)
```

### 3.5 日志系统（统一日志管理）

所有模块通过依赖注入获取 logger 实例，统一输出格式和存储位置。

```python
# core/logger.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logger() -> logging.Logger:
    """
    初始化全局日志系统。
    
    日志级别：
    - DEBUG: 详细调试信息（仅开发环境）
    - INFO: 关键操作记录（任务创建、API 调用、配置变更）
    - WARNING: 可恢复的异常（网络重试、配置回退）
    - ERROR: 需要关注的错误（API 失败、数据库异常）
    - CRITICAL: 致命错误（程序无法继续运行）
    
    日志文件：
    - 路径: %APPDATA%/SeedanceStudio/logs/app.log
    - 轮转: 单文件最大 10MB，保留最近 5 个文件
    - 格式: [时间] [级别] [模块名] 消息内容
    """
    logger = logging.getLogger("SeedanceStudio")
    logger.setLevel(logging.INFO)
    
    # 文件处理器（轮转日志）
    log_dir = Path(os.getenv("APPDATA")) / "SeedanceStudio" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(
        logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s")
    )
    logger.addHandler(file_handler)
    
    # 控制台处理器（开发时可见）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # 控制台只显示警告及以上
    logger.addHandler(console_handler)
    
    return logger
```

日志使用示例：

```python
# infrastructure/ark_api_client.py
class ArkApiClient(IApiClient):
    def __init__(self, config: ConfigStore, logger: logging.Logger):
        self._logger = logger
        
    def create_task(self, request: TaskRequest) -> str:
        self._logger.info(f"Creating task: model={request.model}, type={request.task_type}")
        try:
            resp = self._client.content_generation.tasks.create(...)
            self._logger.info(f"Task created successfully: task_id={resp.id}")
            return resp.id
        except ArkAPIError as e:
            self._logger.error(f"API call failed: {e.status_code} - {e.message}")
            raise ApiError(code=str(e.status_code), message=str(e)) from e
```

---

## 四、功能模块设计

### 4.1 API 配置模块
- 输入并加密保存 `ARK_API_KEY`（`cryptography` Fernet 加密，不明文写入）
- 一键测试 API 连通性
- 支持切换 base_url（默认 `https://ark.cn-beijing.volces.com/api/v3`）

### 4.2 任务创建模块

#### 基础设置
- 选择模型：
  - `doubao-seedance-2-0-260128`（高质量）
  - `doubao-seedance-2-0-fast-260128`（快速/低成本）
- 选择任务类型（切换后动态加载对应 TaskBuilder 的表单）：
  - 文生视频
  - 多模态参考（图片/视频/音频组合）
  - 编辑视频
  - 延长视频

#### 提示词输入
- 大文本框，支持多行输入
- 内置提示词模板库（下拉选择，数据来自 `prompt_templates.json`）
- 素材引用自动编号提示

#### 素材上传区
- 顶部「资产库模式」开关（见 4.5 节），状态持久化
- **普通模式**：图片拖拽上传最多 9 张 / 视频最多 3 个 / 音频最多 3 个，支持公网 URL 输入
- **资产库模式**：切换为资产 ID 输入框 + 「从资产库选择」按钮，文件上传控件隐藏

#### 输出参数设置
| 参数 | 选项 |
|------|------|
| 分辨率 | 480p / 720p / 1080p（fast 版仅 480p/720p）|
| 宽高比 | 21:9 / 16:9 / 4:3 / 1:1 / 3:4 / 9:16 / adaptive |
| 时长 | 4~15 秒（滑块 + 数字输入） |
| 生成音频 | 开关 |
| 水印 | 开关 |
| 联网搜索 | 开关（仅纯文本输入时可用） |
| 离线推理 | 开关（service_tier: flex） |

### 4.3 任务管理模块
- 任务列表（表格视图）：任务ID、模型、创建时间、状态、操作
- 状态标签：`pending`（灰）/ `running`（蓝）/ `succeeded`（绿）/ `failed`（红）
- 自动轮询：`PollingWorker`（独立 QThread）每 30 秒查询，通过事件总线广播状态
- 支持手动刷新、取消、删除任务记录
- 任务历史持久化（SQLite），重启后可查看历史

### 4.4 结果预览与下载模块
- 任务成功后内嵌 QtMultimedia 视频播放器预览
- 一键下载视频到本地（选择保存路径）
- 显示 Token 消耗、生成时间、视频 URL
- 支持复制视频 URL 到剪贴板
- 提示 URL 24 小时有效期

### 4.5 资产库模式（Asset Mode）

素材上传区顶部提供全局开关「使用资产库模式」，开关状态持久化保存：

- **关闭**（默认）：显示文件拖拽上传 + 公网 URL 输入框
- **开启**：切换为资产 ID 输入框 + 「从资产库选择」按钮，文件上传控件隐藏

资产库选择器功能：
- 调用火山引擎资产管理 API，列出账号下已入库的资产列表
- 显示资产名称、类型、审核状态（审核中 / 已通过 / 已拒绝）
- 支持上传新素材到资产库并等待审核
- **审核状态轮询**：上传后自动启动后台轮询（`AssetPollingWorker`），每 10 秒查询审核状态，审核通过/拒绝后通过 EventBus 通知 UI
- 选中资产后自动填入 `asset://{asset_id}` 格式

架构扩展：新增 `IAssetRepository` 接口 + `ArkAssetClient` 实现，符合现有四层架构，不影响其他模块。

审核轮询流程：

```
用户上传素材到资产库
        |
        v
AssetUseCase.upload_asset() -> 返回 asset_id（状态: pending）
        |
        v
EventBus.asset_uploaded.emit(asset_id)
        |
        v
AssetPollingWorker 监听到新资产，加入轮询队列（每 10 秒）
        |
        v
状态变为 approved -> EventBus.asset_approved.emit(asset_id)
状态变为 rejected -> EventBus.asset_rejected.emit(asset_id, reason)
        |
        v
UI 订阅事件，更新资产列表状态，显示审核结果
```

### 4.6 提示词助手（侧边面板）
- 内置 Seedance 2.0 提示词公式速查
- 常用模板一键填入提示词输入框
- 素材引用规则提示（"图片n"、"视频n" 格式说明）

---

## 五、用户偏好记忆（Preference Persistence）

所有用户操作后的设置由 `ConfigStore` 统一持久化，启动时自动恢复，无需用户重复配置。

### 5.1 记忆的设置项

| 设置项 | Key | 默认值 |
|--------|-----|--------|
| API Key | `api_key` | 空（Fernet 加密存储） |
| Base URL | `base_url` | `https://ark.cn-beijing.volces.com/api/v3` |
| 默认模型 | `default_model` | `doubao-seedance-2-0-260128` |
| 默认任务类型 | `default_task_type` | `text_to_video` |
| 资产库模式开关 | `asset_mode_enabled` | `false` |
| 默认分辨率 | `default_resolution` | `720p` |
| 默认宽高比 | `default_aspect_ratio` | `16:9` |
| 默认时长（秒） | `default_duration` | `5` |
| 生成音频开关 | `generate_audio` | `true` |
| 水印开关 | `watermark` | `false` |
| 离线推理开关 | `offline_inference` | `false` |
| 联网搜索开关 | `web_search` | `false` |
| 视频下载路径 | `download_path` | 用户桌面 |
| 窗口宽度 | `window_width` | `1200` |
| 窗口高度 | `window_height` | `800` |
| 窗口位置 X | `window_x` | 居中 |
| 窗口位置 Y | `window_y` | 居中 |
| 深色主题 | `dark_mode` | `false` |

### 5.2 实现方式

```python
# application/settings_usecase.py
class SettingsUseCase:
    def save_preference(self, key: str, value) -> None:
        """任意控件值变化时调用，自动持久化"""
        self._config.set(key, value)

    def load_preferences(self) -> dict:
        """启动时调用，返回所有偏好设置"""
        return self._config.get_all()
```

### 5.3 配置文件备份与恢复

`ConfigStore` 在每次成功写入配置后自动创建备份，读取失败时尝试从备份恢复。

```python
# infrastructure/config_store.py
class ConfigStore:
    def set(self, key: str, value) -> None:
        """保存配置项，成功后自动备份"""
        try:
            self._data[key] = value
            self._save()
            self._create_backup()  # 备份到 config.json.bak
            self._logger.info(f"Preference saved: {key}")
        except Exception as e:
            self._logger.error(f"Failed to save preference: {e}")
            raise StorageError(f"配置保存失败: {e}") from e
    
    def _load(self) -> dict:
        """加载配置，失败时尝试从备份恢复"""
        try:
            with open(self._config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self._logger.warning(f"Config file corrupted, trying backup: {e}")
            return self._load_from_backup()
    
    def _load_from_backup(self) -> dict:
        """从备份文件恢复配置"""
        backup_path = self._config_path.with_suffix(".json.bak")
        try:
            with open(backup_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._logger.info("Config restored from backup")
                # 恢复成功后立即写回主配置文件
                with open(self._config_path, "w", encoding="utf-8") as fw:
                    json.dump(data, fw, indent=2)
                return data
        except Exception as e:
            self._logger.error(f"Backup restore failed: {e}")
            # 备份也失败，返回默认值
            return self._get_defaults()
```

备份策略：
- 每次成功写入配置后创建 `config.json.bak`
- 主配置文件损坏时自动从备份恢复
- 备份也失败时返回默认值表，确保程序可启动

UI 层接入方式（以模型选择下拉框为例）：

```python
# 启动时恢复
prefs = settings_usecase.load_preferences()
self.model_combo.setCurrentText(prefs.get("default_model"))

# 值变化时保存
self.model_combo.currentTextChanged.connect(
    lambda v: settings_usecase.save_preference("default_model", v)
)
```

每个控件只需两行代码接入，不需要各页面自己管理持久化逻辑。

---

## 六、项目目录结构

```
seedance-studio/
├── main.py                           # 程序入口，初始化 DI 容器，启动 Qt App
├── requirements.txt
│
├── domain/                           # 领域层（纯 Python，无框架依赖，可独立单元测试）
│   ├── entities.py                   # Task, MediaItem, TaskRequest, TaskResult 数据类
│   ├── enums.py                      # TaskStatus, MediaType, ModelType, TaskType 枚举
│   ├── interfaces.py                 # IApiClient, ITaskRepository, IAssetRepository 接口
│   └── task_builders/                # 各任务类型请求构建器（插件式扩展点）
│       ├── base.py                   # ITaskBuilder 接口 + TaskBuilderFactory
│       ├── text_to_video.py
│       ├── multimodal_ref.py
│       ├── edit_video.py
│       └── extend_video.py
│
├── application/                      # 应用层（用例编排，不含框架代码）
│   ├── task_usecase.py               # 创建/查询/取消任务
│   ├── settings_usecase.py           # 读写配置、偏好持久化、测试连通性
│   ├── download_usecase.py           # 下载视频到本地
│   └── asset_usecase.py              # 资产库查询、上传、状态查询
│
├── infrastructure/                   # 基础设施层（具体实现，可替换）
│   ├── ark_api_client.py             # IApiClient 的 Ark SDK 实现
│   ├── ark_asset_client.py           # IAssetRepository 的 Ark SDK 实现
│   ├── sqlite_task_repo.py           # ITaskRepository 的 SQLite 实现
│   ├── config_store.py               # Fernet 加密配置 + 偏好读写
│   └── file_storage.py              # 本地文件操作（上传缓存、下载）
│
├── core/                             # 跨层基础设施
│   ├── event_bus.py                  # 全局 Qt 事件总线（单例）
│   ├── polling_worker.py             # 后台任务轮询 QThread
│   ├── asset_polling_worker.py       # 资产审核轮询 QThread
│   ├── logger.py                     # 日志系统初始化
│   ├── di_container.py               # 依赖注入容器（组装各层）
│   └── exceptions.py                # 统一异常定义（ApiError, StorageError, ValidationError）
│
├── themes/                           # 主题系统（独立可插拔模块）
│   ├── __init__.py                   # ThemeInfo 数据结构 + ThemeRegistry 注册表
│   ├── theme_loader.py              # 主题扫描/加载/验证/导入
│   ├── builtin/                      # 内置主题（只读，随应用发布）
│   │   ├── default_light.py         # 默认浅色主题
│   │   ├── default_dark.py          # 默认深色主题
│   │   └── marathon/                # Marathon 深空主题（目录型）
│   │       ├── manifest.json
│   │       ├── theme.qss
│   │       ├── sidebar.qss
│   │       └── fx.py                # MarathonColors + MarathonFX
│   └── community/                    # 第三方主题（用户安装，gitignore）
│
├── ui/                               # 表现层（只做展示和交互，不含业务逻辑）
│   ├── main_window.py                # 主窗口（导航栏 + 页面切换 + 快捷键 + Toast 订阅）
│   ├── title_bar.py                 # 自定义标题栏组件（P9）
│   ├── splash_screen.py             # 启动画面（P9）
│   ├── pages/
│   │   ├── page_create.py            # 新建任务页
│   │   ├── page_task_list.py         # 任务列表页
│   │   └── page_settings.py          # 设置页（P9：新增导入主题按钮）
│   └── widgets/
│       ├── media_upload_widget.py    # 素材上传组件（含资产库模式切换）
│       ├── asset_picker_widget.py    # 资产库选择器弹窗
│       ├── video_player_widget.py    # 视频播放组件
│       ├── prompt_helper_widget.py   # 提示词助手
│       ├── task_card_widget.py       # 任务卡片
│       ├── toast_widget.py          # Toast 通知组件（P9）
│       └── about_dialog.py          # 关于对话框（P9）
│
├── assets/
│   ├── icons/
│   └── templates/
│       └── prompt_templates.json     # 提示词模板库（JSON，运行时加载）
│
└── tests/                            # 单元测试（领域层和应用层可脱离 Qt 测试）
    ├── test_task_builders.py
    ├── test_task_usecase.py
    ├── test_settings_usecase.py
    └── test_sqlite_repo.py
```

---

## 七、核心流程

```
用户填写提示词 + 上传素材（普通/资产库模式）+ 设置参数
        |
        v
TaskBuilderFactory.get(task_type).validate(form_data)  <- 校验，失败则 UI 提示
        |
        v
TaskBuilderFactory.get(task_type).build(form_data)     <- 构建 TaskRequest
        |
        v
TaskUseCase.create_task(request)
        |
        v
IApiClient.create_task(request) -> 返回 task_id
        |
        v
ITaskRepository.save(task)
        |
        v
EventBus.task_created.emit(task_id)
        |
        v
PollingWorker 监听到新任务，加入轮询队列（每 30 秒）
        |
        v
状态变为 succeeded -> EventBus.task_succeeded.emit(task_id, video_url)
        |
        v
UI 订阅事件，自动刷新任务列表 + 弹出预览
```

---

## 八、鲁棒性保障

| 问题场景 | 应对方案 |
|---------|---------|
| API 调用超时/网络异常 | `ArkApiClient` 统一捕获，转为 `ApiError`，应用层处理后通过 EventBus 广播，UI 显示友好提示 |
| 轮询线程崩溃 | `PollingWorker` 内部 try/except 全覆盖，异常通过 EventBus 广播，主线程自动重启 Worker |
| 数据库读写失败 | Repository 层捕获 sqlite3 异常，向上抛出 `StorageError`，不影响 UI 正常运行 |
| 素材格式/数量错误 | `ITaskBuilder.validate()` 在提交前校验，返回错误列表，UI 层逐条展示 |
| 偏好配置文件损坏 | `ConfigStore` 读取失败时回退到默认值表，不崩溃 |
| 新增任务类型 | 新增 `ITaskBuilder` 实现 + 一行注册代码，其他代码零改动 |
| 新增 UI 页面 | 新增 Page 类 + 订阅 EventBus，不改主窗口逻辑 |
| 新增 API 提供商 | 新增 `IApiClient` 实现，在 DI 容器中替换注入，其他层零改动 |
| 视频 URL 过期 | 下载时检测 HTTP 状态码，过期则提示用户重新生成 |
| 资产审核被拒 | `AssetUseCase` 检测状态，UI 显示拒绝原因，引导用户重新上传 |
| 主题包损坏/格式错误 | `ThemeLoader._validate_manifest()` 验证失败则跳过并记录 Warning 日志，不影响默认主题 |
| 偏好键指向不存在的主题 | `ThemeRegistry.get()` 自动回退到默认主题 |
| 主题 ID 冲突 | 后加载覆盖先加载，记录 Warning 日志 |
| 无边框窗口在某些 RDP/虚拟机环境异常 | 通过 `--no-frameless` 命令行参数回退到系统默认标题栏 |
| Toast 累积过多（>5 条） | 自动关闭最早的消息 |

---

## 九、开发阶段规划

| 阶段 | 内容 | 优先级 |
|------|------|--------|
| P0 | 搭建四层架构骨架 + DI 容器 + EventBus + 异常体系 + 偏好持久化框架 | 必须 |
| P1 | API 配置 + 文生视频基础流程（提示词→生成→下载）| 必须 |
| P2 | 素材上传（图片/视频/音频）+ 多模态参考 | 必须 |
| P3 | 任务历史持久化 + 任务列表管理 + 轮询 Worker | 必须 |
| P4 | 资产库模式开关 + 资产选择器 | 重要 |
| P5 | 视频编辑、延长视频任务类型（新增 TaskBuilder 即可）| 重要 |
| P6 | 提示词模板库 + 提示词助手面板 | 重要 |
| P7 | 深色主题 + 界面打磨 + PyInstaller 打包 | 锦上添花 |
| P8 | UI 主题系统：可扩展主题包架构 + Marathon 深空主题 | 锦上添花 |
| P9 | UI 精细化与完成度打磨：自定义窗口框架 + 通知系统 + 侧边栏折叠 | 锦上添花 |

---

## 十、UI 主题系统（Phase 8）

### 10.1 设计理念

主题系统采用"可插拔主题包"架构。每个主题是独立的文件/目录，内置主题随应用发布，第三方主题可自由安装和分享。

### 10.2 主题包规范

**主题有两种格式：目录型（推荐）和单文件型（快速开发）。**

目录型包含 `manifest.json` + `theme.qss` + `sidebar.qss` + 可选 `fx.py`，打包为 `.zip` 分享。
单文件型是一个 `.py` 文件，定义 `THEME_MANIFEST`、`THEME_QSS`、`SIDEBAR_QSS` 模块变量。

**manifest.json 字段：** `manifest_version`(1)、`id`(snake_case)、`name`、`version`、`author`、`is_dark`、`description`(可选)、`tags`(可选)、`min_app_version`(可选)。

### 10.3 安装与分享

- **分享**：目录打包为 `.zip`；`.py` 直接分享
- **安装**：手动放入 `themes/community/` 或通过 UI「导入主题」按钮安装到 `%APPDATA%/SeedanceStudio/themes/`
- **加载优先级**：内置 → 社区 → APPDATA。同名 ID 后加载覆盖。

### 10.4 QSS 选择器约定

| 组件 | 选择器 | 说明 |
|------|--------|------|
| 中央容器 | `#centralWidget` | 主窗口中央 widget |
| 侧边栏 | `#sidebar` | 侧边栏容器 |
| 侧边栏标题 | `#appTitle` | 应用名称 |
| 页面标题 | `#pageTitle` | H1 标题 |
| 主操作按钮 | `[role="primary"]` | Cyan 实色背景 |
| 次要按钮 | `[role="ghost"]` | Cyan 边框透明背景 |
| 危险按钮 | `[role="danger"]` | Orange 边框 |

### 10.5 加载流程

```
main.py: ThemeLoader.discover_all()
  → 扫描 builtin/ + community/ + APPDATA
  → ThemeRegistry.register(theme)
  → MainWindow._apply_theme_from_prefs()  从 ui_theme 偏好项恢复
```

---

## 十一、UI 精细化与完成度打磨（Phase 9）

### 11.1 目标

将软件从"功能完整"提升到"产品级完成度"。引入自定义窗口框架、通知系统、侧边栏动效等 UI 精细化特性。

### 11.2 自定义窗口框架

使用 `Qt.FramelessWindowHint` 替换系统标题栏，实现 Marathon 风格自定义窗口：

- **标题栏**（`QWidget#titleBar`，36px 高）：左侧应用图标+名称，右侧最小化/最大化/关闭按钮
- **窗口控制按钮**：最小化/最大化 hover `#1C2029`；关闭按钮 hover `#FF4D00`
- **窗口拖拽**：标题栏空白区域 `mousePressEvent`/`mouseMoveEvent` 实现移动
- **边缘边框**：Marathon 主题中 `1px solid #1C2029`
- **回退机制**：通过 `--no-frameless` 命令行参数恢复到系统默认标题栏

### 11.3 侧边栏折叠

- 折叠按钮（侧边栏底部）
- 展开态 200px → 折叠态 56px（仅显示图标）
- 过渡动画：200ms `QPropertyAnimation` + `QEasingCurve.OutCubic`
- 偏好持久化：`sidebar_collapsed` (bool)
- 响应式：窗口 <900px 自动折叠

### 11.4 通知/Toast 系统

- `core/event_bus.py` 新增 `toast_requested(type: str, title: str, message: str)` 信号
- `ui/widgets/toast_widget.py` — 右下角弹出，距边缘 16px
- 四种类型：`success(#00FF88)` / `warning(#E5FF00)` / `error(#FF4D00)` / `info(#00E5FF)`
- 自动消失：5 秒 `QTimer.singleShot`
- 多条堆积：最多 5 条同时显示
- 进入/退出动画：`slide_in_right` 300ms / `fade_out` 150ms

### 11.5 菜单栏 & 快捷键

- QMenuBar：文件（导入主题、退出）、帮助（关于）
- 快捷键：`Ctrl+1/2/3` 切换页面，`Escape` 关闭弹窗/Toast
- 通过 `QShortcut` 在 `MainWindow` 中全局注册

### 11.6 启动画面

- `ui/splash_screen.py` — 居中无边框窗口
- 显示应用名称 + 版本号
- 主题加载完成后 500ms `fade_out` → `close()`

### 11.7 细节打磨

- 窗口最大化状态记忆（`window_maximized` 偏好项）
- 提示词助手面板展开/折叠有 `slide_in_right` 动画
- 任务列表空状态提示
- 设置页「导入主题」按钮

---

## 十二、依赖清单

```
volcengine-python-sdk[ark]>=0.3.0,<0.4.0
PyQt6>=6.7.0,<6.8.0
requests>=2.32.0,<3.0.0
cryptography>=42.0.0,<43.0.0
```

---

## 十三、注意事项

1. **API Key 安全**：Fernet 对称加密存储，密钥派生自机器 ID，不明文写入任何文件
2. **素材限制**：图片最多 9 张、视频最多 3 个、音频最多 3 个，`validate()` 层强制校验
3. **不支持的组合**：纯音频输入、文本+音频组合，在对应 `TaskBuilder.validate()` 中拦截
4. **视频 URL 有效期**：生成结果 URL 仅 24 小时有效，任务卡片显示倒计时提示
5. **轮询线程**：使用 `QThread` + `QTimer`，严禁在子线程直接操作 UI 控件
6. **资产库模式**：`asset://` 格式仅适用于已通过平台审核的虚拟人像和授权素材，不能用于规避对真实人脸的内容安全审核
7. **偏好持久化**：所有控件状态变化时立即写入，不依赖程序正常退出，防止意外关闭丢失设置

---

## 十四、Git 版本管理策略

### 14.1 分支模型

```
main ────────────────────────────────────────────────  稳定发布分支
  │
  └── dev ──────────────────────────────────────────  开发集成分支
        │
        ├── feature/xxx ────  功能分支（短期）
        ├── fix/xxx      ────  修复分支（短期）
        └── theme/xxx    ────  主题开发分支（短期）
```

| 分支 | 用途 | 合并方向 |
|------|------|---------|
| `main` | 稳定发布版本，只接受来自 `dev` 的 PR 合并 | ← `dev` |
| `dev` | 日常开发集成，所有 feature/fix 分支合并到此 | ← `feature/*`, `fix/*` |
| `feature/*` | 单个功能开发，完成后合并到 `dev` 并删除 | → `dev` |
| `fix/*` | Bug 修复，完成后合并到 `dev` 并删除 | → `dev` |

### 14.2 工作流程

1. **开始新功能**：从 `dev` 创建 `feature/功能名` 分支
2. **开发 & 测试**：在 feature 分支上开发，通过强制测试后提交
3. **合并到 dev**：PR → code review → squash merge 到 `dev`
4. **版本确定**：`dev` 稳定后，PR merge 到 `main`，打 tag `v1.0`、`v1.1` 等

### 14.3 Tag 命名

```
v1.0.0  — 初始发布
v1.1.0  — 功能更新（向后兼容）
v1.0.1  — Bug 修复（向后兼容）
v2.0.0  — 重大更新（不兼容）
```

### 14.4 当前版本

- **main**: `v1.0` — 初始发布（P0~P8 完成）
- **dev**: P9 开发进行中
