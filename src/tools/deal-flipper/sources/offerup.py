# ------------------------------------------------------------------
# OfferUp — best-effort. OfferUp is a JS-rendered SPA, so requests
# usually gets an empty shell. We still fetch and try to extract any
# embedded JSON data from <script> tags; if that fails, we skip.
# ------------------------------------------------------------------

import json
import re

from http_client import fetch, polite_sleep

NAME = "OfferUp"

_URLS = [
    "https://offerup.com/search/?q=bundle&location=Austin,TX",
    "https://offerup.com/search/?q=lot&location=Austin,TX",
    "https://offerup.com/search/?q=estate&location=Austin,TX",
]


def _extract_listings_from_json(html):
    """OfferUp embeds listing data in a window.__NUXT__ or __NEXT_DATA__."""
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        return []
    try:
        data = json.loads(m.group(1))
    except json.JSONDecodeError:
        return []

    out = []
    # Walk the structure looking for anything that looks like listings.
    def walk(node):
        if isinstance(node, dict):
            title = node.get("title") or node.get("itemName")
            price = node.get("price") or node.get("priceInCents")
            if title and price:
                try:
                    if isinstance(price, (int, float)) and price > 1000:
                        price = price / 100  # assume cents
                    out.append({
                        "source":    NAME,
                        "title":     str(title),
                        "price":     float(price),
                        "url":       f"https://offerup.com{node.get('path', '')}"
                                     if node.get("path") else "https://offerup.com",
                        "location":  "Austin, TX",
                        "is_local":  True,
                        "shippable": bool(node.get("shippingEnabled", False)),
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
        log(f"    · {url.split('=')[1].split('&')[0]}", flush=True)
        html = fetch(url)
        polite_sleep()
        if html is None:
            blocked += 1
            continue
        results.extend(_extract_listings_from_json(html))

    status = ("ok" if results else ("blocked" if blocked else "js-rendered-shell"))
    log(f"    → OfferUp: {len(results)} candidates ({status})")
    return results, status
