# Seedance Studio

> 基于火山引擎 Doubao Seedance 2.0 系列 API 的桌面视频生成工具 — 无需编写代码，即可完成 AI 视频生成、编辑与延长。

## 功能概览

| 模块 | 说明 |
|------|------|
| **文生视频** | 输入提示词，选择模型和参数，一键生成视频 |
| **多模态参考** | 上传图片/视频/音频素材，结合提示词生成定制化视频 |
| **编辑视频** | 对已有视频进行 AI 编辑修改 |
| **延长视频** | 基于已有视频内容，智能延长生成 |
| **任务管理** | 任务列表、状态追踪、自动轮询、历史持久化 |
| **资产库模式** | 对接火山引擎资产管理 API，上传/审核/引用授权素材 |
| **提示词助手** | 内置 Seedance 2.0 提示词公式速查 + 模板库 |
| **UI 主题系统** | 3 套主题（浅色/深色/Marathon 深空），支持安装第三方主题包 |

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

# 启动应用
python main.py
```

### 打包为 .exe

```bash
python -m PyInstaller --clean seedance.spec
# 输出: dist/SeedanceStudio.exe
```

## 项目结构

```
seedance-studio/
├── main.py                       # 程序入口
├── seedance.spec                 # PyInstaller 打包配置
├── requirements.txt
│
├── domain/                       # 领域层（纯 Python，无框架依赖）
│   ├── entities.py               # Task, TaskRequest 等数据类
│   ├── enums.py                  # 状态/类型枚举
│   ├── interfaces.py             # IApiClient, ITaskRepository 接口
│   └── task_builders/            # 任务请求构建器（插件式扩展）
│
├── application/                  # 应用层（用例编排）
│   ├── task_usecase.py           # 任务创建/查询/取消
│   ├── settings_usecase.py       # 配置读写、API 连通性测试
│   ├── download_usecase.py       # 视频下载
│   └── asset_usecase.py          # 资产库管理
│
├── infrastructure/               # 基础设施层（SDK 封装、数据库、文件）
│   ├── ark_api_client.py         # 火山引擎 API 调用
│   ├── sqlite_task_repo.py       # SQLite 任务持久化
│   ├── config_store.py           # Fernet 加密配置存储
│   └── file_storage.py           # 本地文件操作
│
├── core/                         # 跨层基础设施
│   ├── event_bus.py              # Qt 事件总线（解耦通信）
│   ├── di_container.py           # 依赖注入容器
│   ├── exceptions.py             # 统一异常定义
│   └── polling_worker.py         # 后台任务轮询
│
├── themes/                       # UI 主题系统
│   ├── builtin/                  # 内置主题
│   │   ├── default_light.py      # 默认浅色
│   │   ├── default_dark.py       # 默认深色
│   │   └── marathon/             # Marathon 深空科技风
│   ├── community/                # 第三方主题目录
│   └── theme_loader.py           # 主题扫描/加载/验证
│
├── ui/                           # 表现层
│   ├── main_window.py            # 主窗口
│   └── pages/                    # 页面
│       ├── page_create.py        # 创建任务
│       ├── page_task_list.py     # 任务列表
│       └── page_settings.py      # 设置
│
└── tests/                        # 单元测试
```

## 架构特点

- **四层分离**：`domain` → `application` → `infrastructure` + `ui`，严格依赖倒置
- **事件驱动**：模块间通过 `EventBus` Signal 通信，无直接调用
- **插件式扩展**：新增任务类型只需实现 `ITaskBuilder` 并注册
- **偏好持久化**：所有设置项自动记忆，启动时恢复

## UI 主题系统

应用内置 3 套主题，通过「设置 → UI 风格」下拉菜单切换：

| 主题 | 说明 |
|------|------|
| `默认浅色` | 白色背景 + 蓝色强调色 |
| `默认深色` | 深蓝背景 + 蓝色强调色 |
| `Marathon 深空` | Bungie Marathon 深空作战终端风格 |

**主题包分享**：开发者可制作 `.zip` 主题包（含 `manifest.json` + `theme.qss`）分发给他人。详见 `themes/community/readme.txt`。

## 许可证

MIT License

---

Made with PyQt6 ❖ Powered by Doubao Seedance 2.0
