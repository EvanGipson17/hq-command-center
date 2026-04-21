# GoodwillFinds — best-effort SPA scrape.
import json
import re

from http_client import fetch, polite_sleep

NAME = "GoodwillFinds"

_URLS = [
    "https://www.goodwillfinds.com/search?q=lot",
    "https://www.goodwillfinds.com/search?q=bundle",
]


def _extract(html):
    # Try both __NEXT_DATA__ and generic JSON-LD Product arrays.
    out = []
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if m:
        try:
            data = json.loads(m.group(1))
        except json.JSONDecodeError:
            data = None
        if data:
            def walk(node):
                if isinstance(node, dict):
                    title = node.get("productName") or node.get("name")
                    price = node.get("price") or node.get("currentPrice")
                    slug  = node.get("slug") or node.get("url")
                    if title and price:
                        try:
                            out.append({
                                "source":    NAME,
                                "title":     str(title)[:140],
                                "price":     float(price),
                                "url":       f"https://www.goodwillfinds.com{slug}"
                                             if slug and str(slug).startswith("/") else "https://www.goodwillfinds.com",
                                "location":  None,
                                "is_local":  False,
                                "shippable": True,
                            })
                        except (TypeError, ValueError):
                            pass
                    for v in node.values():
                        walk(v)
                elif isinstance(node, list):
                    for v in node:
                        walk(v)
            walk(data)
    return out


def gather(log=print):
    results = []
    blocked = 0
    for url in _URLS:
        log(f"    · {url}", flush=True)
        html = fetch(url)
        polite_sleep()
        if html is None:
            blocked += 1
            continue
        results.extend(_extract(html))
    status = "ok" if results else ("blocked" if blocked else "js-rendered-shell")
    log(f"    → GoodwillFinds: {len(results)} candidates ({status})")
    return results, status
