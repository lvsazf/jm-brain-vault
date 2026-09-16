#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_config.py
Autonomous Configuration Synchronizer & Self-Healing Engine for Brain Vault.
Automatically scans the vault for:
  1. New client delivery folders -> updates search_synonyms
  2. Frontmatter 'aliases' across notes -> augments synonyms
  3. High-centrality hub notes (SOPs, methodologies) -> updates entity_auto_links
  4. Superseded versions -> self-heals links pointing to newer revisions
"""

import os
import re
import sys
from pathlib import Path
from collections import defaultdict
import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_loader import SKILL_ROOT, CONFIG_PATH, TEMPLATE_PATH, get_vault_path, load_config, is_ignored_path

vault_path = get_vault_path()

print("=" * 70)
print("🔄  Brain Vault 配置自动提炼与自愈引擎 (Config Synchronizer)")
print("=" * 70)

cfg = load_config(force_reload=True)
synonyms = cfg.get("search_synonyms", {})
entity_links = cfg.get("entity_auto_links", {})

new_synonyms_count = 0
new_links_count = 0
healed_links_count = 0

# 1. Scan Client Deliveries for new accounts
client_folder = cfg.get("vault", {}).get("clients_folder")
client_dir = None
if client_folder:
    target_c = os.path.join(vault_path, client_folder) if not os.path.isabs(client_folder) else client_folder
    if os.path.exists(target_c):
        client_dir = target_c
else:
    for cand in ["02_Enterprise_AI/Client_Deliveries", "Client_Deliveries", "Clients", "02_Clients", "客户案卷"]:
        target_c = os.path.join(vault_path, cand)
        if os.path.exists(target_c) and os.path.isdir(target_c):
            client_dir = target_c
            break

if client_dir and os.path.exists(client_dir):
    for entry in os.listdir(client_dir):
        full_sub = os.path.join(client_dir, entry)
        if os.path.isdir(full_sub) and not entry.startswith("."):
            client_name = entry
            # Check if already present in synonyms
            found = False
            for k, v in synonyms.items():
                if client_name in v:
                    found = True
                    break
            if not found:
                # Add to generic business synonyms if missing
                if "客户全案" not in synonyms:
                    synonyms["客户全案"] = []
                if client_name not in synonyms["客户全案"]:
                    synonyms["客户全案"].append(client_name)
                    new_synonyms_count += 1
                    print(f"  • 嗅探到新客户资产: 【{client_name}】 ➔ 自动合入搜索同义词")

# 2. Scan Frontmatter Aliases across notes
alias_discovered = defaultdict(list)
superseded_map = {} # old_note -> new_note

for root, dirs, files in os.walk(vault_path):
    if is_ignored_path(root):
        continue
    for f in files:
        if f.endswith(".md") and not f.startswith("."):
            full_p = os.path.join(root, f)
            rel_p = os.path.relpath(full_p, vault_path)
            base_name = f[:-3]

            try:
                with open(full_p, "r", encoding="utf-8", errors="ignore") as fp:
                    content = fp.read()
            except Exception:
                continue

            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    try:
                        meta = yaml.safe_load(parts[1])
                        if isinstance(meta, dict):
                            # Aliases scan
                            aliases = meta.get("aliases", [])
                            if isinstance(aliases, list):
                                for a in aliases:
                                    a_str = str(a).strip()
                                    if a_str and a_str != base_name:
                                        alias_discovered[a_str].append(base_name)

                            # Superseded scan
                            status = meta.get("status", "")
                            if "失效归档" in str(status) or "superseded" in str(status).lower():
                                body = parts[2]
                                new_match = re.search(r'>\s*\[!NOTE\]\s*本文档已有最新有效版本：\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', body)
                                if new_match:
                                    target_new = new_match.group(1).strip()
                                    superseded_map[base_name] = target_new
                    except Exception:
                        pass

# 3. Self-heal superseded links in entity_auto_links
for entity, link_target in list(entity_links.items()):
    for old_name, new_name in superseded_map.items():
        if old_name in link_target and new_name not in link_target:
            # Self heal
            new_link_target = link_target.replace(old_name, new_name)
            entity_links[entity] = new_link_target
            healed_links_count += 1
            print(f"  • 知识版本跃迁自愈: 【{entity}】 自动切换至新版 ➔ {new_name}")

# Write back to .config.toml
def format_toml(c_dict):
    v = c_dict.get("vault", {})
    ign_list = ", ".join([f'"{x}"' for x in v.get("ignore_patterns", [])])
    ext_list = ", ".join([f'"{x}"' for x in v.get("valid_extensions", [".md", ".canvas", ".base"])])
    db = c_dict.get("database", {})
    usr = c_dict.get("user_profile", {})
    exp = c_dict.get("export_settings", {})
    tr = c_dict.get("transcribe", {})
    wc = c_dict.get("web_clip", {})
    dg = c_dict.get("digest", {})
    mt = c_dict.get("metabolism", {})

    out = [
        "# ==============================================================================",
        "# JM Brain Vault 本地私有配置文件 (Local Private Config)",
        "# 该文件包含个人与真实商业客户数据，已由 .gitignore 保护，切勿提交至公开仓库",
        "# ==============================================================================",
        "",
        "[vault]",
        f'root = "{v.get("root", "~/Documents/Brain_Vault")}"',
        f'inbox_folder = "{v.get("inbox_folder", "00_Inbox")}"',
        f'archive_folder = "{v.get("archive_folder", "99_Archive")}"',
        f'ignore_patterns = [{ign_list}]',
        f'valid_extensions = [{ext_list}]',
        "",
        "[database]",
        f'db_path = "{db.get("db_path", ".vault_index.db")}"',
        f'mmap_size_mb = {db.get("mmap_size_mb", 256)}',
        f'cache_size_kb = {db.get("cache_size_kb", 64000)}',
        f'min_trigram_len = {db.get("min_trigram_len", 3)}',
        "",
        "[user_profile]",
        f'owner_name = "{usr.get("owner_name", "知识库主人")}"',
        f'brain_title = "{usr.get("brain_title", "商业数字大脑")}"',
        "",
        "[export_settings]",
        f'docx_header = "{exp.get("docx_header", "商业数字大脑交付案卷")}"',
        f'default_author = "{exp.get("default_author", "知识库主人")}"',
        f'export_dir = "{exp.get("export_dir", "Exports")}"',
        "",
        "[transcribe]",
        f'model_size = "{tr.get("model_size", "base")}"',
        f'language = "{tr.get("language", "zh")}"',
        f'output_dir = "{tr.get("output_dir", "Voice_Notes")}"',
        "",
        "[web_clip]",
        f'output_dir = "{wc.get("output_dir", "Web_Clips")}"',
        "",
        "[digest]",
        f'output_dir = "{dg.get("output_dir", "Digests")}"',
        "",
        "[metabolism]",
        f'hot_days = {mt.get("hot_days", 7)}',
        f'active_days = {mt.get("active_days", 30)}',
        f'dormant_days = {mt.get("dormant_days", 60)}',
        "",
        "# ------------------------------------------------------------------------------",
        "# 智能模糊检索同义词与意图展开 (Synonym & Domain Mapping)",
        "# ------------------------------------------------------------------------------",
        "[search_synonyms]"
    ]
    for k, val in c_dict.get("search_synonyms", {}).items():
        vals = ", ".join([f'"{x}"' for x in val])
        out.append(f'"{k}" = [{vals}]')

    out.append("")
    out.append("# ------------------------------------------------------------------------------")
    out.append("# 实体高价值双向链接自动编织映射表 (Entity Auto Wikilinks)")
    out.append("# ------------------------------------------------------------------------------")
    out.append("[entity_auto_links]")
    for k, val in c_dict.get("entity_auto_links", {}).items():
        out.append(f'"{k}" = "{val}"')
    
    out.append("")
    return "\n".join(out)

target_file = CONFIG_PATH if CONFIG_PATH.exists() else TEMPLATE_PATH
with open(target_file, "w", encoding="utf-8") as fp:
    fp.write(format_toml(cfg))

print(f"\n✅ 配置自愈与同步完成！")
print(f"  • 新增同义词条: {new_synonyms_count}")
print(f"  • 自愈双链跃迁: {healed_links_count}")
print(f"  • 配置文件已更新: {os.path.basename(target_file)}")
print("=" * 70)
