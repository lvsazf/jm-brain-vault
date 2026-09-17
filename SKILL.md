---
name: jm-brain-vault
description: Manage, search, ingest, clip, transcribe, export, and maintain the user's Obsidian knowledge base (Brain Vault). Triggers on requests related to knowledge management, note retrieval ("查资料", "找笔记", "搜索知识库"), health diagnostics ("知识库体检", "运行doctor"), web clipping ("网页剪藏", "保存文章"), audio voice transcription ("录音转录", "会议录音整理"), business document export ("导出Word/HTML", "排版导出"), link integrity and validity verification ("有效性审计", "知识更新"), monthly pulse and digest ("月度大脑脉搏", "知识资产简报"), or any operation on notes, canvases, or bases in the user's vault.
---

# 🧠 JM Brain Vault 知识中枢智能管家 Skill

> **定位**：数字大脑专属业务治理中枢与生命周期调度器  
> **根路径**：默认 `~/Documents/Brain_Vault`（可在根目录 `.config.toml` 中自定义）  
> **核心体验**：**用户零心智负担自然对话 ｜ AI 底层全自动智能路由与多模态编排**  
> **底层组合**：组合官方 `obsidian-markdown`（标准语法）、`json-canvas`（原生视觉白板）、`obsidian-bases`（原生动态数据库）、`defuddle`（网页降噪剪藏）与 `obsidian-cli`（客户端联动）

---

## ⚡ 0. 零心智负担·全自动智能决策路由 (Autonomous Routing)

用户无需学习任何专业指令、软件语法或技术概念，只需在对话框中自然沟通。AI 会在后台自动研判业务场景，并自动匹配最佳的载体与工具链路：

```
                    ┌─────────────────────────┐
                    │      用户自然语言交互   │
                    └────────────┬────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
   【想法/策划/对话】       【多物料/台账/清单】     【网页链接/文章URL】
         │                       │                       │
         ├─ 自动提取核心逻辑     ├─ 自动打标归类         └─ 自动调用 Defuddle
         ├─ 生成 Markdown 笔记   ├─ 自动生成/更新           剥离广告与网页代码
         └─ (若涉及跨界/流程)       .base 原生数据库        生成纯净 Markdown
            主动配发 .canvas        (表格/卡片看板视图)     自动分类打标入库
            视觉关系白板
```

| 用户交互场景 | AI 自动化路由与底层组合 | 用户直接获得的交付形态 |
| :--- | :--- | :--- |
| **发来一段杂乱灵感/对话** | 智能提炼结构，生成标准 Markdown 笔记，打好五维标签并建立双链 | 层次分明的 Markdown 笔记 |
| **梳理跨界协同/复杂战略/短剧大纲** | 自动调用 `json-canvas` 规格，将复杂逻辑可视化串联 | 原生 `.canvas` 视觉无限白板，点开即可在脑图上交互 |
| **成批量的选题/台账/场景卡** | 自动调用 `obsidian-bases` 规格，生成或挂载至 `.base` 文件 | 原生类似 Airtable 的表格/卡片看板视图 |
| **发来一个网页或文章链接** | 自动调用 `defuddle` 剥离页面垃圾代码，仅提纯纯净正文 Markdown | 零噪点、排版清爽的收藏笔记 |
| **发来物理文件 (Office/媒体)** | 物理级 100% 零篡改存盘，同名 MD5 防覆盖，建立看板双链 | 安全存盘回执 ＋ 关联看板索引 |
| **模糊询问“找某个文件”** | 意图与同义词展开 ＋ 全文穿透 ＋ 活跃度加权 | 核心提要 ＋ 终端一键 `open -R` 高亮文件 |

---

## 1. 核心工作模式与双输入分流

> 核心规约：[双输入模式与存盘规约](./references/intake-modes.md)

### 模式一：【文件直传模式】（用户直接发来物理文件）
* **第一红线**：**正文 100% 绝对零篡改，纯物理级安全存盘**。
* **执行工序**：
  1. **防同名覆盖**：入库前比对 MD5；若内容不同，添加自然语义后缀，绝不静默覆盖；
  2. **有效性规则研判**：判定新文件对老文件的取代关系；
  3. **分类入库**：放入对应业务板块（拿不准的入 `00_Inbox` 缓冲区）；
  4. **标签与双链**：
     * Markdown 文件：顶部注入 YAML 标签，并自动与上级或相关笔记建立双链 `[[...]]`；
     * 二进制文件（Office/PDF/媒体）：正文原封不动，建立伴生索引笔记或直接挂载至对应看板；
  5. **输出标准回执**。

