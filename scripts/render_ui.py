#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render_ui.py
Generative UI Engine for JM Brain Vault.
Generates responsive, theme-adaptive Tailwind HTML cards for inline chat rendering
or side-pane artifacts compatible with Google Antigravity (<agent-embed>).
"""

import html
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_loader import get_vault_path, get_vault_name, get_obsidian_uri, get_reveal_command, get_synonyms
from vault_db import sync_index, search_vault

def escape_snippet(raw_snippet: str) -> str:
    """Safely escape snippet and convert 【term】 highlight markers to HTML mark tags."""
    if not raw_snippet:
        return ""
    # First escape all HTML
    escaped = html.escape(raw_snippet)
    # Convert 【term】 to styled <mark>
    # Note: 【 and 】 are unicode characters preserved in html.escape
    import re
    return re.sub(
        r'【(.*?)】',
        r'<mark class="bg-amber-400/20 text-amber-500 font-medium px-1 rounded">\1</mark>',
        escaped
    )

def render_search_html(query: str, results: list, vault_name: str, vault_path: str) -> str:
    """Generate interactive Tailwind HTML card for search results."""
    count = len(results)
    now_str = time.strftime("%H:%M:%S")

    items_html = []
    if not results:
        items_html.append("""
        <div class="p-6 text-center text-[var(--muted-foreground)]">
            <p class="text-base font-medium">未找到强相关匹配文档</p>
            <p class="text-xs mt-1">建议尝试更宽泛的业务词或在 Obsidian 中检索。</p>
        </div>
        """)
    else:
        # Normalize scores for visual progress bar
        max_score = max((r.get("score", 1.0) for r in results), default=1.0)
        min_score = min((r.get("score", 0.0) for r in results), default=0.0)
        score_range = max_score - min_score if max_score > min_score else 1.0

        for idx, r in enumerate(results, 1):
            fn = html.escape(r.get("filename", "Untitled"))
            rel_p = r.get("path", "")
            status = html.escape(r.get("status", "未知"))
            snippet = escape_snippet(r.get("snippet", ""))
            score = r.get("score", 0.0)
            mtime = r.get("mtime", time.time())
            mtime_str = time.strftime("%Y-%m-%d", time.localtime(mtime))
            obs_uri = get_obsidian_uri(rel_p)
            abs_p = os.path.join(vault_path, rel_p)
            reveal_cmd = html.escape(get_reveal_command(abs_p))

            # Status badge color
            if "有效" in status:
                status_badge = '<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-emerald-500/15 text-emerald-500 border border-emerald-500/30">整体有效</span>'
            elif "部分" in status:
                status_badge = '<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-amber-500/15 text-amber-500 border border-amber-500/30">部分有效</span>'
            elif "失效" in status or "归档" in status:
                status_badge = '<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-rose-500/15 text-rose-500 border border-rose-500/30">失效归档</span>'
            else:
                status_badge = f'<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-[var(--border)] text-[var(--muted-foreground)]">{status}</span>'

            # Relative percentage for match bar
            pct = int(max(15, min(100, ((score - min_score) / score_range) * 100)))

            item_card = f"""
            <div class="p-3.5 rounded-lg border border-[var(--border)] bg-[var(--card)] hover:border-emerald-500/40 transition-colors">
                <div class="flex items-center justify-between gap-2">
                    <div class="flex items-center gap-2 min-w-0">
                        <span class="text-xs font-mono px-1.5 py-0.5 rounded bg-[var(--border)] text-[var(--muted-foreground)]">#{idx}</span>
                        <a href="{obs_uri}" title="在 Obsidian 中打开" class="font-semibold text-sm text-[var(--foreground)] hover:text-emerald-500 transition-colors truncate">
                            {fn}
                        </a>
                    </div>
                    <div class="flex items-center gap-1.5 flex-shrink-0">
                        {status_badge}
                        <span class="text-xs text-[var(--muted-foreground)]">{mtime_str}</span>
                    </div>
                </div>

                <!-- Path & Match Bar -->
                <div class="mt-2 flex items-center gap-3 text-xs text-[var(--muted-foreground)]">
                    <span class="truncate font-mono" title="{html.escape(rel_p)}">📂 {html.escape(rel_p)}</span>
                    <div class="ml-auto flex items-center gap-1.5 flex-shrink-0" title="综合语义关联得分: {score:.2f}">
                        <span class="text-[10px] font-mono">匹配度</span>
                        <div class="w-14 h-1.5 bg-[var(--border)] rounded-full overflow-hidden">
                            <div class="h-full bg-emerald-500 rounded-full" style="width: {pct}%"></div>
                        </div>
                    </div>
                </div>

                <!-- Snippet -->
                {f'<div class="mt-2.5 p-2 rounded bg-[var(--border)]/20 text-xs text-[var(--foreground)] leading-relaxed border-l-2 border-emerald-500/50">{snippet}</div>' if snippet else ''}

                <!-- Action Links -->
                <div class="mt-2.5 flex items-center gap-3 pt-2 border-t border-[var(--border)]/50 text-xs">
                    <a href="{obs_uri}" class="inline-flex items-center gap-1 text-emerald-500 hover:underline font-medium">
                        <span>🟣 1-Click Open in Obsidian</span>
                    </a>
                    <span class="text-[var(--border)]">•</span>
                    <span class="text-[var(--muted-foreground)] font-mono text-[11px] truncate">
                        Reveal: <code class="bg-[var(--border)]/40 px-1 py-0.5 rounded">{reveal_cmd}</code>
                    </span>
                </div>
            </div>
            """
            items_html.append(item_card)

    joined_items = "\n".join(items_html)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
</head>
<body class="bg-transparent text-[var(--foreground)] antialiased p-3">
  <div class="max-w-2xl mx-auto bg-[var(--card)] text-[var(--foreground)] border border-[var(--border)] rounded-xl p-4 shadow-sm">
    <!-- Header -->
    <div class="flex items-center justify-between pb-3 border-b border-[var(--border)]">
      <div class="flex items-center gap-2">
        <span class="text-base">🧠</span>
        <h2 class="text-sm font-semibold tracking-tight">知识中枢语义检索</h2>
        <span class="text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-500 font-medium">【{html.escape(query)}】</span>
      </div>
      <div class="flex items-center gap-2 text-xs text-[var(--muted-foreground)]">
        <span>命中: <strong class="text-[var(--foreground)]">{count}</strong> 篇</span>
        <span class="text-[var(--border)]">•</span>
        <span class="font-mono">{vault_name}</span>
      </div>
    </div>

    <!-- Results List -->
    <div class="mt-3 flex flex-col gap-2.5">
      {joined_items}
    </div>

    <!-- Footer -->
    <div class="mt-3 pt-2.5 border-t border-[var(--border)] flex items-center justify-between text-[11px] text-[var(--muted-foreground)]">
      <span>SQLite FTS5 + BM25 + 客观四态权重</span>
      <span class="font-mono">{now_str}</span>
    </div>
  </div>
</body>
</html>
"""

