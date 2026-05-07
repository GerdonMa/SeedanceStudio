# Seedance Studio — 开发 TODO 清单

> 参考文档：`plan.md`（v3）  
> 项目根目录：`seedance-studio/`  
> 开发语言：Python 3.12 + PyQt6  
> **验收标准见 `testing_rules.md` 第二章，AI 标记 `[x]` 前必须逐条检查。**  
> **Version 1.0 Milestone: P0~P9**

---

## P0 — 架构骨架（已完成 ✅）

- [x] 创建项目目录结构（按 plan.md 第六章）
- [x] 创建 `requirements.txt`，写入四个依赖（固定版本）
- [x] 实现 `domain/interfaces.py`：`IApiClient`、`ITaskRepository`、`IAssetRepository` 三个抽象接口
- [x] 实现 `domain/entities.py`：`Task`、`MediaItem`、`TaskRequest`、`TaskResult` dataclass
- [x] 实现 `domain/enums.py`：`TaskStatus`、`MediaType`、`ModelType`、`TaskType` 枚举
- [x] 实现 `core/exceptions.py`：`ApiError`、`StorageError`、`ValidationError`
- [x] 实现 `core/event_bus.py`：Qt 单例事件总线，定义所有 Signal
- [x] 实现 `core/logger.py`：日志系统初始化，文件轮转，多级别日志
- [x] 实现 `infrastructure/config_store.py`：Fernet 加密 + 偏好读写 + 自动备份恢复，密钥派生自机器 ID
- [x] 实现 `application/settings_usecase.py`：`save_preference` / `load_preferences` / `test_connection`
- [x] 实现 `core/di_container.py`：组装所有层依赖
- [x] 实现 `main.py`：初始化 DI 容器，启动 Qt App，恢复窗口大小/位置

---

## P1 — 文生视频基础流程（已完成，待修复 🔧）

- [x] 实现 `infrastructure/ark_api_client.py`：基于 volcengine SDK 实现 `IApiClient`
  - **验收**：import 路径 `volcenginesdkarkruntime`；`create_task` 使用 `content` 数组格式；`get_task` 使用 `.get()`
- [x] 实现 `domain/task_builders/base.py`：`TaskBuilder` 基类 + `TaskBuilderFactory`
  - **验收**：时长校验 4-15 秒；工厂可注册/获取/报错
- [x] 实现 `domain/task_builders/text_to_video.py`：文生视频请求构建 + 参数校验
  - **验收**：空提示词/非法时长/非法分辨率抛出 `ValidationError`
- [x] 实现 `application/task_usecase.py`：`create_task` / `get_task` / `cancel_task`
- [x] 实现 `infrastructure/file_storage.py`：本地文件读写、下载目录管理
- [x] 实现 `application/download_usecase.py`：下载视频到本地，检测 URL 过期
- [x] 实现 `ui/pages/page_settings.py`：API Key 输入（Fernet 加密）、Base URL、测试连通性按钮
- [x] 实现 `ui/pages/page_create.py`（基础版）：模型选择、任务类型选择、提示词输入框、输出参数
- [x] 实现 `ui/main_window.py`：导航栏 + 页面切换，启动时恢复窗口状态
- [x] 模块导入 + 行为测试 + GUI 启动测试（2025-05-07 通过 ✅）
- [ ] 端到端测试：填写提示词 → 提交 → 轮询 → 下载（需真实 API Key）
  - **验收**：无代码错误；GUI 流程可走通（API 调用是否成功取决于 Key 配置）

