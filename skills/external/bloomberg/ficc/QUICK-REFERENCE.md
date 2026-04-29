# FICC Quick Reference

> Bloomberg AI 快速查询参考卡

---

## 一、核心 Ticker 速查表

### 1.1 Government Yields (国债收益率)

| Country | 2Y | 5Y | 10Y | 30Y |
|---------|----|----|-----|-----|
| **US** | GT2 Govt | GT5 Govt | GT10 Govt | GT30 Govt |
| **Germany/EUR** | GTDEM2Y Govt | GTDEM5Y Govt | GTDEM10Y Govt | GTDEM30Y Govt |
| **Japan/JPY** | GJGB2 Index | GJGB5 Index | GJGB10 Index | GJGB30 Index |
| **UK/GBP** | GUKG2 Govt | GUKG5 Govt | GUKG10 Govt | GUKG30 Govt |
| **Australia/AUD** | GACGB2 Govt | GACGB5 Govt | GACGB10 Govt | - |
| **China/CN** | CGB2Y Govt | - | CGB10Y Govt | - |

### 1.2 Central Bank Policy Rates (央行政策利率)

| Central Bank | Policy Rate Ticker | Meeting Schedule |
|--------------|---------------------|------------------|
| **Fed (US)** | FDTR Index | 8 meetings/year |
| **ECB (EUR)** | ECBDFR Index | ~8 meetings/year |
| **BOJ (JPY)** | BOJPOLICY Index | ~8 meetings/year |
| **BOE (UK)** | UKBRBASE Index | 8 meetings/year |
| **RBA (AU)** | RBATCTR Index | ~11 meetings/year |
| **PBOC (CN)** | - | Quarterly |

### 1.3 Credit Indices (信用指数)

| Market | IG Index | HY Index | OAS Field |
|--------|----------|----------|-----------|
| **US USD** | LCGDTRUU Index | HLHO Index | `OAS` |
| **EUR** | LEGATRUU Index | HEHLO Index | `OAS` |
| **UK GBP** | LCUKTRUU Index | - | `OAS` |
| **Asia USD** | - | - | - |

### 1.4 FX Pairs (货币对)

| Pair | Spot Ticker | 3M Forward | 12M Forward |
|------|-------------|------------|--------------|
| EUR/USD | EURUSD Curncy | EURUSD3M Curncy | EURUSD12M Curncy |
| USD/JPY | USDJPY Curncy | USDJPY3M Curncy | USDJPY12M Curncy |
| GBP/USD | GBPUSD Curncy | GBPUSD3M Curncy | GBPUSD12M Curncy |
| AUD/USD | AUDUSD Curncy | AUDUSD3M Curncy | AUDUSD12M Curncy |
| USD/CNH | USDCNH Curncy | USDCNH3M Curncy | USDCNH12M Curncy |

### 1.5 Commodities (商品)

| Commodity | Front Month | M6 | M12 | Vol Index |
|-----------|-------------|----|-----|-----------|
| **WTI Crude** | CL1 Comdty | CL6 Comdty | CL12 Comdty | OVX Index |
| **Brent Crude** | CO1 Comdty | CO6 Comdty | CO12 Comdty | OVX Index |
| **Natural Gas** | NG1 Comdty | NG6 Comdty | NG12 Comdty | - |
| **RBOB Gasoline** | XB1 Comdty | XB6 Comdty | XB12 Comdty | - |
| **Heating Oil** | HO1 Comdty | HO6 Comdty | HO12 Comdty | - |

### 1.6 Volatility Indices (波动率)

| Asset | Vol Index | Interpretation |
|-------|-----------|----------------|
| **Equity** | VIX Index | S&P 500 implied vol |
| **Oil** | OVX Index | WTI options implied vol |
| **Gold** | GVZ Index | Gold options implied vol |
| **EUR/USD** | EURUSDV1M Curncy | 1M FX option vol |

---

## 二、常用 BQL 查询模板

