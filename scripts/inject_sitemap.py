#!/usr/bin/env python3
"""在 sitemap.xml 中写入 news 页面 URL 块（7 个语言版本）。"""
import logging
import re
from datetime import date
from pathlib import Path

SITEMAP = Path(__file__).resolve().parent.parent / "sitemap.xml"
LOGGER = logging.getLogger(__name__)

# 7 个语言的 news URL
NEWS_PAGES = [
    ("https://03xau.com/news.html", "zh-CN"),
    ("https://03xau.com/zh-tw/news.html", "zh-TW"),
    ("https://03xau.com/en/news.html", "en"),
    ("https://03xau.com/ja/news.html", "ja"),
    ("https://03xau.com/ko/news.html", "ko"),
    ("https://03xau.com/de/news.html", "de"),
    ("https://03xau.com/fr/news.html", "fr"),
]

NEWS_BLOCK_PATTERN = re.compile(
    r"\n  <url>\n    <loc>https://03xau\.com/(?:"
    r"(?:zh-tw|en|ja|ko|de|fr)/)?news\.html</loc>.*?  </url>",
    re.DOTALL,
)


def build_url_block(url: str) -> str:
    today = date.today().isoformat()
    parts = [f'  <url>\n    <loc>{url}</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>hourly</changefreq>\n    <priority>0.9</priority>']
    # 7 个 hreflang + x-default
    for href, lang in NEWS_PAGES:
        parts.append(f'    <xhtml:link rel="alternate" hreflang="{lang}" href="{href}"/>')
    parts.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="https://03xau.com/en/news.html"/>')
    parts.append('  </url>')
    return '\n'.join(parts)


def main() -> None:
    text = SITEMAP.read_text(encoding="utf-8")
    without_news = NEWS_BLOCK_PATTERN.sub("", text)
    blocks = [build_url_block(url) for url, _ in NEWS_PAGES]
    insert = "\n".join(blocks) + "\n"
    new_text = without_news.replace("</urlset>", insert + "</urlset>")
    SITEMAP.write_text(new_text, encoding="utf-8")
    LOGGER.info("Wrote %d news URLs to sitemap.xml", len(NEWS_PAGES))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    main()
