#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
smart_flashback.py
Smart Flashback & Associative Thinking Partner for Brain Vault.
Surfaces latent historical insights and forgotten gold nuggets from persistent SQLite DB.
"""

import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_loader import get_vault_path
from vault_db import get_db, sync_index

vault_path = get_vault_path()
if not os.path.exists(vault_path):
    print(f"⚠️ [smart_flashback] 知识库目录不存在: {vault_path}")
    print("   请在 .config.toml 中配置正确的 [vault].root 路径。")
    sys.exit(0)

query = " ".join(sys.argv[1:]).strip()

if not query:
    print("用法: python3 smart_flashback.py <当前正在思考的业务关键词或主题>")
    sys.exit(0)

# 1. Fast incremental sync
sync_index(vault_path)

# 2. Query persistent SQLite FTS5 database
con = get_db()
cur = con.cursor()

clean_query = re.sub(r'[^\w\u4e00-\u9fa5]', '', query)
if not clean_query:
    clean_query = query

sql = """
SELECT path, filename, content, mtime, bm25(vault_index, 5.0, 10.0, 2.0, 1.0) AS bm25_rank
FROM vault_index
WHERE vault_index MATCH ?
ORDER BY bm25_rank ASC
LIMIT 10;
"""

matches = []
if len(clean_query) >= 3:
    try:
        cur.execute(sql, (f'"{clean_query}"',))
        matches = cur.fetchall()
    except Exception:
        pass

if not matches:
    # Substring LIKE fallback
    sql_like = """
    SELECT file_meta.path AS path, file_meta.filename AS filename, vault_index.content AS content, file_meta.mtime AS mtime
    FROM file_meta JOIN vault_index ON file_meta.path = vault_index.path
    WHERE file_meta.filename LIKE ? OR vault_index.content LIKE ?
    LIMIT 5;
    """
    cur.execute(sql_like, (f"%{clean_query}%", f"%{clean_query}%"))
    matches = cur.fetchall()

con.close()

print("=" * 70)
print(f"💡 Brain_Vault 灵感漫步与时空闪回: 【{query}】")
print("=" * 70)

if not matches:
    print("未在历史笔记中探测到相关的时空暗线。建议继续推进当前思考！")
else:
    print("系统在你的历史沉淀中挖出了以下关联思想火花：\n")
    for idx, r in enumerate(matches[:3], 1):
        p = r["path"]
        fn = r["filename"]
        body = r["content"]
        mtime = float(r["mtime"])
        t_str = time.strftime("%Y年%m月%d日", time.localtime(mtime))
        
        pos = body.find(query)
        if pos != -1:
            start = max(0, pos - 40)
            end = min(len(body), pos + 100)
            snippet = body[start:end].replace("\n", " ").strip()
        else:
            snippet = body[:120].replace("\n", " ").strip()
            
        print(f"[{idx}] 🕰️  闪回时间: {t_str}")
        print(f"    • 历史来源: [[{p}|{fn}]]")
        print(f"    • 历史火花: “...{snippet}... ”")
        print(f"    • 启发价值: 这段历史思考可以为当下的【{query}】提供实战验证与避坑参考。")
        print()

print("=" * 70)
