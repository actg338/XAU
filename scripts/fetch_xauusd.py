#!/usr/bin/env python3
"""抓取 XAUUSD 实时价格"""
import json
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def fetch_goldapi():
    """尝试 GoldAPI.io 公开端点(无 key 不可访问,fallback 到其他源)"""
    return None


def fetch_yahoo():
    """通过 Yahoo Finance 抓 XAUUSD=XXAU 符号"""
    url = "https://query1.finance.yahoo.com/v8/finance/chart/XAUUSD=X"
    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read())
        result = data["chart"]["result"][0]
        meta = result["meta"]
        price = meta.get("regularMarketPrice")
        prev = meta.get("chartPreviousClose") or meta.get("previousClose")
        if price is None:
            return None
        change_pct = ((price - prev) / prev * 100) if prev else 0
        return {
            "price": round(float(price), 2),
            "change_pct": round(float(change_pct), 2),
            "prev_close": round(float(prev), 2) if prev else None,
            "source": "Yahoo Finance",
            "fetched_at": datetime.now(timezone.utc).isoformat()
        }
    except (urllib.error.URLError, KeyError, ValueError, json.JSONDecodeError) as e:
        print(f"yahoo failed: {e}", file=sys.stderr)
        return None


def fetch_metals_dev():
    """metals.dev 公开 API(无 key 时返回 placeholder)"""
    url = "https://api.metals.dev/v1/latest?api_key=demo&currency=USD&unit=toz&metal=gold"
    try:
        with urllib.request.urlopen(url, timeout=8) as r:
            data = json.loads(r.read())
        if "metals" in data and "gold" in data["metals"]:
            return {
                "price": round(float(data["metals"]["gold"]), 2),
                "change_pct": 0,
                "source": "metals.dev",
                "fetched_at": datetime.now(timezone.utc).isoformat()
            }
    except Exception as e:
        print(f"metals.dev failed: {e}", file=sys.stderr)
    return None


def main():
    price = fetch_yahoo() or fetch_metals_dev() or fetch_goldapi()
    if not price:
        # 失败时返回 placeholder,GitHub Actions 会保留上一次成功的数据
        print("WARN: no price source available, writing placeholder", file=sys.stderr)
        price = {
            "price": None,
            "change_pct": None,
            "source": "unavailable",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "error": "all upstream sources failed"
        }
    out = DATA_DIR / "xauusd.json"
    out.write_text(json.dumps(price, ensure_ascii=False, indent=2))
    print(f"xauusd.json: {price}")


if __name__ == "__main__":
    main()