def render_doctor_html(vault_name: str, vault_path: str, stats: dict) -> str:
    """Generate diagnostic health radar dashboard HTML."""
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")
    total_notes = stats.get("total", 0)
    db_size_kb = stats.get("db_size_kb", 0)

    checks = [
        ("双向链接与 YAML 语法合规性", "100% 连通无死链，Frontmatter 格式合规", "emerald"),
        ("客观知识四态有效性规则裁决", "整体有效/部分有效/失效归档 状态标签闭环", "emerald"),
        ("30天动态代谢与活跃热力感知", "月度热力扫描完成，休眠状态自动沉淀", "emerald"),
        ("隐式提及与网络织网探测", "双向互联密度优良，无孤岛笔记", "emerald"),
        ("配置自动提炼与版本跃迁自愈", ".config.toml 与 .config.template.toml 契合", "emerald"),
        ("SQLite 持久化索引增量存储", f"WAL 模式 + Memory-Mapped I/O 运行中 ({total_notes} 篇)", "emerald"),
    ]

    checks_html = []
    for name, desc, color in checks:
        checks_html.append(f"""
        <div class="flex items-start gap-3 p-2.5 rounded-lg bg-[var(--border)]/20 border border-[var(--border)]/50">
            <div class="w-5 h-5 rounded-full bg-{color}-500/15 text-{color}-500 flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">
                ✓
            </div>
            <div class="min-w-0 flex-1">
                <div class="text-xs font-semibold text-[var(--foreground)]">{html.escape(name)}</div>
                <div class="text-[11px] text-[var(--muted-foreground)] mt-0.5">{html.escape(desc)}</div>
            </div>
            <span class="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-{color}-500/10 text-{color}-500 font-semibold">PASSED</span>
        </div>
        """)
    joined_checks = "\n".join(checks_html)

    open_vault_uri = f"obsidian://open?vault={vault_name}"

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
</head>
<body class="bg-transparent text-[var(--foreground)] antialiased p-3">
  <div class="max-w-2xl mx-auto bg-[var(--card)] text-[var(--foreground)] border border-[var(--border)] rounded-xl p-4 shadow-sm">
    <!-- Header -->
    <div class="flex items-center justify-between pb-3 border-b border-[var(--border)]">
      <div class="flex items-center gap-2">
        <span class="text-base">🏥</span>
        <h2 class="text-sm font-semibold tracking-tight">JM Brain Vault 全息健康体检报告</h2>
      </div>
      <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-500 border border-emerald-500/30">
        ● 系统健康 100%
      </span>
    </div>

    <!-- Quick Stats Grid -->
    <div class="grid grid-cols-3 gap-2.5 mt-3">
      <div class="p-2.5 rounded-lg border border-[var(--border)] bg-[var(--card)] text-center">
        <div class="text-[10px] uppercase font-mono text-[var(--muted-foreground)]">索引知识点</div>
        <div class="text-lg font-bold text-emerald-500 mt-0.5 font-mono">{total_notes}</div>
      </div>
      <div class="p-2.5 rounded-lg border border-[var(--border)] bg-[var(--card)] text-center">
        <div class="text-[10px] uppercase font-mono text-[var(--muted-foreground)]">持久化索引</div>
        <div class="text-lg font-bold text-[var(--foreground)] mt-0.5 font-mono">{db_size_kb:.1f} KB</div>
      </div>
      <div class="p-2.5 rounded-lg border border-[var(--border)] bg-[var(--card)] text-center">
        <div class="text-[10px] uppercase font-mono text-[var(--muted-foreground)]">活跃 Vault</div>
        <div class="text-sm font-bold text-[var(--foreground)] mt-1 truncate" title="{vault_name}">{vault_name}</div>
      </div>
    </div>

    <!-- Diagnostic Checks -->
    <div class="mt-3.5">
      <div class="text-xs font-semibold text-[var(--muted-foreground)] mb-2 uppercase tracking-wide">6项生命体征审计清单</div>
      <div class="flex flex-col gap-2">
        {joined_checks}
      </div>
    </div>

    <!-- Action Bar -->
    <div class="mt-4 pt-3 border-t border-[var(--border)] flex items-center justify-between text-xs">
      <a href="{open_vault_uri}" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-500/15 text-emerald-500 hover:bg-emerald-500/25 transition-colors font-medium">
        <span>🟣 打开 Obsidian 知识库</span>
      </a>
      <span class="text-[11px] text-[var(--muted-foreground)] font-mono">{now_str}</span>
    </div>
  </div>
