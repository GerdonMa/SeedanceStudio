# Seedance Studio — 测试与验收规范

> **AI 每次完成代码变更后，必须按本规范逐条执行验证。**  
> 未通过验证即标记 `[x]` 记为违规，需退回修复。
> 本规范与 `plan.md`、`coding_rules.md`、`todo.md` 配合使用。

---

## 一、强制测试流程（每次代码变更后必须执行）

每次修改代码后，按以下顺序执行测试，**未通过不得继续下一项**：

```
1. 导入完整性检查
2. 模块构造测试
3. 行为逻辑测试
4. GUI 启动测试（offscreen 模式）
5. 层间依赖合规检查
```

### 1.1 导入完整性检查

验证所有修改过的模块及其直接依赖模块可被 Python 正常导入。

```bash
python -c "
from domain.entities import Task, MediaItem, TaskRequest, TaskResult
from domain.enums import TaskStatus, MediaType, ModelType, TaskType
from domain.interfaces import IApiClient, ITaskRepository, IAssetRepository
from domain.task_builders.base import TaskBuilder, TaskBuilderFactory
from core.exceptions import ApiError, StorageError, ValidationError
from core.event_bus import EventBus
from core.logger import setup_logger
from infrastructure.config_store import ConfigStore
from infrastructure.ark_api_client import ArkApiClient
from infrastructure.file_storage import FileStorage
from application.settings_usecase import SettingsUseCase
from application.task_usecase import TaskUseCase
from application.download_usecase import DownloadUseCase
print('[PASS] All imports OK')
"
```

如果新增了 `.py` 文件，必须将其加入上述导入列表进行验证。

### 1.2 模块构造测试

验证所有可实例化的类能正常构造。使用 offscreen 模式（无需显示器）：

```bash
python -c "
import sys, os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from core.logger import setup_logger
from core.event_bus import EventBus
from infrastructure.config_store import ConfigStore
from infrastructure.file_storage import FileStorage
from infrastructure.ark_api_client import ArkApiClient
from application.settings_usecase import SettingsUseCase
from application.task_usecase import TaskUseCase
from application.download_usecase import DownloadUseCase

log = setup_logger()
eb = EventBus.instance()
config = ConfigStore(log)
api_client = ArkApiClient(config, log)
file_storage = FileStorage(log)
settings_usecase = SettingsUseCase(config, eb, log)
task_usecase = TaskUseCase(api_client, eb, log)
download_usecase = DownloadUseCase(file_storage, log)

from PyQt6.QtWidgets import QApplication
app = QApplication(sys.argv)
from core.di_container import Container
from ui.main_window import MainWindow
container = Container()
window = MainWindow(container)
print('[PASS] All modules construct OK')
app.quit()
"
```

### 1.3 行为逻辑测试

对变更的模块执行核心行为验证。每次修改附录 A 中的对应测试代码。

附录 A — 标准行为测试代码：

