#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vault.py
Unified Command-Line Interface for JM Brain Vault.
Provides ergonomic subcommands:
  vault search <query>        - Hybrid semantic search with BM25 & Obsidian URI
  vault doctor                - Full-system health & validity diagnostics
  vault clip <url>            - Strip clutter & clip web articles to Markdown
  vault export <note> [fmt]   - Export note to polished Word (.docx) or HTML
  vault transcribe <audio>    - Offline Whisper voice-to-note pipeline
  vault pulse                 - 30-day dynamic lifecycle pulse & focus radar
  vault weave [--auto]        - Automatically weave unlinked concept mentions
  vault digest                - Generate monthly growth & milestone brief
  vault graph                 - Cognitive gap & cross-domain bridge diagnosis
  vault verify [--fix]        - Objective 4-state validity auditing
  vault sync                  - Autonomous config sync & link self-healing
  vault status                - Display current vault config & index status
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPTS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))
from config_loader import (
    get_vault_path,
    get_vault_name,
    get_user_profile,
    get_db_path,
    get_domains,
    load_config
)


def run_script(script_name: str, args: list = None) -> int:
    """Run a target python script from scripts/ directory."""
    script_p = SCRIPTS_DIR / script_name
    cmd = [sys.executable, str(script_p)]
    if args:
        cmd.extend(args)
    res = subprocess.run(cmd)
    return res.returncode


def cmd_status():
    """Print overall status of the vault environment."""
    v_path = get_vault_path()
    v_name = get_vault_name()
    db_p = get_db_path()
    usr = get_user_profile()
    domains = get_domains()

    print("=" * 65)
    print("🧠  JM Brain Vault - 知识中枢运行状态")
    print("=" * 65)
    print(f"• 知识库名称:  {v_name}")
    print(f"• 根目录路径:  {v_path}")
    print(f"• 目录存在状态: {'✅ 正常就绪' if os.path.exists(v_path) else '❌ 目录不存在 (请检查 .config.toml)'}")
    print(f"• 知识库所有者: {usr.get('owner_name', '知识库主人')}")
    print(f"• SQLite 索引:  {db_p} ({'✅ 已初始化' if db_p.exists() else '⚠️ 未创建'})")
    print(f"• 探测业务板块: {', '.join(domains) if domains else '(未检测到多级业务目录)'}")
    print("=" * 65)
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="vault",
        description="🧠 JM Brain Vault - 统一命令行中枢管家",
        epilog="使用示例: vault search '烟酒零售' | vault doctor | vault clip 'https://...'"
    )
    subparsers = parser.add_subparsers(dest="command", help="支持的子命令")

    # search
    p_search = subparsers.add_parser("search", aliases=["s", "find"], help="混合语义检索 (FTS5 + BM25 + Obsidian直达)")
    p_search.add_argument("query", nargs="+", help="搜索关键词或模糊意图描述")
    p_search.add_argument("--ui", action="store_true", help="生成可交互式 Tailwind Generative UI 卡片")

    # doctor
    p_doctor = subparsers.add_parser("doctor", aliases=["doc", "check"], help="一体化全息体检医生与双链自愈")
    p_doctor.add_argument("--ui", action="store_true", help="生成可视化生命体征健康雷达 UI 部件")

    # ui
    p_ui = subparsers.add_parser("ui", help="生成 Generative UI HTML 交互部件")
    p_ui.add_argument("target", choices=["search", "doctor"], help="UI 目标: search | doctor")
    p_ui.add_argument("args", nargs="*", help="额外参数 (如搜索词)")

    # clip
    p_clip = subparsers.add_parser("clip", aliases=["c"], help="智能网页降噪去广告提纯剪藏")
    p_clip.add_argument("url", help="待剪藏的网页或文章 URL")

    # export
    p_export = subparsers.add_parser("export", aliases=["e"], help="商业级交付排版导出 (Word/HTML)")
    p_export.add_argument("note_path", help="待导出的 Markdown 笔记路径")
    p_export.add_argument("format", nargs="?", default="docx", choices=["docx", "html", "all"], help="目标格式: docx | html | all")

    # transcribe
    p_trans = subparsers.add_parser("transcribe", aliases=["t"], help="Faster-Whisper 本地离线语音高精度听写")
    p_trans.add_argument("audio_path", help="音频文件路径 (.m4a/.mp3/.wav)")
    p_trans.add_argument("model", nargs="?", default="base", choices=["tiny", "base", "small", "medium", "large-v3"], help="模型规格")

    # pulse
    subparsers.add_parser("pulse", aliases=["p"], help="30天动态生命周期活跃热力感知")

    # weave
    p_weave = subparsers.add_parser("weave", aliases=["w"], help="知识图谱孤岛智能双向织网")
    p_weave.add_argument("--auto", action="store_true", help="直接安全合入 [[wikilinks]] 修改文件")

    # digest
    subparsers.add_parser("digest", help="生成月度数字大脑生长与资产简报")

    # graph
    subparsers.add_parser("graph", help="知识图谱拓扑、超级中枢与业务断层诊断")

    # verify
    p_ver = subparsers.add_parser("verify", help="客观知识有效性四态审计")
    p_ver.add_argument("--fix", action="store_true", help="一键将未标定笔记校准为客观状态")

    # sync
    subparsers.add_parser("sync", help="配置自动提炼与版本跃迁双链自愈")

    # status
    subparsers.add_parser("status", help="查看知识库连接与索引配置状态")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    parsed, remaining = parser.parse_known_args()

    cmd = parsed.command
    if cmd in ["search", "s", "find"]:
        if parsed.ui:
            return run_script("render_ui.py", ["search"] + parsed.query)
        return run_script("hybrid_search.py", parsed.query)
    elif cmd in ["doctor", "doc", "check"]:
        if parsed.ui:
            return run_script("render_ui.py", ["doctor"])
        return run_script("vault_doctor.py", remaining)
    elif cmd == "ui":
        return run_script("render_ui.py", [parsed.target] + parsed.args)
    elif cmd in ["clip", "c"]:
        return run_script("clip_url.py", [parsed.url])
    elif cmd in ["export", "e"]:
        return run_script("export_note.py", [parsed.note_path, parsed.format])
    elif cmd in ["transcribe", "t"]:
        return run_script("transcribe_audio.py", [parsed.audio_path, parsed.model])
    elif cmd in ["pulse", "p"]:
        return run_script("scan_pulse.py", remaining)
    elif cmd in ["weave", "w"]:
        args = ["--auto"] if parsed.auto else []
        return run_script("weave_links.py", args + remaining)
    elif cmd == "digest":
        return run_script("generate_digest.py", remaining)
    elif cmd == "graph":
        return run_script("graph_diagnosis.py", remaining)
    elif cmd == "verify":
        args = ["--fix"] if parsed.fix else []
        return run_script("verify_validity.py", args + remaining)
    elif cmd == "sync":
        return run_script("sync_config.py", remaining)
    elif cmd == "status":
        return cmd_status()
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
