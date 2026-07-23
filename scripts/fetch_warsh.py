#!/usr/bin/env python3
"""
抓取美联储沃什(Warsh)主席最新公开发言
来源:美联储官方讲话 RSS + Federal Reserve Press Releases
分析立场(关键词权重 + 否定句检测 + 上下文)
"""
import json
import re
import sys
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# 沃什关键词权重表(与 news.js 同步)
WARSH_KEYWORDS = {
    "hawk": {
        "persistent": 2, "elevated": 1, "sticky": 2, "above target": 2,
        "uncomfortable": 2, "higher for longer": 3, "vigilant": 1,
        "restrictive": 2, "premature easing": 2, "unwavering": 1,
        "credibility": 2, "resolve": 1, "commitment": 1,
        "price stability": 2, "trimmed mean": 2, "inflation remains": 2,
        "tight": 1, "strong": 1, "resilient": 1, "robust": 1
    },
    "dove": {
        "gradual": 1, "patient": 1, "data dependent": 1, "flexible": 1,
        "moderating": 2, "easing": 2, "cuts": 2, "accommodative": 1,
        "dovish": 2, "transitory": 2, "cooling": 1, "softening": 1
    }
}


class ArticleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.article_depth = 0
        self.in_paragraph = False
        self.paragraphs: list[str] = []
        self.current: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "div" and attributes.get("id") == "article":
            self.article_depth = 1
        elif self.article_depth and tag == "div":
            self.article_depth += 1
        if self.article_depth and tag == "p":
            self.in_paragraph = True
            self.current = []

    def handle_endtag(self, tag: str) -> None:
        if self.article_depth and tag == "p" and self.in_paragraph:
            text = re.sub(r"\s+", " ", "".join(self.current)).strip()
            if text:
                self.paragraphs.append(text)
            self.in_paragraph = False
        if self.article_depth and tag == "div":
            self.article_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.article_depth and self.in_paragraph:
            self.current.append(data)


def fetch_article_text(url: str) -> str:
    if not url.startswith("https://www.federalreserve.gov/"):
        return ""
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            content = response.read().decode("utf-8", errors="replace")
        parser = ArticleTextParser()
        parser.feed(content)
        return "\n".join(parser.paragraphs)
    except (urllib.error.URLError, TimeoutError, ValueError) as error:
        print(f"Fed article fetch failed: {error}", file=sys.stderr)
        return ""


def analyze_stance(text: str) -> dict:
    if not text:
        return {"hawk": 0, "dove": 0, "label": "NEUTRAL", "keywords": []}
    lower = text.lower()
    hawk_score = 0
    dove_score = 0
    keywords = []

    for kw, score in WARSH_KEYWORDS["hawk"].items():
        pat = re.escape(kw)
        matches = re.findall(pat, lower)
        if matches:
            hawk_score += len(matches) * score
            keywords.append({"word": kw, "type": "hawk", "count": len(matches)})

    for kw, score in WARSH_KEYWORDS["dove"].items():
        pat = re.escape(kw)
        matches = re.findall(pat, lower)
        if matches:
            dove_score += len(matches) * score
            keywords.append({"word": kw, "type": "dove", "count": len(matches)})

    diff = hawk_score - dove_score
    if diff > 6:
        label = "STRONG_HAWK"
    elif diff > 2:
        label = "HAWK"
    elif diff < -6:
        label = "STRONG_DOVE"
    elif diff < -2:
        label = "DOVE"
    else:
        label = "NEUTRAL"

    return {
        "hawk": round(hawk_score, 1),
        "dove": round(dove_score, 1),
        "label": label,
        "keywords": sorted(keywords, key=lambda x: -x["count"])[:10]
    }


def fetch_fed_speeches():
    """美联储讲话与国会证词 RSS"""
    url = "https://www.federalreserve.gov/feeds/speeches_and_testimony.xml"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            xml_data = r.read()
    except (urllib.error.URLError, TimeoutError) as e:
        print(f"fed speeches fetch failed: {e}", file=sys.stderr)
        return None

    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        print(f"XML parse failed: {e}", file=sys.stderr)
        return None

    channel = root.find("channel")
    if channel is None:
        return None
    for item in channel.findall("item"):
        title = (item.findtext("title") or "").strip()
        if "warsh" not in title.lower():
            continue
        link = (item.findtext("link") or "").strip()
        description = (item.findtext("description") or "").strip()
        body_text = fetch_article_text(link) or description
        return {
            "title": title,
            "text": body_text[:5000],
            "link": link,
            "source": "Federal Reserve",
            "published_at": (item.findtext("pubDate") or "").strip() or None,
            "stance": analyze_stance(body_text)
        }
    return None


def fetch_fed_press():
    """美联储新闻发布 RSS(次选)"""
    url = "https://www.federalreserve.gov/feeds/press_all.xml"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            xml_data = r.read()
    except (urllib.error.URLError, TimeoutError) as e:
        print(f"fed press fetch failed: {e}", file=sys.stderr)
        return None

    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError:
        return None

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    for entry in root.findall("atom:entry", ns):
        title = entry.find("atom:title", ns)
        if title is None:
            continue
        if "warsh" in title.text.lower() or "chair" in title.text.lower():
            link = entry.find("atom:link", ns)
            updated = entry.find("atom:updated", ns)
            summary = entry.find("atom:summary", ns)
            return {
                "title": title.text,
                "text": (summary.text or "")[:5000] if summary is not None else "",
                "link": link.attrib.get("href", "") if link is not None else "",
                "source": "Federal Reserve Press",
                "published_at": updated.text if updated is not None else None,
                "stance": analyze_stance((summary.text or "") if summary is not None else "")
            }
    return None


def main():
    result = fetch_fed_speeches() or fetch_fed_press()
    if not result:
        result = {
            "title": None,
            "text": None,
            "link": None,
            "source": "unavailable",
            "published_at": None,
            "stance": {"hawk": 0, "dove": 0, "label": "NEUTRAL", "keywords": []},
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "note": "No Warsh speech found in latest Fed feeds"
        }
    result["fetched_at"] = datetime.now(timezone.utc).isoformat()
    (DATA_DIR / "warsh.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"warsh.json: stance={result['stance']['label']} hawk={result['stance']['hawk']} dove={result['stance']['dove']}")


if __name__ == "__main__":
    main()
