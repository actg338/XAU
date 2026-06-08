# H1_router.ex5 使用说明

## 功能
根据 H1 SAR 自动切换两套组合：网格分支与马丁斐波分支。建议使用 MT5 对冲账户。

## 关键参数
- `StartupMode` / `EnableAutoModeSwitch`：启动与自动切换模式。
- `H1SAR_Step`、`H1SAR_Max`：H1 路由信号。
- `GridLot`、`GridStepPoints`、`MaxGridPositions`：网格风险。
- `MartinInitialLots`、`MartinMartingaleFactor`：马丁风险。
- `MaxSpreadPoints`、`MinProjectedMarginLevelPercent`：执行保护。

## 使用
先在 XAUUSD 模拟账户运行，确认账户为对冲模式，再启用自动切换。

## 风险
双分支策略复杂且可能同时累积仓位。不得跳过模拟测试和权益熔断设置。
