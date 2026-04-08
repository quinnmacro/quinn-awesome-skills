#!/bin/bash
# Quinn Awesome Skills 安装脚本
# 用法: bash install.sh [skill_name]
# 如果不指定 skill_name，则安装所有 skill

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$SCRIPT_DIR/skills"

# 要安装的 skill 列表
ALL_SKILLS=("url-fetcher" "presearch")

# 如果指定了 skill，只安装那个
if [ -n "${1:-}" ]; then
    SKILLS=("$1")
else
    SKILLS=("${ALL_SKILLS[@]}")
fi

echo "🚀 安装 Quinn Awesome Skills..."
echo ""

# 安装单个 skill 的函数
install_skill() {
    local SKILL_NAME="$1"
    local SKILL_PATH="$SKILLS_DIR/$SKILL_NAME"

    if [ ! -d "$SKILL_PATH" ]; then
        echo "❌ Skill '$SKILL_NAME' 不存在"
        return 1
    fi

    echo "📦 安装 $SKILL_NAME..."

    # 1. 创建 ~/.agent/skills 目录
    mkdir -p ~/.agent/skills

    # 2. 复制 skill 到 ~/.agent/skills
    if [ -d ~/.agent/skills/$SKILL_NAME ]; then
        rm -rf ~/.agent/skills/$SKILL_NAME
    fi
    cp -r "$SKILL_PATH" ~/.agent/skills/
    echo "  ✅ 复制到 ~/.agent/skills/$SKILL_NAME"

    # 3. 创建软链接到 ~/.claude/skills
    mkdir -p ~/.claude/skills
    ln -sf ~/.agent/skills/$SKILL_NAME ~/.claude/skills/$SKILL_NAME
    echo "  ✅ 链接到 ~/.claude/skills/$SKILL_NAME"

    # 4. 创建软链接到 ~/.openclaw/skills
    mkdir -p ~/.openclaw/skills
    ln -sf ~/.agent/skills/$SKILL_NAME ~/.openclaw/skills/$SKILL_NAME
    echo "  ✅ 链接到 ~/.openclaw/skills/$SKILL_NAME"

    # 5. 设置脚本可执行权限
    if [ -d ~/.agent/skills/$SKILL_NAME/scripts ]; then
        chmod +x ~/.agent/skills/$SKILL_NAME/scripts/*.sh 2>/dev/null || true
        chmod +x ~/.agent/skills/$SKILL_NAME/scripts/*.py 2>/dev/null || true
        echo "  ✅ 设置脚本可执行权限"
    fi

    # 6. 安装斜杠命令
    mkdir -p ~/.claude/commands
    mkdir -p ~/.openclaw/commands

    if [ -f "$SKILL_PATH/SKILL.md" ]; then
        create_slash_command "$SKILL_NAME"
    fi

    echo ""
}

# 创建斜杠命令的函数
create_slash_command() {
    local SKILL_NAME="$1"

    case "$SKILL_NAME" in
        "url-fetcher")
            cat > ~/.claude/commands/$SKILL_NAME.md << 'EOF'
---
description: 获取任意 URL 内容转为 Markdown，支持公众号、飞书、社交媒体、PDF、Web搜索
allowed-tools: Bash(curl *), Bash(bash *), Bash(python3 *)
---

# URL Fetcher - URL 转 Markdown

将任意 URL 转为干净的 Markdown。支持需要登录的页面、PDF、专有平台。

## 用法

```
/url-fetcher <URL>
/url-fetcher <search query>    # Web 搜索
```

## URL 路由

根据 URL 类型自动选择处理方式：

| URL 类型 | 命令 |
|----------|------|
| 微信公众号 | `python3 ~/.claude/skills/url-fetcher/scripts/fetch_weixin.py "URL"` |
| 飞书文档 | `python3 ~/.claude/skills/url-fetcher/scripts/fetch_feishu.py "URL"` |
| Twitter/X | `bash ~/.claude/skills/url-fetcher/scripts/fetch.sh "URL"` |
| Instagram | `bash ~/.claude/skills/url-fetcher/scripts/fetch.sh "URL"` |
| TikTok | `bash ~/.claude/skills/url-fetcher/scripts/fetch.sh "URL"` |
| Reddit | `bash ~/.claude/skills/url-fetcher/scripts/fetch.sh "URL"` |
| PDF 文件 | `bash ~/.claude/skills/url-fetcher/scripts/extract_pdf.sh "PATH"` |
| Web 搜索 | `bash ~/.claude/skills/url-fetcher/scripts/search.sh "query"` |
| 其他 URL | `bash ~/.claude/skills/url-fetcher/scripts/fetch.sh "URL"` |

## 工作流

1. **判断 URL 类型** - 根据域名选择处理脚本
2. **获取内容** - 执行对应脚本
3. **显示结果** - 标题、来源、摘要、正文
4. **保存文件** - 默认保存到 `~/Downloads/{title}.md`

## 依赖

- **基础**: bash, curl, python3
- **微信**: `pip install playwright beautifulsoup4 lxml && playwright install chromium`
- **飞书**: 设置 `FEISHU_APP_ID` + `FEISHU_APP_SECRET` 环境变量
- **PDF**: `pip install marker-pdf` 或 `brew install poppler`
- **搜索**: `npx open-websearch@latest`
EOF
            ;;
        "presearch")
            cat > ~/.claude/commands/$SKILL_NAME.md << 'EOF'
---
description: 开发前搜索现有方案，避免重复造轮子。用法：/presearch <功能描述> [格式]
allowed-tools: Bash(curl *), Bash(python3 *)
---

# Presearch - 开发前搜索

开发前搜索现有方案，避免重复造轮子。

## 用法

```
/presearch "Python web framework"
/presearch "React" emoji      # 表情包格式
```

## 核心命令

```bash
export PRESEARCH_MODULES=~/.claude/skills/presearch/modules
python3 ~/.claude/skills/presearch/modules/presearch_core.py "$@"
```

## 数据源

| 数据源 | 说明 |
|--------|------|
| GitHub | 开源项目，按 stars 排序 |
| npm | JavaScript 包 |
| PyPI | Python 包 |
| Docker Hub | 容器镜像 |
| arXiv | 学术论文 |

## 输出格式

| 格式 | 说明 |
|------|------|
| `table` | 默认表格格式 |
| `json` | JSON 格式 |
| `emoji` | 表情符号装饰 |
| `meme` | 程序员梗图风格 |
| `poetry` | 诗歌形式 |

## 依赖

```bash
pip install requests pydantic
```
EOF
            ;;
    esac

    echo "  ✅ 创建命令 ~/.claude/commands/$SKILL_NAME.md"
    ln -sf ~/.claude/commands/$SKILL_NAME.md ~/.openclaw/commands/$SKILL_NAME.md
    echo "  ✅ 链接命令到 ~/.openclaw/commands/$SKILL_NAME.md"
}

# 安装所有 skill
for skill in "${SKILLS[@]}"; do
    install_skill "$skill"
done

echo "🎉 安装完成！"
echo ""
echo "已安装的 skill:"
for skill in "${SKILLS[@]}"; do
    echo "  • /$skill"
done
echo ""
echo "测试命令:"
echo "  /url-fetcher https://example.com"
echo "  /presearch \"React framework\""
