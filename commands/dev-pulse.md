---
description: 开发者日报（别名）— 与 /daily-dev-pulse 相同
allowed-tools: Bash(gh *), Bash(curl *), Bash(bash *), Bash(python3 *), Bash(mkdir *), Bash(cat *)
---

# /dev-pulse

`/dev-pulse` 是 `/daily-dev-pulse` 的别名，生成个性化开发者早报。

## 用法

与 `/daily-dev-pulse` 完全相同：

```
/dev-pulse                  # 完整早报 (默认)
/dev-pulse --focus news     # 只看技术新闻
/dev-pulse --format json    # JSON 输出
/dev-pulse --repos quinnmacro/gnhf  # 指定仓库
```

## 工作流

运行 `bash ~/.claude/skills/daily-dev-pulse/scripts/daily-dev-pulse.sh --format md`