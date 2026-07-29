#!/usr/bin/env python3
"""Fetch the official CFTC disaggregated futures report for COMEX Gold."""

import csv
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Final

import requests

SOURCE_URL: Final[str] = "https://www.cftc.gov/dea/newcot/f_disagg.txt"
MARKET_CODE: Final[str] = "088691"
OUTPUT_PATH: Final[Path] = Path(__file__).parent.parent / "data" / "cot.json"
TIMEOUT_SECONDS: Final[int] = 30
LOGGER: Final[logging.Logger] = logging.getLogger("fetch_cot")


def parse_integer(row: list[str], index: int) -> int:
    if index >= len(row):
        raise ValueError(f"CFTC row is missing field {index}")
    return int(row[index].strip())


def find_gold_row(content: str) -> list[str]:
    for row in csv.reader(content.splitlines()):
        if len(row) > 3 and row[3].strip() == MARKET_CODE:
            return row
    raise ValueError("COMEX Gold market code was not found")


def previous_payload() -> dict[str, object]:
    if not OUTPUT_PATH.exists():
        return {}
    try:
        value = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def position(long_value: int, short_value: int) -> dict[str, int]:
    return {"long": long_value, "short": short_value, "net": long_value - short_value}


def build_payload(row: list[str]) -> dict[str, object]:
    previous = previous_payload()
    previous_report = previous.get("reportDate")
    previous_managed = previous.get("managedMoney")
    current = position(parse_integer(row, 13), parse_integer(row, 14))
    delta: int | None = None
    if previous_report != row[2].strip() and isinstance(previous_managed, dict):
        old_net = previous_managed.get("net")
        if isinstance(old_net, int):
            delta = current["net"] - old_net
    return {
        "market": "COMEX Gold Futures",
        "marketCode": MARKET_CODE,
        "reportDate": row[2].strip(),
        "publishedAt": datetime.now(timezone.utc).isoformat(),
        "openInterest": parse_integer(row, 7),
        "producer": position(parse_integer(row, 8), parse_integer(row, 9)),
        "swapDealer": position(parse_integer(row, 10), parse_integer(row, 11)),
        "managedMoney": current,
        "managedMoneyWeeklyChange": delta,
        "source": SOURCE_URL,
        "frequency": "weekly",
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    response = requests.get(
        SOURCE_URL,
        headers={"User-Agent": "03xau-market-data/1.0"},
        timeout=TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    payload = build_payload(find_gold_row(response.text))
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    LOGGER.info("CFTC report saved", extra={"report_date": payload["reportDate"]})


if __name__ == "__main__":
    main()
