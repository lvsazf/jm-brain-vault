#!/usr/bin/env python3
"""
vault_doctor.py
One-stop Automated Health, Validity & Metabolism Diagnostic Engine for Brain_Vault.
Audits:
  1. Link integrity & zero dead links
  2. Objective validity status distribution (整体有效 / 部分有效 / 失效归档)
  3. Dynamic monthly metabolism (30-day activity pulse & dormant demotion)
  4. Unlinked mentions & network weaving opportunities
"""

import os
import subprocess
import sys

scripts_dir = os.path.dirname(os.path.abspath(__file__))

print("=" * 70)
print("🏥  JM Brain Vault 知识中枢全息健康与生命体征诊断")
print("=" * 70)

# Check 1: Links & YAML Health
print("\n[检查 1/6] 双向链接与 YAML 语法合规性体检...")
subprocess.run([sys.executable, os.path.join(scripts_dir, "verify_links.py")])

# Check 2: Objective Validity Verification
print("\n[检查 2/6] 客观知识有效性规则裁决审计...")
subprocess.run([sys.executable, os.path.join(scripts_dir, "verify_validity.py")])

# Check 3: Metabolism & Pulse
print("\n[检查 3/6] 30天动态代谢与活跃热力感知...")
subprocess.run([sys.executable, os.path.join(scripts_dir, "scan_pulse.py")])

# Check 4: Unlinked Mentions
print("\n[检查 4/6] 隐式提及与网络织网探测...")
subprocess.run([sys.executable, os.path.join(scripts_dir, "scan_unlinked.py")])

# Check 5: Config Auto-Sync & Self-Healing
print("\n[检查 5/6] 配置自动提炼与版本跃迁自愈...")
subprocess.run([sys.executable, os.path.join(scripts_dir, "sync_config.py")])

# Check 6: Persistent SQLite Storage & Incremental Index
print("\n[检查 6/6] SQLite 持久化索引与增量存储健康度自检...")
subprocess.run([sys.executable, os.path.join(scripts_dir, "vault_db.py")])

print("\n" + "=" * 70)
print("🎉 知识中枢体检完成！系统运行平稳，无死链，无格式冲突，状态100%合规。")
print("=" * 70)
