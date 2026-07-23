#!/usr/bin/env python3
"""
抓取权威新闻流
来源:
- Federal Reserve Press Releases
- Federal Reserve Speeches
- BLS News Releases
- U.S. Treasury Press Releases
- CNBC Top News (RSS)
- Reuters Top News (RSS)
- Kitco Gold News (RSS)
"""
import json
import re
import sys
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

SOURCES = [
    {
        "name": "Federal Reserve Speeches",
        "url": "https://www.federalreserve.gov/feeds/Speeches.xml",
        "source": "fed_speeches",
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
        "url": "https://www.bls.gov/feed/news_release/",
        "source": "bls",
        "key_filter": None
    },
    {
        "name": "U.S. Treasury Press",
        "url": "https://home.treasury.gov/news/press-releases/feed",
        "source": "treasury",
        "key_filter": None
    },
    {
        "name": "CNBC Top News",
        "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "source": "cnbc",
        "key_filter": r"gold|federal reserve|fomc|inflation|warsh|treasury|ecb"
    },
    {
        "name": "Reuters Business",
        "url": "https://feeds.reuters.com/reuters/businessNews",
        "source": "reuters",
        "key_filter": r"gold|federal reserve|fomc|inflation|warsh|treasury|ecb"
    },
    {
        "name": "Kitco Gold News",
        "url": "https://www.kitco.com/rss/gold.xml",
        "source": "kitco",
        "key_filter": None
    }
]


def fetch_rss(url: str, key_filter=None) -> list:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; NewsBot)"})
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
                    "summary": re.sub(r"<[^>]+>", "", (desc.text or "")[:500]) if desc is not None else "",
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
                "summary": re.sub(r"<[^>]+>", "", (summary.text or "")[:500]) if summary is not None else "",
                "published_at": (updated.text or "").strip() if updated is not None else None,
            })
        return items
    except ET.ParseError as e:
        print(f"  {url}: parse error {e}", file=sys.stderr)
        return []


def main():
    all_items = []
    for src in SOURCES:
        print(f"Fetching {src['name']}...")
        items = fetch_rss(src["url"], src.get("key_filter"))
        for it in items:
            it["source"] = src["source"]
        all_items.extend(items)
        print(f"  → {len(items)} items")

    # 按时间倒序
    def parse_dt(s):
        if not s:
            return datetime.min.replace(tzinfo=timezone.utc)
        for fmt in (
            "%a, %d %b %Y %H:%M:%S %Z",
            "%a, %d %b %Y %H:%M:%S %z",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S%z"
        ):
            try:
                return datetime.strptime(s.strip(), fmt)
            except ValueError:
                continue
        return datetime.min.replace(tzinfo=timezone.utc)

    all_items.sort(key=lambda x: parse_dt(x.get("published_at", "")), reverse=True)

    out = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "total": len(all_items),
        "items": all_items[:80]
    }
    (DATA_DIR / "news.json").write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"news.json: {len(all_items)} total, kept top {len(out['items'])}")


if __name__ == "__main__":
    main()
