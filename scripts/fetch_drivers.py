#!/usr/bin/env python3
"""Build an official-rate and market-price driver snapshot."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Final
from xml.etree import ElementTree

import requests

ROOT: Final[Path] = Path(__file__).parent.parent
OUTPUT_PATH: Final[Path] = ROOT / "data" / "drivers.json"
TREASURY_URL: Final[str] = (
    "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml"
)
TIMEOUT_SECONDS: Final[int] = 30
LOGGER: Final[logging.Logger] = logging.getLogger("fetch_drivers")
NS: Final[dict[str, str]] = {
    "atom": "http://www.w3.org/2005/Atom",
    "m": "http://schemas.microsoft.com/ado/2007/08/dataservices/metadata",
    "d": "http://schemas.microsoft.com/ado/2007/08/dataservices",
}


def load_number(name: str, key: str) -> float:
    value = json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))
    number = value.get(key) if isinstance(value, dict) else None
    if not isinstance(number, (int, float)):
        raise ValueError(f"{name}: {key} must be numeric")
    return float(number)


def fetch_curve(data_name: str, year: int) -> dict[str, float | str]:
    response = requests.get(
        TREASURY_URL,
        params={"data": data_name, "field_tdr_date_value": str(year)},
        headers={"User-Agent": "03xau-market-data/1.0"},
        timeout=TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    root = ElementTree.fromstring(response.content)
    entries = root.findall("atom:entry", NS)
    if not entries:
        raise ValueError(f"Treasury returned no rows for {data_name}")
    properties = entries[-1].find("atom:content/m:properties", NS)
    if properties is None:
        raise ValueError("Treasury XML has no properties")
    result: dict[str, float | str] = {}
    for child in properties:
        name = child.tag.rsplit("}", 1)[-1]
        text = (child.text or "").strip()
        if not text:
            continue
        try:
            result[name] = float(text)
        except ValueError:
            result[name] = text
    return result


def number(row: dict[str, float | str], key: str) -> float:
    value = row.get(key)
    if not isinstance(value, float):
        raise ValueError(f"Treasury field {key} is unavailable")
    return value


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    year = datetime.now(timezone.utc).year
    nominal = fetch_curve("daily_treasury_yield_curve", year)
    real = fetch_curve("daily_treasury_real_yield_curve", year)
    payload: dict[str, object] = {
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "treasuryDate": str(nominal.get("NEW_DATE", "")),
        "us2y": number(nominal, "BC_2YEAR"),
        "us10y": number(nominal, "BC_10YEAR"),
        "real10y": number(real, "TC_10YEAR"),
        "xauusd": load_number("xauusd.json", "price"),
        "dxy": load_number("dxy.json", "value"),
        "source": TREASURY_URL,
        "note": "Treasury yields are end-of-day; XAUUSD and DXY use the latest site snapshot.",
    }
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    LOGGER.info("Driver snapshot saved", extra={"treasury_date": payload["treasuryDate"]})


if __name__ == "__main__":
    main()
