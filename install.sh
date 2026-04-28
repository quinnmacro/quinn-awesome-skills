#!/bin/bash
# Quinn Awesome Skills 安装脚本
# 支持动态扫描 skills/ 和 commands/ 目录
# 用法: bash install.sh [skill_name]
# 如果不指定 skill_name，则安装所有 skill

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$SCRIPT_DIR/skills"
COMMANDS_DIR="$SCRIPT_DIR/commands"
CONNECTORS_DIR="$SCRIPT_DIR/connectors"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 安装 Quinn Awesome Skills...${NC}"
echo ""

# 动态扫描所有 skills
scan_skills() {
    local skills=()
    for category_dir in "$SKILLS_DIR"/*/; do
        if [ -d "$category_dir" ]; then
            for skill_dir in "$category_dir"*/; do
                if [ -d "$skill_dir" ] && [ -f "$skill_dir/SKILL.md" ]; then
                    skills+=("$(basename "$skill_dir")")
                fi
            done
        fi
    done
    echo "${skills[@]}"
}

# 获取 skill 的完整路径
get_skill_path() {
    local skill_name="$1"
    for category_dir in "$SKILLS_DIR"/*/; do
        if [ -d "$category_dir$skill_name" ]; then
            echo "$category_dir$skill_name"
            return
        fi
    done
    echo ""
}

# 获取 skill 的类别
get_skill_category() {
    local skill_name="$1"
    for category_dir in "$SKILLS_DIR"/*/; do
        if [ -d "$category_dir$skill_name" ]; then
            basename "$category_dir"
            return
        fi
    done
    echo "unknown"
}

# 安装单个 skill
install_skill() {
    local SKILL_NAME="$1"
    local SKILL_PATH=$(get_skill_path "$SKILL_NAME")

    if [ -z "$SKILL_PATH" ]; then
        echo -e "${RED}❌ Skill '$SKILL_NAME' 不存在${NC}"
        return 1
    fi

    local CATEGORY=$(get_skill_category "$SKILL_NAME")

    echo -e "${YELLOW}📦 安装 $SKILL_NAME [$CATEGORY]...${NC}"

    # 1. 创建 ~/.agent/skills 目录
    mkdir -p ~/.agent/skills

    # 2. 复制 skill 到 ~/.agent/skills
    if [ -d ~/.agent/skills/$SKILL_NAME ]; then
        rm -rf ~/.agent/skills/$SKILL_NAME
    fi
    cp -r "$SKILL_PATH" ~/.agent/skills/
    echo -e "  ${GREEN}✅ 复制到 ~/.agent/skills/$SKILL_NAME${NC}"

    # 3. 创建软链接到 ~/.claude/skills
    mkdir -p ~/.claude/skills
    ln -sf ~/.agent/skills/$SKILL_NAME ~/.claude/skills/$SKILL_NAME
    echo -e "  ${GREEN}✅ 链接到 ~/.claude/skills/$SKILL_NAME${NC}"

    # 4. 创建软链接到 ~/.openclaw/skills
    mkdir -p ~/.openclaw/skills
    ln -sf ~/.agent/skills/$SKILL_NAME ~/.openclaw/skills/$SKILL_NAME
    echo -e "  ${GREEN}✅ 链接到 ~/.openclaw/skills/$SKILL_NAME${NC}"

    # 5. 设置脚本可执行权限
    if [ -d ~/.agent/skills/$SKILL_NAME/scripts ]; then
        chmod +x ~/.agent/skills/$SKILL_NAME/scripts/*.sh 2>/dev/null || true
        chmod +x ~/.agent/skills/$SKILL_NAME/scripts/*.py 2>/dev/null || true
        echo -e "  ${GREEN}✅ 设置脚本可执行权限${NC}"
    fi
    if [ -d ~/.agent/skills/$SKILL_NAME/modules ]; then
        chmod +x ~/.agent/skills/$SKILL_NAME/modules/*.py 2>/dev/null || true
    fi

    # 6. Set up config directory for daily-dev-pulse
    if [ "$SKILL_NAME" = "daily-dev-pulse" ]; then
        mkdir -p ~/.quinn-skills
        if [ ! -f ~/.quinn-skills/pulse-config.yml ]; then
            cp "$SKILL_PATH/config-example.yml" ~/.quinn-skills/pulse-config.yml
            echo -e "  ${GREEN}✅ 安装默认配置到 ~/.quinn-skills/pulse-config.yml${NC}"
        else
            echo -e "  ${YELLOW}⚠️ 配置已存在 ~/.quinn-skills/pulse-config.yml，保留现有配置${NC}"
        fi
    fi

    # 6. 安装斜杠命令（从 commands/ 目录）
    install_command "$SKILL_NAME"

    echo ""
}

# 安装命令
install_command() {
    local SKILL_NAME="$1"
    local COMMAND_FILE="$COMMANDS_DIR/$SKILL_NAME.md"

    mkdir -p ~/.claude/commands
    mkdir -p ~/.openclaw/commands

    if [ -f "$COMMAND_FILE" ]; then
        cp "$COMMAND_FILE" ~/.claude/commands/$SKILL_NAME.md
        echo -e "  ${GREEN}✅ 安装命令 ~/.claude/commands/$SKILL_NAME.md${NC}"
        ln -sf ~/.claude/commands/$SKILL_NAME.md ~/.openclaw/commands/$SKILL_NAME.md
    else
        # 如果没有独立的命令文件，从 SKILL.md 生成
        local SKILL_PATH=$(get_skill_path "$SKILL_NAME")
        if [ -f "$SKILL_PATH/SKILL.md" ]; then
            generate_command_from_skill "$SKILL_NAME" "$SKILL_PATH/SKILL.md"
        fi
    fi
}

# 从 SKILL.md 生成命令文件
generate_command_from_skill() {
    local SKILL_NAME="$1"
    local SKILL_FILE="$2"

    # 提取 description
    local DESCRIPTION=$(grep -A1 "^description:" "$SKILL_FILE" | tail -1 | sed 's/^[ ]*//')

    # 生成命令文件
    cat > ~/.claude/commands/$SKILL_NAME.md << EOF
---
description: $DESCRIPTION
---

# /$SKILL_NAME

使用 $SKILL_NAME 技能。详见 ~/.claude/skills/$SKILL_NAME/SKILL.md
EOF
    echo -e "  ${GREEN}✅ 生成命令 ~/.claude/commands/$SKILL_NAME.md${NC}"
}

