# Seedance Studio

> 基于火山引擎 Doubao Seedance 2.0 系列 API 的桌面视频生成工具 — 无需编写代码，即可完成 AI 视频生成、编辑与延长。

## 功能概览

| 模块 | 说明 |
|------|------|
| **文生视频** | 输入提示词，选择模型和参数，一键生成视频 |
| **多模态参考** | 上传图片/视频/音频素材，结合提示词生成定制化视频 |
| **编辑视频** | 对已有视频进行 AI 编辑修改 |
| **延长视频** | 基于已有视频内容，智能延长生成 |
| **任务管理** | 任务列表、状态追踪、自动轮询、历史持久化、视频内嵌预览 |
| **资产库模式** | 对接火山引擎资产管理 API，上传/审核/引用授权素材 |
| **提示词助手** | 内置 Seedance 2.0 提示词公式速查 + 模板库（≥10 条） |
| **UI 主题系统** | 3 套内置主题 + 动态主题变量系统 + 支持安装第三方主题包 |
| **自定义窗口框架** | 无边框窗口 + 标题栏拖拽移动 + 边缘缩放 + 窗口状态记忆 |
| **Toast 通知系统** | 右下角弹出通知（success/warning/error/info），最多 5 条堆积，5 秒自动消失 |
| **侧边栏折叠** | 展开(200px) ↔ 折叠(56px 图标)，200ms 过渡动画，偏好持久化 |
| **键盘快捷键** | `Ctrl+1/2/3` 切换页面，`Escape` 关闭通知/弹窗 |
| **启动画面** | Splash 启动画面 + 500ms 淡出过渡 |

## 技术栈

```
Python 3.12   — 语言
PyQt6         — UI 框架（Windows 11 原生风格）
volcengine SDK — 火山引擎 API 调用
SQLite        — 任务历史持久化
cryptography  — API Key Fernet 加密存储
PyInstaller   — 单文件 .exe 打包
```

## 快速开始

### 环境要求

