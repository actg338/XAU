#!/usr/bin/env python3
"""Build a compact, deterministic daily gold intelligence brief."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Final, cast

DATA_DIR: Final[Path] = Path(__file__).parent.parent / "data"
LOGGER: Final[logging.Logger] = logging.getLogger("build_brief")


def load(name: str) -> dict[str, object]:
    try:
        value = json.loads((DATA_DIR / name).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return cast(dict[str, object], value) if isinstance(value, dict) else {}


def main() -> None:
    signal = load("signal.json")
    news = load("news.json")
    events = load("events.json")
    items = news.get("items", [])
    high_impact = [
        item for item in items
        if isinstance(item, dict) and item.get("impact") == "high"
    ][:3] if isinstance(items, list) else []
    event_items = events.get("events", [])
    next_event = event_items[0] if isinstance(event_items, list) and event_items else None
    output: dict[str, object] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "direction": signal.get("direction", "neutral"),
        "label_key": signal.get("label_key", "balanced"),
        "confidence": signal.get("confidence", 0),
        "score": signal.get("score", 0),
        "drivers": signal.get("supporting", []),
        "counter_risks": signal.get("opposing", []),
        "top_news": [
            {
                "title": item.get("title"),
                "link": item.get("link"),
                "category": item.get("category"),
                "bias": item.get("gold_bias"),
            }
            for item in high_impact
        ],
        "next_event": next_event,
    }
    (DATA_DIR / "brief.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    LOGGER.info("Generated intelligence brief")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    main()