### 2.1 Yield Curve with Changes
```
for(['GT10 Govt', 'GTDEM10Y Govt', 'GJGB10 Index'])
get(pct_chg(yield(dates=MTD)), pct_chg(yield(dates=YTD)), yield)
with(fill=PREV)
```

### 2.2 Credit Spreads Comparison
```
for(['LCGDTRUU Index', 'HLHO Index'])
get(OAS, CHG_NET_MTD, CHG_NET_YTD)
```

### 2.3 Commodity Futures Curve
```
for(['CL1 Comdty', 'CL2 Comdty', 'CL3 Comdty', 'CL6 Comdty', 'CL12 Comdty'])
get(PX_LAST)
```

### 2.4 FX Spot + Forward
```
for(['EURUSD Curncy', 'EURUSD3M Curncy', 'EURUSD12M Curncy'])
get(PX_LAST, CHG_PCT_MTD, CHG_PCT_YTD)
```

---

## 三、Mini-Prompts (快速分析)

### 3.1 快速收益率对比
```
GOAL: Compare 10Y yields for US, EUR, JPY with MTD/YTD changes.

OUTPUT FORMAT:
| Country | 10Y Yield (%) | MTD Chg (bp) | YTD Chg (bp) |
|---------|---------------|--------------|--------------|
| US | [value] | [value] | [value] |
| EUR | [value] | [value] | [value] |
| JPY | [value] | [value] | [value] |

SOURCE: Bloomberg DAPI via GT10 Govt, GTDEM10Y Govt, GJGB10 Index
```

### 3.2 快速信用利差检查
```
GOAL: Show current US IG and HY credit spreads with spread ratio.

OUTPUT:
- IG OAS: [value] bp
- HY OAS: [value] bp
- IG-HY Ratio: [ratio] (normal range 3-4x)
- MTD Change IG: [value] bp
- MTD Change HY: [value] bp

SOURCE: LCGDTRUU Index, HLHO Index via Bloomberg
```

### 3.3 快速曲线形态判断
```
GOAL: Determine curve shape for {Country} yield curve.

Check:
- M1 vs M2 spread (bp)
- Curve shape: Contango (M2>M1) or Backwardation (M1>M2)
- Interpretation: [supply tightness / storage economics]

SOURCE: {Commodity} futures via Bloomberg
```

### 3.4 快速 FX Carry 计算
```
GOAL: Calculate 12M carry for {FX Pair}.

Formula:
- Forward Points = (Spot - 12M Forward) × precision
- Annual Carry % = Forward Points / Spot × 100

OUTPUT:
- Spot: [value]
- 12M Forward: [value]
- Forward Points: [pips]
- Annual Carry: [%]

SOURCE: {Pair} Curncy, {Pair}12M Curncy
```

---

## 四、分析场景速查

| 你想分析什么 | 用哪个模板 | 变量示例 |
|--------------|------------|----------|
| 德国国债曲线 | sovereign-yields | `EUR` |
| EUR/USD 汇率 + carry | currency-cross | `EURUSD` |
| 美国信用市场 | spreads | `US` |
| WTI 期货曲线 + vol | energy-futures | `WTI` |
| Iran战争跨资产影响 | cross-asset | `Iran War Impact` |
| 快速10Y对比 | Mini-Prompt 3.1 | 无变量 |
| 快速IG-HY ratio | Mini-Prompt 3.2 | 无变量 |

---

## 五、数据时间规范

| 时间维度 | 字段/参数 | 说明 |
|----------|-----------|------|
| **实时** | `PX_LAST` | 最新价格 |
| **日度** | `PX_CLOSE_1D` | 昨日收盘 |
| **周度** | `CHG_NET_1W` | 周变化 |
| **月度** | `CHG_PCT_MTD` / `pct_chg(dates=MTD)` | 月变化 |
| **年度** | `CHG_PCT_YTD` / `pct_chg(dates=YTD)` | 年变化 |
| **历史** | BDH + date range | 指定时间段 |

---

## 六、常见错误排查

