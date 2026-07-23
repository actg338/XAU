#!/usr/bin/env python3
"""抓取美元指数 DXY"""
import json
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def fetch_dxy():
    """Yahoo Finance: DX-Y.NYB"""
    url = "https://query1.finance.yahoo.com/v8/finance/chart/DX-Y.NYB"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        result = data["chart"]["result"][0]
        meta = result["meta"]
        price = meta.get("regularMarketPrice")
        prev = meta.get("chartPreviousClose") or meta.get("previousClose")
        if price is None:
            return None
        change_pct = ((price - prev) / prev * 100) if prev else 0
        return {
            "value": round(float(price), 2),
            "change_pct": round(float(change_pct), 2),
            "source": "Yahoo Finance",
            "fetched_at": datetime.now(timezone.utc).isoformat()
        }
    except (urllib.error.URLError, KeyError, ValueError, json.JSONDecodeError) as e:
        print(f"dxy yahoo failed: {e}", file=sys.stderr)
        return None


def fetch_dxy_stooq():
    """stooq.com DXY"""
    url = "https://stooq.com/q/l/?s=dx.f&f=sd2t2ohlcv&h&e=csv"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            text = r.read().decode("utf-8")
        lines = text.strip().split("\n")
        if len(lines) < 2:
            return None
        headers_row = lines[0].lower().split(",")
        data_row = lines[1].split(",")
        h = dict(zip(headers_row, data_row))
        close = h.get("close")
        open_ = h.get("open")
        if not close or close == "-":
            return None
        change_pct = 0
        if open_ and open_ != "-":
            change_pct = (float(close) - float(open_)) / float(open_) * 100
        return {
            "value": round(float(close), 2),
            "change_pct": round(float(change_pct), 2),
            "source": "stooq.com",
            "fetched_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        print(f"dxy stooq failed: {e}", file=sys.stderr)
        return None


def main():
    d = fetch_dxy() or fetch_dxy_stooq()
    if not d:
        d = {
            "value": None,
            "change_pct": None,
            "source": "unavailable",
            "fetched_at": datetime.now(timezone.utc).isoformat()
        }
    (DATA_DIR / "dxy.json").write_text(json.dumps(d, ensure_ascii=False, indent=2))
    print(f"dxy.json: {d}")


if __name__ == "__main__":
    main()
