#!/usr/bin/env python3
"""Build an explainable, freshness-aware XAUUSD composite signal."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Final, TypedDict, cast

DATA_DIR: Final[Path] = Path(__file__).parent.parent / "data"
LOGGER: Final[logging.Logger] = logging.getLogger("build_signal")


class Component(TypedDict):
    key: str
    score: int
    direction: str
    value: str
    reason_key: str
    updated_at: str | None


def load_mapping(name: str) -> dict[str, object]:
    path = DATA_DIR / name
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        LOGGER.warning("Unable to load %s: %s", name, error)
        return {}
    return cast(dict[str, object], value) if isinstance(value, dict) else {}


def number(value: object) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return None


def component(
    key: str, score: int, value: str, reason_key: str, updated_at: object
) -> Component:
    direction = "bullish" if score > 0 else "bearish" if score < 0 else "neutral"
    timestamp = updated_at if isinstance(updated_at, str) else None
    return {
        "key": key,
        "score": score,
        "direction": direction,
        "value": value,
        "reason_key": reason_key,
        "updated_at": timestamp,
    }


def warsh_component(data: dict[str, object]) -> Component:
    stance_data = data.get("stance")
    stance = stance_data.get("label") if isinstance(stance_data, dict) else "NEUTRAL"
    scores = {"STRONG_HAWK": -30, "HAWK": -20, "DOVE": 20, "STRONG_DOVE": 30}
    score = scores.get(str(stance), 0)
    return component("warsh", score, str(stance), f"warsh_{str(stance).lower()}", data.get("fetched_at"))


def fedwatch_component(data: dict[str, object]) -> Component:
    meetings = data.get("meetings")
    first = meetings[0] if isinstance(meetings, list) and meetings else {}
    if not isinstance(first, dict):
        first = {}
    cut = number(first.get("cut")) or 0.0
    hike = number(first.get("hike")) or 0.0
    score = round((cut - hike) * 0.3)
    value = f"cut {cut:.1f}% / hike {hike:.1f}%"
    return component("fedwatch", score, value, "fedwatch_path", data.get("fetched_at"))


def market_component(
    key: str, data: dict[str, object], multiplier: float
) -> Component:
    change = number(data.get("change_pct"))
    if change is None:
        return component(key, 0, "unavailable", f"{key}_missing", data.get("fetched_at"))
    score = round(max(-25.0, min(25.0, change * multiplier)))
    return component(key, score, f"{change:+.2f}%", f"{key}_momentum", data.get("fetched_at"))


def signal_label(score: int) -> tuple[str, str]:
    if score >= 35:
        return "bullish", "strong_bullish"
    if score >= 12:
        return "bullish", "mild_bullish"
    if score <= -35:
        return "bearish", "strong_bearish"
    if score <= -12:
        return "bearish", "mild_bearish"
    return "neutral", "balanced"


def confidence(components: list[Component], score: int) -> int:
    available = sum(item["value"] != "unavailable" for item in components)
    coverage = available / len(components)
    agreement = abs(sum(1 if item["score"] > 0 else -1 if item["score"] < 0 else 0 for item in components))
    return round(min(92.0, 42.0 + coverage * 28.0 + agreement * 4.0 + abs(score) * 0.2))


def main() -> None:
    components = [
        warsh_component(load_mapping("warsh.json")),
        fedwatch_component(load_mapping("fedwatch.json")),
        market_component("xau", load_mapping("xauusd.json"), 12.0),
        market_component("dxy", load_mapping("dxy.json"), -18.0),
    ]
    score = max(-100, min(100, sum(item["score"] for item in components)))
    direction, label_key = signal_label(score)
    supporting = [item["key"] for item in components if item["direction"] == direction]
    opposing = [item["key"] for item in components if item["direction"] not in (direction, "neutral")]
    output: dict[str, object] = {
        "schema_version": 2,
        "score": score,
        "direction": direction,
        "label_key": label_key,
        "signal": label_key,
        "action": "wait_for_confirmation",
        "confidence": confidence(components, score),
        "components": components,
        "supporting": supporting,
        "opposing": opposing,
        "reason": " · ".join(item["reason_key"] for item in components),
        "reasons": [item["reason_key"] for item in components],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    path = DATA_DIR / "signal.json"
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    LOGGER.info("Generated signal score=%d label=%s", score, label_key)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    main()
