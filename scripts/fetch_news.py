#!/usr/bin/env python3
"""Fetch first-party monetary-policy and macroeconomic news."""
import json
import hashlib
import logging
import re
import sys
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import TypedDict
from urllib.parse import urljoin

from bs4 import BeautifulSoup

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

LOGGER = logging.getLogger("fetch_news")


class Source(TypedDict):
    name: str
    url: str
    source: str
    key_filter: str | None
    kind: str


MARKET_POLICY_FILTER = (
    r"federal reserve|fomc|interest rate|monetary polic|inflation|price|"
    r"employment|payroll|job opening|GDP|personal income|outlays|trade|"
    r"tariff|sanction|foreign exchange|currency|dollar|treasury|debt|"
    r"China|Russia|Iran|war|energy|oil"
)
FED_PRESS_FILTER = (
    r"FOMC|monetary polic|interest rate|discount rate|economic projection|"
    r"financial stability|liquidity|balance sheet|Beige Book"
)

SOURCES: list[Source] = [
    {
        "name": "Federal Reserve Speeches and Testimony",
        "url": "https://www.federalreserve.gov/feeds/speeches_and_testimony.xml",
        "source": "fed_remarks",
        "key_filter": None,
        "kind": "rss",
    },
    {
        "name": "Federal Reserve Monetary Policy",
        "url": "https://www.federalreserve.gov/feeds/press_monetary.xml",
        "source": "fed_policy",
        "key_filter": None,
        "kind": "rss",
    },
    {
        "name": "Federal Reserve Press",
        "url": "https://www.federalreserve.gov/feeds/press_all.xml",
        "source": "fed_press",
        "key_filter": FED_PRESS_FILTER,
        "kind": "rss",
    },
    {
        "name": "BLS Consumer Price Index",
        "url": "https://www.bls.gov/feed/cpi.rss",
        "source": "bls_cpi",
        "key_filter": None,
        "kind": "rss",
    },
    {
        "name": "BLS Employment Situation",
        "url": "https://www.bls.gov/feed/empsit.rss",
        "source": "bls_jobs",
        "key_filter": None,
        "kind": "rss",
    },
    {
        "name": "BLS Job Openings",
        "url": "https://www.bls.gov/feed/jolts.rss",
        "source": "bls_jolts",
        "key_filter": None,
        "kind": "rss",
    },
    {
        "name": "BLS Producer Price Index",
        "url": "https://www.bls.gov/feed/ppi.rss",
        "source": "bls_ppi",
        "key_filter": None,
        "kind": "rss",
    },
    {
        "name": "BEA Economic Releases",
        "url": "https://apps.bea.gov/rss/rss.xml",
        "source": "bea",
        "key_filter": MARKET_POLICY_FILTER,
        "kind": "rss",
    },
    {
        "name": "U.S. Census Economic Indicators",
        "url": "https://www.census.gov/economic-indicators/indicator.xml",
        "source": "census",
        "key_filter": None,
        "kind": "rss",
    },
    {
        "name": "European Central Bank",
        "url": "https://www.ecb.europa.eu/rss/press.html",
        "source": "ecb",
        "key_filter": MARKET_POLICY_FILTER,
        "kind": "rss",
    },
    {
        "name": "White House",
        "url": "https://www.whitehouse.gov/news/feed/",
        "source": "white_house",
        "key_filter": MARKET_POLICY_FILTER,
        "kind": "rss",
    },
    {
        "name": "U.S. Treasury",
        "url": "https://home.treasury.gov/news/press-releases",
        "source": "treasury",
        "key_filter": MARKET_POLICY_FILTER,
        "kind": "treasury_html",
    },
]


def translation_hash(item: dict[str, str | None]) -> str:
    source = f"{item.get('title') or ''}\0{item.get('summary') or ''}"
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def load_translation_cache(path: Path) -> dict[str, dict[str, object]]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        items = data.get("items", []) if isinstance(data, dict) else []
        return {
            str(item.get("link")): item
            for item in items
            if isinstance(item, dict) and item.get("link")
        }
    except (OSError, ValueError, json.JSONDecodeError):
        return {}


def restore_translations(
    items: list[dict[str, str | None]],
    cached: dict[str, dict[str, object]]
) -> None:
    for item in items:
        item_hash = translation_hash(item)
        previous = cached.get(str(item.get("link") or ""))
        item["_translation_hash"] = item_hash
        if not previous or previous.get("_translation_hash") != item_hash:
            continue
        translations = previous.get("translations")
        if isinstance(translations, dict):
            item["translations"] = translations


def clean_summary(value: str | None) -> str:
    if not value:
        return ""
    decoded = unescape(value)
    without_tags = re.sub(r"<[^>]*>", " ", decoded)
    normalized = re.sub(r"\s+", " ", without_tags).strip()
    return normalized[:500]


