# shelltime.ex5 使用说明

## 功能
做空方向 SAR 与斐波间距加仓 EA，带保证金过滤、浮盈比例退出和可选价格限制。

## 关键参数
- `InitialLots`、`MartingaleFactor`：仓位增长。
- `BaseAddPoints`：基础加仓距离。
- `MinMarginLevel`：保证金保护。
- `FloatingPercentThreshold`：组合止盈。
- `EnablePriceLimit`：价格下限限制。

## 使用
安装后在模拟账户按目标品种回测，确认 Magic Number 不与其他 EA 冲突。

## 风险
连续加仓会放大风险。建议启用价格限制并设置严格的最大总手数。
