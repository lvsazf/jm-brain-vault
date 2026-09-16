# 智能模糊检索与交付规范 (Search & Discovery Protocol)

## 一、 自然语义命名哲学 (Natural Semantic Naming)

1. **拒绝死板后缀**：
   * 严禁机械地给每个文件添加 `_V1.0_20260916_正式版` 这种冗长难看的死板后缀；
   * 优先使用人话、自然、有明确业务含义的名称（如：《品牌零售30天选题池》、《戒烟口播逐字稿》、《山海经异兽设定》）。
2. **靠 AI 智能上下文识别版本**：
   * 系统与 AI 会穿透修改时间（`mtime`）与正文内容判断版本演进；
   * 仅在同一目录下同时并存多份不同草案时，使用最简短的区分（如 `文案_初稿`、`文案_定稿`）。

---

## 二、 四级智能模糊检索链路 (4-Tier Retrieval Pipeline)

当用户给出零散关键字、模糊想法或记忆描述时，AI 依次启动四级穿透检索：

### 1. 同义词与拼音扩展 (Synonym Mapping)
自动将用户的生活化口语映射为库内的业务标准术语（可在 `config.json` 中灵活定义）：
* 输入 *“烟酒店 / 零售方案”* ➔ 映射至：`即时零售`、`传统门店数字化`、`行业全案`
* 输入 *“老齐”* ➔ 映射至：`Architecture_Tech/Architecture_PPTs` (74套老齐架构方案)
* 输入 *“避坑 / 短剧经验”* ➔ 映射至：`contents.md` (AI短剧爆款密码：我的8条血泪避坑指南)
* 输入 *“koubo / 脚本”* ➔ 拼音穿透至：`口播`、`Koubo_Scripts`

### 2. 全库正文与标签穿透 (Full-Text Penetration)
* 不仅检索文件名，秒级穿透所有 Markdown 笔记的正文、段落、表格、Callout 框及 YAML Frontmatter 标签；
* 穿透伴生索引卡，关联检索 DOCX / PDF / PPTX 资产。

### 3. 语义与概念联想 (Semantic Association)
* 基于对用户当前核心战略的理解，将抽象场景直接转化为具体文件：
  * *“算家庭压力的表”* ➔ 命中：`财务规划-家庭压力测试表.xlsx`
  * *“发给物业的信”* ➔ 命中：`小区物业_行政履职申请书_定稿.md`
  * *“零售工作流提示词”* ➔ 命中：`content-workflow/adapters/doubao-desktop-prompt.md`

### 4. 活跃度加权排序 (Recency Weighting)
* 若命中多个版本（如 `V1.0`、`V1.1`、`V1.2`），系统根据 `mtime` 与 `#状态/进行中` 标签，自动将最新活跃版本置顶呈现，并折叠提示旧版。

---

## 三、 标准交付输出规范 (Finder Reveal Delivery)

检索完成后，严格按以下格式输出，让用户不仅“看得到”，而且“能立刻拿走”：

```markdown
🔍 **为你找到以下文件：**

* 📄 **[文件简明名称]** (最近更新：YYYY-MM-DD)
  * **一句话提要**：[清晰概述该文档的核心内容与作用]
  * **完整路径**：`~/Documents/Brain_Vault/path/to/file.ext`
  * **Mac 访达一键定位**：
    ```bash
    open -R "$HOME/Documents/Brain_Vault/path/to/file.ext"
    ```
    *(复制并在终端运行，或告诉我“帮我在访达打开”，Mac 访达会立刻弹窗高亮选中该文件，直接鼠标拖走即可！)*
```
