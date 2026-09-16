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
echo -e "\n${YELLOW}[1/5] 检查 Python 环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 未检测到 python3，请先安装 Python 3.11 或更高版本。${NC}"
    exit 1
fi

PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo -e "  • 检测到 Python 版本: ${GREEN}${PY_VER}${NC}"

# 2. Install Dependencies
echo -e "\n${YELLOW}[2/5] 安装 Python 核心依赖...${NC}"
if [ -f "requirements.txt" ]; then
    python3 -m pip install -q -r requirements.txt || true
    echo -e "  • ${GREEN}依赖检查/安装完成${NC}"
fi

# 3. Setup Configuration (.config.toml)
echo -e "\n${YELLOW}[3/5] 初始化本地配置文件...${NC}"
if [ ! -f ".config.toml" ]; then
    if [ -t 0 ]; then
        echo -e "  ${BLUE}检测到交互式终端环境，启动快速配置向导：${NC}"
        read -r -p "  ? 请输入知识库根目录路径 (Obsidian Vault Path) [默认: ~/Documents/Brain_Vault]: " USER_VAULT_PATH
        USER_VAULT_PATH=${USER_VAULT_PATH:-"~/Documents/Brain_Vault"}
        
        # Expand ~ if provided for default name extraction
        EXPANDED_PATH="${USER_VAULT_PATH/#\~/$HOME}"
        DEFAULT_VAULT_NAME=$(basename "$EXPANDED_PATH")
        
        read -r -p "  ? 请输入 Obsidian 库名称 (Vault Name) [默认: ${DEFAULT_VAULT_NAME}]: " USER_VAULT_NAME
        USER_VAULT_NAME=${USER_VAULT_NAME:-"$DEFAULT_VAULT_NAME"}
        
        DEFAULT_OWNER="${USER:-Admin}"
        read -r -p "  ? 请输入知识库主人姓名/昵称 (Owner Name) [默认: ${DEFAULT_OWNER}]: " USER_OWNER_NAME
        USER_OWNER_NAME=${USER_OWNER_NAME:-"$DEFAULT_OWNER"}
        
        cp .config.template.toml .config.toml
        python3 -c "
import sys
with open('.config.template.toml', 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('root = \"~/Documents/Brain_Vault\"', f'root = \"{sys.argv[1]}\"')
content = content.replace('vault_name = \"Brain_Vault\"', f'vault_name = \"{sys.argv[2]}\"')
content = content.replace('owner_name = \"Admin\"', f'owner_name = \"{sys.argv[3]}\"')
with open('.config.toml', 'w', encoding='utf-8') as f:
    f.write(content)
" "$USER_VAULT_PATH" "$USER_VAULT_NAME" "$USER_OWNER_NAME"
        echo -e "  • ${GREEN}已根据您的输入生成专属 .config.toml！${NC}"
    else
        if [ -f ".config.template.toml" ]; then
            cp .config.template.toml .config.toml
            echo -e "  • ${GREEN}已基于模板自动创建 .config.toml${NC}"
            echo -e "  • 提示: 请按需编辑 .config.toml 配置你的个人知识库路径与专属同义词。"
        fi
    fi
else
    echo -e "  • ${GREEN}.config.toml 已存在，保留现有配置${NC}"
fi

# 4. Multi-Agent Ecosystem Auto-Discovery & Link
echo -e "\n${YELLOW}[4/5] 适配主 AI Agent 环境与全局 CLI...${NC}"

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

# 4.2 Hermes Agent Integration
echo -e "  • ${GREEN}Hermes Agent 支持${NC}: 可作为专属长期记忆检索与知识中枢 Toolset 直接挂载"

# 4.3 Codex / OpenAI Agents
echo -e "  • ${GREEN}Codex / OpenAI 支持${NC}: 通过 \`AGENTS.md\` 声明知识中枢客观四态有效性与存盘规约"

# 4.4 Claude Code Integration Guide
echo -e "  • ${GREEN}Claude Code 支持${NC}: 运行 \`claude\` 并在你的项目中通过 \`CLAUDE.md\` 引用本库命令"

# 4.5 Cursor / Windsurf Rules
echo -e "  • ${GREEN}Cursor / Windsurf 支持${NC}: 可将本库规则引用至 \`.cursorrules\` 或 \`.windsurfrules\`"

# 4.6 Standalone CLI Symlink (~/.local/bin/vault)
mkdir -p "$HOME/.local/bin"
if [ -f "$SCRIPT_DIR/vault" ]; then
    chmod +x "$SCRIPT_DIR/vault"
    ln -sf "$SCRIPT_DIR/vault" "$HOME/.local/bin/vault"
    echo -e "  • ${GREEN}已挂载全局命令行命令: ~/.local/bin/vault${NC}"
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo -e "    ${YELLOW}提示: 请确保 ~/.local/bin 已加入您的 PATH 环境变量${NC}"
    fi
fi

# 5. Pre-warm Persistent SQLite Database (.vault_index.db)
echo -e "\n${YELLOW}[5/5] 初始化并预热持久化 SQLite 索引 (.vault_index.db)...${NC}"
if command -v git &> /dev/null && [ -d ".git" ]; then
    git update-index --skip-worktree .vault_index.db 2>/dev/null || true
fi
python3 scripts/vault_db.py || true

# 6. Run Verification Doctor
echo -e "\n${BLUE}======================================================================${NC}"
echo -e "${YELLOW}正在运行系统健康度自检 (vault_doctor.py)...${NC}"
echo -e "${BLUE}======================================================================${NC}"
python3 scripts/vault_doctor.py

echo -e "\n${GREEN}🎉 JM Brain Vault 安装配置完成！随时可以在各大 AI Agent 或终端中调度使用。${NC}\n"
