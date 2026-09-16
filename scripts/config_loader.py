#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Configuration Loader for Brain Vault.
Loads user-specific configurations from .config.toml (or .config.template.toml as fallback)
located at the skill root directory.
"""

import os
from pathlib import Path
from typing import Any, Dict

try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib
    except ModuleNotFoundError:
        tomllib = None

# Skill root directory (one level up from scripts/)
SKILL_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = SKILL_ROOT / ".config.toml"
TEMPLATE_PATH = SKILL_ROOT / ".config.template.toml"

_cached_config: Dict[str, Any] = None


def load_config(force_reload: bool = False) -> Dict[str, Any]:
    """Load configuration from .config.toml, falling back to .config.template.toml."""
    global _cached_config
    if _cached_config is not None and not force_reload:
        return _cached_config

    cfg = {}
    if tomllib is not None:
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, "rb") as f:
                    cfg = tomllib.load(f)
            except Exception as e:
                print(f"⚠️ [config_loader] 无法解析 {CONFIG_PATH}: {e}，尝试读取模板...")

        if not cfg and TEMPLATE_PATH.exists():
            try:
                with open(TEMPLATE_PATH, "rb") as f:
                    cfg = tomllib.load(f)
            except Exception as e:
                print(f"⚠️ [config_loader] 无法解析 {TEMPLATE_PATH}: {e}")
    else:
        print("⚠️ [config_loader] 当前 Python 环境未找到 tomllib 或 tomli，将使用兜底默认值。")

    # Full standard defaults configurable inside skill
    defaults = {
        "vault": {
            "root": "~/Documents/Brain_Vault",
            "inbox_folder": "00_Inbox",
            "archive_folder": "99_Archive",
            "ignore_patterns": [
                ".obsidian",
                ".trash",
                ".git",
                "node_modules",
                "__pycache__"
            ],
            "valid_extensions": [".md", ".canvas", ".base"]
        },
        "database": {
            "db_path": ".vault_index.db",
            "mmap_size_mb": 256,
            "cache_size_kb": 64000,
            "min_trigram_len": 3
        },
        "user_profile": {
            "owner_name": "知识库主人",
            "brain_title": "商业数字大脑"
        },
        "export_settings": {
            "docx_header": "商业数字大脑交付案卷",
            "default_author": "知识库主人",
            "export_dir": "Exports"
        },
        "transcribe": {
            "model_size": "base",
            "language": "zh",
            "output_dir": "Voice_Notes",
            "default_domain": "资产/录音速记"
        },
        "web_clip": {
            "output_dir": "Web_Clips"
        },
        "digest": {
            "output_dir": "Digests"
        },
        "metabolism": {
            "hot_days": 7,
            "active_days": 30,
            "dormant_days": 60
        },
        "search_synonyms": {},
        "entity_auto_links": {}
    }

    # Deep merge defaults
    for k, v in defaults.items():
        if k not in cfg:
            cfg[k] = v
        elif isinstance(v, dict):
            for sub_k, sub_v in v.items():
                if sub_k not in cfg[k]:
                    cfg[k][sub_k] = sub_v

    _cached_config = cfg
    return _cached_config


def get_vault_path() -> str:
    """Return the expanded absolute path to the Obsidian Vault root."""
    cfg = load_config()
    raw_root = cfg.get("vault", {}).get("root", "~/Documents/Brain_Vault")
    return os.path.expanduser(raw_root)


def get_ignored_patterns() -> list:
    """Return list of directory or path patterns to ignore during scan."""
    cfg = load_config()
    return cfg.get("vault", {}).get("ignore_patterns", [".obsidian", ".trash", ".git", "node_modules"])


def is_ignored_path(path: str) -> bool:
    """Check whether a path or directory should be ignored."""
    patterns = get_ignored_patterns()
    norm_path = path.replace("\\", "/")
    for pattern in patterns:
        if pattern in norm_path:
            return True
    return False


def get_db_path() -> Path:
    """Return the absolute Path to the persistent SQLite database file."""
    cfg = load_config()
    raw_path = cfg.get("database", {}).get("db_path", ".vault_index.db")
    p = Path(raw_path)
    if not p.is_absolute():
        p = SKILL_ROOT / p
    return p


def get_database_settings() -> Dict[str, Any]:
    """Return database configuration settings."""
    cfg = load_config()
    return cfg.get("database", {})


def get_synonyms() -> Dict[str, list]:
    """Return search synonym expansion dictionary."""
    cfg = load_config()
    return cfg.get("search_synonyms", {})


def get_entity_links() -> Dict[str, str]:
    """Return entity auto-link mapping dictionary."""
    cfg = load_config()
    return cfg.get("entity_auto_links", {})


def get_export_settings() -> Dict[str, str]:
    """Return export configuration settings."""
    cfg = load_config()
    return cfg.get("export_settings", {})


def get_user_profile() -> Dict[str, str]:
    """Return user profile settings."""
    cfg = load_config()
    return cfg.get("user_profile", {})


def get_transcribe_settings() -> Dict[str, Any]:
    """Return audio transcription settings."""
    cfg = load_config()
    return cfg.get("transcribe", {})


def get_web_clip_settings() -> Dict[str, Any]:
    """Return web clipper settings."""
    cfg = load_config()
    return cfg.get("web_clip", {})


def get_digest_settings() -> Dict[str, Any]:
    """Return digest settings."""
    cfg = load_config()
    return cfg.get("digest", {})


def get_metabolism_settings() -> Dict[str, Any]:
    """Return metabolism thresholds (hot, active, dormant days)."""
    cfg = load_config()
    return cfg.get("metabolism", {})


def get_domains() -> list:
    """Return a list of top-level business domain directory names in the vault."""
    vault_p = get_vault_path()
    if not os.path.exists(vault_p):
        return []
    cfg = load_config()
    inbox = cfg.get("vault", {}).get("inbox_folder", "00_Inbox")
    archive = cfg.get("vault", {}).get("archive_folder", "99_Archive")
    system_excludes = {inbox, archive}
    domains = []
    try:
        for entry in sorted(os.listdir(vault_p)):
            full_sub = os.path.join(vault_p, entry)
            if os.path.isdir(full_sub) and not entry.startswith("."):
                if not is_ignored_path(entry) and entry not in system_excludes:
                    domains.append(entry)
    except Exception:
        pass
    return domains


if __name__ == "__main__":
    c = load_config(force_reload=True)
    print("✅ 成功从 .config.toml 加载全部配置！")
    print(f"  • 知识库路径: {get_vault_path()}")
    print(f"  • 忽略目录数: {len(get_ignored_patterns())}")
    print(f"  • SQLite路径: {get_db_path()}")
    print(f"  • 知识库主人: {get_user_profile().get('owner_name')}")
    print(f"  • 导出案卷页眉: {get_export_settings().get('docx_header')}")
    print(f"  • 同义词词条数: {len(get_synonyms())}")
    print(f"  • 自动双链实体数: {len(get_entity_links())}")