```bash
python -c "
# ===== 领域层测试 =====
from domain.enums import TaskStatus, MediaType, ModelType, TaskType
from domain.entities import TaskRequest, TaskResult, MediaItem
from domain.task_builders.base import TaskBuilderFactory
from domain.task_builders.text_to_video import TextToVideoBuilder
from core.exceptions import ValidationError

# Enums
assert TaskStatus.PENDING.value == 'pending'
assert TaskStatus.SUCCEEDED.value == 'succeeded'
assert ModelType.STANDARD.value == 'doubao-seedance-2-0-260128'
print('[PASS] Enums')

# Entities
req = TaskRequest(model='test', task_type='text_to_video', prompt='hello')
assert req.duration == 5
assert req.generate_audio == True
MediaItem(type=MediaType.IMAGE, url='http://example.com/img.jpg')
print('[PASS] Entities')

# TaskBuilder - valid
builder = TextToVideoBuilder()
request = builder.build(
    model='doubao-seedance-2-0-260128', prompt='a cat playing',
    resolution='720p', aspect_ratio='16:9', duration=5,
)
assert request.duration == 5
assert request.model == 'doubao-seedance-2-0-260128'
print('[PASS] TextToVideoBuilder.build valid')

# TaskBuilder - validation
try:
    builder.build(model='test', prompt='', resolution='720p', aspect_ratio='16:9', duration=5)
    assert False
except ValidationError as e:
    assert len(e.errors) > 0
print('[PASS] TextToVideoBuilder validation')

# Duration bounds
for d in [3, 16]:
    try:
        builder.build(model='test', prompt='cat', resolution='720p', aspect_ratio='16:9', duration=d)
        assert False
    except ValidationError:
        pass
print('[PASS] Duration 4-15s bounds')

# TaskBuilderFactory
TaskBuilderFactory.register('text_to_video', TextToVideoBuilder)
assert 'text_to_video' in TaskBuilderFactory.registered_types()
assert isinstance(TaskBuilderFactory.get('text_to_video'), TextToVideoBuilder)
try:
    TaskBuilderFactory.get('unknown')
    assert False
except ValueError:
    pass
print('[PASS] TaskBuilderFactory')

# ===== Core 层测试 =====
from core.exceptions import ApiError, StorageError
try:
    raise ApiError(code='404', message='Not found')
except ApiError as e:
    assert e.code == '404'
try:
    raise StorageError('disk full')
except StorageError as e:
    assert 'disk full' in str(e)
print('[PASS] Exceptions')

from core.event_bus import EventBus
assert EventBus.instance() is EventBus.instance()
print('[PASS] EventBus singleton')

# ===== 基础设施层测试 =====
from infrastructure.config_store import ConfigStore
import logging
cs = ConfigStore(logging.getLogger('test'))
assert cs.get('base_url') == 'https://ark.cn-beijing.volces.com/api/v3'
print('[PASS] ConfigStore defaults')

from infrastructure.file_storage import FileStorage
fs = FileStorage(logging.getLogger('test'))
fname = fs._generate_filename('http://example.com/video.mp4')
assert fname.startswith('seedance_')
assert fname.endswith('.mp4')
print('[PASS] FileStorage')

print()
print('*** ALL BEHAVIOR TESTS PASSED ***')
"
```

> **注意**：每次新增模块后，在附录 A 中追加对应的测试断言。AI 不得跳过此步。

### 1.4 GUI 启动测试

验证主界面可正常启动（offscreen 模式下）：

```bash
python -c "
import sys, os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PyQt6.QtWidgets import QApplication
from core.di_container import Container
from ui.main_window import MainWindow

app = QApplication(sys.argv)
container = Container()
window = MainWindow(container)
window.show()

# 基础断言
assert window._pages.count() >= 2, f'Expected >= 2 pages, got {window._pages.count()}'
assert 'Seedance' in window.windowTitle()

print(f'[PASS] GUI started: {window._pages.count()} pages, title=\"{window.windowTitle()}\"')
app.quit()
print('*** GUI TEST PASSED ***')
"
```

### 1.5 层间依赖合规检查

使用 grep 或手动检查，确认不存在违反 `coding_rules.md` 第二章的 import：

| 禁止模式 | 检查命令 |
|---------|---------|
| `ui` 层 `import ArkApiClient` | `grep -r "ArkApiClient" ui/` — 如存在则违规 |
| `domain` 层 `import PyQt6` | `grep -r "PyQt6" domain/` — 如存在则违规 |
| `application` 层 `import sqlite3` | `grep -r "sqlite3" application/` — 如存在则违规 |

---

## 二、各阶段验收标准（Definition of Done）

AI 在标记 todo.md 中任何任务为 `[x]` 前，必须逐项检查对应验收标准。

