# timeshell.ex5 使用说明

## 功能
定时间隔做空 EA，结合 SAR、初始止盈、移动止损、动态 SL、浮亏保护和动态最大持仓管理。

## 关键参数
- `Seconds`：最小下单间隔。
- `Lots`：单次手数。
- `TP_USDPer001`：按 0.01 手计算的止盈金额。
- `EnableSAR`：SAR 信号过滤。
- `DynamicSLRatio`：动态止损比例。
- `MinMarginLevel`、`BaseMaxOrders`：风险限制。

## 使用
在模拟账户检查卖出逻辑、经纪商点值、服务器时间和填充模式后再评估实盘。

## 风险
定时做空在持续上涨行情中可能快速累积风险，请启用仓位上限和保证金保护。
