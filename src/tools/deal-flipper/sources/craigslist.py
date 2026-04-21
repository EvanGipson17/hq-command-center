# ------------------------------------------------------------------
# Craigslist Austin — for-sale + free sections.
# ------------------------------------------------------------------
# All Craigslist listings are inherently local pickup (unless seller
# says otherwise). We mark them is_local=True.
# ------------------------------------------------------------------

import re
from bs4 import BeautifulSoup

from http_client import fetch, polite_sleep

NAME = "Craigslist"

_SECTIONS = [
    ("For Sale", "https://austin.craigslist.org/search/sss"),
    ("Free",     "https://austin.craigslist.org/search/zip"),
    ("Bundles",  "https://austin.craigslist.org/search/sss?query=lot"),
    ("Bundles",  "https://austin.craigslist.org/search/sss?query=bundle"),
    ("Bundles",  "https://austin.craigslist.org/search/sss?query=estate"),
]


def _parse(html, section):
    soup = BeautifulSoup(html, "html.parser")
    out = []

    # Modern Craigslist uses <li class="cl-search-result"> wrappers.
    for li in soup.select("li.cl-search-result, li.cl-static-search-result"):
        a = li.select_one("a.cl-app-anchor, a.titlestring, a.posting-title")
        if not a:
            continue
        title = a.get_text(" ", strip=True)
        url = a.get("href", "")

        price_text = ""
        p_el = li.select_one(".priceinfo, .price")
        if p_el:
            price_text = p_el.get_text(" ", strip=True)

        m = re.search(r"\$\s*([\d,]+)", price_text)
        price = float(m.group(1).replace(",", "")) if m else (0.0 if section == "Free" else None)
        if price is None:
            continue

        out.append({
            "source":    NAME,
            "title":     title,
            "price":     price,
            "url":       url,
            "location":  "Austin, TX (pickup)",
            "is_local":  True,
            "shippable": False,
        })
    return out


def gather(log=print):
    results = []
    blocked = 0
    for section, url in _SECTIONS:
        log(f"    · {section}: {url.split('?')[-1] or 'main'}", flush=True)
        html = fetch(url)
        polite_sleep()
        if html is None:
            blocked += 1
            continue
        results.extend(_parse(html, section))

    status = "ok" if results else ("blocked" if blocked else "no results")
    log(f"    → Craigslist: {len(results)} candidates ({blocked} blocks)")
    return results, status
