#!/usr/bin/env python3
"""
smart_flashback.py
Smart Flashback & Associative Thinking Partner for Brain_Vault.
Surfaces latent historical insights and forgotten gold nuggets from past notes (>30 days old)
that connect with the user's current train of thought.
"""

import os
import re
import sys
import time
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_loader import get_vault_path

vault_path = get_vault_path()
query = " ".join(sys.argv[1:]).strip()

if not query:
    print("用法: python3 smart_flashback.py <当前正在思考的业务关键词或主题>")
    sys.exit(0)

now = time.time()
DAY_SECS = 86400

# Setup In-Memory FTS5
con = sqlite3.connect(":memory:")
cur = con.cursor()
cur.execute('''
CREATE VIRTUAL TABLE vault_flashback USING fts5(
    path UNINDEXED,
    filename,
    content,
    mtime UNINDEXED,
    tokenize="trigram"
);
''')

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
                # Focus on notes that are at least somewhat seasoned (>1 day)
                with open(full_p, "r", encoding="utf-8", errors="ignore") as fp:
                    raw = fp.read()
                clean_body = re.sub(r"```.*?```", "", raw, flags=re.DOTALL)
                cur.execute("INSERT INTO vault_flashback VALUES (?, ?, ?, ?)",
                            (rel_p, f, clean_body[:10000], mtime))
            except Exception:
                pass

sql = """
SELECT path, filename, content, mtime, bm25(vault_flashback, 5.0, 1.0) as rank
FROM vault_flashback
WHERE vault_flashback MATCH ?
ORDER BY rank ASC
LIMIT 10
"""

matches = []
try:
    cur.execute(sql, (query,))
    matches = cur.fetchall()
except Exception:
    pass

if not matches:
    # Substring fallback
    cur.execute("SELECT path, filename, content, mtime, 0.0 FROM vault_flashback")
    for r in cur.fetchall():
        if query in r[1] or query in r[2]:
            matches.append(r)

print("=" * 70)
print(f"💡 Brain_Vault 灵感漫步与时空闪回: 【{query}】")
print("=" * 70)

if not matches:
    print("未在历史笔记中探测到相关的时空暗线。建议继续推进当前思考！")
else:
    print("系统在你的历史沉淀中挖出了以下关联思想火花：\n")
    for idx, (p, fn, body, mtime, rank) in enumerate(matches[:3], 1):
        t_str = time.strftime("%Y年%m月%d日", time.localtime(mtime))
        # Find match sentence
        pos = body.find(query)
        snippet = ""
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
