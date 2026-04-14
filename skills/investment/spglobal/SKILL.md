---
name: spglobal
description: |
  S&P Global (Capital IQ) data integration for financial analysis.
  Generate tear sheets, funding digests, earnings previews with live data.
  "标普全球", "Capital IQ", "S&P", "公司简报", "融资摘要", "业绩预览".
version: 1.0.0
author: quinnmacro
requires:
  - Capital IQ Pro subscription or S&P Global LLM-ready API
mcp:
  server: https://kfinance.kensho.com/integrations/mcp
  provider: S&P Global
layer: domain. Triggers: "标普全球", "Capital IQ", "S&P", "公司简报", "融资摘要", "业绩预览".
---

# S&P Global - 标普全球数据集成

使用标普 Capital IQ 实时数据进行 AI 驱动的金融研究。


## 一、快速开始

### 1.1 何时使用

- TODO: 添加触发场景

### 1.2 核心步骤

1. TODO: 步骤1
2. TODO: 步骤2

### 1.3 成功标准

- [ ] TODO: 验证标准
## What is S&P Global?

标普全球（S&P Global）是全球领先的金融数据、分析和评级提供商。其旗下的 **Capital IQ** 平台是投资银行、股票研究、企业发展和销售团队的核心数据工具，提供：

| 数据类型 | 覆盖范围 |
|----------|----------|
| 公司财务数据 | 全球上市+私有公司 |
| 估值指标 | P/E, EV/EBITDA, P/B 等 |
| 交易记录 | M&A, IPO, 融资轮次 |
| 分析师预估 | 共识预测、目标价 |
| 行业数据 | 市场份额、行业趋势 |

## Why It Matters

传统的金融研究需要在多个数据终端之间切换、手动复制粘贴数据，效率低下且容易出错。

**S&P Global MCP 集成**让 Claude 直接访问 Capital IQ 数据：

| 传统方式 | MCP 集成 |
|----------|----------|
| 登录 Capital IQ 网页端 | 一条 `/command` 直接调用 |
| 手动搜索公司、复制数据 | 自动拉取实时数据 |
| 在 Excel/Word 中格式化 | 自动生成格式化报告 |
| 多个浏览器标签页 | 单一 AI 会话完成 |

## Skills Overview

| Skill | Description | Command | Output |
|-------|-------------|---------|--------|
| [Tear Sheet](skills/tear-sheet/SKILL.md) | 公司简报生成器 | `/tear-sheet` | Word 文档 |
| [Funding Digest](skills/funding-digest/SKILL.md) | 行业融资/并购摘要 | `/funding-digest` | PowerPoint |
| [Earnings Preview](skills/earnings-preview/SKILL.md) | 业绩预览报告 | `/earnings-preview` | 研究报告 |

## MCP Configuration

### Prerequisites