def fetch_rss(url: str, key_filter: str | None = None) -> list[dict[str, str | None]]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "XAUQuantNewsBot/1.0 (+https://03xau.com/news.html)",
            "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            xml_data = r.read()
    except (urllib.error.URLError, TimeoutError) as e:
        print(f"  {url}: {e}", file=sys.stderr)
        return []

    items = []
    try:
        # RSS 2.0
        root = ET.fromstring(xml_data)
        channel = root.find("channel")
        if channel is not None:
            for item in channel.findall("item"):
                title = item.find("title")
                link = item.find("link")
                desc = item.find("description")
                pub = item.find("pubDate")
                title_text = (title.text or "").strip() if title is not None else ""
                if key_filter and not re.search(key_filter, title_text, re.IGNORECASE):
                    continue
                items.append({
                    "title": re.sub(r"\s+", " ", title_text),
                    "link": (link.text or "").strip() if link is not None else "",
                    "summary": clean_summary(desc.text if desc is not None else None),
                    "published_at": (pub.text or "").strip() if pub is not None else None,
                })
            return items
        # Atom
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for entry in root.findall("atom:entry", ns):
            title = entry.find("atom:title", ns)
            link = entry.find("atom:link", ns)
            summary = entry.find("atom:summary", ns)
            updated = entry.find("atom:updated", ns)
            title_text = (title.text or "").strip() if title is not None else ""
            if key_filter and not re.search(key_filter, title_text, re.IGNORECASE):
                continue
            link_href = link.attrib.get("href", "") if link is not None else ""
            items.append({
                "title": re.sub(r"\s+", " ", title_text),
                "link": link_href,
                "summary": clean_summary(summary.text if summary is not None else None),
                "published_at": (updated.text or "").strip() if updated is not None else None,
            })
        return items
    except ET.ParseError as e:
        print(f"  {url}: parse error {e}", file=sys.stderr)
        return []


def fetch_treasury(
    url: str, key_filter: str | None = None
) -> list[dict[str, str | None]]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "XAUQuantNewsBot/1.0 (+https://03xau.com/news.html)"},
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            page = BeautifulSoup(response.read(), "html.parser")
    except (urllib.error.URLError, TimeoutError) as error:
        LOGGER.warning("%s: %s", url, error)
        return []
    items: list[dict[str, str | None]] = []
    for row in page.select(".mm-news-row"):
        link = row.select_one(".news-title a[href]")
        published = row.select_one("time[datetime]")
        if link is None or published is None:
            continue
        title = re.sub(r"\s+", " ", link.get_text(" ", strip=True))
        if key_filter and not re.search(key_filter, title, re.IGNORECASE):
            continue
        items.append({
            "title": title,
            "link": urljoin(url, str(link.get("href") or "")),
            "summary": title,
            "published_at": str(published.get("datetime") or ""),
        })
    return items


def fetch_source(source: Source) -> tuple[Source, list[dict[str, str | None]]]:
    if source["kind"] == "treasury_html":
        items = fetch_treasury(source["url"], source["key_filter"])
    else:
        items = fetch_rss(source["url"], source["key_filter"])
    for item in items:
        item["source"] = source["source"]
    return source, items


def main() -> None:
    output_path = DATA_DIR / "news.json"
    cached_translations = load_translation_cache(output_path)
    all_items: list[dict[str, str | None]] = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        tasks = [executor.submit(fetch_source, source) for source in SOURCES]
        for task in as_completed(tasks):
            source, items = task.result()
            all_items.extend(items)
            LOGGER.info("%s: %d items", source["name"], len(items))

    unique_items: dict[str, dict[str, str | None]] = {}
    for item in all_items:
        link = str(item.get("link") or "").strip()
        title = str(item.get("title") or "").strip()
        identity = link or title
        if identity and identity not in unique_items:
            unique_items[identity] = item
    all_items = list(unique_items.values())

    # 按时间倒序
    def parse_dt(s: str | None) -> datetime:
        if not s:
            return datetime.min.replace(tzinfo=timezone.utc)
        for fmt in (
            "%a, %d %b %Y %H:%M:%S %Z",
            "%a, %d %b %Y %H:%M:%S %z",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S%z"
        ):
            try:
                parsed = datetime.strptime(s.strip(), fmt)
                return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
        return datetime.min.replace(tzinfo=timezone.utc)

    all_items.sort(key=lambda x: parse_dt(x.get("published_at", "")), reverse=True)
    restore_translations(all_items, cached_translations)

    out = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "total": len(all_items),
        "items": all_items[:80]
    }
    if not all_items and output_path.exists():
        print("ERROR: every news source failed; preserving previous news.json", file=sys.stderr)
        raise SystemExit(1)
    output_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"news.json: {len(all_items)} total, kept top {len(out['items'])}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    main()
