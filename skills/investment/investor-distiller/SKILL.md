---
name: investor-distiller
description: |
  Extract and distill investment wisdom from legendary investors into actionable frameworks.
  Analyze investment philosophies, decision patterns, and mental models of masters like
  Buffett, Munger, Dalio, Soros, Druckenmiller, etc. "投资大师蒸馏".
version: 1.0.0
author: quinnmacro
layer: domain. Triggers: "投资大师蒸馏", "蒸馏巴菲特", "分析芒格的投资哲学", "瑞·达利欧的投资原则", "索罗斯的反身性理论", "投资大师方法论", "distill investor wisdom", "extract investment framework".
---

# Investor Distiller - 投资大师蒸馏器

将投资大师的投资哲学、方法论蒸馏为可执行的分析框架。


## 一、快速开始

### 1.1 何时使用

- TODO: 添加触发场景

### 1.2 核心步骤

1. TODO: 步骤1
2. TODO: 步骤2

### 1.3 成功标准

- [ ] TODO: 验证标准
## Trigger Phrases

- "蒸馏巴菲特"
- "分析芒格的投资哲学"
- "瑞·达利欧的投资原则"
- "索罗斯的反身性理论"
- "投资大师方法论"
- "distill investor wisdom"
- "extract investment framework"

## Supported Investors 支持的投资大师

### Value Investing 价值投资

| Master | Key Concepts | Famous Works |
|--------|--------------|--------------|
| Warren Buffett | 护城河、安全边际、能力圈 | Berkshire Letters |
| Charlie Munger | 多元思维模型、lollapalooza | Poor Charlie's Almanack |
| Benjamin Graham | 安全边际、市场先生 | The Intelligent Investor |
| Phil Fisher | 成长股投资、闲聊法 | Common Stocks and Uncommon Profits |

### Macro & Hedge Fund 宏观与对冲基金

| Master | Key Concepts | Famous Works |
|--------|--------------|--------------|
| Ray Dalio | 原则、债务周期、全天候策略 | Principles, Debt Crisis |
| George Soros | 反身性、趋势反转点 | Alchemy of Finance |
| Stanley Druckenmiller | 趋势跟随、风险控制 | - |
| Paul Tudor Jones | 宏观交易、风险管理 | - |

### Growth & Tech 成长与科技

| Master | Key Concepts | Famous Works |
|--------|--------------|--------------|
| Peter Lynch | 十倍股、投资你所了解 | One Up on Wall Street |
| Bill Ackman | 激进投资、价值激活 | Pershing Square Letters |
| Cathie Wood | 创新颠覆、技术趋势 | ARK Invest Research |

## Distillation Framework 蒸馏框架

### Step 1: Philosophy Extraction 哲学提炼

```
Extract core investment philosophy:
1. 核心理念 (1-2 sentences)
2. 投资目标 (return profile, time horizon)
3. 风险观 (risk definition, risk management)
4. 市场观 (market efficiency, behavioral aspects)
```

### Step 2: Framework Generation 框架生成

```
Generate actionable framework:
1. 投资清单 (checklist for buy/sell decisions)
2. 分析框架 (analysis template)
3. 决策流程 (decision process flowchart)
4. 风控原则 (risk management rules)
```

### Step 3: Practical Application 实践应用

```
Apply to specific investment:
1. 案例分析 (case study template)
2. 适用性评估 (applicability assessment)
3. 调整建议 (customization suggestions)
```

## Output Format 输出格式

```markdown
# [投资大师名称] 投资框架蒸馏

## 核心理念
[1-2 段核心投资哲学]

## 投资框架

### 选股标准
| 维度 | 标准 | 权重 |
|------|------|------|
| ... | ... | ... |

### 决策清单
- [ ] Checklist item 1
- [ ] Checklist item 2

### 风控原则
1. 原则一
2. 原则二

## 经典语录
> "Quote 1"
> "Quote 2"

## 适用场景
- 适用: [场景描述]
- 不适用: [场景描述]

## 参考来源
- [著作/演讲]
```

## Usage