- [Capital IQ Pro](https://www.spglobal.com/market-intelligence/en/solutions/products/sp-capital-iq-pro) 订阅，或
- [Kensho LLM-ready API](https://docs.kensho.com/llmreadyapi/overview) 访问权限

### Step 1: 获取访问权限

发邮件到 **REDACTED@example.com**：

```
Subject: Request for Kensho LLM-ready API Access

I would like to request access to the Kensho LLM-ready API.
Purpose: AI-powered financial analysis workflows.
```

Kensho 会回复 Okta 凭据（用户名 + 密码）。

### Step 2: 选择认证方式

| 方式 | 用途 | 过期时间 | 推荐度 |
|------|------|----------|--------|
| **Browser Login** | 快速测试 | 会话期 | ⭐⭐ 开发测试 |
| **Refresh Token** | 开发环境 | 7 天 | ⭐⭐⭐ 短期使用 |
| **Public/Private Key** | 生产环境 | 永久 | ⭐⭐⭐⭐⭐ 生产环境 |

### Step 3: 获取 Refresh Token（推荐快速开始）

1. 访问 [LLM-ready API Manual Login](https://kfinance.kensho.com/manual_login/)
2. 用 Okta 凭据登录
3. 复制 Refresh Token

### Step 4: 配置环境变量

```bash
# 方式 1: 设置环境变量
export KENSHO_REFRESH_TOKEN="your_refresh_token_here"

# 方式 2: 添加到 .env 文件
echo "KENSHO_REFRESH_TOKEN=your_refresh_token_here" >> ~/.claude/skills/quinn-awesome-skills/.env
```

### Step 5: Claude Desktop 集成（最简单）

1. 打开 Claude Desktop
2. 点击聊天框 "Search and tools"
3. 点击 "Add connectors"
4. 选择 "S&P Global" connector
5. 用 Kensho Okta 凭据登录
6. 完成！

### 生产环境：Public/Private Key 认证

```bash
# 1. 生成密钥对
openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -outform PEM -pubout -out public.pem

# 2. 发送公钥到 REDACTED@example.com
# 邮件内容:
# - 附件: public.pem
# - 请求加入 users_kfinance 组

# 3. 收到 Client ID 后配置
export KENSHO_CLIENT_ID="your_client_id"
export KENSHO_PRIVATE_KEY_PATH="~/.keys/private.pem"
```

### Python 客户端使用

```python
from kfinance import Client

# 方式 1: Browser Login
client = Client()

# 方式 2: Refresh Token
client = Client(refresh_token="your_refresh_token")

# 方式 3: Key Pair
with open('private.pem', 'rb') as f:
    private_key = f.read()
client = Client(client_id="your_client_id", private_key=private_key)

# 获取 access token
access_token = client.access_token
```

## Example Usage

### Tear Sheet (公司简报)

```
/tear-sheet Palantir --audience equity-research
/tear-sheet 苹果 --audience ib-ma
/tear-sheet Tesla --audience sales-bd
```

**Audience Types:**
- `equity-research` - 股票研究分析师
- `ib-ma` - 投资银行/并购
- `corporate-development` - 企业发展
- `sales-bd` - 销售/业务拓展

### Funding Digest (融资摘要)

```
/funding-digest AI行业 --period weekly
/funding-digest "semiconductor" --period monthly
/funding-digest "data infrastructure" --region US
```

### Earnings Preview (业绩预览)

```
/earnings-preview AAPL 2024Q4
/earnings-preview Salesforce --quarter upcoming
/earnings-preview 微软 --consensus
```

## Data Available via MCP

### Company Data

| Data Point | Description |
|------------|-------------|
| Company Profile | 名称、行业、总部、员工数 |
| Financial Statements | 损益表、资产负债表、现金流 |
| Valuation Metrics | P/E, P/B, EV/EBITDA, P/S |
| Ownership | 机构持股、内部人士持股 |
| Competitors | 同行业可比公司 |

### Transaction Data

| Data Point | Description |
|------------|-------------|
| M&A Deals | 并购交易记录 |
| Funding Rounds | VC/PE 融资轮次 |
| IPO Data | 上市信息 |
| Valuations | 投前/投后估值 |

### Estimates Data

| Data Point | Description |
|------------|-------------|
| Consensus Estimates | 分析师一致预测 |
| Guidance | 公司指引 |
| Target Prices | 目标价 |
| Ratings | 买入/卖出评级 |

## Workflow Integration

### Investment Banking

```bash
# Pre-pitch company research
/tear-sheet [target] --audience ib-ma

# Comparable transactions
/funding-digest [industry] --deal-type m&a

# Management presentation prep
/earnings-preview [company] --focus guidance
```

### Equity Research

```bash
# Earnings season prep
/earnings-preview [ticker] --quarter upcoming

# Industry overview
/funding-digest [sector] --period quarterly

# Company tear sheet
/tear-sheet [company] --audience equity-research
```

### Private Equity

```bash
# Deal sourcing
/funding-digest [sector] --stage early

# Due diligence
/tear-sheet [target] --audience corporate-development

# Market analysis
/funding-digest [industry] --period monthly
```

## Best Practices

1. **数据验证**: MCP 返回的数据需与 Capital IQ 终端交叉验证
2. **时效性**: 实时数据可能有延迟，关键决策前确认更新时间
3. **覆盖范围**: 私有公司数据可能不完整，需标注数据缺口
4. **合规要求**: 数据使用需遵守 S&P Global 许可协议

## Common Errors

### Error: Authentication Failed

```
解决方案:
1. 确认 SPGLOBAL_API_KEY 环境变量已设置
2. 确认 API Key 未过期
3. 确认订阅包含所需数据类型
```

### Error: Company Not Found

```
解决方案:
1. 使用 Capital IQ 公司 ID (IQ ID)
2. 尝试股票代码 + 交易所 (如: AAPL-US)
3. 使用完整公司名称
```

### Error: Rate Limit Exceeded

```
解决方案:
1. 减少请求频率
2. 升级 API 配额
3. 使用缓存机制
```

## Related Skills

- [earnings-analyzer](../earnings-analyzer/) - 财报分析
- [investor-distiller](../investor-distiller/) - 投资大师智慧
- [macro-brief](../macro-brief/) - 宏观经济简报

---

## 检查清单

### 使用前

- [ ] 确认有 Capital IQ Pro 订阅或 Kensho LLM-ready API 访问权限
- [ ] 确认环境变量已配置（SPGLOBAL_API_KEY 或 Okta 凭据）
- [ ] 确认 MCP 服务器已配置（config.yaml）

### 数据查询

- [ ] 确认公司标识符正确（IQ ID / 股票代码 / 公司名称）
- [ ] 确认数据类型在订阅范围内
- [ ] 确认请求频率未超限

### 报告生成

- [ ] 确认模板已准备（tear-sheet / funding-digest / earnings-preview）
- [ ] 确认输出格式正确（Word / PowerPoint / Markdown）
- [ ] 确认数据完整性（标注数据缺口）

### 使用后

- [ ] 验证报告内容准确性
- [ ] 标注数据来源（S&P Global Capital IQ）
- [ ] 遵守合规要求（数据使用许可协议）

---

## Quick Reference

| 任务 | 命令 | 输出 |
|------|------|------|
| 生成公司简报 | `/tear-sheet <公司名>` | Word 文档 |
| 生成融资摘要 | `/funding-digest <行业>` | PowerPoint |
| 生成业绩预览 | `/earnings-preview <公司名>` | 研究报告 |

## References

- [S&P Global Capital IQ](https://www.spglobal.com/market-intelligence/en/solutions/products/sp-capital-iq-pro)
- [Finance Context S&P Plugin](https://financecontext.com/zh/partner-built/spglobal/overview)
- [MCP Protocol](https://modelcontextprotocol.io/)
