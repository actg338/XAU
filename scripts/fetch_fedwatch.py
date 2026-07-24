#!/usr/bin/env python3
"""Fetch current interest-rate probabilities from CME FedWatch."""

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Final, TypedDict
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

DATA_DIR: Final[Path] = Path(__file__).parent.parent / "data"
OUTPUT_PATH: Final[Path] = DATA_DIR / "fedwatch.json"
CME_PAGE_URL: Final[str] = (
    "https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html"
)
QUIKSTRIKE_ORIGIN: Final[str] = "https://cmegroup-tools.quikstrike.net"
ENTRY_PATH: Final[str] = "/User/QuikStrikeTools.aspx"
VIEW_PATH: Final[str] = "/User/QuikStrikeView.aspx"
VIEW_PARAMS: Final[dict[str, str]] = {
    "viewitemid": "IntegratedFedWatchTool",
    "userId": "lwolf",
    "jobRole": "",
    "company": "",
    "companyType": "",
}
REQUEST_TIMEOUT_SECONDS: Final[int] = 45
MEETING_LIMIT: Final[int] = 4
USER_AGENT: Final[str] = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "Chrome/138.0.0.0 Safari/537.36"
)
PERCENT_PATTERN: Final[re.Pattern[str]] = re.compile(r"(-?\d+(?:\.\d+)?)\s*%")
POSTBACK_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"__doPostBack\('([^']+)'"
)
SOURCE_TIME_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"Data as of\s+(\d{1,2}\s+[A-Z][a-z]{2}\s+\d{4}\s+\d{2}:\d{2}:\d{2})\s+CT"
)
CHICAGO_TIMEZONE: Final[ZoneInfo] = ZoneInfo("America/Chicago")

LOGGER: Final[logging.Logger] = logging.getLogger("fetch_fedwatch")


class Meeting(TypedDict):
    date: str
    label: str
    hold: float
    hike: float
    cut: float


def build_url(path: str, extra_query: str = "") -> str:
    query = urlencode(VIEW_PARAMS)
    if extra_query:
        query = f"{query}&{extra_query}"
    return f"{QUIKSTRIKE_ORIGIN}{path}?{query}"


def require_tag(parent: Tag | BeautifulSoup, selector: str) -> Tag:
    value = parent.select_one(selector)
    if not isinstance(value, Tag):
        raise ValueError(f"CME response missing required element: {selector}")
    return value


def input_value(tag: Tag) -> str:
    value = tag.get("value")
    if not isinstance(value, str) or not value:
        raise ValueError("CME response contains an empty session value")
    return value