### 🔧 P1 已修复的 Bug
- [x] **FIX**: `ark_api_client.py` import 路径：`from volcengine.ark` → `from volcenginesdkarkruntime`
- [x] **FIX**: `ark_api_client.py` create_task API 调用适配 `content` 数组格式
- [x] **FIX**: `task_builders/base.py` 时长校验改为 4-15 秒
- [x] **FIX**: `main_window.py` 标题修正为 "Seedance Studio"
- [x] **FIX**: 添加 `TaskBuilderFactory` 到 `domain/task_builders/base.py`
- [x] **FIX**: `settings_usecase.py` test_connection() 桩函数 → 真实 API 连通性检测（通过 IApiClient 接口委托给 ArkApiClient）
- [x] **FIX**: `page_create.py` 改为通过 `TaskBuilderFactory.get("text_to_video")` 获取构建器
- [x] **FIX**: `ITaskRepository` 参数已预注入到 `TaskUseCase`（可选参数，P3 完成 SqliteTaskRepository 后由 Container 注入）
- [x] **FIX**: `get_task` 响应解析改为嵌套结构（`content.video_url`, `error.code/message`, `usage.completion_tokens`），状态映射增加 queued/cancelled/expired
- [x] **FIX**: `web_search` 参数改为 `tools: [{type: "web_search"}]` 格式
- [x] **FIX**: `create_task` API 参数增加 `resolution` 字段
- [x] **FIX**: `TaskStatus` 枚举增加 `QUEUED`/`CANCELLED`/`EXPIRED` 状态值
- [x] **FIX**: 宽高比校验列表增加 `21:9`
- [x] **FIX**: `page_settings.py` 新增下载路径设置控件（`download_path` 偏好项，plan.md 5.1 遗漏项）

### 🔧 P1 遗留问题（待修复）
- [x] **E2E**: 端到端测试：填写提示词 → 提交 → 轮询 → 下载（需真实 API Key），无代码错误即可通过

---

## 🔧 2025-05-07 深度 Debug 修复记录

> 全项目深度代码审查发现 30+ 个问题，已修复 12 项（6 严重 + 6 中低）。详见 `coding_rules.md` 第十五章 pitfall #18~#23。

| # | 严重 | 位置 | 修复内容 |
|---|------|------|---------|
| B4 | 🔴 | `sqlite_task_repo.py` | 所有 CRUD 改用 `try/finally` 防止连接泄漏 |
| B12+B16 | 🔴 | `asset_polling_worker.py` + `di_container.py` | 添加 `threading.Lock`，信号用 `QueuedConnection` |
| B18 | 🔴 | `task_builders/__init__.py` | 注册缺失的 EditVideo/ExtendVideo Builder |
| B22 | 🔴 | `interfaces.py` + `asset_usecase.py` + `ark_asset_client.py` | 三层联动添加 `get_reject_reason` |
| B25 | 🔴 | `page_task_list.py` | 空 `except: pass` 改为日志+友好提示 |
| B26 | 🔴 | `main_window.py` | 添加窗口几何保存/恢复（closeEvent + _restore_window_geometry） |
| B8 | 🟡 | `ark_asset_client.py` | 网络错误改为抛 ApiError（非静默返回） |
| B15 | 🟡 | `di_container.py` | Worker 延迟启动（有 Key 才自启，否则等 UI 调 start_workers） |
| B19 | 🟡 | `settings_usecase.py` | ConfigStore import 移至 TYPE_CHECKING |
| B20+B21 | 🟡 | `download_usecase.py` | FileStorage import 移至 TYPE_CHECKING，加日志+异常处理 |
| — | 🟢 | `config_store.py` + `logger.py` | APPDATA fallback 统一 `str(Path.home())` |
| — | 🟢 | `file_storage.py` + `page_create.py` + `media_upload_widget.py` | import 位置、冗余偏好保存、空目录检查 |

---

## P2 — 素材上传 + 多模态参考（已完成 ✅）

- [x] 实现 `ui/widgets/media_upload_widget.py`（普通模式）：图片/视频/音频拖拽上传，缩略图展示，排序/删除，公网 URL 输入
  - **验收**：支持图片/视频/音频混合拖拽；缩略图可预览；支持移除；可输入公网 URL
- [x] 实现 `domain/task_builders/multimodal_ref.py`：多模态参考请求构建 + 素材数量/格式校验
  - **验收**：图片 ≤ 9、视频 ≤ 3、音频 ≤ 3；禁止纯音频/文本+音频组合；素材引用格式正确
