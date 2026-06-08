# thRO03.ex5 使用说明

## 功能
做多方向 SAR 首仓过滤与斐波间距加仓 EA，包含保证金、权益回撤、余额浮盈与动态价格上限保护。

## 关键参数
- `MaxMartingaleSteps`、`MaxAllowedOpenLot`：持仓上限。
- `SAR_Step`、`SAR_Max`：首仓过滤。
- `BaseAddPoints`：加仓距离。
- `EnableEquityPullbackRule`：权益回撤保护。
- `MagicNumber`：交易识别编号。

## 使用
复制到 `MQL5/Experts`，在模拟账户加载并启用算法交易。先用小手数验证。

## 风险
该 EA 包含加仓逻辑，不适合未设置最大仓位和权益保护的账户。
