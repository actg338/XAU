#!/usr/bin/env python3
"""Fetch the official CFTC disaggregated futures report for COMEX Gold."""

import csv
import io
import json
import logging
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Final

import requests

SOURCE_URL: Final[str] = "https://www.cftc.gov/files/dea/history/fut_disagg_txt_{year}.zip"
MARKET_CODE: Final[str] = "088691"
OUTPUT_PATH: Final[Path] = Path(__file__).parent.parent / "data" / "cot.json"
TIMEOUT_SECONDS: Final[int] = 30
LOGGER: Final[logging.Logger] = logging.getLogger("fetch_cot")


def parse_integer(row: dict[str, str], key: str) -> int:
    value = row.get(key)
    if value is None:
        raise ValueError(f"CFTC row is missing field {key}")
    return int(value.strip())


def gold_rows(content: bytes) -> list[dict[str, str]]:
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        names = archive.namelist()
        if len(names) != 1:
            raise ValueError("CFTC archive must contain one report file")
        text = archive.read(names[0]).decode("utf-8-sig")
    rows = [
        row for row in csv.DictReader(text.splitlines())
        if row.get("CFTC_Contract_Market_Code", "").strip() == MARKET_CODE
    ]
    if len(rows) < 2:
        raise ValueError("CFTC history must contain two COMEX Gold reports")
    return sorted(rows, key=lambda row: row["Report_Date_as_YYYY-MM-DD"], reverse=True)


def position(long_value: int, short_value: int) -> dict[str, int]:
    return {"long": long_value, "short": short_value, "net": long_value - short_value}


def managed_position(row: dict[str, str]) -> dict[str, int]:
    return position(
        parse_integer(row, "M_Money_Positions_Long_All"),
        parse_integer(row, "M_Money_Positions_Short_All"),
    )


def build_payload(rows: list[dict[str, str]], source_url: str) -> dict[str, object]:
    row, previous = rows[0], rows[1]
    current = managed_position(row)
    previous_net = managed_position(previous)["net"]
    return {
        "market": "COMEX Gold Futures",
        "marketCode": MARKET_CODE,
        "reportDate": row["Report_Date_as_YYYY-MM-DD"].strip(),
        "previousReportDate": previous["Report_Date_as_YYYY-MM-DD"].strip(),
        "publishedAt": datetime.now(timezone.utc).isoformat(),
        "openInterest": parse_integer(row, "Open_Interest_All"),
        "producer": position(
            parse_integer(row, "Prod_Merc_Positions_Long_All"),
            parse_integer(row, "Prod_Merc_Positions_Short_All"),
        ),
        "swapDealer": position(
            parse_integer(row, "Swap_Positions_Long_All"),
            parse_integer(row, "Swap__Positions_Short_All"),
        ),
        "managedMoney": current,
        "managedMoneyWeeklyChange": current["net"] - previous_net,
        "source": source_url,
        "frequency": "weekly",
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    source_url = SOURCE_URL.format(year=datetime.now(timezone.utc).year)
    response = requests.get(
        source_url,
        headers={"User-Agent": "03xau-market-data/1.0"},
        timeout=TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    payload = build_payload(gold_rows(response.content), source_url)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    LOGGER.info("CFTC report saved", extra={"report_date": payload["reportDate"]})


if __name__ == "__main__":
    main()
