# FICC 交易员实战技巧

> 从交易员视角的实战技巧、坑点、和有趣的观察

---

## 一、FICC vs Equity 的思维差异

### 1.1 两个世界的根本区别

**Equity 交易员问**：
- "这公司值多少钱？"
- "盈利增长有多少？"
- "管理层靠谱吗？"

**FICC 交易员问**：
- "曲线形态说明什么？"
- "央行想干什么？"
- "流动性在哪？"

| 思维模式 | Equity | FICC |
|----------|--------|------|
| **定价** | 绝对价值 (DCF) | 相对价值 (利差) |
| **驱动** | 公司故事 | 宏观叙事 |
| **风险** | 公司风险 | 系统风险 |
| **时间** | 长期持有 | 短期博弈 |
| **Alpha** | 选股 | 曲线/利差/carry |
| **数据** | 季度财报 | 日频实时 |

### 1.2 FICC 交易员的一天

```
06:00 - 看overnight moves (亚洲时段发生了什么)
06:30 - Pre-Market Scan (早盘扫描)
07:00 - 检查bid-ask (流动性状态)
08:00 - 等欧洲开盘 (第一波交易机会)
09:30 - 美国开盘 (主战场)
10:00 - EIA数据? (每周三)
10:30 - 交易窗口 (最佳流动性时段)
12:00 - Lunch + 监控
14:00 - 下午行情 (欧洲收盘影响)
15:00 - Close Review准备
16:00 - 收盘复盘
17:00 - 检查overnight positioning
```

---

## 二、常见的坑（踩雷指南）

### 2.1 Carry Trade 的坑

| 坑 | 描述 | 教训 |
|----|------|------|
| **Carry不足以抵消spot** | AUD/USD案例：+2.31% carry, 但spot跌-3.1% | Carry是防守，不是进攻 |
| **Vol spike kills carry** | 低vol时carry好看，vol涨了break-even缩短 | Carry-to-vol ratio更重要 |
| **Risk-off funding currency strong** | AUD做长，risk-off时JPY暴涨 | Funding currency是反向指标 |
| **CB divergence flip** | RBA cut while Fed holds → carry消失 | 监控央行预期变化 |

**公式**:
```
Carry-at-risk = Annual Carry / Annual Vol
Break-even Days = (Break-even Move / Spot) / Daily Vol

Example:
Carry: 2.31%
Vol: 12% annual = 0.75% daily
Break-even Move: 2.31%
Break-even Days: 2.31% / 0.75% = 3.08 days

结论：只要3天spot逆向波动就能抹杀全年carry
```

### 2.2 Curve Trade 的坑

| 坑 | 描述 | 教训 |
|----|------|------|
| **过早入场** | Curve 46bp觉得flat，等signal再scale in | 等触发，不要猜 |
| **政策干预** | ECB/OPEC干预逆转curve | 监控政策风险 |
| **Bull vs Bear flattener** | 经济好flatten vs 经济差flatten | 区分驱动因素 |
| **Curve inversion ≠ recession** | Inversion只是信号，不是因果 | 看其他指标确认 |

**Curve形态解读**:

| 形态 | 含义 | 交易 |
|------|------|------|
| **Bull flattener** | 长端下行 > 前端 → risk-off | Long duration |
| **Bear flattener** | 前端上行 > 长端 → CB hawkish | Short front-end |
| **Bull steepener** | 前端下行 > 长端 → CB cutting | Long front-end |
| **Bear steepener** | 长端上行 > 前端 → fiscal/inflation | Short long-end |

### 2.3 Credit Trade 的坑

| 坑 | 描述 | 教训 |
|----|------|------|
| **IG-HY ratio distortion** | Ratio高不一定HY贵，看default cycle | Ratio需context |
| **Liquidity trap** | HY bid-ask宽，难exit | Size control |
| **Rating lag** | Rating downgrade滞后市场spread move | 盯市场而非agency |
| **New issue concession trap** | 新发spread看似便宜，二级更贵 | 等二级rebalance |

---

## 三、有趣的FICC观察

### 3.1 "Vol在哪里，钱就在哪里"

**观察**：
- OVX > 50：油 traders赚钱
- VIX > 30：期权traders赚钱
- IG-HY ratio > 5x：credit traders赚钱
- Curve inversion：rates traders赚钱

**规律**：极端volatility = 交易机会

### 3.2 "央行才是最大player"

**观察**：
- Fed一句话 > 所有公司财报
- ECB一个决定 > 欧洲所有债券
- BOJ一个干预 > 日元全年走势

**规律**：FICC本质是和央行博弈

### 3.3 "曲线是最诚实的指标"

**观察**：
- 2Y-10Y inversion → 经济6-12个月后衰退
- M1-M12 spread → oil供给紧张程度
- IG-HY ratio → risk appetite真实水平

