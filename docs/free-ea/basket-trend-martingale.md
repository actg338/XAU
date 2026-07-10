# XAU_BasketTrendMartingale_EA.ex5 使用说明

## 功能
XAU 篮子净值跟踪趋势马丁 EA，基于已收盘 K 线识别趋势。上涨趋势只做多方向马丁，下跌趋势只做空方向马丁，反向残留仓不继续加仓，由篮子净浮盈跟踪止盈、单方向独立跟踪回撤止盈和风险保护处理。

## 品牌信息
- 编译人：微信：thRO03
- 官网：https://03xau.com

## 关键参数
- `InpEnableBasketTrailing`：启用本 EA 篮子净浮盈跟踪止盈。
- `InpEnableDirectionalTrailing`：启用多空方向独立跟踪回撤止盈。
- `InpBaseLot`、`InpLotMultiplier`、`InpMaxTotalLots`：首单手数、加仓倍率和总手数上限。
- `InpAddBaseAtrMultiplier`：ATR 斐波那契加仓间隔基准。
- `InpAddSarStep`、`InpAddSarMaximum`、`InpAddAdxLowMax`：专用 SAR 与 ADX 加仓限制。
- `InpMaxBasketLossMoney`、`InpMaxEquityDrawdownPercent`：篮子亏损和账户权益保护。

## 回测
MT5-4 / ICMarketsSC-Demo / XAUUSD / M1，2026.06.01-2026.07.09，初始资金 10000 USD，历史质量 100%。净利润 119.50，最大净值回撤 334.10（3.27%），交易 1088，胜率 40.90%，Profit Factor 1.02，Sharpe 1.19。

## 风险
该 EA 包含马丁和加仓逻辑。默认参数只是初版验证参数，Profit Factor 边际较薄，实盘前必须按自己的 Broker 点差、滑点、交易时段和保证金条件重新回测，并先用模拟账户前向测试。