### P0 — 架构骨架
| 任务 | 验收标准 |
|------|---------|
| 项目目录结构 | `ls` 确认 `domain/` `application/` `infrastructure/` `core/` `ui/` `tests/` `assets/` 存在 |
| `domain/interfaces.py` | 包含 `IApiClient` `ITaskRepository` `IAssetRepository`，方法签名与 plan.md 一致 |
| `domain/entities.py` | 包含 `Task` `MediaItem` `TaskRequest` `TaskResult`，字段与 plan.md 一致 |
| `domain/enums.py` | 包含 `TaskStatus` `MediaType` `ModelType` `TaskType`，枚举值与 plan.md 一致 |
| `core/event_bus.py` | 单例模式生效；包含 `task_created` `task_updated` `task_succeeded` `task_failed` `error_occurred` Signal |
| `core/logger.py` | 文件轮转（10MB × 5）；控制台输出 WARNING+；避免重复添加 handler |
| `infrastructure/config_store.py` | Fernet 加密 API Key；`_load()` 失败自动回退到备份；备份也失败返回默认值 |
| `core/di_container.py` | 包含 `logger` `event_bus` `config` `api_client` `settings_usecase` `task_usecase` `download_usecase` |
| `main.py` | 可正常启动 GUI（offscreen 测试通过） |

### P1 — 文生视频基础流程
| 任务 | 验收标准 |
|------|---------|
| `ark_api_client.py` | import 路径为 `volcenginesdkarkruntime`；`create_task` 使用 `content` 数组格式；`get_task` 使用 `.get()` 方法 |
| `task_builders/base.py` | 包含 `TaskBuilder` 基类 + `TaskBuilderFactory`；时长校验 4-15 秒 |
| `text_to_video.py` | 可构建合法 `TaskRequest`；空提示词抛出 `ValidationError`；非法时长抛出 `ValidationError` |
| `task_usecase.py` | `create_task` 调用 `IApiClient` 并广播 `task_created`；异常广播 `error_occurred` |
| `page_create.py` / `page_settings.py` | 可通过偏好持久化保存/恢复控件状态；`main_window` 标题为 "Seedance Studio" |
| **端到端测试** | 模块导入测试 + 行为测试 + GUI 启动测试全部通过 |

### P2 — 素材上传 + 多模态参考
| 任务 | 验收标准 |
|------|---------|
| `media_upload_widget.py` | 支持图片/视频/音频拖拽 + URL 输入；缩略图展示；排序/删除 |
| `multimodal_ref.py` | 素材数量校验：图片 ≤ 9、视频 ≤ 3、音频 ≤ 3；禁止纯音频/文本+音频组合 |
| 集成到 page_create | 任务类型切换时动态显示/隐藏素材区 |

### P3 — 任务历史 + 轮询
| 任务 | 验收标准 |
|------|---------|
| `sqlite_task_repo.py` | 建表 SQL 不含语法错误；`save` `find_all` `update_status` `delete` 正常 |
| `polling_worker.py` | 每 30 秒轮询；线程内全覆盖 try/except；异常通过 EventBus 广播 |
| `page_task_list.py` | 表格显示任务列表；状态标签颜色正确；手动刷新/取消/删除可用 |
| `TaskUseCase` | 注入 `ITaskRepository`；`create_task` 后自动 `save` |

### P4 — 资产库模式
| 任务 | 验收标准 |
|------|---------|
| `IAssetRepository` | 已在 P0 完成，直接复用 |
| `ark_asset_client.py` | 实现 `list_assets` `upload_asset` `get_asset_status` |
| `asset_polling_worker.py` | 每 10 秒轮询；全覆盖 try/except；广播 `asset_approved` / `asset_rejected` |
| 模式开关 | 关闭时显示文件上传；开启时显示资产 ID 输入 + 选择器 |

### P5~P7
| 阶段 | 验收标准 |
|------|---------|
| P5 编辑/延长视频 | 新增 Builder 注册到 Factory；任务类型下拉包含新选项 |
| P6 提示词助手 | `prompt_templates.json` ≥ 10 条模板；侧边面板可折叠 |
| P7~P8 | 打包 + 主题系统 | `pyinstaller` 能生成 exe；`ThemeRegistry` 返回 3+ 主题；静态 import 加载内置主题 |
| P9 | UI 精细化 | 无边框窗口可拖拽移动；自定义标题栏按钮功能正常；Toast 右下角弹出且自动消失；Ctrl+1/2/3 页面切换；快捷键 `Escape` 关闭 Toast；splash 启动画面显示 |

