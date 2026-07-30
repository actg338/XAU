#!/usr/bin/env python3
"""Inject the shared navigation assets into all localized public pages."""

import logging
from pathlib import Path
from typing import Final

ROOT: Final[Path] = Path(__file__).parent.parent
LANGUAGE_DIRS: Final[tuple[str, ...]] = ("", "zh-tw", "en", "ja", "ko", "de", "fr")
PAGE_NAMES: Final[tuple[str, ...]] = (
    "index.html",
    "market-tools.html",
    "news.html",
    "huice.html",
    "free-ea.html",
    "ea-install.html",
)
STYLE: Final[str] = '<link rel="stylesheet" href="/assets/site-nav.css">'
SCRIPT: Final[str] = '<script src="/assets/site-nav.js" defer></script>'
LOGGER: Final[logging.Logger] = logging.getLogger("inject_site_nav")


def inject(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if STYLE in text and SCRIPT in text:
        return False
    if "</head>" not in text:
        raise ValueError(f"{path}: closing head tag is missing")
    assets = "\n".join(item for item in (STYLE, SCRIPT) if item not in text)
    path.write_text(text.replace("</head>", f"{assets}\n</head>", 1), encoding="utf-8")
    return True


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    changed = 0
    for language_dir in LANGUAGE_DIRS:
        directory = ROOT / language_dir if language_dir else ROOT
        for page_name in PAGE_NAMES:
            path = directory / page_name
            if not path.exists():
                raise FileNotFoundError(path)
            changed += int(inject(path))
    LOGGER.info("Shared navigation assets injected", extra={"changed": changed})


if __name__ == "__main__":
    main()
