# Mercari — best-effort SPA scrape via __NEXT_DATA__.
import json
import re

from http_client import fetch, polite_sleep

NAME = "Mercari"

_URLS = [
    "https://www.mercari.com/search/?keyword=lot+bundle",
    "https://www.mercari.com/search/?keyword=huge+lot",
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
            title = node.get("name") or node.get("title")
            price = node.get("price")
            item_id = node.get("id") or node.get("itemId")
            if title and price and item_id:
                try:
                    out.append({
                        "source":    NAME,
                        "title":     str(title)[:140],
                        "price":     float(price),
                        "url":       f"https://www.mercari.com/us/item/{item_id}/",
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
    log(f"    → Mercari: {len(results)} candidates ({status})")
    return results, status
