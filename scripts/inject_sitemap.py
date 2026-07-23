#!/usr/bin/env python3
"""在 sitemap.xml 中为 news 页面插入 URL 块(7 个语言版本)"""
import re
from pathlib import Path

SITEMAP = Path("/Users/apple/.mavis/projects/xau-news/sitemap.xml")

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

ALL_LANGS = ["zh-CN", "zh-TW", "en", "ja", "ko", "de", "fr", "x-default"]
TODAY = "2026-07-23"


def build_url_block(url: str) -> str:
    parts = [f'  <url>\n    <loc>{url}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <changefreq>hourly</changefreq>\n    <priority>0.9</priority>']
    # 7 个 hreflang + x-default
    for href, lang in zip(NEWS_PAGES, ALL_LANGS[:-1]):
        parts.append(f'    <xhtml:link rel="alternate" hreflang="{lang}" href="{href}"/>')
    parts.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="https://03xau.com/en/news.html"/>')
    parts.append('  </url>')
    return '\n'.join(parts)


def main():
    text = SITEMAP.read_text(encoding="utf-8")
    if "news.html" in text:
        print("news already in sitemap, skip")
        return
    # 在 </urlset> 前面插入
    blocks = [build_url_block(url) for url, _ in NEWS_PAGES]
    insert = "\n".join(blocks) + "\n"
    new_text = text.replace("</urlset>", insert + "</urlset>")
    SITEMAP.write_text(new_text, encoding="utf-8")
    print(f"Added {len(NEWS_PAGES)} news URLs to sitemap.xml")


if __name__ == "__main__":
    main()
