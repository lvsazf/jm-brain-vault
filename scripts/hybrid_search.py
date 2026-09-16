#!/usr/bin/env python3
"""
hybrid_search.py
High-performance Hybrid Search Engine for Brain_Vault.
Combines SQLite Trigram FTS5 full-text search, BM25 scoring,
YAML tag matching, recency weighting, and validity ranking.
Outputs actionable results with Mac Finder reveal commands.
"""

import os
import re
import sys
import time
import sqlite3
import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_loader import get_vault_path, get_synonyms

vault_path = get_vault_path()
query = " ".join(sys.argv[1:]).strip()

if not query:
    print("用法: python3 hybrid_search.py <搜索词或模糊想法>")
    sys.exit(0)

# Synonym and domain expansion map loaded from config
synonym_map = get_synonyms()

expanded_terms = [query]
for k, v_list in synonym_map.items():
    if k.lower() in query.lower():
        expanded_terms.extend(v_list)

now = time.time()
DAY_SECS = 86400

# Setup In-Memory SQLite FTS5 database with Trigram tokenizer
con = sqlite3.connect(":memory:")
cur = con.cursor()
cur.execute('''
CREATE VIRTUAL TABLE vault_index USING fts5(
    path UNINDEXED,
    filename,
    tags,
    content,
    status UNINDEXED,
    mtime UNINDEXED,
    tokenize="trigram"
);
''')

files_indexed = 0
for root, dirs, files in os.walk(vault_path):
    if ".obsidian" in root or "newdao-ide-windows" in root or "jdk" in root:
        continue
    for f in files:
        if f.endswith(".md") and not f.startswith("."):
            full_p = os.path.join(root, f)
            rel_p = os.path.relpath(full_p, vault_path)
            try:
                mtime = os.path.getmtime(full_p)
                with open(full_p, "r", encoding="utf-8", errors="ignore") as fp:
                    raw = fp.read()
                
                tags = ""
                status = "未知"
                if raw.startswith("---"):
                    parts = raw.split("---", 2)
                    if len(parts) >= 3:
                        try:
                            meta = yaml.safe_load(parts[1])
                            if isinstance(meta, dict):
                                status = meta.get("status", "未知")
                                t_val = meta.get("tags", [])
                                if isinstance(t_val, list):
                                    tags = " ".join([str(x) for x in t_val])
                        except Exception:
                            pass
                
                clean_content = re.sub(r"```.*?```", "", raw, flags=re.DOTALL)
                cur.execute("INSERT INTO vault_index VALUES (?, ?, ?, ?, ?, ?)",
                            (rel_p, f, tags, clean_content[:15000], str(status), mtime))
                files_indexed += 1
            except Exception:
                pass

scored_candidates = {}

for term in expanded_terms:
    # Clean term for SQLite query
    safe_term = term.replace('"', "").replace("'", "").strip()
    if not safe_term:
        continue
    
    sql = """
    SELECT path, filename, tags, content, status, mtime, bm25(vault_index, 10.0, 5.0, 1.0) as rank
    FROM vault_index
    WHERE vault_index MATCH ?
    LIMIT 30
    """
    try:
        cur.execute(sql, (safe_term,))
        rows = cur.fetchall()
        for r in rows:
            p, fn, tags, body, status, mt, rank = r
            if p not in scored_candidates:
                scored_candidates[p] = {
                    "path": p,
                    "filename": fn,
                    "tags": tags,
                    "body": body,
                    "status": status,
                    "mtime": mt,
                    "score": rank  # Lower BM25 is better in sqlite
                }
    except Exception:
        pass

# Fallback substring search if FTS returned nothing
if not scored_candidates:
    cur.execute("SELECT path, filename, tags, content, status, mtime, 0.0 FROM vault_index")
    for r in cur.fetchall():
        p, fn, tags, body, status, mt, _ = r
        if any(term in fn or term in body or term in tags for term in expanded_terms):
            scored_candidates[p] = {
                "path": p,
                "filename": fn,
                "tags": tags,
                "body": body,
                "status": status,
                "mtime": mt,
                "score": -1.0
            }

final_results = []
for p, item in scored_candidates.items():
    # Adjust score with business weighting
    score = item["score"]
    
    # Priority for title matches
    if any(term in item["filename"] for term in expanded_terms):
        score -= 20.0
    
    # Priority for active/valid files
    if "整体有效" in str(item["status"]):
        score -= 5.0
    elif "失效归档" in str(item["status"]):
        score += 15.0
        
    # Recency weight
    age_days = (now - item["mtime"]) / DAY_SECS
    if age_days <= 7:
        score -= 3.0
    elif age_days <= 30:
        score -= 1.0
        
    item["final_score"] = score
    final_results.append(item)

final_results.sort(key=lambda x: x["final_score"])

print("=" * 65)
print(f"🔍 Brain_Vault 混合语义检索: 【{query}】 (索引库: {files_indexed} 篇)")
if len(expanded_terms) > 1:
    print(f"💡 自动联想关键词: {', '.join(expanded_terms[1:])}")
print("=" * 65)

if not final_results:
    print("未找到强相关匹配文档。建议尝试更宽泛的业务词或查看 00_导航总览_Home.md")
else:
    for idx, res in enumerate(final_results[:5], 1):
        fn = res["filename"]
        p = res["path"]
        st = res["status"]
        mt_str = time.strftime("%Y-%m-%d", time.localtime(res["mtime"]))
        abs_p = os.path.join(vault_path, p)
        
        # Extract meaningful snippet
        snippet = ""
        for term in expanded_terms:
            pos = res["body"].find(term)
            if pos != -1:
                start = max(0, pos - 30)
                end = min(len(res["body"]), pos + 80)
                snippet = res["body"][start:end].replace("\n", " ").strip()
                break
        if not snippet:
            snippet = res["body"][:90].replace("\n", " ").strip()
            
        print(f"[{idx}] 📄 {fn}")
        print(f"    • 路径:  {p}")
        print(f"    • 状态:  {st} | 更新: {mt_str}")
        print(f"    • 摘要:  ...{snippet}...")
        print(f"    • 访达:  open -R \"{abs_p}\"")
        print()

print("=" * 65)
