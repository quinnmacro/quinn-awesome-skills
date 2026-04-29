# FICC 实战案例集

> 真实测试记录 + 虚构场景案例

---

## 一、已测试案例（真实记录）

### 1.1 Sovereign Yields - EUR Analysis

**日期**: 2026-04-28
**输入**: `{Country/Currency} = EUR`

**输出评估**:

| 维度 | 评分 | 状态 |
|------|------|------|
| 数据完整性 | 4/5 | MTD/YTD ✓, EUR-JPY spread N/A |
| 结构清晰度 | 5/5 | 5 sections清晰 |
| 分析深度 | 5/5 | ECB政策定价详尽 |
| 可操作性 | 4/5 | 有交易建议但需量化 |
| 引用规范 | 5/5 | Sources完整 |

**关键输出片段**:

```
EUR Yield Curve Snapshot:
2Y:  2.59%  | MTD: -0.3bp  | YTD: +47bp
10Y: 3.05%  | MTD: +6.7bp  | YTD: +20bp
30Y: 3.58%  | MTD: +12.2bp | YTD: +10bp

Curve Dynamics: Bear steepening
2Y-10Y Spread: 46bp (steepening)
5Y-30Y Spread: 84bp (long-end selling off)

Policy Pricing:
ECB Current: 2.15%
Market Implied 1Y: 2.44%
Rate Expectation: +29bp hikes priced
April 30 Hold Probability: ~97%

Cross-Country:
EUR-US 10Y: -131bp (widened 25bp YTD)

FX Linkage:
EUR/USD: 1.1687 (+1.16% MTD despite negative carry)
→ Correlation breakdown detected
```

**洞察**:
1. EUR曲线bear steepening，长端抛售（财政担忧）
2. ECB定价偏离：市场expect 29bp但official偏鸽
3. EUR/USD与carry背离：非rate driver主导（安全港flow）
4. **交易信号**: 曲线steepener有空间，FX carry失效

---

### 1.2 Energy Futures - WTI Analysis

**日期**: 2026-04-28
**输入**: `{Commodity} = WTI`

**输出评估**:

| 维度 | 评分 | 状态 |
|------|------|------|
| 数据完整性 | 5/5 | 全部数据完整 |
| 结构清晰度 | 5/5 | 曲线+时间spread+库存 |
| 分析深度 | 5/5 | Hormuz危机深度分析 |
| 可操作性 | 5/5 | 有roll yield计算 |
| 引用规范 | 5/5 | Sources丰富 |

**关键输出片段**:

```
Curve Structure:
M1: $99.67/bbl
M2: $94.38/bbl (-$5.29) → Backwardation
M12: $75.23/bbl (-$24.44) → Extreme backwardation

Time Spreads:
M1-M2: $5.29/bbl (front tightness)
M1-M12: $24.44/bbl (supply recovery priced)

Inventory:
U.S. Commercial: 465.7mm bbls (+5.11% Y/Y)
Global drawdown: 4.8mm bpd (85mm bbls in 1 month)

Supply Shock:
Hormuz: 14.2mm bpd offline
From 2.3mm bpd surplus → 10mm bpd deficit

Demand Destruction:
IEA: -80kbpd 2026 forecast (first decline since COVID)
Q2: -1.5mm bpd expected

Roll Yield:
Positive roll: $5.29/bbl/month for longs
→ Backwardation benefits long positions
```

**洞察**:
1. 极端backwardation：$24.44/bbl M1-M12
2. 历史性供给冲击：从surplus→deficit翻转
3. 正roll yield：做多有利（$5.29/月）
4. **交易信号**: Long front month受益roll + backwardation

**后续优化**: 添加OVX波动率分析

---

## 二、虚构实战案例（逼真场景）

### 2.1 案例：Fed鹰派惊喜 - 2026-05-15

**场景**: Fed意外加息50bp，市场定价仅+25bp

**输入**: `{Central Bank} = Fed` → Rate Decision Reaction

**虚构输出**:

