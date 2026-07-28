#!/usr/bin/env python3
"""Build an official-source economic event radar."""

import json
import logging
import re
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Final, TypedDict
from zoneinfo import ZoneInfo

DATA_DIR: Final[Path] = Path(__file__).parent.parent / "data"
BLS_ICS_URL: Final[str] = "https://www.bls.gov/schedule/news_release/bls.ics"
FEDWATCH_URL: Final[str] = "https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html"
LOGGER: Final[logging.Logger] = logging.getLogger("build_events")
EASTERN: Final[ZoneInfo] = ZoneInfo("America/New_York")
HIGH_IMPACT: Final[tuple[str, ...]] = (
    "consumer price index",
    "employment situation",
    "producer price index",
    "job openings",
    "employment cost index",
)


class Event(TypedDict):
    event_key: str
    title: str
    starts_at: str
    impact: str
    source: str
    source_url: str


def fetch_text(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; XAUQuantCalendar/1.0; +https://03xau.com/news.html)",
            "Accept": "text/calendar,text/plain;q=0.9,*/*;q=0.8",
            "Referer": "https://www.bls.gov/schedule/2026/home.htm",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError) as error:
        LOGGER.warning("Unable to fetch %s: %s", url, error)
        return ""


def unfold_ics(text: str) -> list[str]:
    return re.sub(r"\r?\n[ \t]", "", text).splitlines()


def parse_ics_datetime(value: str) -> datetime | None:
    cleaned = value.strip()
    formats = ("%Y%m%dT%H%M%S", "%Y%m%dT%H%M", "%Y%m%d")
    for date_format in formats:
        try:
            parsed = datetime.strptime(cleaned.rstrip("Z"), date_format)
            zone = timezone.utc if cleaned.endswith("Z") else EASTERN
            return parsed.replace(tzinfo=zone).astimezone(timezone.utc)
        except ValueError:
            continue
    return None


def event_key(title: str) -> str:
    lowered = title.lower()
    keys = {
        "consumer price index": "cpi",
        "employment situation": "nfp",
        "producer price index": "ppi",
        "job openings": "jolts",
        "employment cost index": "eci",
    }
    return next((key for phrase, key in keys.items() if phrase in lowered), "bls_release")


def parse_bls_events(text: str, now: datetime) -> list[Event]:
    events: list[Event] = []
    blocks = "\n".join(unfold_ics(text)).split("BEGIN:VEVENT")
    for block in blocks[1:]:
        summary = re.search(r"^SUMMARY:(.+)$", block, re.MULTILINE)
        start = re.search(r"^DTSTART(?:;[^:]*)?:(.+)$", block, re.MULTILINE)
        if summary is None or start is None:
            continue
        starts_at = parse_ics_datetime(start.group(1))
        if starts_at is None or not now <= starts_at <= now + timedelta(days=120):
            continue
        title = summary.group(1).replace("\\,", ",").strip()
        impact = "high" if any(term in title.lower() for term in HIGH_IMPACT) else "medium"
        events.append({
            "event_key": event_key(title),
            "title": title,
            "starts_at": starts_at.isoformat(),
            "impact": impact,
            "source": "BLS",
            "source_url": BLS_ICS_URL,
        })
    return events


def load_fomc_events(now: datetime) -> list[Event]:
    path = DATA_DIR / "fedwatch.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    events: list[Event] = []
    meetings = data.get("meetings", []) if isinstance(data, dict) else []
    for meeting in meetings:
        date_value = meeting.get("date") if isinstance(meeting, dict) else None
        if not isinstance(date_value, str):
            continue
        try:
            starts_at = datetime.fromisoformat(date_value[:10] + "T14:00:00").replace(tzinfo=EASTERN)
        except ValueError:
            continue
        starts_utc = starts_at.astimezone(timezone.utc)
        if starts_utc >= now:
            events.append({
                "event_key": "fomc",
                "title": "FOMC Rate Decision",
                "starts_at": starts_utc.isoformat(),
                "impact": "high",
                "source": "CME/Federal Reserve",
                "source_url": FEDWATCH_URL,
            })
    return events


def main() -> None:
    now = datetime.now(timezone.utc)
    events = parse_bls_events(fetch_text(BLS_ICS_URL), now) + load_fomc_events(now)
    events.sort(key=lambda item: item["starts_at"])
    output = {
        "fetched_at": now.isoformat(),
        "timezone": "UTC",
        "events": events[:24],
    }
    (DATA_DIR / "events.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    LOGGER.info("Generated event radar with %d events", len(output["events"]))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    main()
