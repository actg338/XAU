# XAUUSD_M1_Resonance_EA.ex5 使用说明

## 功能
面向 XAUUSD M1 的双指标共振策略，使用 Ichimoku 与 SAR 进行趋势确认，并配合 ATR 动态止损、时段过滤和亏损惩罚冷却机制。

## 建议设置
- 图表：XAUUSD 或 Broker 对应黄金后缀品种，优先使用 M1 周期。
- 先在策略测试器中验证点差、滑点和历史数据质量。
- 检查手数、Magic Number、ATR 止损和交易时段参数。
- 同账户运行多个 EA 时，必须保持 Magic Number 唯一。

## 安装
将 `XAUUSD_M1_Resonance_EA.ex5` 放入 MT5 的 `MQL5/Experts`，重启 MT5 或刷新导航器，加载到 XAUUSD M1 图表并允许算法交易。

## 风险
自动交易不保证盈利。黄金 M1 在新闻、换日和低流动性时段可能出现快速波动、滑点和点差扩大，请先在模拟账户验证。
