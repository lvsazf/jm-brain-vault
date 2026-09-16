#!/usr/bin/env python3
"""
graph_diagnosis.py
Knowledge Graph Topology & Cognitive Gap Analysis Engine for Brain_Vault.
Calculates:
  - Hub Centrality (Super-connector notes)
  - Cross-Domain Bridges (Connecting different business lines)
  - Isolated Islands (Zero-link orphan notes)
  - Cognitive Gap Matrix (Under-connected business domains)
"""

import os
import re
from collections import defaultdict

import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_loader import get_vault_path, is_ignored_path, get_domains

vault_path = get_vault_path()
if not os.path.exists(vault_path):
    print(f"⚠️ [graph_diagnosis] 知识库目录不存在: {vault_path}")
    print("   请在 .config.toml 中配置正确的 [vault].root 路径。")
    sys.exit(0)

nodes = set()
edges = []
out_degree = defaultdict(int)
in_degree = defaultdict(int)
node_folder = {}

# Map file basename to canonical relative path
file_map = {}

link_regex = re.compile(r"\[\[(.*?)\]\]")

for root, dirs, files in os.walk(vault_path):
    if is_ignored_path(root):
        continue
    for f in files:
        if f.endswith(".md") and not f.startswith("."):
            full_p = os.path.join(root, f)
            rel_p = os.path.relpath(full_p, vault_path)
            nodes.add(rel_p)
            file_map[f] = rel_p
            file_map[f.replace(".md", "")] = rel_p
            
            top_dir = rel_p.split("/")[0]
            if top_dir.endswith(".md"):
                top_dir = "看板总控"
            node_folder[rel_p] = top_dir

for src in nodes:
    full_p = os.path.join(vault_path, src)
    try:
        with open(full_p, "r", encoding="utf-8", errors="ignore") as fp:
            content = fp.read()
        
        # Remove code blocks
        clean_content = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
        links = link_regex.findall(clean_content)
        for link in links:
            target = link.split("|")[0].split("#")[0].strip()
            if not target or target.startswith("^") or "\\" in target:
                continue
            # Resolve target
            resolved = None
            if target in nodes:
                resolved = target
            elif target + ".md" in nodes:
                resolved = target + ".md"
            elif target in file_map:
                resolved = file_map[target]
            elif target.split("/")[-1] in file_map:
                resolved = file_map[target.split("/")[-1]]
            
            if resolved and resolved != src:
                edges.append((src, resolved))
                out_degree[src] += 1
                in_degree[resolved] += 1
    except Exception:
        pass

# Top Centrality Hubs
centrality = []
for n in nodes:
    total_conn = out_degree[n] + in_degree[n]
    centrality.append((total_conn, in_degree[n], out_degree[n], n))

centrality.sort(key=lambda x: x[0], reverse=True)

# Cross-Domain Bridges
bridges = []
domain_matrix = defaultdict(lambda: defaultdict(int))

for src, dst in edges:
    src_dom = node_folder.get(src, "其他")
    dst_dom = node_folder.get(dst, "其他")
    domain_matrix[src_dom][dst_dom] += 1
    if src_dom != dst_dom:
        bridges.append((src, dst, src_dom, dst_dom))

# Isolated Islands
islands = [n for n in nodes if out_degree[n] == 0 and in_degree[n] == 0]

print("=" * 70)
print("🕸️  Brain_Vault 知识图谱拓扑与商业认知断层诊断报告")
print("=" * 70)
print(f"• 节点总数 (Markdown): {len(nodes)} 篇")
print(f"• 显式双向连接总数:    {len(edges)} 条")
print(f"• 孤岛无连接笔记:      {len(islands)} 篇 (占比 {len(islands)/len(nodes)*100:.1f}%)")
print("=" * 70)

print("\n👑 【全库五大超级中枢 (Hub Notes)】 (连接度最高的战略底座):")
for total, ind, outd, n in centrality[:6]:
    fn = os.path.basename(n)
    dom = node_folder.get(n, "未分类")
    print(f"  • [{fn}] ({dom}) ➔ 总连接: {total} (入链: {ind}, 出链: {outd})")

print("\n🌉 【跨业务协同桥梁 (Cross-Domain Bridges)】:")
unique_bridge_sources = set()
for src, dst, s_dom, d_dom in bridges:
    if s_dom != "看板总控" and d_dom != "看板总控":
        unique_bridge_sources.add((os.path.basename(src), os.path.basename(dst), s_dom, d_dom))

for s_fn, d_fn, s_dom, d_dom in list(unique_bridge_sources)[:5]:
    print(f"  • {s_dom}【{s_fn}】 ──协同──➔ {d_dom}【{d_fn}】")

print("\n⚠️ 【认知断层与业务盲区诊断 (Knowledge Gap Analysis)】:")
detected_domains = get_domains()
if not detected_domains:
    detected_domains = sorted(list({v for v in node_folder.values() if v != "看板总控"}))

if len(detected_domains) < 2:
    print(f"  ℹ️ 检测到知识库目前包含 {len(detected_domains)} 个核心业务板块，暂未形成多域交叉网络。")
else:
    for d1 in detected_domains:
        for d2 in detected_domains:
            if d1 < d2:
                conn_count = domain_matrix[d1][d2] + domain_matrix[d2][d1]
                if conn_count == 0:
                    print(f"  ❌ 断层发现: 【{d1}】与【{d2}】之间目前为 0 深度双链关联！")
                elif conn_count < 3:
                    print(f"  ⚠️ 弱连接预警: 【{d1}】与【{d2}】之间仅有 {conn_count} 处连接，协同偏薄弱。")
                else:
                    print(f"  ✅ 强协同连接: 【{d1}】与【{d2}】之间有 {conn_count} 处跨域网络协同。")

print("\n💡 【智能优化建议】:")
if islands:
    print(f"  1. 运行 `python3 weave_links.py --auto` 可一键为 {len(islands)} 篇孤岛笔记织入上下文网；")
print("  2. 建议在重点业务交付全案与核心方法论手册之间建立更多跨业务双向引用；")
print("  3. 建议为跨领域的弱连接业务板块增补关联索引台账。")
print("=" * 70)
