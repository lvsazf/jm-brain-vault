# 🧠 JM Brain Vault (数字大脑知识中枢智能管家)

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License">
  <img src="https://img.shields.io/badge/Python-3.11+-brightgreen.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Obsidian-Native%20Bases%20%26%20Canvas-purple.svg" alt="Obsidian">
  <img src="https://img.shields.io/badge/Multi--Agent-Hermes%20|%20Codex%20|%20Antigravity%20|%20Claude%20Code%20|%20Cursor-orange.svg" alt="Multi-Agent Supported">
  <img src="https://img.shields.io/badge/Architecture-Zero--Leak%20Config-success.svg" alt="Architecture">
</p>

> **用户零心智负担自然对话 ｜ AI 底层全自动智能决策路由与多模态编排**  
> **面向 Obsidian 工业级规范的跨平台多智能体（Multi-Agent）数字大脑治理中枢与生命周期调度器**

---

## 🌐 多 AI Agent 生态支持 (Multi-Agent Compatibility)

`JM Brain Vault` 采用 **Agent-Agnostic（智能体中立）** 架构设计。底层由**工业级规范提示词（SKILL.md / references）**、**纯本地 Python 算法引擎（scripts/）** 以及 **TOML 隐藏配置** 组成。

它原生适配目前各类核心 AI Agent 框架与开发环境：

| AI Agent 载体 | 适配方式 | 交互与应用体验 |
| :--- | :--- | :--- |
| 🦅 **Hermes Agent** | 作为专属长期工作记忆与中枢 Toolset 挂载 | 原生记忆织网、有效性校验与多模态资产检索 |
| 🧠 **Codex / OpenAI Agent** | 通过 `AGENTS.md` / System Prompt 规则驱动 | 执行严格的物理零篡改存盘红线与客观四态研判 |
| 🪐 **Google Antigravity / Gemini CLI** | 原生 Skill 挂载 (`~/.gemini/config/skills/`) | 对话框直接发需求，AI 自主多模态路由编排 |
| 🟣 **Claude Code (Anthropic)** | 在 `CLAUDE.md` 声明工具指令或终端直接调用 | 强大推理能力配合本地混合搜索、体检与自愈 |
| ⚡ **Cursor / Windsurf** | 引入 `.cursorrules` / `.windsurfrules` | 在 IDE 边写笔记/代码边秒级呼出图谱与导出 |
| 💻 **独立终端 (Standalone Python CLI)** | 直接运行 `python3 scripts/vault_doctor.py` | 即使脱离任何 AI，人类也能一键检索、体检与导出 |

---

## 🌟 核心设计哲学 (Core Philosophy)

1. **⚡ 零心智负担智能路由 (Zero Cognitive Load)**  
   用户无需学习任何专业指令、软件语法或技术概念，只需在对话框中自然沟通。AI 后台自动研判业务场景，按需生成标准 Markdown、原生 `.canvas` 视觉白板或 `.base` 数据库看板。
2. **🛡️ 双输入分流与物理存盘红线 (Dual-Mode Ingestion)**  
   - **文件直传模式**：正文 **100% 绝对零篡改**，MD5 哈希防静默覆盖，保留原始时间戳与物理原貌；
   - **内容整理模式**：去粗取精、专业结构化梳理，注入标准五维 YAML 标签并自动编织双向链接。
3. **⚖️ 客观知识有效性规则校验 (Objective 4-State Validity)**  
   彻底摒弃主观模糊的“进行中”状态，严格基于客观规则研判知识的生命周期：
   - 🟢 `状态/整体有效` (现行直接引用的主力依据)
   - 🟡 `状态/部分有效` (含待核验标记或局部补丁)
   - 🧊 `状态/失效归档` (已被更高版本取代，绝不物理删除，顶部注入新版跳转)
   - 🛡️ `状态/客观事实` (合同、司法凭证、声音克隆母本，永久有效)
4. **🔥 30天动态代谢与月度巡检 (Dynamic Pulse Metabolism)**  
   看板不是死板分类表，而是当下活跃战场的动态聚光灯。由全库文件的实际修改时间戳（`mtime`）客观驱动，每月进行一次生命周期新老代谢。