```bash
# Distill Buffett's investment framework
bash scripts/llm.sh "蒸馏巴菲特的投资方法论，生成选股清单和分析框架" --system "你是一位专业的投资研究分析师"

# Analyze specific investor's approach to a sector
bash scripts/llm.sh "用芒格的思维模型分析科技股投资" --json

# Compare multiple investors
bash scripts/llm.sh "比较巴菲特和达利欧对风险的理解差异"
```

## Example Output

### 巴菲特投资框架蒸馏

```markdown
# Warren Buffett 投资框架蒸馏

## 核心理念

以合理价格买入优秀公司，长期持有。核心是"护城河"概念——
企业抵御竞争的可持续竞争优势。投资决策基于对企业内在价值的评估，
而非市场情绪或短期波动。

## 投资框架

### 选股标准

| 维度 | 标准 | 权重 |
|------|------|------|
| 护城河 | 品牌溢价/成本优势/网络效应/转换成本 | 30% |
| 管理层 | 诚信、能力、股东导向 | 25% |
| 财务 | 高ROE、稳定现金流、低负债 | 25% |
| 估值 | 安全边际 > 25% | 20% |

### 决策清单

- [ ] 是否在能力圈范围内？
- [ ] 商业模式是否可理解？
- [ ] 护城河是否可持续？
- [ ] 管理层是否值得信任？
- [ ] 价格是否有安全边际？
- [ ] 如果股市关闭10年，是否愿意持有？

### 风控原则

1. 永不亏损 (Rule #1: Never lose money)
2. 不懂不投 (Stay within circle of competence)
3. 安全边际 (Margin of safety > 25%)
4. 集中持仓 (6-10 positions max)

## 经典语录

> "Rule No. 1: Never lose money. Rule No. 2: Never forget rule No. 1."
> "Price is what you pay. Value is what you get."
> "It's far better to buy a wonderful company at a fair price than a fair company at a wonderful price."

## 适用场景

- 适用: 消费、金融、公用事业等成熟行业
- 不适用: 早期科技、高增长但未盈利公司
```

## Advanced Features

### Multi-Manager Synthesis 多管理人综合

Combine insights from multiple investors:

```bash
# Synthesize investment framework from multiple value investors
bash scripts/llm.sh "综合巴菲特、芒格、格林厄姆的价值投资框架，生成统一的分析清单"
```

### Contrarian Analysis 逆向分析

Understand when a master's approach might not work:

```bash
# Analyze limitations
bash scripts/llm.sh "分析巴菲特投资框架在2020年美股熔断期间的表现和局限性"
```

### Real-Time Application 实时应用

Apply distilled framework to current market:

```bash
# Apply framework to specific stock
bash scripts/llm.sh "用巴菲特的护城河框架分析苹果公司"
```

## Notes

- 蒸馏结果仅供参考，不构成投资建议
- 投资大师的方法论需结合市场环境调整
- 过去表现不代表未来收益

---

## 检查清单

### 选择投资大师

- [ ] 确认投资大师有长期可验证业绩
- [ ] 确认有充分的投资著作/访谈/信函
- [ ] 确认方法论可系统化提炼
- [ ] 选择合适的大师（与投资风格匹配）

### 框架蒸馏

- [ ] 阅读主要著作和访谈
- [ ] 提取核心投资原则
- [ ] 识别关键决策框架
- [ ] 总结风险控制方法

### 验证与应用

- [ ] 用历史案例验证框架有效性
- [ ] 标注框架适用范围
- [ ] 识别局限性
- [ ] 实时应用测试

### 输出文档

- [ ] 投资原则清晰
- [ ] 决策框架可操作
- [ ] 案例分析完整
- [ ] 风险提示明确

---

## Quick Reference

| 投资大师 | 核心框架 | 代表著作 |
|---------|---------|---------|
| Warren Buffett | 护城河、价值投资 | 《巴菲特致股东信》 |
| Peter Lynch | 成长投资、十倍股 | 《彼得·林奇的成功投资》 |
| Ray Dalio | 全天候策略、债务周期 | 《原则》 |
| Howard Marks | 周期投资、风险控制 | 《投资最重要的事》 |
