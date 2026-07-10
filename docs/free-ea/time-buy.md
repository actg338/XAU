# timebuy.ex5 使用说明

## 功能
定时间隔做多 EA，结合 SAR、初始止盈、跟踪回撤止盈、动态 SL、浮亏保护、自动填充模式识别、动态最大持仓管理和商业化彩色面板。

## 品牌信息
- 编译人：微信：thRO03
- 官网：https://03xau.com

## 关键参数
- `Seconds`：最小下单间隔。
- `Lots`：单次手数。
- `TP_USDPer001`：按 0.01 手计算的止盈金额。
- `EnableSAR`：SAR 信号过滤。
- `DynamicSLRatio`：动态止损跟踪比例。
- `MinMarginLevel`、`BaseMaxOrders`：风险限制。
- `PreferredFilling`、`ForceUseIOC`、`AllowUseFOK`：自动识别并回退订单填充模式。
- `InpEnableCommercialPanel`、`InpPanelScale`、`InpPanelAlpha`：商业化面板、缩放和透明度。

## 使用
优先在 XAUUSD 模拟账户测试服务器时间、点值和美元金额换算是否符合预期。面板会自动显示下单最小间隔倒计时、BUY 持仓状态、拒绝开仓原因、多周期 ADX、授权状态、编译人微信和官网。

## 风险
定时开仓可能在单边逆势期间累积仓位。必须限制最大订单数并监控保证金。
