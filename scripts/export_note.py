#!/usr/bin/env python3
"""
export_note.py
Multi-Channel Commercial Exporter for Brain_Vault.
Converts any Markdown note into a beautifully styled Word (.docx) or print-ready HTML
without raw YAML tags, ready for client delivery or social media publishing.
"""

import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_loader import get_vault_path, get_export_settings

vault_path = get_vault_path()
if not os.path.exists(vault_path):
    print(f"⚠️ [export_note] 知识库目录不存在: {vault_path}")
    print("   请在 .config.toml 中配置正确的 [vault].root 路径。")
    sys.exit(0)

export_settings = get_export_settings()
header_text = export_settings.get("docx_header", "商业数字大脑交付案卷")
exp_sub = export_settings.get("export_dir", "Exports")
export_dir = os.path.join(vault_path, exp_sub) if not os.path.isabs(exp_sub) else exp_sub
os.makedirs(export_dir, exist_ok=True)

md_path = sys.argv[1] if len(sys.argv) > 1 else ""
if not md_path or not os.path.exists(md_path):
    print("用法: python3 export_note.py <Markdown文件路径> [格式: docx|html|all]")
    sys.exit(0)

fmt = sys.argv[2] if len(sys.argv) > 2 else "docx"
print(f"📤 正在准备导出商业交付文档: {md_path} (目标格式: {fmt})")

with open(md_path, "r", encoding="utf-8", errors="ignore") as fp:
    raw_content = fp.read()

# Strip YAML header and extract title
body_content = raw_content
doc_title = os.path.splitext(os.path.basename(md_path))[0]

if raw_content.startswith("---"):
    parts = raw_content.split("---", 2)
    if len(parts) >= 3:
        body_content = parts[2]

# Clean first H1 if present to use as title
m_h1 = re.search(r"^#\s+(.+)$", body_content, re.MULTILINE)
if m_h1:
    doc_title = m_h1.group(1).strip()
    body_content = body_content.replace(m_h1.group(0), "", 1)

clean_base = re.sub(r"[\\/:*?\"<>|\s]", "_", doc_title)[:50].strip() or "导出文档"

# 1. Export DOCX via python-docx
if fmt in ["docx", "all"]:
    try:
        from docx import Document
        from docx.shared import Pt, Inches, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        
        doc = Document()
        
        # Add Title
        p_title = doc.add_paragraph()
        p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_title = p_title.add_run(doc_title)
        run_title.font.name = "Arial"
        run_title.font.size = Pt(20)
        run_title.font.bold = True
        run_title.font.color.rgb = RGBColor(0x1F, 0x29, 0x37)
        
        # Add Subtitle / Meta
        p_sub = doc.add_paragraph()
        p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_sub = p_sub.add_run(f"{header_text} ｜ 导出日期：{time.strftime('%Y年%m月%d日')}")
        run_sub.font.size = Pt(10)
        run_sub.font.color.rgb = RGBColor(0x6B, 0x72, 0x80)
        doc.add_paragraph() # Spacer
        
        lines = body_content.splitlines()
        in_table = False
        table_rows = []
        
        for line in lines:
            s_line = line.strip()
            if not s_line or s_line == "---":
                continue
                
            # Table handling
            if s_line.startswith("|") and s_line.endswith("|"):
                # Ignore separator row | --- | --- |
                if set(s_line.replace("|", "").strip()) <= {"-", " ", ":"}:
                    continue
                cells = [c.strip() for c in s_line[1:-1].split("|")]
                table_rows.append(cells)
                in_table = True
                continue
            elif in_table:
                # Flush table
                if table_rows:
                    cols = max(len(r) for r in table_rows)
                    t = doc.add_table(rows=len(table_rows), cols=cols)
                    t.style = "Table Grid"
                    for r_idx, r_data in enumerate(table_rows):
                        for c_idx, c_val in enumerate(r_data):
                            if c_idx < cols:
                                t.cell(r_idx, c_idx).text = c_val
                in_table = False
                table_rows = []
                
            if s_line.startswith("#### "):
                h = doc.add_heading(level=4)
                r = h.add_run(s_line[5:])
                r.font.size = Pt(12)
            elif s_line.startswith("### "):
                h = doc.add_heading(level=3)
                r = h.add_run(s_line[4:])
                r.font.size = Pt(13)
            elif s_line.startswith("## "):
                h = doc.add_heading(level=2)
                r = h.add_run(s_line[3:])
                r.font.size = Pt(15)
            elif s_line.startswith("# "):
                h = doc.add_heading(level=1)
                r = h.add_run(s_line[2:])
                r.font.size = Pt(17)
            elif s_line.startswith("* ") or s_line.startswith("- "):
                clean_item = re.sub(r"\[\[(.*?)\]\]", r"\1", s_line[2:])
                doc.add_paragraph(clean_item, style="List Bullet")
            elif s_line.startswith("> "):
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.4)
                r = p.add_run(s_line[2:])
                r.font.italic = True
                r.font.color.rgb = RGBColor(0x4B, 0x55, 0x63)
            else:
                # Regular paragraph with stripped wikilinks
                clean_p = re.sub(r"\[\[(.*?)\]\]", r"\1", s_line)
                p = doc.add_paragraph(clean_p)
                p.paragraph_format.line_spacing = 1.25
                
        docx_target = os.path.join(export_dir, f"{clean_base}.docx")
        doc.save(docx_target)
        rel_docx = os.path.relpath(docx_target, vault_path)
        print(f"✅ Word 文档生成成功: {rel_docx}")
        print(f"• 访达打开: open -R \"{docx_target}\"")
    except Exception as e:
        print(f"❌ Word 导出失败: {e}")

# 2. Export HTML for print/PDF
if fmt in ["html", "all"]:
    try:
        html_target = os.path.join(export_dir, f"{clean_base}.html")
        html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{doc_title}</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", sans-serif; max-width: 860px; margin: 40px auto; padding: 20px; line-height: 1.6; color: #1F2937; }}
h1, h2, h3, h4 {{ color: #111827; }}
h1 {{ border-bottom: 2px solid #E5E7EB; padding-bottom: 8px; }}
h2 {{ border-bottom: 1px solid #E5E7EB; padding-bottom: 6px; margin-top: 30px; }}
blockquote {{ border-left: 4px solid #3B82F6; padding-left: 16px; margin: 16px 0; color: #4B5563; background: #F9FAFB; padding: 12px 16px; border-radius: 0 6px 6px 0; }}
table {{ border-collapse: collapse; width: 100%; margin: 20px 0; font-size: 14px; }}
th, td {{ border: 1px solid #D1D5DB; padding: 8px 12px; text-align: left; }}
th {{ background: #F3F4F6; }}
code {{ background: #F3F4F6; padding: 2px 6px; border-radius: 4px; font-size: 85%; }}
</style>
</head>
<body>
<h1>{doc_title}</h1>
<p style="color:#6B7280; font-size:13px;">{header_text} ｜ 导出日期：{time.strftime('%Y年%m月%d日')}</p>
{body_content}
</body>
</html>"""
        with open(html_target, "w", encoding="utf-8") as fp:
            fp.write(html_content)
        rel_html = os.path.relpath(html_target, vault_path)
        print(f"✅ HTML 打印排版页生成成功: {rel_html}")
    except Exception as e:
        print(f"❌ HTML 导出失败: {e}")

print("=" * 65)