5. **🔒 零隐私残留架构 (Zero-Leak Architecture)**  
   代码与私有配置彻底分离。本地个人路径、姓名、商业客户同义词与专属实体双链字典保存在以 `.` 开头的 `.config.toml` 中，受 `.gitignore` 保护，代码库本身 100% 零隐私泄露。

---

## 🛠️ 底层智能化武器库 (Script Arsenal)

技能内置了 14 个纯本地、离线优先的 Python 算法引擎，支持静默调度与一键体检：

| 脚本工具 | 核心功能与技术底座 | 典型触发场景 |
| :--- | :--- | :--- |
| **`hybrid_search.py`** | SQLite Trigram FTS5 + BM25 混合语义检索 | 用户提出模糊查文件、找资料时秒级调用 |
| **`sync_config.py`** | 配置自动提炼与版本跃迁自愈引擎 | 自动嗅探新客户目录、别名与版本更迭 |
| **`vault_doctor.py`** | 一体化全息体检医生 (链接/有效性/热力/自愈) | 全面系统体检与交付自愈时调用 |
| **`weave_links.py`** | 知识图谱孤岛提及自动探测与双向编织 | 定期图谱自愈、织密上下文网络时调用 |
| **`scan_unlinked.py`** | 隐式提及与未链接网络深度探测 | 扫描文中提及但未打 `[[...]]` 的高价值概念 |
| **`transcribe_audio.py`** | Faster-Whisper 本地离线高精度听写提纯 | 用户发来录音文件（.m4a/.mp3/.wav）时调用 |
| **`export_note.py`** | 商业级 Word (.docx) / 打印排版 HTML 导出 | 用户要求将笔记发给客户或对外交付时调用 |
| **`graph_diagnosis.py`** | 图网络拓扑、超级中枢与商业断层算法诊断 | 深度研判知识库盲区、弱连接与中枢节点 |
| **`generate_digest.py`** | 月度/周期性数字大脑生长与里程碑简报 | 月末复盘或用户要求查看大脑成长时调用 |
| **`verify_validity.py`** | 客观知识有效性规则裁决审计 | 入库校验与全库状态客观校准时调用 |
| **`scan_pulse.py`** | 30天动态生命周期与 mtime 活跃热力感知 | 保持作战看板动态更迭时调用 |
| **`verify_links.py`** | 全库双向链接零死链与 YAML 语法合规体检 | 日常维护与健康巡检时调用 |
| **`clip_url.py`** | 工业级网页/公众号降噪去广告提纯管道 | 用户发来文章/微信 URL 链接时调用 |
| **`smart_flashback.py`** | 历史笔记时空闪回与跨周期灵感漫步 | 用户思考新业务时自动联想历史沉淀 |

---

## 🚀 快速安装 (Quick Installation)

无论你使用哪种 Agent 载体，第一步先克隆代码并执行一键配置程序：

```bash
git clone https://github.com/lvsazf/jm-brain-vault.git
cd jm-brain-vault
./install.sh
```

> **`./install.sh` 执行动作**：自动检测 Python 3.11+ 环境、自动安装依赖、基于模板初始化隐藏配置文件 `.config.toml`，并自动探测当前机器上的 Agent 环境完成软链挂载。

---

## 🔌 主AI Agent 接入配置 (Agent Integration Guides)

安装完成后，根据你的主力 AI 工具，选择对应的配置方式：

### 1. 🦅 Hermes Agent 接入
在你的 Hermes Agent 工作区中，将 `scripts/` 作为长期记忆与知识中枢 Toolset 挂载：
```python
# Hermes Agent 工具链挂载示例
from scripts.config_loader import get_vault_path
from scripts.hybrid_search import search_vault
from scripts.vault_doctor import run_health_check
```
*或者直接配置 Hermes 的 Shell 执行权限*，让 Hermes 自主根据用户问题调用：
```bash
python3 <skill-path>/scripts/hybrid_search.py "<query>"
```

