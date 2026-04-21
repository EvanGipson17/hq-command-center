# Poshmark — best-effort SPA scrape. Poshmark embeds a
# window.__INITIAL_DATA__ blob we can mine.
import json
import re

from http_client import fetch, polite_sleep

NAME = "Poshmark"

_URLS = [
    "https://poshmark.com/search?query=bundle&availability=available",
    "https://poshmark.com/search?query=lot&availability=available",
]


def _extract(html):
    m = re.search(r"__INITIAL_DATA__\s*=\s*(\{.*?\})\s*;\s*<", html, re.S)
    if not m:
        return []
    try:
        data = json.loads(m.group(1))
    except json.JSONDecodeError:
        return []

    out = []
    def walk(node):
        if isinstance(node, dict):
            title = node.get("title")
            price = node.get("price")
            pid   = node.get("id") or node.get("post_id")
            if title and price and pid:
                try:
                    out.append({
                        "source":    NAME,
                        "title":     str(title)[:140],
                        "price":     float(price),
                        "url":       f"https://poshmark.com/listing/{pid}",
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
    log(f"    → Poshmark: {len(results)} candidates ({status})")
    return results, status
