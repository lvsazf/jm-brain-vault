#!/usr/bin/env python3
"""
transcribe_audio.py
Voice-to-Knowledge Pipeline for Brain_Vault powered by faster-whisper.
Transcribes audio files (.m4a, .mp3, .wav, .aac, .ogg) into structured Markdown notes
with timestamps, summaries, and standard YAML metadata.
"""

import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_loader import get_vault_path, get_transcribe_settings, get_obsidian_uri, get_reveal_command

vault_path = get_vault_path()
if not os.path.exists(vault_path):
    print(f"⚠️ [transcribe_audio] 知识库目录不存在: {vault_path}")
    print("   请在 .config.toml 中配置正确的 [vault].root 路径。")
    sys.exit(0)

tr_cfg = get_transcribe_settings()
tr_sub = tr_cfg.get("output_dir", "Voice_Notes")
output_dir = os.path.join(vault_path, tr_sub) if not os.path.isabs(tr_sub) else tr_sub
os.makedirs(output_dir, exist_ok=True)

audio_path = sys.argv[1] if len(sys.argv) > 1 else ""
if not audio_path or not os.path.exists(audio_path):
    print("用法: python3 transcribe_audio.py <音频文件路径> [模型规格: tiny|base|small]")
    sys.exit(0)

default_model = tr_cfg.get("model_size", "base")
model_size = sys.argv[2] if len(sys.argv) > 2 else default_model
print(f"🎙️ 正在启动 Whisper 语音听写引擎 (模型: {model_size})...")
print(f"📁 音频源文件: {audio_path}")

try:
    from faster_whisper import WhisperModel
    # Run locally on CPU with int8 quantization (lightweight & fast)
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, info = model.transcribe(audio_path, beam_size=5, language="zh")
    
    print(f"⚡ 检测到语言: {info.language} (置信度: {info.language_probability:.2f}), 音频时长: {info.duration:.1f} 秒")
    
    transcript_segments = []
    full_text_list = []
    
    for seg in segments:
        m, s = divmod(int(seg.start), 60)
        time_str = f"{m:02d}:{s:02d}"
        text = seg.text.strip()
        if text:
            transcript_segments.append(f"• **[{time_str}]** {text}")
            full_text_list.append(text)
            
    full_text = " ".join(full_text_list)
    
    # Title from first 20 chars or filename
    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    safe_title = re.sub(r"[\\/:*?\"<>|\s]", "_", base_name)[:40].strip()
    target_path = os.path.join(output_dir, f"{safe_title}_语音整理.md")
    
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")
    default_domain = tr_cfg.get("default_domain", "资产/录音速记")
    yaml_header = f"""---
category: 资产/录音转录
domain: {default_domain}
status: 状态/整体有效
source_audio: "{audio_path}"
duration_seconds: {info.duration:.1f}
created_at: "{now_str}"
topics:
  - 录音转录
  - 灵感速记
confidentiality: 内部/限制
---

# 🎙️ {safe_title} (语音实录与提纯)

> **音频源文件**：`{audio_path}`  
> **音频时长**：{info.duration / 60:.1f} 分钟 ({info.duration:.0f} 秒) ｜ **转录引擎**：Faster-Whisper ({model_size})  
> **整理时间**：{now_str}

---

## 💡 一、 核心要点速览 (全文字数: {len(full_text)})

{full_text[:300]}...

---

## 📋 二、 逐字分段对照 (带时间戳)

"""
    
    final_content = yaml_header + "\n".join(transcript_segments) + "\n"
    with open(target_path, "w", encoding="utf-8") as fp:
        fp.write(final_content)
        
    rel_p = os.path.relpath(target_path, vault_path)
    obs_uri = get_obsidian_uri(rel_p)
    reveal_cmd = get_reveal_command(target_path)
    print("=" * 65)
    print("✅ 语音转录与提纯笔记生成成功！")
    print(f"• 保存路径:  {rel_p}")
    print(f"• 笔记直达:  {obs_uri}")
    print(f"• 定位文件:  {reveal_cmd}")
    print("=" * 65)

except Exception as e:
    print(f"❌ 转录失败: {e}")
    sys.exit(1)
