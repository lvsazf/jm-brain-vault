#!/usr/bin/env python3
"""
weave_links.py
Autonomous Knowledge Graph Weaver for Brain_Vault.
Identifies unlinked mentions of key entities and safely weaves them into [[wikilinks]].
Supports --preview (default) and --auto (safely injects links).
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_loader import get_vault_path, get_entity_links

vault_path = get_vault_path()
do_auto = "--auto" in sys.argv

# Dictionary of high-value entities and their canonical note link loaded from config
entity_link_map = get_entity_links()

modified_files = 0
total_links_woven = 0

for root, dirs, files in os.walk(vault_path):
    if ".obsidian" in root or "newdao-ide-windows" in root or "jdk" in root:
        continue
    for f in files:
        if f.endswith(".md") and not f.startswith("."):
            full_p = os.path.join(root, f)
            rel_p = os.path.relpath(full_p, vault_path)
            
            with open(full_p, "r", encoding="utf-8", errors="ignore") as fp:
                original_text = fp.read()
            
            # Skip files that are themselves about this entity
            file_modified = False
            lines = original_text.splitlines()
            new_lines = []
            in_yaml = False
            in_code = False
            
            for line_idx, line in enumerate(lines):
                if line_idx == 0 and line.strip() == "---":
                    in_yaml = True
                    new_lines.append(line)
                    continue
                if in_yaml:
                    if line.strip() == "---":
                        in_yaml = False
                    new_lines.append(line)
                    continue
                if line.strip().startswith("```"):
                    in_code = not in_code
                    new_lines.append(line)
                    continue
                if in_code or line.strip().startswith("#") or line.strip().startswith("|"):
                    new_lines.append(line)
                    continue
                
                # Check for unlinked mention on this content line
                modified_line = line
                for ent, canonical_link in entity_link_map.items():
                    if ent in f:
                        continue
                    # Match entity if not already preceded by [[ and not followed by ]]
                    # Simple safe regex: match ent not inside [[ ... ]]
                    pattern = r"(?<!\[\[)(?<!\|)" + re.escape(ent) + r"(?!\]\])"
                    if re.search(pattern, modified_line):
                        if do_auto:
                            # Replace only the first occurrence per line to prevent over-linking
                            modified_line = re.sub(pattern, canonical_link, modified_line, count=1)
                            file_modified = True
                            total_links_woven += 1
                        else:
                            total_links_woven += 1
                new_lines.append(modified_line)
            
            if file_modified and do_auto:
                with open(full_p, "w", encoding="utf-8") as fp:
                    fp.write("\n".join(new_lines) + "\n")
                modified_files += 1

print("=" * 65)
print("🕸️  Brain_Vault 知识图谱智能织网器 (Graph Weaver)")
print("=" * 65)
if do_auto:
    print(f"✅ 自动织网完成！在 {modified_files} 篇笔记中成功编织了 {total_links_woven} 条高价值双向链接！")
else:
    print(f"🔍 预览模式：探测到 {total_links_woven} 处可安全自动织网的孤岛提及。")
    print("💡 提示: 运行 `python3 weave_links.py --auto` 可一键自动完成知识图谱织网。")
print("=" * 65)