```
Decision Summary:
Rate Change: +50bp (vs expected +25bp)
Statement Tone: Hawkish (vs expected neutral)
Forward Guidance: "Further tightening may be warranted"

Immediate Market Reaction (within 30 min):

| Asset | Pre | Post | Move | Speed |
|-------|-----|------|------|-------|
| USD 2Y | 4.25% | 4.45% | +20bp | 5 min |
| USD 10Y | 4.36% | 4.52% | +16bp | 10 min |
| EUR/USD | 1.1687 | 1.1420 | -2.27% | 2 min |
| US IG OAS | 98bp | 105bp | +7bp | 15 min |
| VIX | 18 | 24 | +6pts | 1 min |

Implication Analysis:

1. Policy Path Repricing:
   - Before: Terminal 4.50%
   - After: Terminal 4.75-5.00%
   - +50bp additional hikes now priced

2. Curve Impact:
   - Front-end +20bp vs Long-end +16bp
   - Bear flattening triggered
   - 2Y-10Y compressing from +11bp to +7bp

3. Cross-Asset Transmission:
   - USD surge: +2.27% vs EUR
   - Risk-off: IG spreads widening, VIX spike
   - Gold: -3% on stronger USD

Trading Implications:
- Duration: Bearish for bonds, flatteners favored
- FX: Long USD, short EUR/JPY
- Credit: Defensive, favor IG over HY
- Curve: 2Y-10Y flattener entry
```

**事后分析（虚构）**:

| 时间 | 曲线变化 | FX变化 | Credit变化 |
|------|----------|--------|------------|
| +1H | 2Y-10Y: 11bp→7bp | EUR/USD: -2.5% | IG +5bp |
| +4H | 2Y-10Y: 7bp→5bp | EUR/USD: -3.0% | IG +8bp |
| +1D | 2Y-10Y: 5bp→3bp | EUR/USD: -3.5% | IG +12bp |

**交易复盘**:
- Flattener入场7bp → 目标3bp → 实现4bp ✓
- USD/JPY做多 → 收益+150pips ✓
- IG short HY → IG widens 12bp, HY widens 25bp → ratio improves ✓

---

### 2.2 案例：OPEC+意外增产 - 2026-06-01

**场景**: Saudi宣布增产2mm bpd，市场expect增产1mm

**输入**: `{Event} = OPEC Surprise Production Increase` → Geopolitical Shock

**虚构输出**:

```
Event Summary:
Saudi Announcement: +2mm bpd (vs expected +1mm bpd)
Timing: Surprise, no prior signaling
Reason: Offset Hormuz losses + price stabilization

Immediate Reaction:

| Asset | Pre | Post | Move | Speed |
|-------|-----|------|------|-------|
| WTI M1 | $99.67 | $85.50 | -14.2% | 30 sec |
| Brent M1 | $103.50 | $88.20 | -14.7% | 30 sec |
| OVX | 52 | 38 | -14pts | 5 min |
| Energy Credit | 125bp | 145bp | +20bp | 10 min |
| USD/CAD | 1.38 | 1.42 | +2.9% | 5 min |

Curve Shift:

| Spread | Pre-event | Post-event | Change |
|--------|-----------|------------|--------|
| M1-M2 | $5.29 | $2.10 | -$3.19 (backwardation easing) |
| M1-M12 | $24.44 | $12.50 | -$11.94 (curve normalizing) |

Supply Impact:
- Before: 10mm bpd deficit
- After: 8mm bpd deficit (assuming full ramp)
- Timeline: 2-3 months to reach full capacity

Demand Equation:
- Price drop -14% → stimulates demand
- Lower price may offset some demand destruction
- Net effect: deficit narrows but persists

Trading Implications:

Short-term (1-2 weeks):
- WTI: Sell front month, backwardation easing
- Curve: Short M1-M2 spread (backwardation collapsing)
- Vol: Short OVX, vol crushing

Medium-term (1-3 months):
- Wait for curve to stabilize at new level
- Monitor Saudi production ramp progress
- Assess Hormuz recovery timeline

Position Recommendations:
- Short WTI M1: Entry $99.67 → Target $85-90
- Short M1-M2 spread: Entry $5.29 → Target $2.00
- Short OVX: Entry 52 → Target 35
```

**事后分析（虚构）**:

| Day | WTI M1 | M1-M2 | OVX |
|-----|--------|-------|-----|
| D0 | $99.67 | $5.29 | 52 |
| D+1 | $88.20 | $3.50 | 40 |
| D+3 | $86.50 | $2.20 | 35 |
| D+7 | $85.00 | $1.80 | 32 |

**交易复盘**:
- Short WTI: 入场$99.67 → 出场$86.50 → 收益$13.17/bbl ✓
- Short M1-M2: 入场$5.29 → 出场$2.20 → 收益$3.09/bbl ✓
- Short OVX: 入场52 → 出场35 → vol收益-17pts ✓