| 现象 | 可能原因 | 解决方案 |
|------|----------|----------|
| 显示 N/A | Ticker 错误或无数据 | 检查 Govt/Index/Comdty 后缀 |
| MTD/YTD 全 0 | 字段名错误 | 用 BQL pct_chg 替代 BDP CHG |
| 字段不返回 | DAPI 字段不存在 | 换同义字段如 `YLD_YTM_MID` → `yield` |
| 期权数据缺失 | 需要 VCUB 函数 | 查询 VOLATILITY_* 字段或用 VCUB |
| 曲线数据不完整 | futures 命名错误 | 检查 M1/M2/M6/M12 编号 |

---

## 七、Bloomberg 函数速查

### 7.1 数据查询函数

| 函数 | 用途 | 示例 |
|------|------|------|
| **BDP** | 单点数据查询 | `BDP("CL1 Comdty", "PX_LAST")` |
| **BDH** | 历史时间序列 | `BDH("GT10 Govt", "PX_LAST", "2026-01-01", "2026-04-28")` |
| **BQL** | 批量查询 + 计算 | `for(['GT10 Govt']) get(yield, pct_chg(yield(dates=MTD)))` |
| **BDHIST** | 多字段历史 | 同BDH，多字段同时查询 |

### 7.2 分析函数

| 函数 | 用途 | 备注 |
|------|------|------|
| **VCUB** | 期权波动率曲面 | FX, Commodity options |
| **ECO** | 经济数据查询 | 宏观指标 |
| **NEWS** | 新闻查询 | 搜索关键词 |
| **PIPE** | 新发行管道 | Credit new issues |
| **RATINGS** | 评级查询 | Rating actions |

### 7.3 导航函数

| 函数 | 用途 | 备注 |
|------|------|------|
| **YAS** | Yield Analysis | Bond analytics |
| **VCUB** | Volatility Cube | Option vol surface |
| **OV** | Option Valuation | Option pricing |
| **CV** | Curve Analysis | Yield curves |
| **GC** | Government Curve | Govt bond curves |

---

## 八、常见错误排查

| 现象 | 可能原因 | 解决方案 |
|------|----------|----------|
| 显示 N/A | Ticker 错误或无数据 | 检查 Govt/Index/Comdty 后缀 |
| MTD/YTD 全 0 | 字段名错误 | 用 BQL pct_chg 替代 BDP CHG |
| 字段不返回 | DAPI 字段不存在 | 换同义字段如 `YLD_YTM_MID` → `yield` |
| 期权数据缺失 | 需要 VCUB 函数 | 查询 VOLATILITY_* 字段或用 VCUB |
| 曲线数据不完整 | futures 命名错误 | 检查 M1/M2/M6/M12 编号 |
| BQL语法错误 | get/with搭配错误 | 检查语法：for() get() with() |
| 经济数据找不到 | 用ECO函数 | 用ECO而非BDP查宏观指标 |

---

## 九、数据源权威性

| 数据源 | 可靠性 | 适用场景 |
|--------|--------|----------|
| Bloomberg Real-time | ★★★★★ | 交易决策 |
| Bloomberg End-of-Day | ★★★★★ | 日终复盘 |
| EIA (via Bloomberg) | ★★★★★ | 能源库存 |
| Rating Agencies | ★★★★★ | 评级变更 |
| Central Bank Official | ★★★★★ | 政策利率 |
| IEA/OPEC (via Bloomberg) | ★★★★☆ | 需求/供给预测 |
| Analyst Estimates | ★★★☆☆ | 参考用 |

---

## 十、更新频率速查

| 数据 | 更新频率 | 最佳查询时间 |
|------|----------|--------------|
| Futures prices | 实时 | Trading hours |
| FX spot | 实时 | Trading hours |
| Bond yields | 日度 | EOD (~5pm local) |
| Credit spreads | 日度 | EOD (~5pm local) |
| EIA inventory | 周度 | Wed 10:30 EST |
| OPEC production | 月度 | End of month |
| Rating actions | 不定期 | Announcement |
| Economic data | 按日程 | Scheduled release |

---

**版本**: v0.4
**更新**: 2026-04-28
**新增**: 函数速查、数据源权威性、更新频率