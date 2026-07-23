#!/usr/bin/env python3
"""Validate generated market data before it is published."""

import json
from pathlib import Path
from typing import Final

DATA_DIR: Final[Path] = Path(__file__).parent.parent / "data"


def load_json(name: str) -> object:
    with (DATA_DIR / name).open(encoding="utf-8") as stream:
        return json.load(stream)


def require_mapping(name: str) -> dict[str, object]:
    value = load_json(name)
    if not isinstance(value, dict):
        raise ValueError(f"{name}: root must be an object")
    return value


def main() -> None:
    news = require_mapping("news.json")
    items = news.get("items")
    if not isinstance(items, list) or not items:
        raise ValueError("news.json: items must contain at least one article")

    fedwatch = require_mapping("fedwatch.json")
    meetings = fedwatch.get("meetings")
    if not isinstance(meetings, list) or not meetings:
        raise ValueError("fedwatch.json: meetings must not be empty")

    xauusd = require_mapping("xauusd.json")
    if not isinstance(xauusd.get("price"), (int, float)) or float(xauusd["price"]) <= 0:
        raise ValueError("xauusd.json: price must be a positive number")

    dxy = require_mapping("dxy.json")
    if not isinstance(dxy.get("value"), (int, float)) or float(dxy["value"]) <= 0:
        raise ValueError("dxy.json: value must be a positive number")
    require_mapping("warsh.json")
    require_mapping("signal.json")


if __name__ == "__main__":
    main()
