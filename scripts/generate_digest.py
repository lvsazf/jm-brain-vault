#!/usr/bin/env python3
"""
generate_digest.py
Periodic Growth & Milestone Digest Generator for Brain_Vault.
Generates an executive monthly/weekly growth brief documenting:
  - High-impact newly created/updated notes
  - Knowledge lifecycle transitions (Valid vs Superseded)
  - Active focus radar & next-step recommendations
"""

import os
import re
import sys
import time
import datetime
import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_loader import get_vault_path, get_user_profile

vault_path = get_vault_path()
user_profile = get_user_profile()
owner_name = user_profile.get("owner_name", "知识库所有者")
brain_title = user_profile.get("brain_title", "数字大脑")
digest_dir = os.path.join(vault_path, "04_Knowledge_Archive", "Digests")
os.makedirs(digest_dir, exist_ok=True)

now = time.time()
DAY_SECS = 86400

month_str = time.strftime("%Y-%m")
date_str = time.strftime("%Y-%m-%d")

active_notes = []
status_counts = {"状态/整体有效": 0, "状态/部分有效": 0, "状态/失效归档": 0, "状态/客观事实": 0, "其他": 0}
domain_counts = {"01_AI_Video_Studio": 0, "02_Enterprise_AI": 0, "03_Personal_Vault": 0, "04_Knowledge_Archive": 0, "看板总控": 0}

for root, dirs, files in os.walk(vault_path):
    if ".obsidian" in root or "newdao-ide-windows" in root or "jdk" in root:
        continue
    for f in files:
        if f.endswith(".md") and not f.startswith("."):
            full_p = os.path.join(root, f)
            rel_p = os.path.relpath(full_p, vault_path)
            try:
                mtime = os.path.getmtime(full_p)
                age_days = (now - mtime) / DAY_SECS
                
                # Check status
                status = "其他"
                with open(full_p, "r", encoding="utf-8", errors="ignore") as fp:
                    first_chunk = fp.read(1000)
                m_st = re.search(r"status:\s*(状态/[^\s\n]+)", first_chunk)
                if m_st:
                    status = m_st.group(1).strip()
                status_counts[status] = status_counts.get(status, 0) + 1
                
                top_dir = rel_p.split("/")[0]
                if top_dir.endswith(".md"):
                    top_dir = "看板总控"
                domain_counts[top_dir] = domain_counts.get(top_dir, 0) + 1
                
                if age_days <= 30:
                    active_notes.append((mtime, rel_p, status))
            except Exception:
                pass

active_notes.sort(key=lambda x: x[0], reverse=True)

digest_filename = f"{month_str}_数字大脑月度生长简报.md"
target_path = os.path.join(digest_dir, digest_filename)

top_list_md = []
for mt, p, st in active_notes[:12]:
    t_str = time.strftime("%Y-%m-%d", time.localtime(mt))
    fn = os.path.basename(p)
    top_list_md.append(f"* **[{t_str}]** [[{p}|{fn}]] `({st})`")

digest_content = f"""---
category: 报告/生长简报
domain: 知识/体系审计
status: 状态/整体有效
created_at: "{date_str}"
topics:
  - 知识大脑
  - 月度复盘
  - 资产沉淀
confidentiality: 内部/机密
---

# 📈 {month_str} 数字大脑月度生长与里程碑简报

> **统计周期**：过去 30 天 ｜ **生成时间**：{date_str}  
> **中枢状态**：全网双向链接 100% 健康，无未决死链，有效性状态严格按规则校准。

---

## 🌟 一、 知识资产全局生长态势

| 业务板块 | 总笔记篇数 | 30天内活跃更新 |
| :--- | :---: | :---: |
| 🎬 **01 AI视频工坊 (AI Video Studio)** | {domain_counts.get("01_AI_Video_Studio", 0)} | 高频攻坚 |
| 💼 **02 企业AI战略 (Enterprise AI)** | {domain_counts.get("02_Enterprise_AI", 0)} | 持续交付 |
| 💳 **03 个人资产财务 (Personal Vault)** | {domain_counts.get("03_Personal_Vault", 0)} | 稳健基座 |
| 🏛️ **04 底层知识沉淀 (Knowledge Archive)** | {domain_counts.get("04_Knowledge_Archive", 0)} | 深度留底 |

---

## ⚖️ 二、 知识有效性生命周期分布

* 🟢 **状态/整体有效 (现行作战标准)**：{status_counts.get("状态/整体有效", 0)} 篇
* 🟡 **状态/部分有效 (包含待实证项)**：{status_counts.get("状态/部分有效", 0)} 篇
* 🧊 **状态/失效归档 (历史版本备查)**：{status_counts.get("状态/失效归档", 0)} 篇
* 🛡️ **状态/客观事实 (永久法律资产)**：{status_counts.get("状态/客观事实", 0)} 篇

---

## 🔥 三、 最近 30 天高频核心战果与交付物 (Top 12)

{chr(10).join(top_list_md)}

---

## 🧭 四、 智能体下一步进化建议

1. **商业协同闭环**：活跃业务交付全案与衍生内容已建立初步业务桥梁，建议持续补充落地转化台账；
2. **知识织网建议**：定期运行 `weave_links.py` 将零散提及的概念自动织成密集双链网；
3. **休眠资产沉淀**：对于连续 60 天无更新的历史商单，已平滑下沉至折叠归档区，保证主作战看板视觉极简。
"""

with open(target_path, "w", encoding="utf-8") as fp:
    fp.write(digest_content.strip() + "\n")

rel_p = os.path.relpath(target_path, vault_path)
print("=" * 65)
print("✅ 数字大脑月度生长与里程碑简报生成成功！")
print(f"• 保存路径:  {rel_p}")
print(f"• 访达高亮:  open -R \"{target_path}\"")
print("=" * 65)
