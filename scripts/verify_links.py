#!/usr/bin/env python3
import os
import re
import yaml

import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_loader import get_vault_path, is_ignored_path

vault_path = get_vault_path()
if not os.path.exists(vault_path):
    print(f"⚠️ [verify_links] 知识库目录不存在: {vault_path}")
    print("   请在 .config.toml 中配置正确的 [vault].root 路径。")
    sys.exit(0)

all_files = set()
for root, dirs, files in os.walk(vault_path):
    if is_ignored_path(root):
        continue
    for f in files:
        all_files.add(f)
        all_files.add(os.path.relpath(os.path.join(root, f), vault_path))
    for d in dirs:
        all_files.add(d)
        all_files.add(os.path.relpath(os.path.join(root, d), vault_path))

link_regex = re.compile(r'\[\[(.*?)\]\]')
broken_links = []
yaml_errors = []
total_md = 0
total_links = 0

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
            
            # YAML check
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    try:
                        yaml.safe_load(parts[1])
                    except Exception as e:
                        yaml_errors.append((rel_p, str(e)))

            # Link check - ignore links inside code blocks
            clean_content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
            clean_content = re.sub(r'`.*?`', '', clean_content)
            links = link_regex.findall(clean_content)
            total_links += len(links)
            for link in links:
                target = link.split("|")[0].split("#")[0].strip()
                if not target or target.startswith("^") or "\\" in target:
                    continue
                found = (target in all_files) or os.path.exists(os.path.join(vault_path, target))
                if not found:
                    broken_links.append((rel_p, link))

print("=" * 60)
print(f"🔍 Brain_Vault 知识库双向链接与健康度体检")
print("=" * 60)
print(f"• 扫描 Markdown 笔记总数: {total_md} 篇")
print(f"• 检测双向链接总数:       {total_links} 条")
print(f"• YAML 格式异常数量:      {len(yaml_errors)} 篇")
print(f"• 断链 / 死链数量:        {len(broken_links)} 处")

if yaml_errors:
    print("\n⚠️ YAML 格式异常笔记:")
    for p, err in yaml_errors[:5]:
        print(f"  • {p}: {err}")

if broken_links:
    print("\n❌ 发现断链 / 死链:")
    for p, l in broken_links[:10]:
        print(f"  • 在 [{p}] 中: [[{l}]] (目标不存在)")
else:
    print("\n✅ 全库双向链接 100% 有效，零断链、零死链！")

print("=" * 60)
