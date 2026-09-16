#!/usr/bin/env python3
import os
import sys
import time
import datetime
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_loader import get_vault_path

vault_path = get_vault_path()
now = time.time()
DAY_SECS = 86400

tier1_hot = []      # < 7 days
tier2_active = []   # 7 - 30 days
tier3_cool = []     # 30 - 60 days
tier4_cold = []     # > 60 days
inbox_items = []

subsystem_activity = defaultdict(lambda: {"count": 0, "latest_mtime": 0, "recent_30d": 0})

for root, dirs, files in os.walk(vault_path):
    if ".obsidian" in root or "newdao-ide-windows" in root or "jdk" in root:
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
            if age_days <= 30:
                subsystem_activity[top_dir]["recent_30d"] += 1

            if rel.startswith("00_Inbox/"):
                inbox_items.append((age_days, rel))

            if age_days <= 7:
                tier1_hot.append((mtime, rel))
            elif age_days <= 30:
                tier2_active.append((mtime, rel))
            elif age_days <= 60:
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
