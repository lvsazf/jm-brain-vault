#!/usr/bin/env python3
"""
verify_validity.py
Objective rule-based validity auditor for Brain_Vault Markdown documents.
Validates:
  1. 状态/整体有效 (Fully Valid)
  2. 状态/部分有效 (Partially Valid)
  3. 状态/失效归档 (Superseded)
  4. 状态/客观事实 (Immutable Fact)
"""

import os
import re
import sys
import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_loader import get_vault_path, is_ignored_path, load_config

vault_path = get_vault_path()
if not os.path.exists(vault_path):
    print(f"⚠️ [verify_validity] 知识库目录不存在: {vault_path}")
    print("   请在 .config.toml 中配置正确的 [vault].root 路径。")
    sys.exit(0)

do_fix = "--fix" in sys.argv
cfg = load_config()

default_markers = [
    "【待确认】",
    "【待核验】",
    "【待核验数据】",
    "【旧分类原文】",
    "TODO:",
    "TODO：",
    "待补充",
    "待确定"
]
pending_markers = cfg.get("validity", {}).get("pending_markers", default_markers)

results = {
    "整体有效": [],
    "部分有效": [],
    "失效归档": [],
    "客观事实": [],
    "未标定或旧标签": []
}

mismatches = []
total_md = 0

for root, dirs, files in os.walk(vault_path):
    if is_ignored_path(root):
        continue
    for f in files:
        if f.endswith(".md") and not f.startswith("."):
            total_md += 1
            full_p = os.path.join(root, f)
            rel_p = os.path.relpath(full_p, vault_path)
            
            with open(full_p, "r", encoding="utf-8", errors="ignore") as fp:
                content = fp.read()
            
            # Extract YAML status
            current_status = None
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    try:
                        meta = yaml.safe_load(parts[1])
                        if isinstance(meta, dict):
                            current_status = meta.get("status")
                            if not current_status and "tags" in meta and isinstance(meta["tags"], list):
                                for t in meta["tags"]:
                                    if str(t).startswith("状态/"):
                                        current_status = t
                                        break
                    except Exception:
                        pass
            
            # Objective Rule Assessment
            is_fact = ("Finance_Assets" in rel_p or "Legal" in rel_p or "Contract" in rel_p or "金刚经" in rel_p)
            
            is_superseded = False
            if ("已有最新版本" in content or "已有新版本" in content or "备查归档" in str(current_status) 
                or "/_Archive" in rel_p or "Career_Archive" in rel_p or "Welcome.md" in f or "失效归档" in str(current_status)):
                is_superseded = True
            
            clean_body = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
            clean_body = re.sub(r"`.*?`", "", clean_body)
            clean_lines = [l for l in clean_body.splitlines() if not l.strip().startswith("|") and not l.strip().startswith(">")]
            clean_text = "\n".join(clean_lines)
            has_pending = any(m in clean_text for m in pending_markers)
            
            if is_superseded:
                rule_status = "状态/失效归档"
                reasons = "存在新版本取代提示或处于归档目录"
            elif is_fact:
                rule_status = "状态/客观事实"
                reasons = "属于不可变客观资产/法务财务底座"
            elif has_pending:
                found = [m for m in pending_markers if m in clean_text]
                m_str = ", ".join(found[:2])
                rule_status = "状态/部分有效"
                reasons = f"正文中包含未决标记: {m_str}"
            else:
                rule_status = "状态/整体有效"
                reasons = "全文闭环自洽，无未决标记，与现行规范对齐"
            
            key = rule_status.replace("状态/", "")
            results[key].append((rel_p, reasons))
            
            if current_status != rule_status:
                mismatches.append((rel_p, current_status, rule_status, reasons))
                if do_fix:
                    if content.startswith("---"):
                        parts = content.split("---", 2)
                        yaml_str = parts[1]
                        if "status:" in yaml_str:
                            yaml_str = re.sub(r"status:.*", f"status: {rule_status}", yaml_str)
                        else:
                            yaml_str = f"status: {rule_status}\n" + yaml_str.strip() + "\n"
                        new_content = f"---{yaml_str}---" + parts[2]
                        with open(full_p, "w", encoding="utf-8") as fp:
                            fp.write(new_content)

print("=" * 65)
print("⚖️  Brain_Vault 文档客观知识有效性校验审计报告")
print("=" * 65)
print(f"• 扫描 Markdown 笔记总数:  {total_md} 篇")
print(f"• 状态/整体有效 (现行标准): {len(results['整体有效'])} 篇")
print(f"• 状态/部分有效 (含未决项): {len(results['部分有效'])} 篇")
print(f"• 状态/失效归档 (备查留底): {len(results['失效归档'])} 篇")
print(f"• 状态/客观事实 (永久有效): {len(results['客观事实'])} 篇")
print("=" * 65)

if mismatches:
    print(f"\n🔍 发现 {len(mismatches)} 篇文件的状态需校准为客观有效性状态 (AI 禁打主观【进行中】):")
    for rel_p, curr, rule, reason in mismatches[:8]:
        print(f"  • [{rel_p}]")
        print(f"    旧状态: {curr} ➔ 校准为: {rule}")
        print(f"    校验依据: {reason}")
    if len(mismatches) > 8:
        print(f"  ... 另有 {len(mismatches) - 8} 篇待校准")
else:
    print("\n✅ 全库所有文档的有效性状态均已与客观校验规则 100% 对齐！")

if not do_fix and mismatches:
    print("\n💡 提示: 可运行 `python3 verify_validity.py --fix` 一键校准全库状态。")
print("=" * 65)
