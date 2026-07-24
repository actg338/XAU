#!/usr/bin/env python3
"""Pre-translate dynamic news data during GitHub Actions runs."""
import json
import logging
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
NEWS_PATH = DATA_DIR / "news.json"
WARSH_PATH = DATA_DIR / "warsh.json"
TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single"
TARGET_LANGUAGES = ("zh-CN", "zh-TW", "ja", "ko", "de", "fr")
NEWS_LIMIT = 30
BATCH_SIZE = 5
MAX_WORKERS = 3
FIELD_SEPARATOR = "\n__XAU_FIELD__\n"
ITEM_SEPARATOR = "\n__XAU_ITEM__\n"
LOGGER = logging.getLogger("pretranslate")


def translate_text(text: str, target: str) -> str:
    if not text:
        return ""
    query = urllib.parse.urlencode({
        "client": "gtx",
        "sl": "en",
        "tl": target,
        "dt": "t",
        "q": text,
    })
    request = urllib.request.Request(
        f"{TRANSLATE_URL}?{query}",
        headers={"User-Agent": "XAUQuantTranslationBot/1.0"},
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                payload = json.loads(response.read())
            if not isinstance(payload, list) or not isinstance(payload[0], list):
                raise ValueError("unexpected translation response")
            return "".join(
                str(part[0])
                for part in payload[0]
                if isinstance(part, list) and part
            )
        except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as error:
            if attempt == 2:
                raise RuntimeError(f"translation failed for {target}") from error
            time.sleep(attempt + 1)
    return text


def missing_news_batches(
    items: list[dict[str, object]],
    language: str
) -> list[list[tuple[int, dict[str, object]]]]:
    missing = []
    for index, item in enumerate(items[:NEWS_LIMIT]):
        translations = item.get("translations")
        if not isinstance(translations, dict) or language not in translations:
            missing.append((index, item))
    return [missing[index:index + BATCH_SIZE] for index in range(0, len(missing), BATCH_SIZE)]


def translate_news_batch(
    batch: list[tuple[int, dict[str, object]]],
    language: str
) -> tuple[str, list[tuple[int, str, str]]]:
    combined = ITEM_SEPARATOR.join(
        f"{str(item.get('title') or '—')}{FIELD_SEPARATOR}{str(item.get('summary') or '')}"
        for _, item in batch
    )
    translated = translate_text(combined, language)
    translated_items = translated.split(ITEM_SEPARATOR)
    if len(translated_items) != len(batch):
        return language, translate_news_items_individually(batch, language)
    result = []
    for (index, _), content in zip(batch, translated_items):
        title, separator, summary = content.partition(FIELD_SEPARATOR)
        if not separator:
            return language, translate_news_items_individually(batch, language)
        result.append((index, title.strip(), summary.strip()))
    return language, result


def translate_news_items_individually(
    batch: list[tuple[int, dict[str, object]]],
    language: str
) -> list[tuple[int, str, str]]:
    result: list[tuple[int, str, str]] = []
    for index, item in batch:
        title = translate_text(str(item.get("title") or "—"), language)
        summary = translate_text(str(item.get("summary") or ""), language)
        result.append((index, title.strip(), summary.strip()))
    return result


def translate_news(data: dict[str, object]) -> bool:
    items = data.get("items")
    if not isinstance(items, list):
        return False
    typed_items = [item for item in items if isinstance(item, dict)]
    tasks = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for language in TARGET_LANGUAGES:
            for batch in missing_news_batches(typed_items, language):
                tasks.append(executor.submit(translate_news_batch, batch, language))
        changed = apply_news_tasks(tasks, typed_items)
    return changed


def apply_news_tasks(tasks: list[object], items: list[dict[str, object]]) -> bool:
    changed = False
    for task in as_completed(tasks):
        try:
            language, results = task.result()
            for index, title, summary in results:
                translations = items[index].setdefault("translations", {})
                if isinstance(translations, dict):
                    translations[language] = {"title": title, "summary": summary}
                    changed = True
        except RuntimeError as error:
            LOGGER.warning("%s", error)
    return changed


def translate_warsh(data: dict[str, object]) -> bool:
    translations = data.setdefault("translations", {})
    if not isinstance(translations, dict):
        return False
    text = str(data.get("text") or "")[:280]
    stance = data.get("stance")
    keywords = stance.get("keywords", []) if isinstance(stance, dict) else []
    words = [str(item.get("word") or "") for item in keywords if isinstance(item, dict)]
    changed = False
    for language in TARGET_LANGUAGES:
        if language in translations:
            continue
        try:
            excerpt = translate_text(text, language)
            translated_words = [translate_text(word, language) for word in words]
            translations[language] = {"excerpt": excerpt, "keywords": translated_words}
            changed = True
        except RuntimeError as error:
            LOGGER.warning("%s", error)
    return changed


def load_json(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must contain an object")
    return data


def save_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    news = load_json(NEWS_PATH)
    warsh = load_json(WARSH_PATH)
    news_changed = translate_news(news)
    warsh_changed = translate_warsh(warsh)
    if news_changed:
        save_json(NEWS_PATH, news)
    if warsh_changed:
        save_json(WARSH_PATH, warsh)
    LOGGER.info("pretranslation complete: news=%s warsh=%s", news_changed, warsh_changed)


if __name__ == "__main__":
    main()