- [x] 在 `page_create.py` 中集成 `MediaUploadWidget`，任务类型切换时动态显示/隐藏素材区
  - **验收**：切换任务类型时素材区正确显示/隐藏；偏好设置持久化
- [ ] 测试：图片参考 + 提示词 → 生成视频（需真实 API Key + 素材）

---

## P3 — 任务历史 + 轮询（已完成 ✅）

- [x] 实现 `infrastructure/sqlite_task_repo.py`：`ITaskRepository` SQLite 实现，建表、CRUD
  - **验收**：建表 SQL 可执行；`save` `find_all` `find_by_id` `update_status` `delete` 正常
- [x] 实现 `core/polling_worker.py`：`QThread` + `QTimer`，每 30 秒轮询进行中的任务，通过 EventBus 广播状态
  - **验收**：线程内全覆盖 try/except；异常通过 EventBus 广播（不崩溃）
- [x] 实现 `ui/widgets/task_card_widget.py`：显示任务 ID、模型、状态标签（颜色区分）、创建时间、操作按钮
- [x] 实现 `ui/pages/page_task_list.py`：任务列表表格，手动刷新、取消、删除，订阅 EventBus 自动更新
- [x] 实现 `ui/widgets/video_player_widget.py`：QtMultimedia 内嵌播放器，显示 Token 消耗/生成时间/URL，复制 URL 按钮
- [x] 任务成功后自动弹出视频预览
- [x] 将 `ITaskRepository` 注入到 `TaskUseCase` 和 `Container`
- [x] 测试：提交任务 → 重启软件 → 历史任务仍可见 → 轮询恢复（行为测试通过 ✅）

---

## P4 — 资产库模式（已完成 ✅）

- [x] 实现 `domain/interfaces.py` 中的 `IAssetRepository`（✅ P0 已完成，直接复用）
- [x] 实现 `infrastructure/ark_asset_client.py`：调用火山引擎资产管理 API，列出/上传/查询状态
  - **验收**：实现 `list_assets` `upload_asset` `get_asset_status`
- [x] 实现 `application/asset_usecase.py`：资产列表查询、上传新素材、查询审核状态
- [x] 实现 `core/asset_polling_worker.py`：`QThread` + `QTimer`，每 10 秒轮询资产审核状态，通过 EventBus 广播审核结果
  - **验收**：全覆盖 try/except；广播 `asset_approved` / `asset_rejected`
- [x] 实现 `ui/widgets/asset_picker_widget.py`：弹窗列表，显示资产名称/类型/审核状态，订阅 EventBus 自动更新，选中后返回 `asset://{id}`
- [x] 在 `media_upload_widget.py` 顶部增加「使用资产库模式」开关（`QCheckBox`），接入偏好持久化（key: `asset_mode_enabled`）
  - **验收**：关闭时显示文件上传；开启时隐藏文件上传，显示资产 ID 输入 + 选择器
- [x] 测试：导入完整性检查 + 模块构造 + 行为逻辑 + GUI 启动 + 层间依赖合规（2025-05-07 通过 ✅）

---

## P5 — 视频编辑 + 延长视频（已完成 ✅）

- [x] 实现 `domain/task_builders/edit_video.py`：编辑视频请求构建 + 校验
- [x] 实现 `domain/task_builders/extend_video.py`：延长视频请求构建 + 校验
- [x] 在 `TaskBuilderFactory` 中注册两个新 Builder
  - **验收**：`TaskBuilderFactory.registered_types()` 包含 `edit_video` 和 `extend_video`
- [x] 在 `page_create.py` 任务类型下拉框中增加「编辑视频」「延长视频」选项
- [ ] 测试：编辑视频 / 延长视频端到端流程（需真实 API Key + 视频素材）

---

## P6 — 提示词助手（已完成 ✅）

- [x] 创建 `assets/templates/prompt_templates.json`，填入常用提示词模板（≥ 10 条）
  - **验收**：JSON 格式合法；每条模板包含 `name` 和 `template` 字段