---

### 2.3 案例：中国信用危机蔓延 - 2026-07-15

**场景**: 中国某大型地产商违约，引发亚洲信用市场恐慌

**输入**: `{Event} = China Property Default Cascade` → Geopolitical Shock

**虚构输出**:

```
Event Summary:
Company: [Major Chinese Property Developer]
Default: $5bn bond missed payment
Trigger: 6-month liquidity crunch, sales collapse
Spillover: Asian USD credit, EM FX

Immediate Reaction:

| Asset | Pre | Post | Move |
|-------|-----|------|------|
| China HY | 450bp | 680bp | +230bp |
| Asia USD IG | 120bp | 150bp | +30bp |
| USDCNH | 7.25 | 7.42 | +2.3% |
| AUD/USD | 0.68 | 0.65 | -4.4% |
| Iron Ore | $110 | $95 | -13.6% |

Cross-Asset Transmission Chain:

China Property Default
→ China HY spreads +230bp (direct)
→ Asia IG spreads +30bp (contagion)
→ USDCNH +2.3% (capital flight)
→ AUD/USD -4.4% (China demand proxy)
→ Iron Ore -13.6% (construction demand)
→ Australian Credit +25bp (resource-linked)

Contagion Risk Assessment:

| Region | Exposure | Vulnerability |
|--------|----------|---------------|
| HK | High (property ties) | Credit widening risk |
| Singapore | Medium (ASEAN hub) | Indirect via HK |
| Australia | High (iron ore export) | Commodity + FX risk |
| EM Asia | Medium (USD debt) | Funding stress risk |

Flight-to-Quality:

| Safe Asset | Move | Interpretation |
|------------|------|----------------|
| US Treasuries | -5bp | Bid for safety |
| German Bunds | -3bp | Euro safety |
| Gold | +2% | Safe-haven bid |
| JPY | +1.5% vs USD | Funding currency strength |

Trading Implications:

Risk-Off Positioning:
- Short Asia HY, Long US IG (quality trade)
- Short AUD, Long USD (China-proxy trade)
- Long Gold, Long JPY (safe-haven)
- Short Iron Ore (demand destruction)

Duration Consideration:
- Credit stress may persist 3-6 months
- Monitor Chinese policy response
- Track contagion to other EM regions

Position Recommendations:
- Short China HY: Entry 450bp → Target 600bp
- Short AUD/USD: Entry 0.68 → Target 0.63
- Long US IG: Entry 98bp → Target 90bp (tightening)
- Long Gold: Entry $2000 → Target $2100
```

**事后分析（虚构）**:

| Week | China HY | Asia IG | USDCNH | AUD |
|------|----------|---------|--------|-----|
| W0 | 450bp | 120bp | 7.25 | 0.68 |
| W+1 | 600bp | 140bp | 7.35 | 0.64 |
| W+2 | 650bp | 145bp | 7.40 | 0.62 |
| W+4 | 580bp | 135bp | 7.38 | 0.65 |

**政策干预**: 中国央行降息50bp + 流动性注入 → W4开始修复

---

## 三、相对价值案例

### 3.1 案例：曲线Steepener - EUR 2Y-10Y

**场景**: EUR curve过度flat，预期steepening

**输入**: `{Country} = EUR` → Curve Trade Setup

**虚构输出**:

```
Current Curve Shape:
2Y-10Y Spread: 46bp
Historical Avg: 85bp (5Y average)
Current vs Avg: -39bp (flat vs history)
Z-Score: -1.8 (significantly flat)

Relative Position:
| Spread | Current | 1M Ago | 1Y Ago | 5Y Avg |
|--------|---------|--------|--------|--------|
| 2Y-10Y | 46bp | 38bp | 110bp | 85bp |
| 5Y-30Y | 84bp | 70bp | 95bp | 60bp |

Trade Recommendation:
Position: Steepener (long 10Y, short 2Y)
Entry Level: 46bp
Target: 70bp (reversion toward avg)
Stop: 35bp (further flattening)
Conviction: Medium (2/5)

Rationale:
1. Policy divergence: ECB may hike while Fed holds
2. Fiscal concerns: Germany debt brake debate steepening long-end
3. Term premium: Inflation risk adding to 10Y+

Risk Factors:
- ECB stays dovish longer: front-end anchored, flatten
- Growth shock: risk-off flattening
- Data surprises: inflation softening flattens

Entry Timing:
- Now: 46bp, at 1.8 SD below mean
- Wait for trigger: ECB hawkish signal / fiscal news
- Scale: 50% position, add on confirmation
```

