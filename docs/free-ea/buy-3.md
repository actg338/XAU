# buy3.0.ex5 使用说明

## 功能
做多方向 EA，使用 SAR 过滤首仓和加仓，并支持动态价格上限、浮盈比例止盈及账户保护。

## 建议设置
- `InitialLots`：建议从 0.01 开始。
- `UseAddSARFilter`：控制加仓 SAR 过滤。
- `BaseAddPoints`：基础加仓距离。
- `FloatingPercentThreshold`：组合浮盈退出阈值。
- `MagicNumber`：每个实例使用不同编号。

## 安装
复制到 `MQL5/Experts`，刷新导航器后加载至目标图表，开启算法交易。

## 风险
包含连续加仓机制。实盘前必须针对经纪商点差、合约规格和资金规模完成测试。
