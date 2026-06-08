# timebuy.ex5 使用说明

## 功能
定时间隔做多 EA，结合 SAR、初始止盈、移动止损、动态 SL、浮亏保护和动态最大持仓管理。

## 关键参数
- `Seconds`：最小下单间隔。
- `Lots`：单次手数。
- `TP_USDPer001`：按 0.01 手计算的止盈金额。
- `EnableSAR`：SAR 信号过滤。
- `DynamicSLRatio`：动态止损跟踪比例。
- `MinMarginLevel`、`BaseMaxOrders`：风险限制。

## 使用
优先在 XAUUSD 模拟账户测试服务器时间、点值和美元金额换算是否符合预期。

## 风险
定时开仓可能在单边逆势期间累积仓位。必须限制最大订单数并监控保证金。