---

## 三、Mock 与 Fixture 数据规范

### 3.1 ConfigStore 测试用临时文件

```python
import tempfile, json, logging
from pathlib import Path
from infrastructure.config_store import ConfigStore

# 自建临时配置目录
tmp_dir = Path(tempfile.mkdtemp())
config_path = tmp_dir / "config.json"
config_path.write_text(json.dumps({"api_key": "", "base_url": "https://test.com/api"}), encoding="utf-8")

# 注入 ConfigStore 时可通过修改 _config_dir 来指向临时目录（见具体实现）
```

### 3.2 ArkApiClient Mock 测试

```python
from unittest.mock import MagicMock, patch

# 对 ArkApiClient._get_client 进行 mock
client = MagicMock()
client.content_generation.tasks.create.return_value = MagicMock(id="mock_task_123")
client.content_generation.tasks.get.return_value = MagicMock(status="succeeded")

with patch.object(ArkApiClient, '_get_client', return_value=client):
    task_id = api_client.create_task(request)
    assert task_id == "mock_task_123"
```

### 3.3 通用测试数据

```python
from domain.entities import TaskRequest, MediaItem
from domain.enums import MediaType, TaskStatus

SAMPLE_TASK_REQUEST = TaskRequest(
    model="doubao-seedance-2-0-260128",
    task_type="text_to_video",
    prompt="一只猫在草地上玩耍",
    resolution="720p",
    aspect_ratio="16:9",
    duration=5,
    generate_audio=True,
    watermark=False,
)

SAMPLE_MEDIA_ITEM_IMAGE = MediaItem(type=MediaType.IMAGE, url="https://example.com/img.jpg")
SAMPLE_MEDIA_ITEM_VIDEO = MediaItem(type=MediaType.VIDEO, url="https://example.com/video.mp4")
SAMPLE_MEDIA_ITEM_AUDIO = MediaItem(type=MediaType.AUDIO, url="https://example.com/audio.mp3")
```

---

## 四、高风险模块回归清单

以下模块改动时，**必须同时验证其所有依赖方**（不只是改动的模块本身）：

| 模块 | 修改时必须重新验证 |
|------|------------------|
| `domain/interfaces.py` | 所有实现类（`ArkApiClient` `SqliteTaskRepo` `ArkAssetClient` 等） |
| `core/event_bus.py` | 所有 `emit` / `connect` 该 Signal 的模块 |
| `core/di_container.py` | 所有引用了 Container 中属性的代码（`main.py`、`MainWindow`、各 Page） |
| `infrastructure/config_store.py` | 所有读写配置的 use case + UI 页面 |
| `domain/task_builders/base.py` | 所有子类 Builder + `page_create.py` |
| `infrastructure/ark_api_client.py` | 所有调用它的 use case + poll worker |
| `core/event_bus.py`（新增 toast_requested） | 所有 emit / connect toast_requested 的模块（MainWindow、各 Page） |
| `ui/main_window.py`（P9 无边框窗口） | `main.py`（窗口初始化）、所有页面（快捷键上下文） |

检查方法：修改上述任一文件后，运行完整测试流程（1.1 → 1.5）一遍。

---

## 五、AI 任务完成自查清单

**在标记 todo.md 中任何 `[ ]` 为 `[x]` 之前，AI 必须逐项回答以下问题：**

