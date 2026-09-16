#!/usr/bin/env python3
"""
clip_url.py
Intelligent Web Clipper for Brain_Vault.
Extracts clean Markdown from public URLs, strips clutter,
injects standard YAML frontmatter, and archives into configured web_clip output directory.
"""

import os
import re
import sys
import time
import urllib.request
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_loader import get_vault_path, get_web_clip_settings, get_obsidian_uri, get_reveal_command

vault_path = get_vault_path()
if not os.path.exists(vault_path):
    print(f"⚠️ [clip_url] 知识库目录不存在: {vault_path}")
    print("   请在 .config.toml 中配置正确的 [vault].root 路径。")
    sys.exit(0)

wc_cfg = get_web_clip_settings()
wc_sub = wc_cfg.get("output_dir", "Web_Clips")
clips_dir = os.path.join(vault_path, wc_sub) if not os.path.isabs(wc_sub) else wc_sub
os.makedirs(clips_dir, exist_ok=True)

url = sys.argv[1] if len(sys.argv) > 1 else ""
if not url:
    print("用法: python3 clip_url.py <URL地址>")
    sys.exit(0)

print(f"🌐 正在抓取并提纯网页内容: {url}")

class MarkdownExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.title = ""
        self.in_title = False
        self.ignore = False
        
    def handle_starttag(self, tag, attrs):
        if tag in ["script", "style", "nav", "footer", "aside", "header"]:
            self.ignore = True
        elif tag == "title":
            self.in_title = True
        elif tag in ["h1", "h2", "h3", "h4"]:
            level = int(tag[1])
            self.text.append("\n\n" + ("#" * level) + " ")
        elif tag in ["p", "div", "article", "section"]:
            self.text.append("\n\n")
        elif tag == "li":
            self.text.append("\n* ")
            
    def handle_endtag(self, tag):
        if tag in ["script", "style", "nav", "footer", "aside", "header"]:
            self.ignore = False
        elif tag == "title":
            self.in_title = False
            
    def handle_data(self, data):
        if self.in_title and not self.title:
            self.title = data.strip()
        if not self.ignore:
            cleaned = data.strip()
            if cleaned:
                self.text.append(cleaned + " ")

try:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        raw_html = resp.read().decode(charset, errors="ignore")
        
    parser = MarkdownExtractor()
    parser.feed(raw_html)
    
    title = parser.title or "网页剪藏文章"
    body_md = "".join(parser.text).strip()
    # Normalize multiple newlines
    body_md = re.sub(r"\n{3,}", "\n\n", body_md)
    
    safe_title = re.sub(r"[\\/:*?\"<>|\s]", "_", title)[:50].strip() or "网页剪藏"
    filename = f"{safe_title}.md"
    target_path = os.path.join(clips_dir, filename)
    
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")
    yaml_header = f"""---
category: 资料/网页剪藏
domain: 知识/行业资讯
status: 状态/整体有效
source_url: "{url}"
clipped_at: "{now_str}"
topics:
  - 网页剪藏
  - 外部参考
confidentiality: 公开
---

# {title}

> **来源网址**：[{url}]({url})  
> **剪藏时间**：{now_str}  
> **提纯状态**：已剥离网页杂质，转换为标准 Markdown

---

"""
    
    with open(target_path, "w", encoding="utf-8") as fp:
        fp.write(yaml_header + body_md + "\n")
        
    rel_p = os.path.relpath(target_path, vault_path)
    obs_uri = get_obsidian_uri(rel_p)
    reveal_cmd = get_reveal_command(target_path)
    print("=" * 65)
    print("✅ 网页剪藏与降噪提纯入库成功！")
    print(f"• 保存路径:  {rel_p}")
    print(f"• 标题提炼:  {title}")
    print(f"• 笔记直达:  {obs_uri}")
    print(f"• 定位文件:  {reveal_cmd}")
    print("=" * 65)

except Exception as e:
    print(f"❌ 抓取失败: {e}")
    sys.exit(1)
