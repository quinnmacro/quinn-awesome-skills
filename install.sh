#!/usr/bin/env bash
# Quinn Awesome Skills 安装脚本
# 支持动态扫描 skills/ 和 commands/ 目录
# 用法: bash install.sh [skill_name]
# 如果不指定 skill_name，则安装所有 skill

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$SCRIPT_DIR/skills"
COMMANDS_DIR="$SCRIPT_DIR/commands"
CONNECTORS_DIR="$SCRIPT_DIR/connectors"

# 颜色定义（使用 printf 保证跨 shell 兼容）
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()  { printf "${BLUE}%b${NC}\n" "$1"; }
warn()  { printf "${YELLOW}%b${NC}\n" "$1"; }
ok()    { printf "${GREEN}%b${NC}\n" "$1"; }
fail()  { printf "${RED}%b${NC}\n" "$1"; }

# 检查依赖
check_deps() {
    local missing=()

    # 核心依赖
    for cmd in bash curl python3; do
        if ! command -v "$cmd" &>/dev/null; then
            missing+=("$cmd")
        fi
    done

    # 可选依赖（仅警告）
    local optional_missing=()
    for cmd in npx playwright; do
        if ! command -v "$cmd" &>/dev/null; then
            optional_missing+=("$cmd")
        fi
    done

    if [ ${#missing[@]} -gt 0 ]; then
        fail "❌ 缺少核心依赖: ${missing[*]}"
        echo "  请先安装: brew install ${missing[*]}  (macOS)"
        echo "  或:       apt-get install ${missing[*]}  (Linux)"
        exit 1
    fi

    if [ ${#optional_missing[@]} -gt 0 ]; then
        warn "⚠️  可选依赖未安装: ${optional_missing[*]}"
        echo "  部分 skill 功能可能受限（如 WeChat 公众号、Web 搜索）"
        echo ""
    fi
}

# 检查 shell 环境
check_shell() {
    if [ -z "${BASH_VERSION:-}" ]; then
        warn "⚠️  当前非 bash 环境 (shell: $0)"
        echo "  某些功能可能异常，建议使用: bash install.sh"
        echo ""
    fi
}

# 确保目录结构存在
check_dirs() {
    if [ ! -d "$SKILLS_DIR" ]; then
        fail "❌ skills 目录不存在: $SKILLS_DIR"
        exit 1
    fi
    mkdir -p "$COMMANDS_DIR" "$CONNECTORS_DIR"
}

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
    # 修复空数组问题：set -u 下空数组展开报错
    if [ ${#skills[@]} -eq 0 ]; then
        echo ""
    else
        echo "${skills[*]}"
    fi
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
    local SKILL_PATH
    SKILL_PATH=$(get_skill_path "$SKILL_NAME")

    if [ -z "$SKILL_PATH" ]; then
        fail "❌ Skill '$SKILL_NAME' 不存在"
        return 1
    fi

    local CATEGORY
    CATEGORY=$(get_skill_category "$SKILL_NAME")

    warn "📦 安装 $SKILL_NAME [$CATEGORY]..."

    # 1. 创建 ~/.agent/skills 目录
    mkdir -p ~/.agent/skills

    # 2. 复制 skill 到 ~/.agent/skills（安全处理已有目录）
    local target=~/.agent/skills/$SKILL_NAME
    if [ -d "$target" ]; then
        rm -rf "$target"
    fi
    cp -r "$SKILL_PATH" ~/.agent/skills/
    ok "  ✅ 复制到 ~/.agent/skills/$SKILL_NAME"

    # 3. 创建软链接到 ~/.claude/skills（安全处理已有目标）
    mkdir -p ~/.claude/skills
    safe_symlink ~/.agent/skills/$SKILL_NAME ~/.claude/skills/$SKILL_NAME
    ok "  ✅ 链接到 ~/.claude/skills/$SKILL_NAME"

    # 4. 创建软链接到 ~/.openclaw/skills
    mkdir -p ~/.openclaw/skills
    safe_symlink ~/.agent/skills/$SKILL_NAME ~/.openclaw/skills/$SKILL_NAME
    ok "  ✅ 链接到 ~/.openclaw/skills/$SKILL_NAME"

    # 5. 设置脚本可执行权限
    if [ -d ~/.agent/skills/$SKILL_NAME/scripts ]; then
        chmod +x ~/.agent/skills/$SKILL_NAME/scripts/*.sh 2>/dev/null || true
        chmod +x ~/.agent/skills/$SKILL_NAME/scripts/*.py 2>/dev/null || true
        ok "  ✅ 设置脚本可执行权限"
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

        # Ensure command directories exist before copying alias commands
        mkdir -p ~/.claude/commands
        mkdir -p ~/.openclaw/commands

        # Install alias commands: morning-brief and dev-pulse
        for alias_cmd in morning-brief dev-pulse; do
            local ALIAS_FILE="$COMMANDS_DIR/$alias_cmd.md"
            if [ -f "$ALIAS_FILE" ]; then
                cp "$ALIAS_FILE" ~/.claude/commands/$alias_cmd.md
                ln -sf ~/.claude/commands/$alias_cmd.md ~/.openclaw/commands/$alias_cmd.md
                echo -e "  ${GREEN}✅ 安装别名命令 /$alias_cmd${NC}"
            fi
        done
    fi

    # 7. Set up skill-hub dependencies
    if [ "$SKILL_NAME" = "skill-hub" ]; then
        mkdir -p ~/.quinn-skills
        echo -e "  ${BLUE}Installing skill-hub Python dependencies...${NC}"
        pip install fastapi uvicorn jinja2 aiosqlite httpx websockets 2>/dev/null || pip3 install fastapi uvicorn jinja2 aiosqlite httpx websockets 2>/dev/null || true
        echo -e "  ${GREEN}✅ Skill Hub ready — run with: bash ~/.claude/skills/skill-hub/scripts/start.sh${NC}"
    fi

    # 6. 安装斜杠命令（从 commands/ 目录）
    install_command "$SKILL_NAME"

    echo ""
}

# 安全创建软链接：如果目标是目录则先移除
safe_symlink() {
    local source="$1"
    local target="$2"
    if [ -L "$target" ]; then
        rm "$target"
    elif [ -e "$target" ]; then
        warn "  ⚠️  $target 已存在且非软链接，将被替换"
        rm -rf "$target"
    fi
    ln -s "$source" "$target"
}

# 安装命令
install_command() {
    local SKILL_NAME="$1"
    local COMMAND_FILE="$COMMANDS_DIR/$SKILL_NAME.md"

    mkdir -p ~/.claude/commands
    mkdir -p ~/.openclaw/commands

    if [ -f "$COMMAND_FILE" ]; then
        cp "$COMMAND_FILE" ~/.claude/commands/$SKILL_NAME.md
        ok "  ✅ 安装命令 ~/.claude/commands/$SKILL_NAME.md"
        safe_symlink ~/.claude/commands/$SKILL_NAME.md ~/.openclaw/commands/$SKILL_NAME.md
    else
        # 如果没有独立的命令文件，从 SKILL.md 生成
        local SKILL_PATH
        SKILL_PATH=$(get_skill_path "$SKILL_NAME")
        if [ -f "$SKILL_PATH/SKILL.md" ]; then
            generate_command_from_skill "$SKILL_NAME" "$SKILL_PATH/SKILL.md"
        fi
    fi
}

# 从 SKILL.md 生成命令文件（更健壮的 description 提取）
generate_command_from_skill() {
    local SKILL_NAME="$1"
    local SKILL_FILE="$2"

    # 提取 description：处理多行 YAML 和管道符
    local DESCRIPTION=""
    DESCRIPTION=$(sed -n '/^description:/,/^[a-z]/p' "$SKILL_FILE" \
        | head -n 10 \
        | sed '1s/^description:[ ]*//' \
        | sed '/^[a-z]/d' \
        | sed 's/^[ ]*//' \
        | sed 's/|//' \
        | tr '\n' ' ' \
        | sed 's/  */ /g' \
        | sed 's/ *$//')

    if [ -z "$DESCRIPTION" ]; then
        DESCRIPTION="$SKILL_NAME skill"
    fi

    # 生成命令文件
    cat > ~/.claude/commands/$SKILL_NAME.md << EOF
---
description: $DESCRIPTION
---

# /$SKILL_NAME

使用 $SKILL_NAME 技能。详见 ~/.claude/skills/$SKILL_NAME/SKILL.md
EOF
    ok "  ✅ 生成命令 ~/.claude/commands/$SKILL_NAME.md"
}

# 安装连接器配置
install_connectors() {
    info "🔗 安装连接器配置..."

    if [ -f "$CONNECTORS_DIR/mcp-servers.json" ]; then
        mkdir -p ~/.claude/connectors
        cp "$CONNECTORS_DIR/mcp-servers.json" ~/.claude/connectors/
        ok "  ✅ 复制 MCP 配置到 ~/.claude/connectors/"
    else
        warn "  ⚠️  无连接器配置文件"
    fi
    echo ""
}

# 安装共享脚本
install_shared_scripts() {
    info "📜 安装共享脚本..."

    if [ -d "$SCRIPT_DIR/scripts" ] && [ "$(ls -A "$SCRIPT_DIR/scripts/")" ]; then
        mkdir -p ~/.agent/scripts
        cp -r "$SCRIPT_DIR/scripts/"* ~/.agent/scripts/
        chmod +x ~/.agent/scripts/*.sh 2>/dev/null || true
        chmod +x ~/.agent/scripts/*.py 2>/dev/null || true
        ok "  ✅ 复制共享脚本到 ~/.agent/scripts/"
    else
        warn "  ⚠️  无共享脚本"
    fi
    echo ""
}

# 主逻辑
main() {
    check_shell
    check_deps
    check_dirs

    # 扫描所有可用的 skills
    local skills_output
    skills_output=$(scan_skills)

    if [ -z "$skills_output" ]; then
        fail "❌ 未找到任何 skill"
        exit 1
    fi

    local ALL_SKILLS
    read -ra ALL_SKILLS <<< "$skills_output"

    info "📋 发现 ${#ALL_SKILLS[@]} 个 skills: ${ALL_SKILLS[*]}"
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

    ok "🎉 安装完成！"
    echo ""
    echo "已安装的 skills:"
    for skill in "${ALL_SKILLS[@]}"; do
        local CATEGORY
        CATEGORY=$(get_skill_category "$skill")
        printf "  • ${YELLOW}/%s${NC} [%s]\n" "$skill" "$CATEGORY"
    done
    echo ""
    echo "测试命令:"
    echo "  /url-fetcher https://example.com"
    echo "  /presearch \"React framework\""
echo "  /daily-dev-pulse"
echo "  /skill-hub"
    echo "  /daily-dev-pulse --focus security"
}

# 运行主程序
main "$@"
