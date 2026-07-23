#!/usr/bin/env python3
"""抓取美元指数 DXY"""
import json
import sys
import urllib.request
import urllib.error
import math
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
FRANKFURTER_URL = (
    "https://api.frankfurter.app/latest"
    "?from=USD&to=EUR,JPY,GBP,CAD,SEK,CHF"
)
TRADINGVIEW_URL = (
    "https://scanner.tradingview.com/symbol"
    "?symbol=TVC%3ADXY&fields=close%2Cchange%2Cupdate_mode"
)


def fetch_dxy_tradingview() -> dict[str, object] | None:
    """Fetch TradingView's streaming TVC:DXY quote."""
    request = urllib.request.Request(
        TRADINGVIEW_URL,
        headers={
            "User-Agent": "XAUQuant/1.0 (+https://03xau.com/news.html)",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            data = json.loads(response.read())
        if not isinstance(data, dict):
            return None
        value = data.get("close")
        change = data.get("change")
        if not isinstance(value, (int, float)) or float(value) <= 0:
            return None
        return {
            "value": round(float(value), 2),
            "change_pct": round(float(change), 2) if isinstance(change, (int, float)) else None,
            "source": "TradingView TVC:DXY",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
    except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as error:
        print(f"dxy TradingView failed: {error}", file=sys.stderr)
        return None


def calculate_dxy(rates: object) -> float | None:
    if not isinstance(rates, dict):
        return None
    required = ("EUR", "JPY", "GBP", "CAD", "SEK", "CHF")
    if any(not isinstance(rates.get(code), (int, float)) for code in required):
        return None
    usd_eur = float(rates["EUR"])
    usd_jpy = float(rates["JPY"])
    usd_gbp = float(rates["GBP"])
    usd_cad = float(rates["CAD"])
    usd_sek = float(rates["SEK"])
    usd_chf = float(rates["CHF"])
    value = (
        50.14348112
        * math.pow(1 / usd_eur, -0.576)
        * math.pow(usd_jpy, 0.136)
        * math.pow(1 / usd_gbp, -0.119)
        * math.pow(usd_cad, 0.091)
        * math.pow(usd_sek, 0.042)
        * math.pow(usd_chf, 0.036)
    )
    return round(value, 2)


def fetch_dxy_from_fx() -> dict[str, object] | None:
    """Calculate the DXY basket from keyless ECB reference FX rates."""
    request = urllib.request.Request(
        FRANKFURTER_URL,
        headers={
            "User-Agent": "XAUQuant/1.0 (+https://03xau.com/news.html)",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            data = json.loads(response.read())
        if not isinstance(data, dict):
            return None
        value = calculate_dxy(data.get("rates"))
        if value is None:
            return None
        return {
            "value": value,
            "change_pct": None,
            "source": "ECB FX reference rates via Frankfurter",
            "source_date": data.get("date"),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
    except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as error:
        print(f"dxy FX basket failed: {error}", file=sys.stderr)
        return None


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
    # Prefer intraday market quotes. The ECB basket is a daily reference-rate
    # fallback and must not mask a fresher DXY quote.
    d = fetch_dxy_tradingview() or fetch_dxy() or fetch_dxy_stooq() or fetch_dxy_from_fx()
    out = DATA_DIR / "dxy.json"
    if not d:
        if out.exists():
            print("WARN: no DXY source available; preserving previous dxy.json", file=sys.stderr)
            return
        raise SystemExit("no DXY source available and no previous data exists")
    out.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"dxy.json: {d}")


if __name__ == "__main__":
    main()