- Windows 11（推荐）或 Windows 10
- Python 3.12+
- 火山引擎 API Key（[申请地址](https://console.volcengine.com/ark)）

### 安装运行

```bash
# 克隆仓库
git clone https://github.com/GerdonMa/SeedanceStudio.git
cd SeedanceStudio

# 安装依赖
pip install -r requirements.txt

# 启动应用（无边框窗口）
python main.py

# 启动应用（回退到系统默认标题栏）
python main.py --no-frameless
```

### 打包为 .exe

```bash
python -m PyInstaller --clean seedance.spec
# 输出: dist/SeedanceStudio-v1.2.1.exe
```

## 项目结构

```
seedance-studio/
├── main.py                           # 程序入口（QApplication 初始化、DI 容器、启动画面）
├── seedance.spec                     # PyInstaller 打包配置
├── requirements.txt
│
├── domain/                           # 领域层（纯 Python，无框架依赖，可独立单元测试）
│   ├── entities.py                   # Task, MediaItem, TaskRequest, TaskResult 数据类
│   ├── enums.py                      # TaskStatus, MediaType, ModelType, TaskType 枚举
│   ├── interfaces.py                 # IApiClient, ITaskRepository, IAssetRepository 抽象接口
│   └── task_builders/                # 任务请求构建器（插件式扩展点）
│       ├── base.py                   # ITaskBuilder 接口 + TaskBuilderFactory 工厂
│       ├── text_to_video.py          # 文生视频
│       ├── multimodal_ref.py         # 多模态参考
│       ├── edit_video.py             # 编辑视频
│       └── extend_video.py           # 延长视频
│
├── application/                      # 应用层（用例编排，不含框架代码）
│   ├── task_usecase.py               # 任务创建/查询/取消
│   ├── settings_usecase.py           # 配置读写、API 连通性测试
│   ├── download_usecase.py           # 视频下载
│   └── asset_usecase.py              # 资产库管理（列表/上传/状态查询）
│
├── infrastructure/                   # 基础设施层（SDK 封装、数据库、文件）
│   ├── ark_api_client.py             # 火山引擎 API 调用（IApiClient 实现）
│   ├── ark_asset_client.py           # 火山引擎资产管理 API（IAssetRepository 实现）
│   ├── sqlite_task_repo.py           # SQLite 任务持久化（ITaskRepository 实现）
│   ├── config_store.py               # Fernet 加密配置存储 + 自动备份恢复
│   └── file_storage.py               # 本地文件操作（下载缓存）
│
├── core/                             # 跨层基础设施
│   ├── event_bus.py                  # Qt 事件总线（单例，解耦 UI 与业务）
│   ├── polling_worker.py             # 后台任务轮询 QThread（每 30 秒）
│   ├── asset_polling_worker.py       # 资产审核轮询 QThread（每 10 秒）
│   ├── logger.py                     # 日志系统（文件轮转 10MB×5，多级别日志）
│   ├── di_container.py               # 依赖注入容器（组装各层）
│   └── exceptions.py                 # 统一异常定义（ApiError, StorageError, ValidationError）
│
├── themes/                           # UI 主题系统（可插拔主题包架构）
│   ├── __init__.py                   # ThemeInfo 数据结构 + ThemeRegistry 注册表
│   ├── theme_loader.py               # 主题扫描/加载/验证/导入
│   ├── theme_context.py              # ThemeContext 运行时主题变量系统（动态颜色）
│   ├── builtin/                      # 内置主题（只读，随应用发布）
│   │   ├── default_light.py          # 默认浅色
│   │   ├── default_dark.py           # 默认深色
│   │   └── marathon/                 # Marathon 深空终端风格（目录型主题）
│   │       ├── manifest.json
│   │       ├── theme.qss
│   │       ├── sidebar.qss
│   │       └── fx.py                 # MarathonColors + MarathonFX 动效
│   └── community/                    # 第三方主题（用户安装，gitignore）
│
├── ui/                               # 表现层（只做展示和交互，不含业务逻辑）
│   ├── main_window.py                # 主窗口（导航栏 + 页面切换 + 快捷键 + 无边框窗口）
│   ├── title_bar.py                  # 自定义标题栏（拖拽移动 + 最小化/最大化/关闭按钮）
│   ├── splash_screen.py              # 启动画面（居中无边框 + 淡出动画）
│   ├── pages/
│   │   ├── page_create.py            # 新建任务页（模型选择、提示词、素材上传、输出参数）
│   │   ├── page_task_list.py         # 任务列表页（表格视图、状态追踪、手动刷新/取消/删除）
│   │   └── page_settings.py          # 设置页（API Key、主题切换、下载路径、导入主题）
│   └── widgets/
│       ├── media_upload_widget.py    # 素材上传组件（拖拽上传 + 公网 URL + 资产库模式切换）
│       ├── asset_picker_widget.py    # 资产库选择器弹窗
│       ├── video_player_widget.py    # 视频播放组件（QtMultimedia 内嵌播放 + Token 信息）
│       ├── prompt_helper_widget.py   # 提示词助手（公式速查 + 模板库 + 一键填入）
│       ├── task_card_widget.py       # 任务卡片
│       ├── toast_widget.py           # Toast 通知组件（右下角弹出 + 进入/退出动画）
│       ├── about_dialog.py           # 关于对话框（版本 + 技术栈 + 作者信息）
│       └── sidebar_icons.py          # 侧边栏 SVG 图标（折叠态图标按钮）
│
├── assets/
│   ├── icons/
│   └── templates/
│       └── prompt_templates.json     # 提示词模板库（≥10 条，JSON 格式）
│
└── tests/                            # 单元测试（领域层和应用层可脱离 Qt 测试）
    ├── test_task_builders.py
    ├── test_task_usecase.py
    ├── test_settings_usecase.py
    └── test_sqlite_repo.py
```

## 架构特点

- **四层分离**：`domain` → `application` → `infrastructure` + `ui`，严格依赖倒置原则
- **事件驱动**：模块间通过 `EventBus` Signal 通信，无直接调用，UI 与业务解耦
- **插件式扩展**：新增任务类型只需实现 `ITaskBuilder` 并注册到 `TaskBuilderFactory`，不改其他代码
- **偏好持久化**：所有设置项（API Key、模型、分辨率、窗口状态、侧边栏折叠等 20+ 项）自动记忆，启动时恢复
- **主题变量系统**：`ThemeContext` 提供运行时颜色变量访问（19 个语义化颜色），组件通过 `get_color()` 获取，支持实时主题切换
- **异常分层处理**：infrastructure 层 SDK 异常 → `ApiError`；application 层广播 → EventBus；UI 层显示友好提示
- **配置备份恢复**：每次成功写入自动备份 `config.json.bak`，主配置文件损坏时自动从备份恢复，备份也失败则返回默认值表

## UI 主题系统

应用内置 3 套主题，通过「设置 → UI 风格」下拉菜单切换：

| 主题 | 说明 |
|------|------|
| `默认浅色` (default_light) | 白色背景 + 蓝色强调色 |
| `默认深色` (default_dark) | 深蓝背景 + 蓝色强调色 |
| `Marathon 深空` (marathon) | Bungie Marathon 深空作战终端风格 + 动效 |

### 运行时主题变量（ThemeContext）

```python
from themes.theme_context import ThemeContext

# 获取当前主题颜色（带回退值）
primary = ThemeContext.get_color("primary", "#00E5FF")
is_dark = ThemeContext.is_dark()
```

颜色变量规范：`bg_base`, `bg_surface`, `bg_overlay`, `bg_raised`, `primary`, `danger`, `warning`, `success`, `info`, `text_primary`, `text_secondary`, `text_tertiary`, `border_subtle`, `border_default`, `border_focus`, `toast_success`, `toast_warning`, `toast_error`, `toast_info`, `media_image`, `media_video`, `media_audio`。

### 主题切换机制

1. 用户选择主题 → `MainWindow._apply_theme(theme_id)`
2. `ThemeContext.set_current(theme_id)` 更新运行时变量
3. 应用全局 QSS + 侧边栏 QSS
4. 触发组件 `on_theme_changed()` 钩子刷新动态样式
5. 失败回退：当前主题加载失败 → ERROR 日志 → 自动回退到 `default_light`

### 主题包分享

开发者可制作 `.zip` 主题包（含 `manifest.json` + `theme.qss` + `sidebar.qss` + 可选 `fx.py`）分发给他人。通过「设置 → 导入主题」或手动放入 `themes/community/` 安装。

## 键盘快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+1` | 切换到「创建任务」页 |
| `Ctrl+2` | 切换到「任务列表」页 |
| `Ctrl+3` | 切换到「设置」页 |
| `Escape` | 关闭当前 Toast 通知/弹窗 |

## Toast 通知系统

应用右下角弹出通知，距边缘 16px：

| 类型 | 色条 | 用途 |
|------|------|------|
| `success` | 绿色 `#00FF88` | 操作成功（任务创建、下载完成） |
| `warning` | 黄色 `#E5FF00` | 警告（URL 即将过期、配置异常） |
| `error` | 橙色 `#FF4D00` | 错误（API 调用失败、网络异常） |
| `info` | 青色 `#00E5FF` | 提示信息（主题切换、设置已保存） |

- 自动消失：5 秒后 `fade_out` 150ms
- 多条堆积：最多 5 条，超出自动关闭最早消息
- 进入动画：`slide_in_right` 300ms

## 命令行参数

| 参数 | 说明 |
|------|------|
| `--no-frameless` | 使用系统默认标题栏（替代自定义无边框窗口） |

## 配置安全

- **API Key 加密**：`cryptography` Fernet 对称加密，密钥派生自机器 ID，换机器需重新输入
- **自动备份**：每次成功写入配置后创建 `config.json.bak` 备份
- **自动恢复**：主配置文件损坏时自动从备份恢复；备份也损坏时返回默认值表，确保程序启动
- **配置文件位置**：`%APPDATA%/SeedanceStudio/config.json`

## 许可证

MIT License

---

Made with PyQt6 ❖ Powered by Doubao Seedance 2.0
