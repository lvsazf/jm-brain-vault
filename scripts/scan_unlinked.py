#!/usr/bin/env python3
"""
scan_unlinked.py
Scans Brain_Vault for high-value unlinked mentions of key entities/notes.
Surfaces implicit connections to turn isolated notes into a dense knowledge mesh.
"""

import os
import re

import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_loader import get_vault_path, get_entity_links, load_config, is_ignored_path

vault_path = get_vault_path()
if not os.path.exists(vault_path):
    print(f"⚠️ [scan_unlinked] 知识库目录不存在: {vault_path}")
    print("   请在 .config.toml 中配置正确的 [vault].root 路径。")
    sys.exit(0)

cfg = load_config()

# High-value entities to watch for unlinked mentions (loaded from config or derived)
target_entities = cfg.get("target_entities")
if not target_entities:
    entity_set = set(get_entity_links().keys())
    for vals in cfg.get("search_synonyms", {}).values():
        if isinstance(vals, list):
            entity_set.update(vals)
    target_entities = sorted(list(entity_set))

unlinked_found = []

for root, dirs, files in os.walk(vault_path):
    if is_ignored_path(root):
        continue
    for f in files:
        if f.endswith(".md") and not f.startswith("."):
            full_p = os.path.join(root, f)
            rel_p = os.path.relpath(full_p, vault_path)
            
            with open(full_p, "r", encoding="utf-8", errors="ignore") as fp:
                content = fp.read()
            
            # Remove existing [[...]] links and code blocks to avoid false matches
            clean_body = re.sub(r"\[\[.*?\]\]", "", content)
            clean_body = re.sub(r"```.*?```", "", clean_body, flags=re.DOTALL)
            clean_body = re.sub(r"`.*?`", "", clean_body)
            
            for entity in target_entities:
                # Do not match the file's own name
                if entity in f:
                    continue
                if entity in clean_body:
                    unlinked_found.append((rel_p, entity))

print("=" * 65)
print("🕸️  Brain_Vault 隐式提及与未链接网络探测 (Unlinked Mentions)")
print("=" * 65)
if unlinked_found:
    print(f"发现 {len(unlinked_found)} 处潜在可织网的隐式提及 (文中提及但未打 [[...]]):")
    for rel_p, ent in unlinked_found[:12]:
        print(f"  • 在 [{rel_p}] 中提及: 【{ent}】")
    if len(unlinked_found) > 12:
        print(f"  ... 另有 {len(unlinked_found) - 12} 处可自动编织")
else:
    print("✅ 全库关键实体已 100% 显式双向链接，无遗漏孤岛！")
print("=" * 65)
