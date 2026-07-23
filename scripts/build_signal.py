#!/usr/bin/env python3
"""
综合策略信号生成
结合:
- 沃什立场(鹰派/鸽派)
- FedWatch 利率路径
- 黄金价格变化
- DXY 美元指数

输出:简单的多空信号 + 仓位建议
"""
import json
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def load(name):
    p = DATA_DIR / name
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


def main():
    warsh = load("warsh.json") or {}
    fedwatch = load("fedwatch.json") or {}
    xau = load("xauusd.json") or {}
    dxy = load("dxy.json") or {}

    score = 0
    reasons = []

    # 沃什立场权重
    stance = (warsh.get("stance") or {}).get("label", "NEUTRAL")
    if stance in ("STRONG_HAWK",):
        score -= 3
        reasons.append("沃什强鹰派立场")
    elif stance == "HAWK":
        score -= 2
        reasons.append("沃什鹰派立场")
    elif stance in ("DOVE", "STRONG_DOVE"):
        score += 2
        reasons.append("沃什鸽派立场")

    # FedWatch 概率
    meetings = fedwatch.get("meetings", [])
    if meetings:
        first = meetings[0]
        if first.get("hike", 0) > 50:
            score -= 1
            reasons.append(f"下次 FOMC 加息概率 {first['hike']:.0f}%")
        elif first.get("cut", 0) > 50:
            score += 1
            reasons.append(f"下次 FOMC 降息概率 {first['cut']:.0f}%")

    # 黄金价格变化
    if xau.get("change_pct") is not None:
        cp = float(xau["change_pct"])
        if cp < -1:
            score -= 1
            reasons.append(f"黄金 24h 跌 {cp:.2f}%")
        elif cp > 1:
            score += 1
            reasons.append(f"黄金 24h 涨 {cp:.2f}%")

    # DXY 美元
    if dxy.get("change_pct") is not None:
        dp = float(dxy["change_pct"])
        if dp > 0.5:
            score -= 1
            reasons.append(f"美元指数走强 {dp:.2f}%")
        elif dp < -0.5:
            score += 1
            reasons.append(f"美元指数走弱 {dp:.2f}%")

    # 综合判断
    if score >= 3:
        signal = "偏多 · 关注做多机会"
        action = "策略 B 顺势做多端,1.5% 风险"
    elif score <= -3:
        signal = "偏空 · 关注做空机会"
        action = "策略 A 做空端,1% 风险"
    elif score <= -1:
        signal = "震荡偏空 · 关注阻力位做空"
        action = "策略 A 做空端,1% 风险"
    elif score >= 1:
        signal = "震荡偏多 · 关注支撑位做多"
        action = "策略 A 做多端,1% 风险"
    else:
        signal = "震荡 · 高抛低吸"
        action = "策略 A 回归,1% 风险"

    out = {
        "score": score,
        "signal": signal,
        "action": action,
        "reasons": reasons,
        "reason": " · ".join(reasons) if reasons else "暂无明确信号",
        "generated_at": datetime.now(timezone.utc).isoformat()
    }
    (DATA_DIR / "signal.json").write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"signal.json: score={score} signal={signal}")


if __name__ == "__main__":
    main()
