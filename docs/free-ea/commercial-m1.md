# XAUUSD_M1_Commercial_EA.ex5 使用说明

## 功能
面向 XAUUSD / XAUUSD 后缀品种的 M1 自动交易 EA，使用布林带中轨方向和 SAR 真翻转进行开仓确认，内置 ATR 动态硬止损、阶梯移动止损、平仓冷却、亏损惩罚、多空 Magic 分离和左下角商业信息面板。

## 建议设置
- 图表：XAUUSD 或 Broker 对应黄金后缀品种，周期固定 M1。
- `InpFixedLot`：默认 0.01 手，实盘前按账户资金和杠杆调整。
- `InpMaxSpreadPoints`：标准模板为 360 points，需根据 Broker 点差重新确认。
- `InpBuyMagic` / `InpSellMagic`：多单和空单必须使用不同 Magic。
- `InpUseStepTrailingStop`：默认开启，按盈利方向独立移动止损。

## 安装
将 `XAUUSD_M1_Commercial_EA.ex5` 放入 MT5 的 `MQL5/Experts`，重启 MT5 或刷新导航器，加载到黄金 M1 图表并允许算法交易。

## 风险
黄金 M1 波动大，点差扩大、滑点、跳空和服务器执行差异都可能影响结果。请先回测和模拟运行，不保证盈利。
