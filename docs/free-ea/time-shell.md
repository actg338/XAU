# timeshell.ex5 使用说明

## 功能
定时间隔做空 EA，结合 SAR、初始止盈、跟踪回撤止盈、动态 SL、浮亏保护、自动填充模式识别、动态最大持仓管理和商业化彩色面板。

## 本版面板
- 显示当前 Magic 结算金额、结算单数、结算手数和均单收益。
- 显示当前浮动盈亏、当前持仓单数、当前持仓手数。
- 分开显示多单与空单的单数和手数，便于检查方向暴露。
- 显示止损出场单数与手数、止盈出场单数与手数、胜率。
- 总运行动态统计固定为：当前 Magic 结算统计 + 当前浮动盈亏。

## 品牌信息
- 编译人：微信：thRO03
- 官网：https://03xau.com

## 关键参数
- `Seconds`：最小下单间隔。
- `Lots`：单次手数。
- `TP_USDPer001`：按 0.01 手计算的止盈金额。
- `EnableSAR`：SAR 信号过滤。
- `DynamicSLRatio`：动态止损比例。
- `MinMarginLevel`、`BaseMaxOrders`：风险限制。
- `PreferredFilling`、`ForceUseIOC`、`AllowUseFOK`：自动识别并回退订单填充模式。
- `InpEnableCommercialPanel`、`InpPanelScale`、`InpPanelAlpha`：商业化面板、缩放和透明度。

## 使用
在模拟账户检查卖出逻辑、经纪商点值、服务器时间和填充模式后再评估实盘。面板会自动显示下单最小间隔倒计时、持仓状态、拒绝开仓原因、多周期 ADX、Magic 运行统计、授权状态、编译人微信和官网。

## 风险
定时做空在持续上涨行情中可能快速累积风险，请启用仓位上限和保证金保护。