- [ ] 1. 是否已运行导入完整性检查（1.1）并全部通过？
- [ ] 2. 是否已运行模块构造测试（1.2）并全部通过？
- [ ] 3. 是否已运行行为逻辑测试（1.3）并全部通过？如涉及新增模块，是否已在测试附录 A 中追加断言？
- [ ] 4. 是否已运行 GUI 启动测试（1.4）并全部通过？
- [ ] 5. 是否已检查层间依赖（1.5），未发现违规 import？
- [ ] 6. 对照"验收标准"检查完毕，确认满足该任务的 Definition of Done？
- [ ] 7. 修改是否涉及"高风险模块回归清单"（第四章）中的模块？若是，是否已完成回归验证？
- [ ] 8. 新增的字符串是否已包含中文翻译？（无需英文硬编码再转译）
- [ ] 9. 如果修改了 API 调用代码，是否确认使用了 `content` 数组格式（非扁平 params）？
- [ ] 10. 如果修改了 import 语句，是否确认不违反 `coding_rules.md` 第二章层间依赖规则？

**10 项全部为 "是" 时，才允许标记完成。**

---

## 附录 A — 行为测试代码（可执行）

每次新增模块后，在此附录末尾追加对应测试断言。

```python
# ===== 领域层测试 =====
from domain.enums import TaskStatus, MediaType, ModelType, TaskType
from domain.entities import TaskRequest, TaskResult, MediaItem
from domain.task_builders.base import TaskBuilderFactory
from domain.task_builders.text_to_video import TextToVideoBuilder
from core.exceptions import ValidationError

assert TaskStatus.PENDING.value == 'pending'
assert TaskStatus.SUCCEEDED.value == 'succeeded'
assert ModelType.STANDARD.value == 'doubao-seedance-2-0-260128'
print('[PASS] Enums')

req = TaskRequest(model='test', task_type='text_to_video', prompt='hello')
assert req.duration == 5
assert req.generate_audio == True
MediaItem(type=MediaType.IMAGE, url='http://example.com/img.jpg')
print('[PASS] Entities')

builder = TextToVideoBuilder()
request = builder.build(
    model='doubao-seedance-2-0-260128', prompt='a cat playing',
    resolution='720p', aspect_ratio='16:9', duration=5,
)
assert request.duration == 5
assert request.model == 'doubao-seedance-2-0-260128'
print('[PASS] TextToVideoBuilder.build valid')

try:
    builder.build(model='test', prompt='', resolution='720p', aspect_ratio='16:9', duration=5)
    assert False
except ValidationError as e:
    assert len(e.errors) > 0
print('[PASS] TextToVideoBuilder validation')

for d in [3, 16]:
    try:
        builder.build(model='test', prompt='cat', resolution='720p', aspect_ratio='16:9', duration=d)
        assert False
    except ValidationError:
        pass
print('[PASS] Duration 4-15s bounds')

TaskBuilderFactory.register('text_to_video', TextToVideoBuilder)
assert 'text_to_video' in TaskBuilderFactory.registered_types()
assert isinstance(TaskBuilderFactory.get('text_to_video'), TextToVideoBuilder)
try:
    TaskBuilderFactory.get('unknown')
    assert False
except ValueError:
    pass
print('[PASS] TaskBuilderFactory')

# ===== Core 层测试 =====
from core.exceptions import ApiError, StorageError
try:
    raise ApiError(code='404', message='Not found')
except ApiError as e:
    assert e.code == '404'
try:
    raise StorageError('disk full')
except StorageError as e:
    assert 'disk full' in str(e)
print('[PASS] Exceptions')

from core.event_bus import EventBus
assert EventBus.instance() is EventBus.instance()
print('[PASS] EventBus singleton')

# ===== 基础设施层测试 =====
from infrastructure.config_store import ConfigStore
import logging
cs = ConfigStore(logging.getLogger('test'))
assert cs.get('base_url') == 'https://ark.cn-beijing.volces.com/api/v3'
print('[PASS] ConfigStore defaults')

from infrastructure.file_storage import FileStorage
fs = FileStorage(logging.getLogger('test'))
fname = fs._generate_filename('http://example.com/video.mp4')
assert fname.startswith('seedance_')
assert fname.endswith('.mp4')
print('[PASS] FileStorage')

# ===== P1 补充测试 =====
from infrastructure.ark_api_client import ArkApiClient
api = ArkApiClient(cs, logging.getLogger('test'))
ok, msg = api.test_connection()
assert isinstance(ok, bool)
assert isinstance(msg, str)
print('[PASS] ArkApiClient.test_connection')

# ===== P2 多模态参考构建器测试 =====
from domain.task_builders.multimodal_ref import MultimodalRefBuilder

mb = MultimodalRefBuilder()

media = [MediaItem(type=MediaType.IMAGE, url='http://example.com/img.jpg')]
req = mb.build(model='test', prompt='cat', media_items=media, resolution='720p', aspect_ratio='16:9', duration=5)
assert req.media_items == media
assert req.task_type == 'multimodal_ref'
print('[PASS] MultimodalRefBuilder.build valid')

try:
    mb.build(model='test', prompt='cat', media_items=[], resolution='720p', aspect_ratio='16:9', duration=5)
    assert False
except ValidationError as e:
    assert '至少一个素材' in str(e.errors)
print('[PASS] MultimodalRefBuilder no media rejected')

audio = [MediaItem(type=MediaType.AUDIO, url='http://example.com/audio.mp3')]
try:
    mb.build(model='test', prompt='cat', media_items=audio, resolution='720p', aspect_ratio='16:9', duration=5)
    assert False
except ValidationError as e:
    assert '音频' in str(e.errors)
print('[PASS] MultimodalRefBuilder audio-only rejected')

mixed = [MediaItem(type=MediaType.IMAGE, url='http://example.com/img.jpg'),
         MediaItem(type=MediaType.AUDIO, url='http://example.com/audio.mp3')]
req = mb.build(model='test', prompt='cat', media_items=mixed, resolution='720p', aspect_ratio='16:9', duration=5)
assert len(req.media_items) == 2
print('[PASS] MultimodalRefBuilder image+audio OK')

errs = mb.validate(prompt='', media_items=[], duration=3, resolution='8k')
assert len(errs) > 0
print('[PASS] MultimodalRefBuilder.validate errors list')

# ===== P4 资产管理模块测试 =====
from infrastructure.ark_asset_client import ArkAssetClient
from application.asset_usecase import AssetUseCase
from core.asset_polling_worker import AssetPollingWorker

ac = ArkAssetClient(cs, logging.getLogger('test'))
au2 = AssetUseCase(ac, EventBus.instance(), logging.getLogger('test'))
assert isinstance(au2.list_assets(), list)
print('[PASS] AssetUseCase.list_assets returns list')

status = au2.get_asset_status('test_id')
assert isinstance(status, str)
print('[PASS] AssetUseCase.get_asset_status returns str')

aw = AssetPollingWorker(au2, EventBus.instance(), logging.getLogger('test'))
aw.add_asset('test_asset')
aw.stop()
print('[PASS] AssetPollingWorker add/stop')

print()
print('*** ALL BEHAVIOR TESTS PASSED ***')
```

### P9 模块测试（待实现后追加）

```python
# ===== P9 通知/Toast 系统测试 =====
from core.event_bus import EventBus
eb = EventBus.instance()
# 验证 toast_requested 信号存在
assert hasattr(eb, 'toast_requested')
print('[PASS] EventBus.toast_requested signal exists')

# ===== P9 快捷键测试（需 offscreen 模式）=====
import sys, os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
from PyQt6.QtWidgets import QApplication
from core.di_container import Container
from ui.main_window import MainWindow
app = QApplication(sys.argv)
container = Container()
window = MainWindow(container)
# 验证快捷键已注册（Ctrl+1/2/3 应该映射到 switch_page）
assert hasattr(window, '_nav_buttons')
assert len(window._nav_buttons) >= 3
print('[PASS] MainWindow shortcuts registered')

# ===== P9 配置默认值测试 =====
from infrastructure.config_store import ConfigStore
import logging
cs = ConfigStore(logging.getLogger('test'))
prefs = cs.get_all()
assert 'ui_theme' in prefs
assert 'window_x' in prefs
print('[PASS] ConfigStore includes P9 preference keys')
```
```