def start_session() -> tuple[requests.Session, requests.Response]:
    session = requests.Session()
    session.headers.update(
        {"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"}
    )
    response = session.get(
        build_url(ENTRY_PATH),
        headers={"Referer": CME_PAGE_URL},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return session, response


def open_view(
    session: requests.Session, entry_response: requests.Response
) -> tuple[str, requests.Response]:
    entry = BeautifulSoup(entry_response.text, "html.parser")
    cache = input_value(require_tag(entry, "#global_instanceCache"))
    view_url = build_url(VIEW_PATH, cache)
    response = session.get(
        view_url,
        headers={"Referer": entry_response.url},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return view_url, response


def parse_probability(value: str) -> float:
    match = PERCENT_PATTERN.search(value)
    if match is None:
        raise ValueError(f"Invalid CME probability: {value!r}")
    probability = float(match.group(1))
    if not 0.0 <= probability <= 100.0:
        raise ValueError(f"CME probability out of range: {probability}")
    return probability


def parse_meeting(page: BeautifulSoup) -> Meeting:
    info = require_tag(page, "table.grid-thm.grid-thm-v2.no-shadow.w-lg")
    rows = info.select("tr")
    if len(rows) < 3:
        raise ValueError("CME meeting table is incomplete")
    cells = rows[2].select("td")
    if not cells:
        raise ValueError("CME meeting date is missing")
    meeting_date = datetime.strptime(cells[0].get_text(" ", strip=True), "%d %b %Y")

    probability_table: Tag | None = None
    for table in page.select("table.grid-thm.grid-thm-v2.no-shadow.w-lg"):
        heading = table.find("th")
        if heading is not None and heading.get_text(" ", strip=True) == "Probabilities":
            probability_table = table
            break
    if probability_table is None:
        raise ValueError("CME probability summary is missing")
    number_cells = probability_table.select("td.number")
    if len(number_cells) != 3:
        raise ValueError("CME probability summary must contain three values")
    cut, hold, hike = (parse_probability(cell.get_text()) for cell in number_cells)
    if abs((cut + hold + hike) - 100.0) > 0.2:
        raise ValueError("CME probabilities do not total 100%")
    return {
        "date": meeting_date.date().isoformat(),
        "label": meeting_date.strftime("%Y-%m"),
        "hold": hold,
        "hike": hike,
        "cut": cut,
    }


def meeting_targets(page: BeautifulSoup) -> list[str]:
    targets: list[str] = []
    for link in page.select("a[id*='lvMeetings'][href*='__doPostBack']"):
        href = link.get("href")
        if not isinstance(href, str):
            continue
        match = POSTBACK_PATTERN.search(href)
        if match is not None:
            targets.append(match.group(1))
    if not targets:
        raise ValueError("CME response contains no FOMC meeting selectors")
    return targets[:MEETING_LIMIT]


def hidden_form_values(page: BeautifulSoup) -> dict[str, str]:
    values: dict[str, str] = {}
    for field in page.select("form#Form1 input[type='hidden'][name]"):
        name = field.get("name")
        value = field.get("value", "")
        if isinstance(name, str) and isinstance(value, str):
            values[name] = value
    return values


def post_meeting(
    session: requests.Session, view_url: str, page: BeautifulSoup, target: str
) -> requests.Response:
    payload = hidden_form_values(page)
    payload["__EVENTTARGET"] = target
    payload["__EVENTARGUMENT"] = ""
    response = session.post(
        view_url,
        data=payload,
        headers={"Referer": view_url},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response


def parse_source_time(page: BeautifulSoup) -> str:
    text = page.get_text(" ", strip=True)
    match = SOURCE_TIME_PATTERN.search(text)
    if match is None:
        raise ValueError("CME source timestamp is missing")
    local_time = datetime.strptime(match.group(1), "%d %b %Y %H:%M:%S")
    return local_time.replace(tzinfo=CHICAGO_TIMEZONE).astimezone(timezone.utc).isoformat()


def current_rate(page: BeautifulSoup) -> str:
    current = page.find(string=re.compile(r"\(Current\)"))
    if current is None:
        raise ValueError("CME current target rate is missing")
    match = re.search(r"(\d+)-(\d+)", str(current))
    if match is None:
        raise ValueError("CME current target rate has an invalid format")
    low, high = int(match.group(1)) / 100, int(match.group(2)) / 100
    return f"{low:.2f}-{high:.2f}%"


def fetch_cme_fedwatch() -> dict[str, object]:
    session, entry_response = start_session()
    with session:
        view_url, response = open_view(session, entry_response)
        page = BeautifulSoup(response.text, "html.parser")
        targets = meeting_targets(page)
        source_updated_at = parse_source_time(page)
        rate = current_rate(page)
        meetings: list[Meeting] = []
        for index, target in enumerate(targets):
            if index:
                response = post_meeting(session, view_url, page, target)
                page = BeautifulSoup(response.text, "html.parser")
            meetings.append(parse_meeting(page))
    return {
        "as_of": source_updated_at,
        "source_updated_at": source_updated_at,
        "source": "CME FedWatch via QuikStrike",
        "source_url": CME_PAGE_URL,
        "current_rate": rate,
        "meetings": meetings,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def existing_data_is_valid() -> bool:
    if not OUTPUT_PATH.exists():
        return False
    try:
        value = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return isinstance(value, dict) and isinstance(value.get("meetings"), list)


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    try:
        data = fetch_cme_fedwatch()
    except (requests.RequestException, ValueError, OSError) as error:
        if existing_data_is_valid():
            LOGGER.warning("CME fetch failed; retained last valid file: %s", error)
            return
        LOGGER.exception("CME fetch failed and no valid previous file exists")
        raise SystemExit(1) from error
    OUTPUT_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    LOGGER.info("Updated %s with %d meetings", OUTPUT_PATH, len(data["meetings"]))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    main()
