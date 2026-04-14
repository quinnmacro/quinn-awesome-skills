---
name: macro-brief
description: |
  Generate daily macroeconomic briefs, market summaries, and economic analysis.
  Create structured reports on economic indicators, central bank policies, and market trends.
  "宏观经济简报", "市场晨报", "经济日报".
version: 1.0.0
author: quinnmacro
layer: domain. Triggers: "宏观经济简报", "市场晨报", "经济日报", "生成宏观简报", "宏观分析", "macro brief", "economic summary", "market overview".
---

# Macro Brief - 宏观经济简报

生成专业的宏观经济简报和市场分析报告。


## 一、快速开始

### 1.1 何时使用

- TODO: 添加触发场景

### 1.2 核心步骤

1. TODO: 步骤1
2. TODO: 步骤2

### 1.3 成功标准

- [ ] TODO: 验证标准
## Trigger Phrases

- "生成宏观简报"
- "市场晨报"
- "经济日报"
- "宏观分析"
- "macro brief"
- "economic summary"
- "market overview"

## Brief Types 简报类型

### Daily Brief 每日简报

```markdown
# 宏观晨报 [日期]

## 市场概览

| 资产 | 收盘 | 涨跌 |
|------|------|------|
| 标普500 | ... | ... |
| 10Y美债 | ... | ... |
| 美元指数 | ... | ... |
| 黄金 | ... | ... |
| WTI原油 | ... | ... |

## 宏观要闻

1. [要点1]
2. [要点2]
3. [要点3]

## 数据日历

| 时间 | 事件 | 预期 | 前值 |
|------|------|------|------|
| ... | ... | ... | ... |

## 今日关注

- 关注点1
- 关注点2
```

### Weekly Review 周度回顾

```markdown
# 宏观周报 [周次]

## 本周回顾

### 资产表现
[周度资产表现分析]

### 宏观事件
[重要宏观事件回顾]

### 数据解读
[关键经济数据解读]

## 下周展望

### 数据日历
[下周重要数据发布]

### 事件前瞻
[央行会议、重要讲话等]

### 策略建议
[短期策略方向]
```

### Thematic Report 专题报告

```markdown
# 专题报告: [主题]

## 背景
[问题背景和研究意义]

## 核心观点
[主要结论，3-5点]

## 分析框架
[分析方法论]

## 数据支持
[关键数据和图表]

## 风险因素
[潜在风险点]

## 结论
[总结和展望]
```

## Key Indicators 关键指标

### US Economy 美国经济

| Indicator | Frequency | Impact |
|-----------|-----------|--------|
| 非农就业 (NFP) | 月度 | 高 |
| CPI/PCE | 月度 | 高 |
| GDP | 季度 | 高 |
| FOMC决议 | 8次/年 | 极高 |
| ISM PMI | 月度 | 中 |
| 零售销售 | 月度 | 中 |

### China Economy 中国经济

| Indicator | Frequency | Impact |
|-----------|-----------|--------|
| PMI | 月度 | 高 |
| 工业增加值 | 月度 | 中 |
| 社融/信贷 | 月度 | 高 |
| CPI/PPI | 月度 | 中 |
| GDP | 季度 | 高 |
| LPR | 月度 | 中 |

### Global Markets 全球市场

| Indicator | Frequency | Impact |
|-----------|-----------|--------|
| 美债收益率 | 日度 | 高 |
| 美元指数 | 日度 | 高 |
| VIX恐慌指数 | 日度 | 中 |
| 油价/金价 | 日度 | 中 |
| 主要股指 | 日度 | 高 |

## Analysis Framework 分析框架

### Growth-Inflation Matrix 增长-通胀矩阵

```
        低通胀           高通胀
高增长  | 衰退复苏       | 过热风险
        | 风险资产利好   | 央行紧缩风险
--------+----------------+----------------
低增长  | 衰退/滞胀风险   | 滞胀
        | 避险资产利好   | 最差情境
```

### Central Bank Watch 央行观察

```
美联储 (Fed):
- 利率水平: [当前利率]
- 点阵图信号: [鹰/鸽]
- QT进度: [缩表节奏]
- 关注措辞: "通胀"、"就业"、"数据依赖"

中国人民银行 (PBOC):
- 政策利率: [MLF/LPR]
- 存准率: [当前水平]
- 流动性态度: [宽松/中性/紧缩]
- 关注措辞: "稳健"、"精准"、"跨周期"
```

## Usage

```bash
# Generate daily macro brief
bash scripts/llm.sh "生成今日宏观简报，包含美股、美债、大宗商品市场回顾" --system "你是一位专业的宏观研究员"

# Generate thematic report
bash scripts/llm.sh "写一份关于美国高利率环境下新兴市场风险的专题报告" --json

# Analyze economic data
bash scripts/llm.sh "解读最新的美国非农就业数据对市场的影响"
```

## Output Format

```markdown
# [简报类型] [日期/标题]

## 摘要
[3句话核心观点]

## 正文
[详细分析]

## 市场影响
[对各类资产的影响分析]

## 风险提示
[潜在风险点]

---
*数据来源: Bloomberg/Reuters/Wind*
*免责声明: 仅供参考，不构成投资建议*
```

## Notes

- 数据需从可靠来源获取
- 简报应客观中立，避免主观预测
- 风险提示必不可少
- 建议标注数据来源和免责声明

---

## 检查清单

### 生成前

- [ ] 确认简报类型（日报/周报/专题）
- [ ] 确认时间范围和覆盖市场
- [ ] 确认数据源可用（Bloomberg/Reuters/Wind）

### 数据收集

- [ ] 收集主要资产价格数据
- [ ] 收集重要经济数据
- [ ] 收集政策事件和央行动态
- [ ] 验证数据准确性

### 简报撰写

- [ ] 市场概览表格完整
- [ ] 宏观要闻提炼准确（3-5条）
- [ ] 数据日历更新
- [ ] 今日关注/下周展望明确

### 发布前

- [ ] 检查格式和排版
- [ ] 标注数据来源
- [ ] 添加免责声明
- [ ] 验证无敏感信息泄露

---

## Quick Reference

| 简报类型 | 频率 | 主要内容 |
|---------|------|---------|
| Daily Brief | 每日 | 市场概览 + 宏观要闻 + 数据日历 |
| Weekly Review | 每周 | 周度回顾 + 下周展望 |
| Thematic Report | 按需 | 深度专题分析 |
