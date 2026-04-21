# ------------------------------------------------------------------
# Depop — best-effort. SPA, so parsing is hit-or-miss with requests.
# We scrape the Next.js __NEXT_DATA__ blob if present.
# ------------------------------------------------------------------

import json
import re

from http_client import fetch, polite_sleep

NAME = "Depop"

_URLS = [
    "https://www.depop.com/search/?q=bundle",
    "https://www.depop.com/search/?q=lot",
]


def _extract(html):
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        return []
    try:
        data = json.loads(m.group(1))
    except json.JSONDecodeError:
        return []

    out = []
    def walk(node):
        if isinstance(node, dict):
            title = node.get("description") or node.get("title")
            price = node.get("priceAmount") or node.get("price")
            slug  = node.get("slug")
            if title and price and slug:
                try:
                    out.append({
                        "source":    NAME,
                        "title":     str(title)[:140],
                        "price":     float(price),
                        "url":       f"https://www.depop.com/products/{slug}/",
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
    log(f"    → Depop: {len(results)} candidates ({status})")
    return results, status