# 安装连接器配置
install_connectors() {
    echo -e "${BLUE}🔗 安装连接器配置...${NC}"

    if [ -f "$CONNECTORS_DIR/mcp-servers.json" ]; then
        mkdir -p ~/.claude/connectors
        cp "$CONNECTORS_DIR/mcp-servers.json" ~/.claude/connectors/
        echo -e "  ${GREEN}✅ 复制 MCP 配置到 ~/.claude/connectors/${NC}"
    fi
    echo ""
}

# 安装共享脚本
install_shared_scripts() {
    echo -e "${BLUE}📜 安装共享脚本...${NC}"

    if [ -d "$SCRIPT_DIR/scripts" ]; then
        mkdir -p ~/.agent/scripts
        cp -r "$SCRIPT_DIR/scripts/"* ~/.agent/scripts/
        chmod +x ~/.agent/scripts/*.sh 2>/dev/null || true
        chmod +x ~/.agent/scripts/*.py 2>/dev/null || true
        echo -e "  ${GREEN}✅ 复制共享脚本到 ~/.agent/scripts/${NC}"
    fi
    echo ""
}

# 主逻辑
main() {
    # 扫描所有可用的 skills
    ALL_SKILLS=($(scan_skills))

    if [ ${#ALL_SKILLS[@]} -eq 0 ]; then
        echo -e "${RED}❌ 未找到任何 skill${NC}"
        exit 1
    fi

    echo -e "${BLUE}📋 发现 ${#ALL_SKILLS[@]} 个 skills: ${ALL_SKILLS[*]}${NC}"
    echo ""

    # 如果指定了 skill，只安装那个
    if [ -n "${1:-}" ]; then
        install_skill "$1"
    else
        # 安装所有 skills
        for skill in "${ALL_SKILLS[@]}"; do
            install_skill "$skill"
        done
    fi

    # 安装连接器和共享脚本
    install_connectors
    install_shared_scripts

    echo -e "${GREEN}🎉 安装完成！${NC}"
    echo ""
    echo "已安装的 skills:"
    for skill in "${ALL_SKILLS[@]}"; do
        local CATEGORY=$(get_skill_category "$skill")
        echo -e "  • ${YELLOW}/$skill${NC} [$CATEGORY]"
    done
    echo ""
    echo "测试命令:"
    echo "  /url-fetcher https://example.com"
    echo "  /presearch \"React framework\""
    echo "  /investor-distiller 巴菲特"
}

# 运行主程序
main "$@"
