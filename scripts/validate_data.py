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

    require_mapping("xauusd.json")
    require_mapping("dxy.json")
    require_mapping("warsh.json")
    require_mapping("signal.json")


if __name__ == "__main__":
    main()
