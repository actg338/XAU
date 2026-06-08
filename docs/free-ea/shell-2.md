# shell2.0.ex5 使用说明

## 功能
做空方向的 SAR 首仓过滤与加仓 EA，支持保证金检查、价格下限和组合浮盈退出。

## 关键参数
- `InitialLots`：首单手数。
- `MartingaleFactor`：加仓倍数，默认值风险较高。
- `BaseAddPoints`：加仓价格间距。
- `MinMarginLevel`：最低保证金比例。
- `FloatingPercentThreshold`：组合退出阈值。
- `MagicNumber`：实例标识。

## 使用
加载到目标图表后先保持最小手数，确认卖出方向、填充模式与品种规格兼容。

## 风险
做空加仓在单边上涨中可能产生大幅回撤，必须限制总手数和最大加仓次数。
