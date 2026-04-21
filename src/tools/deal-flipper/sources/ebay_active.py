# ------------------------------------------------------------------
# eBay Active Listings source.
# ------------------------------------------------------------------
# Pulls current listings across the same categories used in catalog.py.
# Each listing is returned as a candidate to feed into the analyzer.
# Also pulls "local pickup near 78701" results and tags those as local.
# ------------------------------------------------------------------

import re
from bs4 import BeautifulSoup

from http_client import fetch, polite_sleep

NAME = "eBay"

_PAGES_PER_QUERY = 1
_CATEGORIES = {
    "Electronics":    "293",
    "Sneakers":      "15709",
    "Video Games":   "1249",
    "Home & Tools":   "11700",
    "Collectibles":  "1",
    "Toys & Hobbies": "220",
}

_LOCAL_ZIP = "78701"
_BUNDLE_QUERIES = ["lot of", "bundle", "huge lot", "estate sale", "mixed lot"]


def _price_of(el):
    if not el:
        return None
    text = el.get_text(" ", strip=True)
    m = re.search(r"\$\s*([\d,]+(?:\.\d{2})?)", text)
    return float(m.group(1).replace(",", "")) if m else None


def _parse(html, *, is_local):
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for li in soup.select("li.s-item"):
        t_el = li.select_one(".s-item__title")
        p_el = li.select_one(".s-item__price")
        a_el = li.select_one("a.s-item__link")
        if not (t_el and p_el and a_el):
            continue
        title = t_el.get_text(" ", strip=True)
        if title.lower() in ("shop on ebay", ""):
            continue
        price = _price_of(p_el)
        if not price or not (5 <= price <= 5000):
            continue
        url = a_el.get("href", "").split("?")[0]
        out.append({
            "source":    NAME,
            "title":     title,
            "price":     price,
            "url":       url,
            "location":  "Austin, TX (local)" if is_local else None,
            "is_local":  is_local,
            "shippable": not is_local,  # local pickup listings often don't ship
        })
    return out


def _url(cat_id, page, *, local, query=None):
    qs = [f"_sacat={cat_id}", f"_pgn={page}"]
    if local:
        qs += [f"_stpos={_LOCAL_ZIP}", "LH_PickUp=1", "_fspt=1"]
    if query:
        qs.append(f"_nkw={query.replace(' ', '+')}")
    return "https://www.ebay.com/sch/i.html?" + "&".join(qs)


def gather(log=print):
    results = []
    blocked = 0

    for cat_label, cat_id in _CATEGORIES.items():
        log(f"    · {cat_label} (active)", flush=True)
        for page in range(1, _PAGES_PER_QUERY + 1):
            html = fetch(_url(cat_id, page, local=False),
                         referer="https://www.ebay.com/")
            polite_sleep()
            if html is None:
                blocked += 1
                continue
            results.extend(_parse(html, is_local=False))

        # Austin local pickup
        html = fetch(_url(cat_id, 1, local=True),
                     referer="https://www.ebay.com/")
        polite_sleep()
        if html is None:
            blocked += 1
        else:
            results.extend(_parse(html, is_local=True))

    # Bundle-specific searches (cross-category)
    for q in _BUNDLE_QUERIES:
        log(f"    · bundle query: {q}", flush=True)
        html = fetch(_url("0", 1, local=False, query=q),
                     referer="https://www.ebay.com/")
        polite_sleep()
        if html is None:
            blocked += 1
            continue
        results.extend(_parse(html, is_local=False))

    status = "ok" if results else ("blocked" if blocked else "no results")
    log(f"    → eBay active: {len(results)} candidates ({blocked} blocks)")
    return results, status
