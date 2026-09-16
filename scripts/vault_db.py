#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vault_db.py
High-Performance Persistent SQLite Engine for Brain Vault.
Features:
  1. Disk-Backed Persistence (.vault_index.db, WAL Mode, survives reboots)
  2. Memory-Mapped I/O (PRAGMA mmap_size, PRAGMA cache_size for in-memory read speeds)
  3. Incremental Timestamp Sync (mtime-based, re-indexes only modified notes)
  4. FTS5 Trigram Full-Text Search (>=3 chars) + Substring LIKE fallback (<3 chars) + BM25 Scoring
"""

import os
import re
import sys
import time
import sqlite3
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_loader import SKILL_ROOT, get_vault_path, get_synonyms

DB_PATH = SKILL_ROOT / ".vault_index.db"
DAY_SECS = 86400


def get_db(timeout: float = 10.0) -> sqlite3.Connection:
    """Connect to the persistent SQLite database with high-performance PRAGMAs."""
    con = sqlite3.connect(str(DB_PATH), timeout=timeout)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    
    # Enable WAL mode for non-blocking concurrency
    cur.execute("PRAGMA journal_mode = WAL;")
    cur.execute("PRAGMA synchronous = NORMAL;")
    
    # Enable memory-mapped I/O (256MB) & RAM cache (64MB)
    cur.execute("PRAGMA mmap_size = 268435456;")
    cur.execute("PRAGMA cache_size = -64000;")
    
    # Initialize Schema if not exists
    cur.execute("""
    CREATE TABLE IF NOT EXISTS file_meta (
        path TEXT PRIMARY KEY,
        filename TEXT,
        mtime REAL,
        title TEXT,
        status TEXT,
        tags TEXT
    );
    """)
    
    cur.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS vault_index USING fts5(
        path UNINDEXED,
        filename,
        tags,
        content,
        status UNINDEXED,
        mtime UNINDEXED,
        tokenize="trigram"
    );
    """)
    con.commit()
    return con


def sync_index(vault_path: Optional[str] = None, force: bool = False) -> Dict[str, Any]:
    """
    Perform lightning-fast incremental synchronization.
    Only re-parses and re-indexes notes whose mtime has changed.
    Prunes deleted notes automatically.
    """
    if vault_path is None:
        vault_path = get_vault_path()

    t0 = time.time()
    con = get_db()
    cur = con.cursor()

    # Load existing database state
    cur.execute("SELECT path, mtime FROM file_meta")
    db_files = {row["path"]: row["mtime"] for row in cur.fetchall()}

    # Scan vault filesystem
    fs_files = {}
    for root, dirs, files in os.walk(vault_path):
        if ".obsidian" in root or "newdao-ide-windows" in root or "jdk" in root:
            continue
        for f in files:
            if f.endswith(".md") and not f.startswith("."):
                full_p = os.path.join(root, f)
                rel_p = os.path.relpath(full_p, vault_path)
                try:
                    fs_files[rel_p] = (os.path.getmtime(full_p), full_p, f)
                except OSError:
                    pass

    added_count = 0
    updated_count = 0
    deleted_count = 0

    # 1. Prune Deleted Files
    deleted_paths = set(db_files.keys()) - set(fs_files.keys())
    if deleted_paths:
        for p in deleted_paths:
            cur.execute("DELETE FROM file_meta WHERE path = ?", (p,))
            cur.execute("DELETE FROM vault_index WHERE path = ?", (p,))
            deleted_count += 1

    # 2. Find Added or Modified Files
    dirty_files = []
    for rel_p, (mtime, full_p, f) in fs_files.items():
        if force or (rel_p not in db_files):
            dirty_files.append((rel_p, mtime, full_p, f, True))
        elif mtime > db_files[rel_p] + 0.001:
            dirty_files.append((rel_p, mtime, full_p, f, False))

    # 3. Process Dirty Files
    for rel_p, mtime, full_p, f, is_new in dirty_files:
        try:
            with open(full_p, "r", encoding="utf-8", errors="ignore") as fp:
                raw_content = fp.read()
        except Exception:
            continue

        title = f[:-3]
        tags = ""
        status = "未知"

        if raw_content.startswith("---"):
            parts = raw_content.split("---", 2)
            if len(parts) >= 3:
                try:
                    meta = yaml.safe_load(parts[1])
                    if isinstance(meta, dict):
                        status = str(meta.get("status", "未知"))
                        tag_list = meta.get("tags", [])
                        if isinstance(tag_list, list):
                            tags = " ".join([str(t) for t in tag_list])
                        elif isinstance(tag_list, str):
                            tags = tag_list
                        if "title" in meta:
                            title = str(meta["title"])
                except Exception:
                    pass

        # Strip codeblocks for search purity
        clean_content = re.sub(r"```.*?```", "", raw_content, flags=re.DOTALL)

        if not is_new:
            cur.execute("DELETE FROM vault_index WHERE path = ?", (rel_p,))
            updated_count += 1
        else:
            added_count += 1

        cur.execute("""
        INSERT OR REPLACE INTO file_meta (path, filename, mtime, title, status, tags)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (rel_p, f, mtime, title, status, tags))

        cur.execute("""
        INSERT INTO vault_index (path, filename, tags, content, status, mtime)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (rel_p, f, tags, clean_content[:15000], status, mtime))

    con.commit()
    elapsed_ms = round((time.time() - t0) * 1000, 2)

    cur.execute("SELECT count(*) as total FROM file_meta")
    total_docs = cur.fetchone()["total"]

    con.close()
    return {
        "added": added_count,
        "updated": updated_count,
        "deleted": deleted_count,
        "total": total_docs,
        "elapsed_ms": elapsed_ms
    }