**规律**：曲线不会骗人，数据会

### 3.4 "Carry是免费的午餐...until it's not"

**观察**：
- 正常时期：carry steady income
- Risk-off：carry瞬间消失 + spot反向
- 历史规律：carry策略平均2年一劫

**规律**：Carry有效，但要准备2%的年份亏损

---

## 四、实战技巧速查

### 4.1 快速判断技巧

| 快问 | 快答 | 判断 |
|------|------|------|
| VIX多少? | <20正常，>30压力，>40危机 | Risk regime |
| OVX多少? | <30正常，>50恐慌 | Oil情绪 |
| Curve斜率? | <50bp flat，>100bp steep | Curve regime |
| IG-HY ratio? | <3x HY便宜，>5x HY贵 | Credit value |
| OVX vs VIX? | OVX>VIX oil主导，反之equity主导 | Risk source |

### 4.2 数据日策略

**高impact数据日（CPI/NFP/GDP）**：

| 时机 | 策略 |
|------|------|
| 数据发布前1小时 | 减仓50%，等direction |
| 数据发布后5分钟 | 观察第一波reaction |
| 数据发布后30分钟 | 第二波才是真实direction |
| 数据发布后1小时 | 如果direction明确，入场 |

**黄金法则**：
- Don't guess the number
- Don't fade the first move
- Wait for second wave

### 4.3 央行会议日策略

| 时机 | 观察 | 策略 |
|------|------|------|
| 会议前24小时 | Positioning检查 | 看是否crowded |
| 会议前1小时 | Final pricing | 减仓等结果 |
| Statement发布 | 第一反应 | 观察不action |
| Press conference | 第二反应 | 看真正direction |
|会后1小时 | 如果direction明确 | 入场 |

**黄金法则**：
- Statement是面子，Press conference是里子
- Chair语气比数字更重要

---

## 五、有趣的数字

### 5.1 关键数字阈值

| 数字 | 阈值 | 意义 |
|------|------|------|
| **2** | CPI > 2% | 通胀警报 |
| **50** | ISM < 50 | 制造业收缩 |
| **0** | 2Y-10Y < 0 | Curve inversion |
| **3** | IG-HY ratio > 3x | Risk appetite |
| **100** | Oil > $100/bbl | 能源压力 |
| **20** | VIX > 20 | 市场压力 |
| **4** | Policy rate > 4% | High rate regime |

### 5.2 历史极端数字

| 极端 | 数值 | 年份 | 背景 |
|------|------|------|------|
| VIX peak | 82.69 | 2008 | GFC |
| OVX peak | 80+ | 2020 | COVID oil crash |
| Oil peak | $147 | 2008 | Pre-GFC |
| Oil trough | -$40 | 2020 | COVID storage crisis |
| US 10Y peak | 15.84% | 1981 | Volcker |
| US 10Y trough | 0.52% | 2020 | COVID QE |
| IG spread peak | 600bp+ | 2008 | GFC credit |
| EUR/USD trough | 0.82 | 2000 | Euro launch |

### 5.3 一年的典型数字

| 指标 | 正常年份波动范围 |
|------|------------------|
| US 10Y | ±50bp |
| EUR/USD | ±5% |
| IG spread | ±20bp |
| HY spread | ±50bp |
| WTI | ±20% |
| VIX | 12-30 |

---

## 六、交易员黑话翻译

| 黑话 | 翻译 | 含义 |
|------|------|------|
| **"Bid"** | 有人买 | 需求在，价格稳 |
| **"Offer"** | 有人卖 | 供给在，价格压 |
| **"Well bid"** | 很多买方 | 强需求，price up |
| **"Well offered"** | 很多卖方 | 强供给，price down |
| **"Whack"** | 大卖单砸盘 | Aggressive sell |
| **"Lift"** | 大买单拉升 | Aggressive buy |
| **"Fade"** | 反向操作 | 逆向交易 |
| **"Puke"** | 强制平仓 | Panic selling |
| **"Squeeze"** | 被迫平仓 | Position trap |
| **"Steepener"** | 买长卖短 | Curve交易 |
| **"Flattener"** | 买短卖长 | Curve交易 |
| **"Rich"** | 价格偏高 | 不便宜 |
| **"Cheap"** | 价格偏低 | 可以买 |
| **"Cleared"** | 全部成交 | Liquidity好 |
| **"Tight"** | Bid-ask小 | Liquidity好 |
| **"Wide"** | Bid-ask大 | Liquidity差 |
| **"Axed"** | 必须买卖 | Aggressive need |

---

## 七、实用公式

### 7.1 Carry公式

