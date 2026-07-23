# Wwise WAAPI Skill

一个面向 AI Agent 的 Wwise Authoring API (WAAPI) 参考资料集。它的目的是让 Agent 能够
查明：Wwise Authoring API 提供哪些接口、每个接口的参数结构，以及如何正确构造调用。

> 本 README 面向人类读者。Agent 的入口是 [`SKILL.md`](SKILL.md)，其余页面在使用时按需加载。

---

## 目的与内容

该 Skill 由两部分组成。

### 1. 离线文档语料

`data/WwiseSDK-Windows.jsonl` 收录了 **Wwise SDK 2024.1.13 (Windows)** 的完整文档，约
9,400 页，涵盖：

- **C++ SDK**：头文件、类、宏、枚举等；
- **WAAPI 参考**：`ak.wwise.*` / `ak.soundengine.*` 过程及其参数 schema；
- **WAQL**：Wwise Authoring 查询语言。

文档通过 `scripts/search.py` 检索，不需要将整份文件载入上下文。

### 2. 整理的参考与工作流页面

`references/` 与 `workflows/` 将常用接口的用法、参数形状及约定（枚举取值、单位、路径
转义、返回结构等）整理为可直接查阅的页面，作为语料的补充与索引。

借助上述内容，Agent 可以：

- 确认某个 WAAPI 过程或 C++ 符号是否存在，并取得其准确签名；
- 查明参数字段、类型、枚举取值与单位；
- 按规范构造对象查询（WAQL）、创建 / 修改（`set_objects`）、音频导入、SoundBank
  生成、事件投递、RTPC / State / Switch 等调用；
- 在需要时通过 Python 客户端实际发起调用并读回结果进行核对。

---

## 环境要求

| 组件 | 要求 | 说明 |
| --- | --- | --- |
| Wwise Authoring | 2024.1 及以上 | 需在 `Project → User Preferences → Enable Wwise Authoring API` 中开启 WAAPI |
| Python | 3.9+ | 运行 `scripts/search.py`（文档检索，仅用标准库） |
| `waapi-client` | `pip install waapi-client` | 仅当需要通过 `scripts/wwise_waapi.py` 实际发起调用时才需要；纯文档检索不需要 |

`waapi-client` 默认连接 WAMP 端口 `ws://127.0.0.1:8080/waapi`（WebSocket 端口，非 HTTP 的
8090/8095）。

文档语料对应版本 2024.1.13，适用于该版本及以上；若更高版本重命名了 URI 或更改了参数
结构，以运行中 Wwise 的 `ak.wwise.waapi.getSchema` 返回为准。

---

## 快速开始（安装）

该 Skill 采用 SKILL.md 的 Agent Skill 格式：安装 = 把整个 `wwise-waapi-skill/` 目录
放进工具的 skills 目录。放好后 Agent 会通过 `SKILL.md` 自动发现，无需注册。下面以
**Cursor（Windows）** 为例，逐步说明。

### 第 1 步：先决定放在哪

- **全局**（所有项目都能用）：放到用户目录下的 `.cursor\skills\`
  完整路径为 `C:\Users\<你的用户名>\.cursor\skills\`。
- **项目级**（只对某个项目生效）：放到该项目根目录下的 `.cursor\skills\`。

下面用全局为例。

### 第 2 步：获取文件（二选一）

**方式 A — 用 git 克隆（推荐）**

```powershell
# 这台机器上 git 没进 PATH，先临时加进来
$env:PATH = "C:\Program Files\Git\cmd;$env:PATH"

