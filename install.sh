#!/usr/bin/env bash
# ==============================================================================
# JM Brain Vault - Multi-Agent & Standalone One-Click Installer
# Supports: Google Antigravity, Claude Code, Cursor, Windsurf, Standalone CLI
# ==============================================================================

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================================================${NC}"
echo -e "${GREEN}🧠  JM Brain Vault 知识中枢智能管家 - 多智能体一键安装程序${NC}"
echo -e "${BLUE}======================================================================${NC}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Check Python Version
echo -e "\n${YELLOW}[1/4] 检查 Python 环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 未检测到 python3，请先安装 Python 3.11 或更高版本。${NC}"
    exit 1
fi

PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo -e "  • 检测到 Python 版本: ${GREEN}${PY_VER}${NC}"

# 2. Install Dependencies
echo -e "\n${YELLOW}[2/4] 安装 Python 核心依赖...${NC}"
if [ -f "requirements.txt" ]; then
    python3 -m pip install -q -r requirements.txt || true
    echo -e "  • ${GREEN}依赖检查/安装完成${NC}"
fi

# 3. Setup Configuration (.config.toml)
echo -e "\n${YELLOW}[3/4] 初始化本地配置文件...${NC}"
if [ ! -f ".config.toml" ]; then
    if [ -f ".config.template.toml" ]; then
        cp .config.template.toml .config.toml
        echo -e "  • ${GREEN}已基于模板创建 .config.toml${NC}"
        echo -e "  • 提示: 请记得稍后按需编辑 .config.toml 配置你的个人知识库路径与专属同义词。"
    fi
else
    echo -e "  • ${GREEN}.config.toml 已存在，保留现有配置${NC}"
fi

# 4. Multi-Agent Ecosystem Auto-Discovery & Link
echo -e "\n${YELLOW}[4/4] 适配主流 AI Agent 环境...${NC}"

# 4.1 Google Antigravity / Gemini CLI
GEMINI_SKILLS_DIR="$HOME/.gemini/config/skills"
if [ -d "$HOME/.gemini" ]; then
    mkdir -p "$GEMINI_SKILLS_DIR"
    TARGET_LINK="$GEMINI_SKILLS_DIR/jm-brain-vault"
    if [ "$SCRIPT_DIR" != "$TARGET_LINK" ] && [ ! -e "$TARGET_LINK" ]; then
        ln -sf "$SCRIPT_DIR" "$TARGET_LINK"
        echo -e "  • ${GREEN}已成功挂载至 Google Antigravity / Gemini CLI 技能库: ${TARGET_LINK}${NC}"
    else
        echo -e "  • ${GREEN}Google Antigravity / Gemini CLI 技能已就绪${NC}"
    fi
fi

# 4.2 Claude Code Integration Guide
echo -e "  • ${GREEN}Claude Code 支持${NC}: 运行 \`claude\` 并在你的项目中通过 \`CLAUDE.md\` 引用本库命令"

# 4.3 Cursor / Windsurf Rules
echo -e "  • ${GREEN}Cursor / Windsurf 支持${NC}: 可将本库的 SKILL.md 规则引用至 \`.cursorrules\`"

# 5. Run Verification Doctor
echo -e "\n${BLUE}======================================================================${NC}"
echo -e "${YELLOW}正在运行系统健康度自检 (vault_doctor.py)...${NC}"
echo -e "${BLUE}======================================================================${NC}"
python3 scripts/vault_doctor.py

echo -e "\n${GREEN}🎉 JM Brain Vault 安装配置完成！随时可以在各大 AI Agent 或终端中调度使用。${NC}\n"