### 模式二：【内容整理生成模式】（用户发来零散想法、语音转文字或草稿）
* **第一红线**：**去粗取精、专业结构化梳理，生成符合 Obsidian 工业级规范的新笔记**。
* **执行工序**：
  1. **体裁识别与标准化提炼**：口播按黄金前3秒，短剧提炼冲突与镜头，方案提炼落地步骤；
  2. **自然语义命名**：清晰自然的业务名，拒绝死板冗长后缀；
  3. **多模态增强（自动决策）**：
     * 需要视觉化时主动生成 `.canvas` 原生白板；
     * 需要表格化时主动生成 `.base` 原生数据库；
  4. **落盘与双向织网**：存入最佳目录，自动关联看板。

---

## 2. 知识有效性状态与客观校验规则 (取代主观“进行中”)

> 核心规约：[客观四态研判与演进规约](./references/evolution-states.md)

AI 绝不主观猜测现实中业务处于所谓的“进行中”，而是**严格基于客观规则校验文件的知识有效性状态**：

| 有效性状态 | 判定特征与规则 | 裁决动作 |
| :--- | :--- | :--- |
| **① 整体有效**<br/>(Fully Valid) | 结构完整自洽，与现行最高标准对齐，**无任何待决标记**（无【待确认】等） | 标注 `status: 状态/整体有效`，作为现行直接引用的主力依据 |
| **② 部分有效**<br/>(Partially Valid) | 主体有效，但**包含未决标记**（如【待确认】、【待核验】、【旧分类】）或局部被新补丁修改 | 标注 `status: 状态/部分有效`，提示待清洗与核验的章节 |
| **③ 失效归档**<br/>(Superseded) | 整体改版或已被更高版本（如 V3.1 取代旧版）全量取代 | 标注 `status: 状态/失效归档`，**绝不物理删除**，顶部插入新版跳转索引 `[[新版文件名]]` |
| **④ 客观事实**<br/>(Immutable Fact) | 合同扫描件、资产凭证、克隆音频母本、历史原始档案 | 标注 `status: 状态/客观事实`，纯物理保存，永久有效不参与淘汰 |

### ⚡ 主动闭环校准与整体性深度研判 (Autonomous Calibration & Holistic Analysis)
- **拒绝被动等待，主动闭环自愈**：AI 绝不能成为仅输出“发现待校准，等待用户手工跑脚本”的被动汇报者，而必须在发现状态偏差、目录沉淀或版本跃迁时，**主动穿透正文、结合业务全景进行整体性分析，并自动执行闭环校准（Auto-Heal）**。
- **整体性正文语义研判**：
  1. **语义环境智能甄别**：区分“真正的业务待办标记”与“规范文档/代码示例中的用词提及”，杜绝教条式子字符串误伤；
  2. **过渡期全集资料研判**：若一份文档前半部分是现行执行手册，后半部分保留了大量“待确认旧版本”，AI 自动研判其为“过渡期全集资料库”，客观评定为 `状态/部分有效`，防止旧规则干扰现行决策；
  3. **自动化闭环**：扫描 ➔ 正文语义与依赖研判 ➔ 自动校准 Frontmatter ➔ 同步更新 SQLite 持久化索引 ➔ 向用户输出宏观格局与健康洞察。

---

## 3. 动态代谢与月度巡检机制 (看板不写死)

> **核心哲学**：**看板不是死板分类表，而是“当下活跃战场的动态聚光灯”！**  
> 主航道与看板内容由全库文件的实际修改时间戳（`mtime`）客观驱动，每月进行一次生命周期新老代谢。[详见动态代谢规约](./references/monthly-pulse.md)

* 运行内置扫描脚本：`python3 scripts/scan_pulse.py`
* 运行有效性校验脚本：`python3 scripts/verify_validity.py`
* 运行隐式提及扫描脚本：`python3 scripts/scan_unlinked.py`

---

## 4. 智能模糊检索与语义召回协议

> 核心规约：[智能模糊检索与交付规约](./references/search-protocol.md)