**交易执行**（虚构）:

| Week | 2Y-10Y | Position | Action |
|------|---------|----------|--------|
| W0 | 46bp | Initiate 50% | Entry steepener |
| W+2 | 52bp | Add 25% | ECB hints hawkish |
| W+4 | 60bp | Add 25% | Fiscal debate escalates |
| W+6 | 70bp | Close | Target reached |

**收益**: 
- Entry 46bp → Exit 70bp = +24bp
- DV01 $1mm position ≈ $240k profit

---

### 3.2 案例：FX Carry Trade - AUD/USD

**场景**: AUD高息，USD低息，评估carry吸引力

**输入**: `{Currency Pair} = AUDUSD` → FX Carry Trade

**虚构输出**:

```
Carry Calculation:
Spot: 0.6500
12M Forward: 0.6350
Forward Points: +150 pips (AUD below forward)
Annual Carry: +2.31% (150/6500)

Rate Differential:
AUD Policy: 4.35% (RBA)
USD Policy: 3.75% (Fed)
Rate Diff: +60bp (AUD advantage)

Risk-Adjusted Carry:
3M Realized Vol: 12%
Carry-to-Vol Ratio: 0.19 (medium)
Break-even Spot Move: -2.31% (how much AUD can fall)

Volatility Assessment:
3M Implied Vol: 14%
Vol Risk Premium: +2% (implied > realized)
25D Risk Reversal: +0.5% (AUD calls bid)

Trade Recommendation:
Direction: Long AUD (carry + risk reversal support)
Entry: 0.6500
Carry: +2.31% annual
Break-even: 0.6350 (12M forward)
Conviction: Medium (carry attractive, vol moderate)

Risk Factors:
- RBA cut: reduces carry advantage
- China slowdown: AUD demand proxy
- Risk-off: AUD funding currency stress
- Fed hike: USD strength

Hedging:
- Buy AUD puts at 0.6200 (stop protection)
- Cost: ~0.5% premium
- Net carry: 2.31% - 0.5% = 1.81%
```

**交易执行**（虚构）:

| Month | AUD/USD | Carry Earned | Cumulative |
|-------|---------|--------------|------------|
| M0 | 0.6500 | - | Initiate |
| M1 | 0.6450 | +0.19% | +0.19% |
| M2 | 0.6400 | +0.19% | +0.38% |
| M3 | 0.6380 | +0.19% | +0.57% |
| M6 | 0.6350 | +0.19% | +1.15% |
| M12 | 0.6300 | +0.19% | +2.31% |

**结果**: 
- Carry收益 +2.31%
- Spot损失 -3.1% (0.65 → 0.63)
- 净损失 -0.8% (carry不足以抵消spot下跌)
- **教训**: Carry trade需警惕spot direction风险

---

## 四、案例总结

### 4.1 成功案例特征

| 成功要素 | 描述 |
|----------|------|
| 数据完整 | 无N/A，MTD/YTD可用 |
| 结构清晰 | 5 sections，逻辑流畅 |
| 深度分析 | 超表面洞察，传导链 |
| 可操作 | 具体entry/target/stop |
| 引用规范 | Sources完整可追溯 |

### 4.2 失败案例教训

| 问题 | 案例 | 教训 |
|------|------|------|
| Carry不足以抵消spot | AUD/USD | Carry trade需看vol和direction |
| 过早入场 | Curve trade | 等触发信号再scale in |
| 单一因素 | Oil supply shock | 需看demand response |
| 忽略政策干预 | China credit crisis | 监管干预可能逆转 |

### 4.3 案例库索引

| 案例编号 | 类型 | 日期 | 状态 |
|----------|------|------|------|
| C001 | Sovereign Yields | 2026-04-28 | ✓ 已测试 |
| C002 | Energy Futures | 2026-04-28 | ✓ 已测试 |
| C003 | Fed Hawkish Surprise | 2026-05-15 | 虚构案例 |
| C004 | OPEC Surprise | 2026-06-01 | 虚构案例 |
| C005 | China Credit Crisis | 2026-07-15 | 虚构案例 |
| C006 | EUR Curve Steepener | - | 虚构案例 |
| C007 | AUD/USD Carry | - | 虚构案例 |

---

**版本**: v0.1
**状态**: Active
**下一步**: 测试更多模板，添加真实案例