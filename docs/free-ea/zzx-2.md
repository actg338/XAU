# zzx2.0.ex5 使用说明

## 功能
做多方向 SAR 首仓过滤 EA，支持固定间距加仓、动态价格上限、浮盈比例退出与账户保护。

## 关键参数
- `InitialLots`、`MartingaleFactor`：仓位规模。
- `BaseAddPoints`：固定加仓距离。
- `PriceUpperTimeframe`、`PriceUpperBars`：动态价格上限。
- `FloatingPercentThreshold`：组合退出阈值。
- `MagicNumber`：默认 2333，多个实例需调整。

## 使用
安装后先以 0.01 手在模拟账户运行，检查 XAUUSD 报价位数和距离参数。

## 风险
加仓策略可能在下跌行情中持续扩大仓位，应限制总手数并配置权益止损。
