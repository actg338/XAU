#!/usr/bin/env python3
"""
批量给 7 个语言版本的 index.html 加新闻导航按钮
策略:在 <a class="bug-nav"> 前面插入 <a class="news-nav">
"""
import re
from pathlib import Path

ROOT = Path("/Users/apple/.mavis/projects/xau-news")

# 每个语言对应的 nav 按钮文案 + 链接
NAVS = {
    "index.html": ("新闻·信号", "新闻", "/news.html"),
    "en/index.html": ("News & Signals", "News", "/en/news.html"),
    "zh-tw/index.html": ("新聞·信號", "新聞", "/zh-tw/news.html"),
    "ja/index.html": ("ニュース·シグナル", "ニュース", "/ja/news.html"),
    "ko/index.html": ("뉴스·시그널", "뉴스", "/ko/news.html"),
    "de/index.html": ("News & Signale", "News", "/de/news.html"),
    "fr/index.html": ("Actualités & Signaux", "Actus", "/fr/news.html"),
}


def insert_news_nav(path: Path, full: str, short: str, href: str) -> bool:
    """在 <a class="bug-nav"> 前面插入 news-nav"""
    text = path.read_text(encoding="utf-8")
    if "news-nav" in text:
        print(f"  [{path}] already has news-nav, skip")
        return False

    new_btn = (
        f'<a class="news-nav" href="{href}">'
        f'<span class="news-nav-full">{full}</span>'
        f'<span class="news-nav-short">{short}</span>'
        f'</a>'
    )

    # 找到 <a class="bug-nav" 这行,在它前面插入
    pattern = re.compile(r'(<a class="bug-nav"[^>]*>)')
    new_text, n = pattern.subn(new_btn + r'\1', text, count=1)
    if n == 0:
        print(f"  [{path}] no bug-nav found, FAIL")
        return False

    path.write_text(new_text, encoding="utf-8")
    print(f"  [{path}] OK")
    return True


def add_news_css(path: Path) -> bool:
    """在 </style></head> 前面或 </head> 前加 news-nav 样式
    但更稳妥的方式是查找已存在的 .bug-nav 样式块,在它后面追加 .news-nav 样式
    """
    text = path.read_text(encoding="utf-8")
    if ".news-nav{" in text:
        print(f"  [{path}] news CSS already present, skip")
        return False

    css = (
        '.news-nav{order:99;display:inline-flex;align-items:center;'
        'justify-content:center;min-height:40px;padding:0 15px;'
        'border:1px solid rgba(184,163,255,.48);border-radius:11px;'
        'text-decoration:none;'
        'background:linear-gradient(135deg,#6d6bff,#b8a3ff 58%,#f3d58a);'
        'box-shadow:0 10px 24px rgba(109,107,255,.18);'
        'font-size:13px;font-weight:900;white-space:nowrap;color:#061019}'
        '.nav-links .news-nav{color:#061019}'
        '.news-nav:hover{transform:translateY(-2px)}'
        '.news-nav-short{display:none}'
        '@media(max-width:580px){.news-nav{padding:0 10px;font-size:12px}'
        '.news-nav-full{display:none}.news-nav-short{display:inline}}'
    )

    # 在 </style> 之后但还在 <body> 之前注入
    # 最安全:在 <body> 前注入一个新的 <style> 块
    pattern = re.compile(r'(<body[^>]*>)')
    inject = f'<style>{css}</style>\n{path.name and ""}\1'
    new_text, n = pattern.subn(inject, text, count=1)
    if n == 0:
        print(f"  [{path}] no <body> found, FAIL CSS")
        return False

    path.write_text(new_text, encoding="utf-8")
    print(f"  [{path}] CSS OK")
    return True


def main():
    print("=== Insert news nav button ===")
    for rel, (full, short, href) in NAVS.items():
        path = ROOT / rel
        if not path.exists():
            print(f"  [{path}] FILE NOT FOUND, skip")
            continue
        insert_news_nav(path, full, short, href)

    print()
    print("=== Inject news-nav CSS ===")
    for rel in NAVS:
        path = ROOT / rel
        if not path.exists():
            continue
        add_news_css(path)


if __name__ == "__main__":
    main()
