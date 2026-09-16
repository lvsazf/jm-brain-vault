#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hybrid_search.py
High-performance Hybrid Search Engine for Brain Vault backed by Persistent SQLite FTS5.
Features:
  - Persistent disk storage (.vault_index.db) with WAL mode & Memory-Mapped I/O
  - Automatic incremental timestamp synchronization (mtime-based)
  - Trigram full-text search with BM25 ranking + business status weighting
  - Mac Finder reveal command generation
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_loader import get_vault_path, get_synonyms
from vault_db import sync_index, search_vault

vault_path = get_vault_path()
query = " ".join(sys.argv[1:]).strip()

if not query:
    print("用法: python3 hybrid_search.py <搜索词或模糊想法>")
    sys.exit(0)

# 1. Background fast incremental sync (< 0.05s if no changes)
sync_stats = sync_index(vault_path)

# 2. Get synonym mappings
synonym_map = get_synonyms()
expanded_terms = [query]
for k, v_list in synonym_map.items():
    if k.lower() in query.lower():
        expanded_terms.extend(v_list)

# 3. Search persistent SQLite FTS5 database
results = search_vault(query, synonym_map=synonym_map, limit=6)

print("=" * 65)
print(f"🔍 Brain_Vault 混合语义检索: 【{query}】 (持久化索引库: {sync_stats['total']} 篇)")
if len(expanded_terms) > 1:
    print(f"💡 自动联想关键词: {', '.join(expanded_terms[1:])}")
print("=" * 65)

if not results:
    print("未找到强相关匹配文档。建议尝试更宽泛的业务词或查看 00_导航总览_Home.md")
else:
    for idx, res in enumerate(results[:5], 1):
        fn = res["filename"]
        p = res["path"]
        st = res["status"]
        mt_str = time.strftime("%Y-%m-%d", time.localtime(res["mtime"]))
        abs_p = os.path.join(vault_path, p)
        snippet = res.get("snippet", "").replace("\n", " ").strip()
        
        print(f"[{idx}] 📄 {fn}")
        print(f"    • 路径:  {p}")
        print(f"    • 状态:  {st} | 更新: {mt_str}")
        print(f"    • 摘要:  ...{snippet}...")
        print(f"    • 访达:  open -R \"{abs_p}\"")
        print()

print("=" * 65)