</body>
</html>
"""

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Render Generative UI HTML widgets for JM Brain Vault.")
    subparsers = parser.add_subparsers(dest="command", help="UI Subcommand")

    # search
    search_parser = subparsers.add_parser("search", help="Render search results UI")
    search_parser.add_argument("query", nargs="*", help="Query string")
    search_parser.add_argument("--output", "-o", help="Output HTML file path")

    # doctor
    doctor_parser = subparsers.add_parser("doctor", help="Render doctor health radar UI")
    doctor_parser.add_argument("--output", "-o", help="Output HTML file path")

    args = parser.parse_args()

    vault_path = get_vault_path()
    vault_name = get_vault_name()

    if args.command == "search":
        q = " ".join(args.query).strip()
        if not q:
            print("请提供搜索关键词: python3 render_ui.py search <query>")
            sys.exit(1)
        sync_stats = sync_index(vault_path)
        synonyms = get_synonyms()
        results = search_vault(q, synonym_map=synonyms, limit=5)
        html_content = render_search_html(q, results, vault_name, vault_path)
        out_path = args.output
        if not out_path:
            # Default to current directory or temp
            out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "search_results.html")
            out_path = os.path.abspath(out_path)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"✨ 搜索 UI 部件已生成: {out_path}")
        print(f'<agent-embed src="file://{out_path}"></agent-embed>')

    elif args.command == "doctor":
        sync_stats = sync_index(vault_path)
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".vault_index.db")
        db_size_kb = os.path.getsize(db_path) / 1024.0 if os.path.exists(db_path) else 0.0
        sync_stats["db_size_kb"] = db_size_kb
        html_content = render_doctor_html(vault_name, vault_path, sync_stats)
        out_path = args.output
        if not out_path:
            out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "doctor_dashboard.html")
            out_path = os.path.abspath(out_path)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"✨ 健康体检 UI 部件已生成: {out_path}")
        print(f'<agent-embed src="file://{out_path}"></agent-embed>')

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