def search_vault(query: str, synonym_map: Optional[Dict[str, list]] = None, limit: int = 8) -> List[Dict[str, Any]]:
    """
    Execute high-speed FTS5 BM25 search across the persistent database.
    Supports both Trigram (>=3 chars) and LIKE fallback (<3 chars).
    """
    con = get_db()
    cur = con.cursor()

    if synonym_map is None:
        synonym_map = get_synonyms()

    expanded_terms = [query]
    for k, v_list in synonym_map.items():
        if k.lower() in query.lower():
            expanded_terms.extend(v_list)

    # Clean terms
    sanitized_terms = []
    for term in expanded_terms:
        clean = re.sub(r'[^\w\u4e00-\u9fa5]', '', term)
        if clean and clean not in sanitized_terms:
            sanitized_terms.append(clean)

    if not sanitized_terms:
        con.close()
        return []

    trigram_terms = [t for t in sanitized_terms if len(t) >= 3]
    short_terms = [t for t in sanitized_terms if len(t) < 3]

    now = time.time()
    seen_paths = set()
    results = []

    # 1. Trigram FTS5 query for terms with >= 3 chars
    if trigram_terms:
        match_query = " OR ".join([f'"{t}"' for t in trigram_terms])
        sql_fts = """
        SELECT 
            path,
            filename,
            tags,
            status,
            mtime,
            bm25(vault_index, 5.0, 10.0, 2.0, 1.0) AS bm25_rank,
            snippet(vault_index, 3, '【', '】', '...', 25) AS snippet
        FROM vault_index
        WHERE vault_index MATCH ?
        LIMIT 50;
        """
        try:
            cur.execute(sql_fts, (match_query,))
            for r in cur.fetchall():
                path = r["path"]
                seen_paths.add(path)
                mtime = float(r["mtime"])
                status = r["status"]
                bm25_score = float(r["bm25_rank"])
                snippet = r["snippet"]

                age_days = (now - mtime) / DAY_SECS
                recency_bonus = max(0.0, 1.0 - (age_days / 60.0)) * 2.0

                status_weight = 1.0
                if "整体有效" in status:
                    status_weight = 1.8
                elif "部分有效" in status:
                    status_weight = 1.2
                elif "失效归档" in status:
                    status_weight = 0.4
                elif "客观事实" in status:
                    status_weight = 1.5

                composite_score = (-bm25_score) * status_weight + recency_bonus
                results.append({
                    "path": path,
                    "filename": r["filename"],
                    "status": status,
                    "mtime": mtime,
                    "score": composite_score,
                    "snippet": snippet
                })
        except Exception as e:
            pass

    # 2. Substring LIKE query for short terms (< 3 chars) or missing matches
    if short_terms or len(results) < limit:
        target_short = short_terms if short_terms else sanitized_terms
        for term in target_short:
            sql_like = """
            SELECT 
                file_meta.path AS path,
                file_meta.filename AS filename,
                file_meta.status AS status,
                file_meta.mtime AS mtime,
                vault_index.content AS content
            FROM file_meta
            JOIN vault_index ON file_meta.path = vault_index.path
            WHERE file_meta.filename LIKE ? OR vault_index.content LIKE ?
            LIMIT 20;
            """
            pattern = f"%{term}%"
            try:
                cur.execute(sql_like, (pattern, pattern))
                for r in cur.fetchall():
                    path = r["path"]
                    if path in seen_paths:
                        continue
                    seen_paths.add(path)
                    mtime = float(r["mtime"])
                    status = r["status"]
                    content = r["content"]
                    
                    pos = content.find(term)
                    if pos != -1:
                        snippet = content[max(0, pos - 20):min(len(content), pos + 60)].replace("\n", " ").strip()
                    else:
                        snippet = content[:80].replace("\n", " ").strip()

                    age_days = (now - mtime) / DAY_SECS
                    recency_bonus = max(0.0, 1.0 - (age_days / 60.0)) * 2.0
                    title_bonus = 5.0 if term in r["filename"] else 0.0
                    
                    status_weight = 1.0
                    if "整体有效" in status:
                        status_weight = 1.5
                    elif "失效归档" in status:
                        status_weight = 0.4

                    composite_score = (2.0 + title_bonus) * status_weight + recency_bonus
                    results.append({
                        "path": path,
                        "filename": r["filename"],
                        "status": status,
                        "mtime": mtime,
                        "score": composite_score,
                        "snippet": snippet
                    })
            except Exception:
                pass

    con.close()
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]


if __name__ == "__main__":
    print("=" * 70)
    print("💽  Brain Vault SQLite 持久化存储引擎自检")
    print("=" * 70)
    print(f"• 数据库路径: {DB_PATH}")
    stats = sync_index()
    print(f"✅ 增量同步完成 (耗时 {stats['elapsed_ms']} ms):")
    print(f"  - 现有文档总数: {stats['total']} 篇")
    print(f"  - 新增入库: {stats['added']} 篇")
    print(f"  - 增量更新: {stats['updated']} 篇")
    print(f"  - 清理已删: {stats['deleted']} 篇")
    print("=" * 70)
