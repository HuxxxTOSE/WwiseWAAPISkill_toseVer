# Wwise WAAPI Skill

一个面向 **AI Agent** 的 Wwise 开发辅助 Skill。它把"查 API"和"操作 Wwise"这两件事
打包成一套可离线检索、可实时验证的能力，让 Agent 在开发/脚本化 Wwise 时既能查准
API，又能真正动手并确认结果。

> 这是一个 [Cursor Agent Skill](https://docs.cursor.com)。核心入口是 [`SKILL.md`](SKILL.md)，
> Agent 会按需渐进式加载 `workflows/` 与 `references/` 下的页面。本 README 面向**人类读者**。

---

## 这个 Skill 能干嘛

它围绕两条主线（KNOW → DO → VERIFY）：

1. **KNOW —— 离线知识库**
   内置整份 **Wwise SDK 2024.1.13 (Windows)** 文档（约 9,400 页，涵盖 C++ SDK 头文件/
   类/宏 + 完整 WAAPI 参考 `ak.wwise.*` / `ak.soundengine.*` + WAQL），通过
   `scripts/search.py` 秒级检索，**无需联网、无需把 19MB 文档塞进上下文**。

2. **DO + VERIFY —— 驱动实时 Wwise**
   通过 **Wwise MCP 服务器（`user-wwise-mcp`）** 作为 Agent 的"手和眼"，对正在运行的
   Wwise 执行操作并回读验证。

典型能覆盖的任务：

- 查询 / 创建 / 修改 / 移动 / 删除 Wwise 对象（WAQL、`set_objects` 批量编辑）
- 导入音频、生成 SoundBank、编辑 Bank 包含项
- 投递 Event、设置 RTPC / State / Switch、Mute/Solo、Transport 播放测试
- Profiler 采集与性能数据读取
- UI 命令、布局、视图停靠、截屏
- 查任意 `AK*` 头文件、`AK_*` 宏、`ak.wwise.*` / `ak.soundengine.*` 过程签名、WAQL 语法
- 需要时把逻辑固化成一次性脚本，或打包成可分发的独立工具（`.exe`）

---

## 环境要求

| 组件 | 要求 | 用途 |
| --- | --- | --- |
| **Wwise Authoring** | 2024.1 及以上 | 被操作的目标；需开启 WAAPI（见下） |
| **`user-wwise-mcp` MCP 服务器** | 可用 | Agent 操作/验证 Wwise 的默认接口 |
| **Python** | 3.9+ | 运行 `scripts/search.py`（文档检索，纯标准库）；以及 `scripts/wwise_waapi.py`（CLI/脚本） |
| **`waapi-client`** | `pip install waapi-client` | **仅** `scripts/wwise_waapi.py` 与独立脚本需要；纯 MCP 操作和文档检索**不需要** |

**Wwise 端开启 WAAPI：** `Project → User Preferences → Enable Wwise Authoring API` 勾选。
`waapi-client` 默认连接 WAMP 端口 `ws://127.0.0.1:8080/waapi`（8080 是 WebSocket 端口，
不是 HTTP 的 8090/8095）。

> 说明：文档语料是 2024.1.13 快照，但适用于**该版本及以上**——只要新版本没有重命名
> URI 或更改参数架构即可；有疑问时以实时 `getSchema` 为准。

---

## 快速开始

### 1) 确认与 Wwise 的连接

- **MCP 方式（Agent 默认）**：调用 `ping_waapi`，健康返回 `{"isAvailable": true}`。
- **CLI 方式**（需 `waapi-client`）：

```powershell
python scripts\wwise_waapi.py ak.wwise.core.ping
```

连接失败时参见 [workflows/setup-and-connect.md](workflows/setup-and-connect.md)。

### 2) 查文档（KNOW）

```powershell
# 关键词 AND 搜索（大小写不敏感），返回命中页 id
python scripts\search.py ak.wwise.core.object.get
python scripts\search.py IAkPlugin factory

# 按 id 打印整页
python scripts\search.py --get 3375

# 常用过滤：--regex / --type / --file / --limit / --context
python scripts\search.py AK_STATIC_LINK_PLUGIN --type MemberDetail
python scripts\search.py --file AkSoundEngine.h
```

> 首次检索会在 `data/` 旁生成一个小的索引 `WwiseSDK-Windows.jsonl.idx`（自动维护、可安全
> 删除），之后每次查询约几十毫秒。**切勿直接读取 19MB 的 `data/WwiseSDK-Windows.jsonl`。**

### 3) 操作并验证（DO + VERIFY）

优先用 **MCP 工具**（工具名基本镜像 WAAPI URI，如 `get_objects` ≈ `ak.wwise.core.object.get`）。
需要批量逻辑时再写一次性脚本：

```powershell
# CLI：<uri> <args-json> [options-json]
python scripts\wwise_waapi.py ak.wwise.core.object.get `
  '{"waql":"$ from type Sound take 5"}' '{"return":["id","name"]}'
```

```python
# 作为库导入，复用连接跑批量
from scripts.wwise_waapi import call
for s in call("ak.wwise.core.object.get",
              args={"waql": "$ from type Sound where volume > 0"},
              options={"return": ["id", "name"]})["return"]:
    ...  # 你的批处理逻辑
```

**验证闭环**：`ping` → 操作 → 回读状态（`get_objects` / `get_log_info`）→ 必要时
`post_event` + Profiler / 截屏确认 → 对比预期与实际。**任何"成功"结论都要有回读或截图支撑。**

---

## 目录结构

```
wwise-waapi-skill/
├─ SKILL.md                      # Agent 入口（能力总览 + 渐进式加载索引）
├─ README.md                     # 本文档（面向人类）
├─ scripts/
│  ├─ search.py                  # 离线文档检索（纯标准库，带持久化索引）
│  └─ wwise_waapi.py             # waapi-client 的轻量封装（CLI + 库）
├─ data/
│  └─ WwiseSDK-Windows.jsonl     # Wwise SDK 2024.1.13 全量文档（~19MB，勿直读）
├─ workflows/                    # 按任务分类的操作指南（执行时按需加载）
│  ├─ setup-and-connect.md       # 连接排错、端口、安装
│  ├─ query-objects.md           # 用 WAQL 查询对象
│  ├─ create-and-modify.md       # 创建/修改/移动/删除（含 set_objects 批量）
│  ├─ import-audio.md            # 导入音频/语音
│  ├─ soundbank.md               # SoundBank 包含项与生成
│  ├─ transport-soundengine.md   # Event / RTPC / State / Switch / 播放测试
│  ├─ profiler.md                # Profiler 采集与数据读取
│  ├─ ui-and-layout.md           # UI 命令、布局、视图、截屏
│  └─ project-and-meta.md        # 工程信息、保存、打开/关闭、schema 发现
└─ references/                   # 构造参数/解读结果时的查表页
   ├─ waapi-procedures.md        # WAAPI URI 目录 + 参数签名 + URI↔MCP 工具对照
   ├─ waql-syntax.md             # WAQL 语法（源、变换、运算符）
   ├─ object-types.md            # 路径式创建的 <nodeType> 标签
   ├─ object-accessors.md        # 常用属性/引用（@Volume、parent.descendants 等）
   ├─ set-objects-cookbook.md    # set_objects 规范化 payload 范式
   ├─ enums-and-conventions.md   # 枚举/魔法数字、路径转义、单位、返回结构
   └─ state-properties.md        # 可作为 State 列的属性
```

---

## 常见问题

- **报 `waapi-client is not installed` 但其实装了？** 只有 `scripts/wwise_waapi.py` 与独立
  脚本需要它；`pip install waapi-client` 即可。纯文档检索（`search.py`）与纯 MCP 操作都不需要。
- **连接超时 / `isAvailable: false`？** 多半是 Wwise 弹了模态对话框（迁移/保存提示）阻塞了
  Authoring；手动点掉即可。
- **自定义了 WAAPI 端口？** 在 `scripts/wwise_waapi.py` 里改
  `WaapiClient(url="ws://127.0.0.1:<port>/waapi")`。
- **检查静态文档是否与语料漂移：**
  `python scripts\search.py --drift-check references/waapi-procedures.md`

---

## 安全约定（重点）

- **破坏性操作先确认**：`delete_object`、不保存关闭工程、`generate_soundbanks` 带
  `clearAudioFileCache`、`set_soundbank_inclusions` 的 `replace` 都会销毁状态。
- **`copy_object` 一个 Work Unit 不可撤销且会强制保存**——务必先警告。
- **多步写操作用 undo group 包裹**（`begin_undo_group` … `end_undo_group`）。
- **别编属性名/枚举值**：不确定就用 `getPropertyInfo` / `getPropertyAndReferenceNames` 现场自省。
- **路径在 JSON 里要用 `\\` 转义**。

更完整的规则见 [SKILL.md](SKILL.md) 的 *Hard rules* 一节。
