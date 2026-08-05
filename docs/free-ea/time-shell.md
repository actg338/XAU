# timeshell.ex5 使用说明

## 功能
定时间隔做空 EA，结合 SAR、初始止盈、跟踪回撤止盈、动态 SL、单仓硬止损、浮亏保护、自动填充模式识别、动态最大持仓管理和商业化彩色面板。

## 本版面板
- 显示当前 Magic 结算金额、结算单数、结算手数和均单收益。
- 显示当前 Magic 持仓均价，并在图表绘制 SELL 平均持仓线。
- 显示当前浮动盈亏、当前持仓单数、当前持仓手数。
- 分开显示多单与空单的单数和手数，便于检查方向暴露。
- 显示止损出场单数与手数、止盈出场单数与手数、胜率。
- 总运行动态统计固定为：当前 Magic 结算统计 + 当前浮动盈亏。
- 显示单仓硬止损开关和每 0.01 手风险金额，触发后市价平当前 ticket 并进入下单间隔倒计时。

## 品牌信息
- 编译人：微信：thRO03
- 官网：https://03xau.com

## 关键参数
- `Seconds`：最小下单间隔。
- `Lots`：单次手数。
- `TP_USDPer001`：按 0.01 手计算的止盈金额。
- `EnableSAR`：SAR 信号过滤。
- `DynamicSLRatio`：动态止损比例。
- `EnableSinglePositionHardStop`：单仓硬止损开关。
- `SinglePositionHardStopUSD`：每 0.01 手单仓硬止损金额，实际阈值 = 当前手数 / 0.01 * 参数值。
- `MinMarginLevel`、`BaseMaxOrders`：风险限制。
- `PreferredFilling`、`ForceUseIOC`、`AllowUseFOK`：自动识别并回退订单填充模式。
- `InpEnableCommercialPanel`、`InpPanelScale`、`InpPanelAlpha`：商业化面板、缩放和透明度。
- `InpShowAveragePositionLine`、`InpAveragePositionLineColor`、`InpAveragePositionLineWidth`：当前 Magic 平均持仓线显示、颜色和宽度。

## 使用
在模拟账户检查卖出逻辑、经纪商点值、服务器时间和填充模式后再评估实盘。面板会自动显示下单最小间隔倒计时、SELL 持仓状态、持仓均价、单仓硬止损、拒绝开仓原因、多周期 ADX、Magic 运行统计、授权状态、编译人微信和官网。

## 风险
定时做空在持续上涨行情中可能快速累积风险，请启用仓位上限和保证金保护。