### 2. 🧠 Codex / OpenAI Agent 接入
在项目根目录创建或追加至 `AGENTS.md`（或用于 Codex 的系统指令文件）：
```markdown
# 知识中枢治理规约 (Brain Vault Invariants)
- 知识库根路径: `~/Documents/Brain_Vault`
- 文件直传模式: 正文必须 100% 物理零篡改，比对 MD5 防止同名覆盖；
- 知识有效性状态: 严格按照【状态/整体有效】【状态/部分有效】【状态/失效归档】【状态/客观事实】客观裁决；
- 资料检索: 优先执行 `python3 <skill-path>/scripts/hybrid_search.py "<query>"` 并向用户提供 Mac 访达直达命令 `open -R "<path>"`;
- 关联编织: 定期调度 `python3 <skill-path>/scripts/weave_links.py`。
```

### 3. 🟣 Claude Code (Anthropic) 接入
在你的工作区根目录下创建或配置 `CLAUDE.md`：
```markdown
## Brain Vault 知识中枢调用指令
当需要检索历史资料、检查知识库健康度或导出交付物时，直接调用：
- 混合语义搜索: `python3 <skill-path>/scripts/hybrid_search.py "<关键词>"`
- 全息健康自愈: `python3 <skill-path>/scripts/vault_doctor.py`
- 商业排版导出: `python3 <skill-path>/scripts/export_note.py "<file.md>" all`
```

### 4. 🪐 Google Antigravity / Gemini CLI 接入
`install.sh` 已自动将本库软链接至 `~/.gemini/config/skills/jm-brain-vault`。
> **直接交互**：在 Antigravity 聊天框中自然对话（如：*“帮我把这份行业调研整理进企业AI库”* 或 *“查一下关于烟酒零售的最新方案”*），AI 自动研判意图并驱动底层工具。

### 5. ⚡ Cursor / Windsurf 接入
在项目根目录下的 `.cursorrules` 或 `.windsurfrules` 中添加：
```markdown
# Brain Vault Rules
知识库位于 `~/Documents/Brain_Vault`，编码与整理文档时遵循客观四态有效性校验，检索资料优先运行 `python3 <skill-path>/scripts/hybrid_search.py "<query>"`。
```

### 6. 💻 独立终端 CLI 运行 (无需 Agent)
日常脱离任何 AI，直接在终端执行命令行工具管理知识库：
```bash
# 1. 秒级混合语义检索（自动同义词展开 + BM25 排序 + Finder 一键高亮）
python3 scripts/hybrid_search.py "零售方案"

# 2. 一体化全息体检与配置自愈
python3 scripts/vault_doctor.py

# 3. 将任意 Markdown 导出为精美 Word (.docx) 和排版 HTML
python3 scripts/export_note.py "~/Documents/Brain_Vault/00_导航总览_Home.md" all
```

---

## ⚙️ 配置文件说明 (.config.toml)

本架构采用 **TOML** 作为配置格式，具备三大核心优势：
- **原生支持注释 (`#`)**：随时随地为项目和客户添加中文备注；
- **原生标准库解析**：Python 3.11+ 原生内置 `tomllib`，零外部依赖，极速读取；
- **隐藏文件规范 (`.config.toml`)**：以 `.` 开头，默认在访达与 Obsidian 文件列表隐藏，清爽干净；已写入 `.gitignore`，杜绝私有数据误提交。

编辑 `.config.toml` 配置示例：
```toml
[vault]
root = "~/Documents/Brain_Vault"   # 你的 Obsidian 仓库本地路径

[user_profile]
owner_name = "你的名字"
brain_title = "商业数字大脑"

[search_synonyms]
# 搜索同义词扩展
"零售" = ["即时零售", "传统门店数字化"]

[entity_auto_links]
# 自动双链实体映射
"商业定位" = "[[02_Enterprise_AI/Business_Strategy/定位方法论.md|商业定位]]"
```

---

## 📄 许可证 (License)

本项目基于 [MIT License](LICENSE) 协议开源，允许自由用于个人与商业数字大脑管理。
