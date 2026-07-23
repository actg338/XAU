#!/usr/bin/env python3
"""
抓取权威新闻流
来源:
- Federal Reserve Press Releases
- Federal Reserve Speeches and Testimony
- BLS News Releases
- BEA Economic Releases
- CNBC Top News (RSS)
"""
import json
import hashlib
import re
import sys
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html import unescape
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

SOURCES = [
    {
        "name": "Federal Reserve Speeches and Testimony",
        "url": "https://www.federalreserve.gov/feeds/speeches_and_testimony.xml",
        "source": "fed_remarks",
        "key_filter": None
    },
    {
        "name": "Federal Reserve Press",
        "url": "https://www.federalreserve.gov/feeds/press_all.xml",
        "source": "fed_press",
        "key_filter": None
    },
    {
        "name": "BLS News Releases",
        "url": "https://www.bls.gov/feed/bls_latest.rss",
        "source": "bls",
        "key_filter": None
    },
    {
        "name": "BEA Economic Releases",
        "url": "https://apps.bea.gov/rss/rss.xml",
        "source": "bea",
        "key_filter": r"inflation|price|GDP|personal income|outlays|trade|international transactions"
    },
    {
        "name": "CNBC Top News",
        "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "source": "cnbc",
        "key_filter": r"gold|federal reserve|fomc|inflation|warsh|treasury|ecb"
    }
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


def main() -> None:
    output_path = DATA_DIR / "news.json"
    cached_translations = load_translation_cache(output_path)
    all_items: list[dict[str, str | None]] = []
    for src in SOURCES:
        print(f"Fetching {src['name']}...")
        items = fetch_rss(src["url"], src.get("key_filter"))
        for it in items:
            it["source"] = src["source"]
        all_items.extend(items)
        print(f"  → {len(items)} items")

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
    main()