# 确保目标目录存在，然后克隆进去
New-Item -ItemType Directory -Force "$env:USERPROFILE\.cursor\skills" | Out-Null
cd "$env:USERPROFILE\.cursor\skills"
git clone https://github.com/HuxxxTOSE/WwiseSDKSkill_toseVer.git wwise-waapi-skill
```

**方式 B — 下载 ZIP**

1. 打开仓库页面 → 绿色 **Code** 按钮 → **Download ZIP**。
2. 解压。注意解压后文件夹名通常是 `WwiseSDKSkill_toseVer-main`，里面才是内容。
3. 把它放到 `C:\Users\<你的用户名>\.cursor\skills\` 下，并**重命名为 `wwise-waapi-skill`**。

### 第 3 步：核对目录结构

最终必须是这样（`SKILL.md` 直接位于 `wwise-waapi-skill` 下，不能多套一层）：

```
C:\Users\<你的用户名>\.cursor\skills\wwise-waapi-skill\
├─ SKILL.md
├─ scripts\
├─ data\
├─ workflows\
└─ references\
```

可以用命令快速确认（应输出 `True`）：

```powershell
Test-Path "$env:USERPROFILE\.cursor\skills\wwise-waapi-skill\SKILL.md"
```

> `.cursor` 是隐藏文件夹。在资源管理器里如果看不到，勾选"查看 → 隐藏的项目"，
> 或直接在地址栏输入 `%USERPROFILE%\.cursor\skills` 回车进入。

### 第 4 步：让 Cursor 识别

重启 Cursor（或新建一个对话）。当你的提问涉及 Wwise / WAAPI 时，Agent 会自动加载
本 Skill，无需手动开启。

### （可选）第 5 步：装脚本依赖

只有当你要用 `scripts/` 里的 Python 脚本时才需要（纯文档检索只需 Python，实际发起
调用还需 `waapi-client`），详见上方 [环境要求](#环境要求)：

```powershell
pip install waapi-client
```

> 其他遵循同一 Skill 格式的工具，放入各自的 skills 目录即可（如 Claude Code 的
> `.claude/skills/`）。

---

## 目录结构

```
wwise-waapi-skill/
├─ SKILL.md                      # Agent 入口（能力总览 + 按需加载索引）
├─ README.md                     # 本文档
├─ scripts/
│  ├─ search.py                  # 离线文档检索（标准库，带持久化索引）
│  └─ wwise_waapi.py             # waapi-client 封装（CLI + 库）
├─ data/
│  └─ WwiseSDK-Windows.jsonl     # Wwise SDK 2024.1.13 全量文档（约 19MB，勿直读）
├─ workflows/                    # 按任务分类的操作指南（执行时按需加载）
│  ├─ setup-and-connect.md       # 连接、端口、安装排错
│  ├─ query-objects.md           # 用 WAQL 查询对象
│  ├─ create-and-modify.md       # 创建 / 修改 / 移动 / 删除（含 set_objects 批量）
│  ├─ import-audio.md            # 导入音频
│  ├─ soundbank.md               # SoundBank 包含项与生成
│  ├─ transport-soundengine.md   # Event / RTPC / State / Switch / 播放
│  ├─ profiler.md                # Profiler 采集与数据读取
│  ├─ ui-and-layout.md           # UI 命令、布局、视图、截屏
│  └─ project-and-meta.md        # 工程信息、保存、打开 / 关闭、schema 发现
└─ references/                   # 构造参数 / 解读结果时的查表页
   ├─ waapi-procedures.md        # WAAPI URI 目录与参数签名
   ├─ waql-syntax.md             # WAQL 语法（源、变换、运算符）
   ├─ object-types.md            # 路径式创建的 <nodeType> 标签
   ├─ object-accessors.md        # 常用属性 / 引用（@Volume、parent.descendants 等）
   ├─ set-objects-cookbook.md    # set_objects 规范化 payload 范式
   ├─ enums-and-conventions.md   # 枚举、路径转义、单位、返回结构
   └─ state-properties.md        # 可作为 State 列的属性
```

---

## 使用约定

- **不臆造属性名与枚举值**：不确定时用 `getPropertyInfo` /
  `getPropertyAndReferenceNames` 查询，或检索文档确认。
- **路径需转义**：JSON 中对象路径的分隔符使用 `\\`。
- **枚举为按属性的 0 基索引**：同一整数在不同属性含义不同，逐属性解析。
- **区分对象模型与运行时接口**：`ak.wwise.*` 操作 Authoring 工程数据，
  `ak.soundengine.*` 控制连接的声音引擎，二者语义不同。
- **注意破坏性操作**：删除对象、不保存关闭工程、清理缓存的 SoundBank 生成、
  以 `replace` 方式设置 Bank 包含项等都会改变或销毁状态。

更详细的规则见 [`SKILL.md`](SKILL.md) 与 [`references/enums-and-conventions.md`](references/enums-and-conventions.md)。

---

## 校验

```powershell
# 检查静态文档中引用的 URI 是否仍存在于语料中（漂移自查）
python scripts\search.py --drift-check references/waapi-procedures.md
```