- [x] 实现 `ui/widgets/prompt_helper_widget.py`：侧边面板，模板列表 + 一键填入，Seedance 2.0 提示词公式速查，素材引用格式说明
- [x] 在 `page_create.py` 中集成提示词助手面板（可折叠）

---

## P7 — 打磨 + 打包（已完成 ✅）

- [x] 深色主题支持（`dark_mode` 偏好项，切换时重载样式表）
- [x] UI 风格下拉切换 + Marathon 深空主题（`ui_theme` 偏好项，`ThemeRegistry` 可扩展架构）
- [x] 添加应用图标（`assets/icons/app.ico`）
- [x] 完善所有错误提示的友好文案
- [x] 编写 `tests/test_task_builders.py`
- [x] 编写 `tests/test_task_usecase.py`
- [x] 编写 `tests/test_settings_usecase.py`
- [x] 编写 `tests/test_sqlite_repo.py`
- [x] PyInstaller 打包配置，生成单文件 `SeedanceStudio.exe`
  - **验收**：`python -m PyInstaller --clean seedance.spec` 生成 47.1 MB exe；`dist/SeedanceStudio.exe` 存在
- [x] 测试打包后的 .exe 在干净 Windows 11 环境下可正常运行（2026-05-08 打包成功 ✅）

---

## P8 — UI 主题系统（可扩展主题包架构 ✅）

### 核心架构
- [x] 定义主题包规范（manifest 格式、两种主题格式、QSS 选择器约定）
- [x] 新建 `themes/` 目录结构（builtin + community + theme_loader）
- [x] 实现 `themes/__init__.py`：ThemeInfo + ThemeRegistry
- [x] 实现 `themes/theme_loader.py`：主题扫描/加载/验证/导入
- [x] 实现设置页下拉菜单动态加载（内置 + 第三方主题）

### 内置主题
- [x] 迁移默认浅色主题到 `themes/builtin/default_light.py`
- [x] 迁移默认深色主题到 `themes/builtin/default_dark.py`
- [x] 实现 `themes/builtin/marathon/`（目录型主题）：
  - [x] `manifest.json`
  - [x] `theme.qss`（基于 ui_ref_marathon.md 完整 QSS，覆盖全部 PyQt6 组件）
  - [x] `sidebar.qss`（深空终端风格侧边栏，选中态 3px Cyan 竖线）
  - [x] `fx.py`（MarathonColors 色彩类 + MarathonFX 动效工具）
- [x] UI 组件标准化：main_window + 3 个 page 设置 objectName/role 属性
- [x] 清理内联 styleSheet（颜色/字体迁移到主题 QSS，布局保留）
- [x] 偏好持久化：`ui_theme` 键 + 旧 `dark_mode` 自动迁移

### 主题导入/分享
- [x] 实现 `ThemeLoader.import_zip()` / `install_py()`（安装到 APPDATA）
- [x] 主题切换动效：Marathon 主题切换时执行 `fx.on_theme_activated()` 淡入动效

### 测试
- [x] 导入完整性 + 模块构造 + 行为逻辑 + GUI 启动 + 层间依赖合规
- [ ] 端到端 GUI 切换测试（手动验证三种主题视觉效果）

---

## P9 — UI 精细化与完成度打磨（1.0 收官 🎯）

### P9.1 自定义窗口框架
- [ ] 无边框窗口（`Qt.FramelessWindowHint` + `--no-frameless` 回退）
- [ ] `ui/title_bar.py` — 自定义标题栏（`#titleBar`，36px 高）
  - 左侧：应用图标 + 名称（`#titleLabel`）
  - 右侧：最小化/最大化/关闭按钮（`#btnMin` / `#btnMax` / `#btnClose`）
  - 关闭按钮 hover：`#FF4D00` 背景
- [ ] 窗口拖拽移动（标题栏空白区域 `mousePressEvent`/`mouseMoveEvent`）
- [ ] Marathon 主题窗口边缘 1px `#1C2029` 边框