```
Annual Carry = (Forward Points / Spot) × 100%

Forward Points = Spot - Forward

Example (EUR/USD):
Spot = 1.10
12M Forward = 1.08
Forward Points = 1.10 - 1.08 = 0.02 = 200 pips
Annual Carry = 200 / 11000 × 100% = 1.82%
```

### 7.2 Vol公式

```
Daily Vol ≈ Annual Vol / 16

Example:
Annual Vol = 12%
Daily Vol ≈ 12% / 16 = 0.75%

Carry-to-Vol Ratio = Annual Carry / Annual Vol

Example:
Carry = 2.31%
Vol = 12%
Ratio = 2.31% / 12% = 0.19

Interpretation: Ratio > 0.5 = good, < 0.2 = poor
```

### 7.3 Break-even公式

```
Break-even Move = Annual Carry (as % of spot)

Break-even Days = Break-even Move / Daily Vol

Example:
Carry = 2.31%
Daily Vol = 0.75%
Break-even Days = 2.31% / 0.75% = 3.08 days

结论：只要spot逆向波动超过3天，carry就没了
```

### 7.4 DV01公式

```
DV01 = Dollar Value of 01bp

Example:
$10mm 10Y Treasury position
DV01 ≈ $10,000 per 1bp move

If 10Y moves 50bp:
P&L = $10,000 × 50 = $500,000
```

### 7.5 Curve公式

```
Curve Slope = Long-end Yield - Short-end Yield

Steepener P&L = (Slope Change) × DV01 differential

Example:
2Y-10Y Steepener position
Entry slope: 50bp
Exit slope: 70bp
Slope change: +20bp
If equal DV01: P&L = 20bp × position DV01
```

---

## 八、常见错误心态

### 8.1 不要犯的错误

| 错误心态 | 正确心态 |
|----------|----------|
| "这次不一样" | 这次和上次一样，看历史 |
| "央行不会犯错" | 央行经常犯错，盯市场而非声明 |
| "曲线不会骗人" | 曲线不会骗，但时间不确定 |
| "carry很安全" | Carry有效但不安全，看vol |
| "spread会收敛" | Spread可能发散，设stop |

### 8.2 正确的交易习惯

| 习惯 | 描述 |
|------|------|
| **每日复盘** | Close Review必做 |
| **数据日减仓** | 等direction而非猜数字 |
| **央行日观望** | 看reaction而非预判 |
| **设定stop** | 不要移动stop |
| **监控流动性** | Bid-ask比price更重要 |
| **看vol而非只看price** | Vol regime决定策略 |

---

## 九、FICC 交易员技能树

```
Level 1: 基础
├── 知道关键ticker (GT10, CL1, EURUSD...)
├── 理解bid-ask含义
├── 能看曲线形态
└── 知道央行政策利率

Level 2: 进阶
├── 理解curve trades (steepener/flattener)
├── 理解carry trades
├── 能算DV01/CS01
└── 能看vol regime

Level 3: 高级
├── 能做相对价值分析
├── 理解央行博弈
├── 能识别政策mistake
└── 能做压力测试

Level 4: 专家
├── 能预测curve形态变化
├── 能识别黑天鹅前兆
├── 能做跨资产联动分析
└── 能设计complex position

Level 5: 大师
├── 能识别市场结构性变化
├── 能预判政策框架转变
├── 能管理尾部风险组合
└── 能教Level 1-4
```

---

## 十、有趣的事实

### 10.1 FICC市场规模

| 市场 | 日均交易量 | 对比 |
|------|------------|------|
| FX | $7.5 trillion | > Equity × 10 |
| Rates | $500+ billion | 巨大 |
| Credit | $50+ billion | 相对小但重要 |
| Commodities | $300+ billion | 中等 |

### 10.2 FICC vs Equity体量

| 维度 | FICC | Equity |
|------|------|--------|
| 日交易量 | 巨大 (FX $7.5T) | 小 (US equity ~$200B) |
| 参与者 | 机构主导 | 机构+散户 |
| 信息来源 | 宏观+央行 | 公司财报 |
| 波动性 | 相对稳定 | 更volatile |
| Alpha来源 | Curve/Spread/Carry | 选股 |

### 10.3 历史有趣事件

| 年份 | 事件 | 教训 |
|------|------|------|
| 1998 | LTCM collapse | Curve trade可以kill |
| 2008 | GFC | Liquidity危机最可怕 |
| 2013 | Taper tantrum | CB communication很重要 |
| 2016 | Brexit | Tail risk真实存在 |
| 2020 | COVID oil negative | Storage arbitrage崩塌 |
| 2022 | Fed超鹰派 | Policy mistake交易机会 |

---

**版本**: v0.1
**状态**: Active
**目标**: 帮助理解FICC交易员思维