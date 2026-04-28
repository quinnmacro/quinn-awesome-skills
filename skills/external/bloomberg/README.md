# Bloomberg AI Prompt Templates

Bloomberg Terminal `{AKSB <GO>}` AI workflow prompts for financial analysis.

## 模板索引

| 名称 | 视角 | 用途 | 变量 |
|------|------|------|------|
| [Trends Analysis](company/trends-analysis/template.md) | Company | 股价+财务+运营趋势分析 | `{Company Name/Ticker}` |
| [Management & Governance](company/management-governance/template.md) | Company | 管理层+治理结构评估 | `{Company Name/Ticker}`, `N` |
| [Company Snapshot](company/company-snapshot/template.md) | Company | 投资论点支撑概览 | `{Company Name/Ticker}` |
| [Performance Tracker](company/performance-tracker/template.md) | Company | 季度财务绩效追踪 | `{Company Name/Ticker}`, `N` |
| [Sector Snapshot](sector/sector-snapshot/template.md) | Sector | 行业+同行对比分析 | `{Sector Name}`, `{Focus: Company Name/Ticker}` |
| [Breaking Event](event/breaking-event/template.md) | Event | 突发重大事件分析 | `{Company Name/Ticker}` |
| [Credit Strategy](market/credit-strategy/template.md) | Market | 信用市场早报 | `{Market to Analyze}` |

## 分类说明

```
bloomberg/
├── company/          # 公司视角：单公司深度分析
│   ├── trends-analysis/        # 股价+财务+运营趋势
│   ├── management-governance/  # 治理+管理层评估
│   ├── company-snapshot/       # 投资概览手册
│   └── performance-tracker/    # 季度财务追踪
├── sector/           # 行业视角：同行对比+定位
│   └── sector-snapshot/
├── event/            # 事件视角：突发事件快速评估
│   └── breaking-event/
└── market/           # 市场视角：宏观信用市场
    └── credit-strategy/
```

## 使用方法

### 1. 在 Bloomberg 终端使用

1. 打开 Bloomberg Terminal，输入 `{AKSB <GO>}` 进入 AI 助手
2. 选择对应模板
3. 替换 `{Variable}` 为实际值（如 `{Company Name/Ticker}` → `AAPL US Equity`）
4. 执行分析

### 2. 变量替换规则

| 变量 | 格式 | 示例 |
|------|------|------|
| `{Company Name/Ticker}` | Bloomberg Ticker | `AAPL US Equity`, `700 HK Equity` |
| `{Sector Name}` | 行业名称 | `Technology`, `Healthcare` |
| `{Market to Analyze}` | 市场类型 | `US IG`, `Asia HY`, `EM USD` |
| `{Region}` | 地区 | `US`, `Europe`, `Asia` |
| `N` | 周期数 | `4`, `8` |

### 3. 数据周期规则

| 规则 | 说明 |
|------|------|
| N+1 | 计算 YoY 需要额外 1 个周期数据 |
| N+5 | Performance Tracker 要求最严格 |
| < 366 days | 数据新鲜度优先级 |

## 模板来源

| 模板 | 来源 |
|------|------|
| Trends Analysis | Bloomberg Official |
| Management & Governance | Bloomberg Official |
| Company Snapshot | Bloomberg Official |
| Performance Tracker | Bloomberg Official |
| Sector Snapshot | Bloomberg Official |
| Breaking Event | Bloomberg Official |
| Credit Strategy | **Custom** (用户自写) |

## 与 Wind 的区分

| 维度 | Bloomberg | Wind |
|------|-----------|------|
| 市场 | 全球市场 | 中国市场为主 |
| 数据源 | Bloomberg Terminal | Wind Terminal |
| 指标体系 | 全球标准 | A股特色 |
| 适用场景 | 跨境投资、全球配置 | A股研究、国内债券 |

## 注意事项

- 模板需在 Bloomberg Terminal 内使用，依赖 Bloomberg 数据 API
- Credit Strategy 模板包含 70+ Bloomberg Index Tickers
- 部分模板有严格的 DAPI 字段限制（如 `INDEX_TOTAL_RETURN_MTD`）
- 过期数据（>180/366 days）应移至 Historical Data section