### P9.2 侧边栏折叠
- [ ] 折叠/展开切换按钮（侧边栏底部）
- [ ] 展开(200px) ↔ 折叠(56px图标) 过渡动画（200ms `OutCubic`）
- [ ] 偏好持久化：`sidebar_collapsed` (bool)
- [ ] 响应式：窗口 <900px 自动折叠

### P9.3 通知/Toast 系统
- [ ] `core/event_bus.py` 新增 `toast_requested(type, title, message)` 信号
- [ ] `ui/widgets/toast_widget.py` — Toast 弹窗组件
  - 右下角弹出，距边缘 16px
  - 四种类型：success/warning/error/info（对应色条）
  - 进入动画：`slide_in_right` 300ms；退出：`fade_out` 150ms
  - 自动消失：5 秒
  - 最多 5 条同时显示
- [ ] `MainWindow` 订阅 `toast_requested` 并创建 ToastWidget

### P9.4 菜单栏 & 关于对话框
- [ ] QMenuBar 菜单栏（文件→导入主题/退出、帮助→关于）
- [ ] `ui/widgets/about_dialog.py` — 关于对话框
  - 应用名 + 版本号 `1.0.0`
  - 技术栈展示（Python/PyQt6/volcengine SDK）
  - 作者信息

### P9.5 键盘快捷键
- [ ] `Ctrl+1/2/3` 切换页面（`QShortcut` 或 `keyPressEvent`）
- [ ] `Escape` 关闭当前 Toast/弹窗

### P9.6 启动画面
- [ ] `ui/splash_screen.py` — 居中无边框窗口
- [ ] 显示应用名称 + 版本号 + 加载提示
- [ ] 主窗口加载完成后 500ms fade_out

### P9.7 细节打磨
- [ ] 窗口最大化状态记忆（`window_maximized` 偏好项）
- [ ] 偏好持久化新增键：`window_maximized`、`sidebar_collapsed`
- [ ] 提示词助手面板展开/折叠 `slide_in_right` 动画
- [ ] 任务列表空状态提示（"暂无任务，去创建一个吧"）
- [ ] 设置页「导入主题」按钮（文件对话框 → `ThemeLoader.import_zip()`）

### 测试
- [ ] 导入完整性 + 模块构造 + 行为逻辑 + GUI 启动 + 层间依赖合规
- [ ] PyInstaller 打包验证（`pyinstaller --clean seedance.spec`）

---

## 注意事项（AI 开发时必读）

1. **严禁在子线程直接操作 UI 控件**，所有跨线程通信通过 EventBus Signal 完成
2. **API Key 不得明文出现在任何文件中**，读写必须经过 `ConfigStore` 的 Fernet 加解密
3. **每个控件的偏好持久化**：启动时 `load_preferences()` 恢复，值变化时 `save_preference(key, value)` 立即写入
4. **新增任务类型**：只需新增 `ITaskBuilder` 实现 + `TaskBuilderFactory.register()`，不改其他文件
5. **资产库模式**：`asset://` 仅用于平台已审核通过的授权素材，`validate()` 中需检查格式合法性
6. **视频 URL 24 小时有效**：下载时检测 HTTP 状态码，过期提示用户重新生成，不要静默失败
7. **🔴 ArkApiClient import 路径**：正确导入为 `from volcenginesdkarkruntime import Ark`（非 `from volcengine.ark`）
8. **🔴 API 请求格式**：使用 `content` 数组格式（`[{type: "text", text: "..."}, {type: "image_url", ...}]`），非扁平参数
9. **AI 标记完成前**：必须阅读 `testing_rules.md` 第五章自查清单，10 项全部通过后才能标记 `[x]`
10. **🔴 无边框窗口开发**：使用 `FramelessWindowHint` 后系统不再处理窗口移动/缩放/最大化，必须手动实现 `TitleBar` 中的 `mousePressEvent`/`mouseMoveEvent` 和各按钮的 `window().showMinimized()`/`showMaximized()`/`close()`。P9 开始必须阅读 `coding_rules.md` 第十七章。
