#!/bin/bash
# URL Fetcher Skill 安装脚本
# 用法: bash install.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_NAME="url-fetcher"

echo "🚀 安装 $SKILL_NAME skill..."

# 1. 创建 ~/.agent/skills 目录
mkdir -p ~/.agent/skills

# 2. 复制 skill 到 ~/.agent/skills
if [ -d ~/.agent/skills/$SKILL_NAME ]; then
    echo "  ⚠️  已存在，更新中..."
    rm -rf ~/.agent/skills/$SKILL_NAME
fi
cp -r "$SCRIPT_DIR/skills/$SKILL_NAME" ~/.agent/skills/
echo "  ✅ 复制到 ~/.agent/skills/$SKILL_NAME"

# 3. 创建软链接到 ~/.claude/skills
mkdir -p ~/.claude/skills
ln -sf ~/.agent/skills/$SKILL_NAME ~/.claude/skills/$SKILL_NAME
echo "  ✅ 链接到 ~/.claude/skills/$SKILL_NAME"

# 4. 创建软链接到 ~/.openclaw/skills
mkdir -p ~/.openclaw/skills
ln -sf ~/.agent/skills/$SKILL_NAME ~/.openclaw/skills/$SKILL_NAME
echo "  ✅ 链接到 ~/.openclaw/skills/$SKILL_NAME"

# 5. 安装斜杠命令
mkdir -p ~/.claude/commands
mkdir -p ~/.openclaw/commands

# 创建命令文件
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

## 示例

### 获取网页
```bash
bash ~/.claude/skills/url-fetcher/scripts/fetch.sh "https://example.com"
```

### 微信公众号文章
```bash
python3 ~/.claude/skills/url-fetcher/scripts/fetch_weixin.py "https://mp.weixin.qq.com/s/xxx"
```

### 飞书文档
```bash
python3 ~/.claude/skills/url-fetcher/scripts/fetch_feishu.py "https://xxx.feishu.cn/docx/xxx"
```

### Web 搜索
```bash
bash ~/.claude/skills/url-fetcher/scripts/search.sh "Claude Code usage"
```

### PDF 提取
```bash
bash ~/.claude/skills/url-fetcher/scripts/extract_pdf.sh "/path/to/paper.pdf"
```

## 依赖

- **基础**: bash, curl, python3
- **微信**: `pip install playwright beautifulsoup4 lxml && playwright install chromium`
- **飞书**: 设置 `FEISHU_APP_ID` + `FEISHU_APP_SECRET` 环境变量
- **PDF**: `pip install marker-pdf` 或 `brew install poppler`
- **搜索**: `npx open-websearch@latest`

## 社交媒体支持（无需登录）

| 平台 | 服务 | 状态 |
|------|------|------|
| Twitter/X | fxtwitter.com | ✅ |
| Instagram | fxstagram.com | ✅ |
| TikTok | tnktok.com | ✅ |
| Reddit | vxreddit.com | ✅ |
| Threads | fixthreads.seria.moe | ✅ |
| Bluesky | fxbsky.app | ✅ |

## 注意

- 获取后默认保存到 `~/Downloads/`
- 私有账号和已删除内容无法获取
- 遵守各平台的使用条款
EOF
echo "  ✅ 创建命令 ~/.claude/commands/$SKILL_NAME.md"

ln -sf ~/.claude/commands/$SKILL_NAME.md ~/.openclaw/commands/$SKILL_NAME.md
echo "  ✅ 链接命令到 ~/.openclaw/commands/$SKILL_NAME.md"

# 6. 设置脚本可执行权限
chmod +x ~/.agent/skills/$SKILL_NAME/scripts/*.sh 2>/dev/null || true
chmod +x ~/.agent/skills/$SKILL_NAME/scripts/*.py 2>/dev/null || true
echo "  ✅ 设置脚本可执行权限"

# 7. 测试安装
echo ""
echo "🧪 测试安装..."
if bash ~/.claude/skills/$SKILL_NAME/scripts/fetch.sh "https://example.com" &>/dev/null; then
    echo "  ✅ 测试通过"
else
    echo "  ⚠️  测试失败，请检查依赖"
fi

echo ""
echo "🎉 安装完成！"
echo ""
echo "使用方法:"
echo "  /url-fetcher <URL>         # 获取网页"
echo "  /url-fetcher <search query> # Web 搜索"
echo ""
echo "或直接调用脚本:"
echo "  bash ~/.claude/skills/url-fetcher/scripts/fetch.sh \"https://example.com\""
