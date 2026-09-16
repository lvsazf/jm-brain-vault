#!/usr/bin/env python3
import os
import sys
import time
import datetime
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_loader import get_vault_path, is_ignored_path, load_config, get_metabolism_settings

vault_path = get_vault_path()
if not os.path.exists(vault_path):
    print(f"⚠️ [scan_pulse] 知识库目录不存在: {vault_path}")
    print("   请在 .config.toml 中配置正确的 [vault].root 路径。")
    sys.exit(0)

cfg = load_config()
inbox_folder = cfg.get("vault", {}).get("inbox_folder", "00_Inbox")
meta_cfg = get_metabolism_settings()
hot_days = meta_cfg.get("hot_days", 7)
active_days = meta_cfg.get("active_days", 30)
dormant_days = meta_cfg.get("dormant_days", 60)

now = time.time()
DAY_SECS = 86400

tier1_hot = []      # <= hot_days
tier2_active = []   # hot_days - active_days
tier3_cool = []     # active_days - dormant_days
tier4_cold = []     # > dormant_days
inbox_items = []

subsystem_activity = defaultdict(lambda: {"count": 0, "latest_mtime": 0, "recent_30d": 0})

for root, dirs, files in os.walk(vault_path):
    if is_ignored_path(root):
        continue
    for f in files:
        if f.startswith("."):
            continue
        p = os.path.join(root, f)
        rel = os.path.relpath(p, vault_path)
        try:
            mtime = os.path.getmtime(p)
            age_days = (now - mtime) / DAY_SECS
            
            top_dir = rel.split("/")[0]
            if top_dir.endswith(".md"):
                top_dir = "看板与总控"
            
            subsystem_activity[top_dir]["count"] += 1
            if mtime > subsystem_activity[top_dir]["latest_mtime"]:
                subsystem_activity[top_dir]["latest_mtime"] = mtime
            if age_days <= active_days:
                subsystem_activity[top_dir]["recent_30d"] += 1

            if rel.startswith(f"{inbox_folder}/"):
                inbox_items.append((age_days, rel))

            if age_days <= hot_days:
                tier1_hot.append((mtime, rel))
            elif age_days <= active_days:
                tier2_active.append((mtime, rel))
            elif age_days <= dormant_days:
                tier3_cool.append((mtime, rel))
            else:
                tier4_cold.append((mtime, rel))
        except Exception:
            pass

print("=" * 60)
print(f"📊 Brain_Vault 知识库月度活跃脉搏报告 ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M')})")
print("=" * 60)

print("\n🏢 板块活跃度分布 (过去 30 天):")
for dom, stat in sorted(subsystem_activity.items(), key=lambda x: -x[1]["recent_30d"]):
    latest_dt = datetime.datetime.fromtimestamp(stat["latest_mtime"]).strftime('%Y-%m-%d') if stat["latest_mtime"] > 0 else "N/A"
    hot_flag = "🔥 高频攻坚" if stat["recent_30d"] >= 5 else ("⚡ 有活跃更新" if stat["recent_30d"] > 0 else "❄️ 休眠归档")
    print(f"  • {dom:<25} | 30天更新: {stat['recent_30d']:3d} 篇 | 最新: {latest_dt} | {hot_flag}")

print(f"\n📈 全库文件生命周期分布 (共 {len(tier1_hot)+len(tier2_active)+len(tier3_cool)+len(tier4_cold)} 个文件):")
print(f"  🔥 超高频攻坚 (最近 7 天内):    {len(tier1_hot):4d} 个文件")
print(f"  ⚡ 持续推进中 (8 ~ 30 天内):     {len(tier2_active):4d} 个文件")
print(f"  ❄️ 休眠与完成 (31 ~ 60 天内):    {len(tier3_cool):4d} 个文件")
print(f"  🧊 永久备查底座 (> 60 天):       {len(tier4_cold):4d} 个文件")

if tier1_hot:
    print("\n🔥 最近 7 天最新更新 Top 10 (建议看板首推):")
    tier1_hot.sort(key=lambda x: x[0], reverse=True)
    for mt, r in tier1_hot[:10]:
        dt = datetime.datetime.fromtimestamp(mt).strftime('%Y-%m-%d %H:%M')
        print(f"  [{dt}] {r}")

if inbox_items:
    print(f"\n📥 00_Inbox 缓冲区积攒状态 (共 {len(inbox_items)} 篇):")
    inbox_items.sort(key=lambda x: -x[0])
    for age, r in inbox_items[:5]:
        print(f"  • {r} (已停留 {int(age)} 天，建议归类)")
else:
    print("\n📥 00_Inbox 缓冲区状态: 清空 (Inbox Zero)")

print("\n" + "=" * 60)