当用户提出模糊查文件需求（关键字、零散记忆、想法描述）时：
1. **同义词与意图展开**：自动映射业务词汇（如“烟酒店” ➔ “即时零售”、“传统门店数字化”）；
2. **全库正文与标签穿透**：秒级穿透全库正文与 YAML 标签；
3. **活跃度加权优先**：同类候选文件中，优先推荐修改时间最近且处于 `状态/整体有效` 的最新版本；
4. **Obsidian 原生 URI 直达与跨平台文件管理器定位**：
   * 客户端一键唤起：`[在 Obsidian 中打开笔记](obsidian://open?vault=Brain_Vault&file=path/to/file.md)`
   * 跨平台终端文件定位：macOS `open -R "<path>"` ｜ Windows `explorer.exe /select,"<path>"` ｜ Linux `xdg-open "<dir>"`

---

## 5. 标准执行回执格式

```markdown
✅ **JM Brain Vault 执行回执**
- **操作模式**：[文件直传 (零篡改) ｜ 内容整理生成 ｜ 外链提纯]
- **文件路径**：`[相对 Brain_Vault 的完整路径]`
- **有效性状态**：`状态/整体有效` ｜ `状态/部分有效` ｜ `状态/客观事实`
- **模态增强**：[伴生 .canvas 视觉白板 ｜ 伴生 .base 原生数据库 ｜ 纯净 Markdown]
- **新旧演进**：[全量取代 [[旧版]] ｜ 增量补充 [[母本]] ｜ 跨业务协同]
- **看板联动**：已挂载至对应作战看板
- **客户端直达**：[在 Obsidian 客户端中一键打开](obsidian://open?vault=[Vault名]&file=[URL编码路径])
- **系统文件定位**：`[系统文件管理器定位命令]`
```
---

## 🛠️ 6. 底层智能化脚本与武器库一览 (AI 自主按需调度)

所有工具均支持静默调用，无需用户记忆命令：

| 脚本工具 | 核心功能与技术底座 | 典型调用命令与触发场景 |
| :--- | :--- | :--- |
| `hybrid_search.py` | SQLite Trigram FTS5 + BM25 混合语义检索 | `python3 scripts/hybrid_search.py "<关键词>"`<br/>用户提出模糊查文件、找资料时秒级调用 |
| `smart_flashback.py` | 历史笔记时空闪回与跨周期灵感漫步 | `python3 scripts/smart_flashback.py "<业务主题>"`<br/>用户思考新业务时自动联想历史沉淀 |
| `clip_url.py` | 工业级网页/公众号降噪去广告提纯管道 | `python3 scripts/clip_url.py "<URL>"`<br/>用户发来文章/微信 URL 链接时调用 |
| `export_note.py` | 商业级 Word (.docx) / 打印排版 HTML 导出 | `python3 scripts/export_note.py "<文件路径>" [docx\|html\|all]`<br/>用户要求将笔记发给客户或导出时调用 |
| `transcribe_audio.py` | Faster-Whisper 本地离线高精度听写提纯 | `python3 scripts/transcribe_audio.py "<音频路径>" [tiny\|base\|small]`<br/>用户发来录音文件（.m4a/.mp3/.wav）时调用 |
| `graph_diagnosis.py` | 图网络拓扑、超级中枢与动态业务断层算法诊断 | `python3 scripts/graph_diagnosis.py`<br/>用户询问知识库盲区或宏观结构时调用 |
| `generate_digest.py` | 动态数字大脑生长态势与里程碑简报 | `python3 scripts/generate_digest.py`<br/>月末复盘或用户要求查看大脑成长时调用 |
| `weave_links.py` | 知识图谱孤岛提及自动探测与双向编织 | `python3 scripts/weave_links.py [--auto]`<br/>定期图谱自愈、织密上下文网络时调用（`--auto` 写入） |
| `scan_unlinked.py` | 隐式提及与未链接概念网络深度探测 | `python3 scripts/scan_unlinked.py`<br/>探测库内已提及但未打双链的高频概念 |
| `verify_validity.py` | 客观知识有效性规则裁决审计 (整体/部分/失效) | `python3 scripts/verify_validity.py [--fix]`<br/>入库校验与全库状态客观校准时调用 |
| `scan_pulse.py` | 30天动态生命周期与 mtime 活跃热力感知 | `python3 scripts/scan_pulse.py`<br/>保持作战看板动态更迭时调用 |
| `verify_links.py` | 全库双向链接零死链与 YAML 语法合规体检 | `python3 scripts/verify_links.py`<br/>日常维护与健康巡检时调用 |
| `sync_config.py` | 配置自动提炼与版本跃迁双链自愈引擎 | `python3 scripts/sync_config.py`<br/>嗅探新客户目录、别名与版本更新时调用 |
| `vault_db.py` | SQLite 持久化索引引擎 (WAL + mmap + 增量同步) | `python3 scripts/vault_db.py`<br/>初始化、重建索引或持久化健康自检时调用 |
| `vault_doctor.py` | 一体化全息体检医生 (链接/有效性/热力/自愈) | `python3 scripts/vault_doctor.py`<br/>全面系统体检与交付自愈时一键调用 |

---

## ⚙️ 7. 根目录配置与开源自定义 (Config System)

本技能采用**代码引擎与用户私有配置彻底分离**的设计（Zero-Leak 架构），保证开源与商业交付时的绝对隐私安全：

- **`.config.toml`**（本地私有配置）：以 `.` 开头存放于本技能根目录，包含用户真实的知识库路径、个人称谓、商业客户专属同义词与自动双链字典。采用 TOML 语法，支持中文注释（`#`），**被 `.gitignore` 保护，永不上传**。
- **`.config.template.toml`**（开源公共模板）：包含完整的 TOML 配置结构、字段注释与通用示例（如电商、零售、战略定位等），供开源克隆用户参考。
- **动态加载器**：所有底层 Python 脚本统一通过 `scripts/config_loader.py` 动态调用原生 `tomllib` 加载。若未检测到 `.config.toml`，自动安全回退至 `.config.template.toml`。

---

## 🚀 8. 统一门面与全局命令行工具 (Unified CLI Facade)

无论是终端开发者还是在各类 AI Agent 交互中，均可直接使用统一人性化门面 `./vault`（或已安装至 `~/.local/bin/vault` 的全局命令）：

```bash
# 检索与状态
vault search "烟酒零售"          # 混合语义检索 + Obsidian 客户端一键直达
vault search "零售" --ui         # 渲染可交互 Generative UI 卡片
vault status                    # 查看当前连接知识库、有效性分布与索引健康度

# 诊断与体检
vault doctor                    # 全库一体化生命体征健康审计
vault doctor --ui               # 渲染可视化健康体检雷达仪表盘

# 内容输入与转换
vault clip "https://..."        # 网页智能降噪纯净剪藏
vault export "01_思考/复盘.md" docx # 商业级排版 Word/HTML 导出
vault transcribe "meeting.m4a"  # Faster-Whisper 本地离线高精度听写

# 图谱治理与生命周期
vault pulse                     # 30天活跃热力感知与休眠沉淀
vault weave --auto              # 孤岛笔记概念提及智能双向织网
vault digest                    # 生成月度数字大脑生长与资产简报
vault graph                     # 知识图谱拓扑与断层盲区诊断
vault verify --fix              # 客观知识四态有效性全库校准
vault sync                      # 配置自动同步与版本自愈
```

---

## 🎨 9. 可视化 Generative UI 交互体验 (<agent-embed>)

在 Google Antigravity 中，AI 可自主生成并内嵌原生响应式 UI 卡片：
- **搜索卡片**：展示匹配度进度条、客观有效性标签、高亮摘要，以及 `🟣 1-Click Open in Obsidian` 客户端一键直达。
- **健康雷达**：可视化展示 6 大生命体征自检清单、知识点总数、索引库容量与 Vault 运行指标。

---

## ⏰ 10. 定时自动化任务推荐 (/schedule Automation)

用户可随时在 Antigravity 聊天窗口中键入 `/schedule`，设定自动化后台周期任务保持知识中枢常青：

- **每月初知识大脑脉搏与生长简报**：
  > `/schedule` 每月 1 号早上 9:00：`运行 vault doctor 与 vault digest，生成本月知识中枢健康审计与数字大脑生长简报。`
  > *(Cron: `0 9 1 * *`)*

- **每周生命周期热力感知与休眠降级**：
  > `/schedule` 每周日晚 22:00：`运行 vault pulse，感知 30 天笔记活跃热力，自动识别并沉淀休眠档案。`
  > *(Cron: `0 22 * * 0`)*


