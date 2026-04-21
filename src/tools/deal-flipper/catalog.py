# ------------------------------------------------------------------
# catalog.py  —  "what's hot right now" catalog from eBay Sold.
# ------------------------------------------------------------------
# Strategy:
#   Instead of guessing categories, we browse eBay's recently-sold
#   listings across a handful of popular categories and roll up the
#   results into a catalog of {keyword-set -> median sold price}.
#
# This catalog is the yardstick every candidate listing is measured
# against in flip_analyzer.py.
#
# Each catalog entry:
#   {
#     "tokens":       frozenset of meaningful tokens from sold titles,
#     "label":        representative title,
#     "median_price": median sold price,
#     "samples":      number of sold comps backing this entry,
#   }
# ------------------------------------------------------------------

import re
import statistics
from collections import defaultdict

from bs4 import BeautifulSoup

from http_client import fetch, polite_sleep
from bundle_detector import analyze as analyze_bundle

# eBay category IDs that are hot for flipping. See
# https://www.ebay.com/b/<slug>/<id>  for the full list.
EBAY_CATEGORIES = {
    "Electronics":     "293",
    "Sneakers":       "15709",
    "Video Games":    "1249",
    "Home & Tools":    "11700",
    "Collectibles":   "1",
    "Toys & Hobbies": "220",
    "Clothing":       "11450",
}

PAGES_PER_CATEGORY = 2  # keep requests modest — 2 pages * ~60 items each

# Words we drop when tokenizing titles (too generic to identify an item).
_STOP = set("""
a an and the of for with in on at by to is it as from this that these those
new used open box sealed lot bundle sale hot rare original authentic
free shipping ship read description condition working tested excellent great
mint vg vintage retro shipping included good pre pre-owned preowned s
""".split())


def _tokenize(title):
    t = re.sub(r"[^a-z0-9\s]+", " ", (title or "").lower())
    return frozenset(
        w for w in t.split()
        if w and w not in _STOP and not w.isdigit() and len(w) > 1
    )


def _price_from(el):
    if not el:
        return None
    text = el.get_text(" ", strip=True)
    m = re.search(r"\$\s*([\d,]+(?:\.\d{2})?)", text)
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", ""))
    except ValueError:
        return None


def _parse_sold_page(html):
    """Yield (title, price) for every valid listing on a sold page."""
    soup = BeautifulSoup(html, "html.parser")
    for li in soup.select("li.s-item"):
        t_el = li.select_one(".s-item__title")
        p_el = li.select_one(".s-item__price")
        if not (t_el and p_el):
            continue
        title = t_el.get_text(" ", strip=True)
        if title.lower() in ("shop on ebay", ""):
            continue
        price = _price_from(p_el)
        if price and 5 <= price <= 5000:
            yield title, price


def _fetch_sold(cat_id, page):
    url = (f"https://www.ebay.com/sch/i.html?"
           f"_sacat={cat_id}&LH_Sold=1&LH_Complete=1&_pgn={page}")
    html = fetch(url, referer="https://www.ebay.com/")
    polite_sleep()
    return html


def build_catalog(log=print):
    """
    Scrape a few pages of sold listings across categories, group by
    similar titles, and return a catalog of median sold prices.
    """
    log("Building sold-price catalog from eBay…")

    # Map tokens -> list of (title, price)
    groups = defaultdict(list)
    pages_fetched = 0
    pages_blocked = 0

    for cat_label, cat_id in EBAY_CATEGORIES.items():
        log(f"  · {cat_label}", flush=True)
        for page in range(1, PAGES_PER_CATEGORY + 1):
            html = _fetch_sold(cat_id, page)
            if html is None:
                pages_blocked += 1
                log(f"    page {page}: blocked/skipped")
                continue
            pages_fetched += 1
            count = 0
            for title, price in _parse_sold_page(html):
                # Skip bundles from the catalog — they distort medians.
                if analyze_bundle(title)["is_bundle"]:
                    continue
                tokens = _tokenize(title)
                if len(tokens) >= 3:
                    groups[tokens].append((title, price))
                    count += 1
            log(f"    page {page}: {count} comps")

    # Also merge near-duplicate token sets (≥75% overlap) so small
    # wording variations roll up together.
    merged = _merge_similar(groups)

    catalog = []
    for tokens, rows in merged.items():
        if len(rows) < 3:
            continue  # need 3+ comps for any confidence
        prices = [p for _, p in rows]
        catalog.append({
            "tokens":       tokens,
            "label":        rows[0][0],  # representative title
            "median_price": round(statistics.median(prices), 2),
            "samples":      len(rows),
        })

    # Sort by sample count (most reliable first)
    catalog.sort(key=lambda e: e["samples"], reverse=True)
    log(f"Catalog built: {len(catalog)} items from {pages_fetched} pages "
        f"({pages_blocked} blocked)")
    return catalog


def _merge_similar(groups):
    """Token-set buckets with ≥75% overlap get merged."""
    keys = list(groups.keys())
    parent = {k: k for k in keys}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i in range(len(keys)):
        a = keys[i]
        for j in range(i + 1, len(keys)):
            b = keys[j]
            if not a or not b:
                continue
            overlap = len(a & b) / max(len(a | b), 1)
            if overlap >= 0.75:
                ra, rb = find(a), find(b)
                if ra != rb:
                    # Pick the larger-group canonical key
                    if len(groups[ra]) >= len(groups[rb]):
                        parent[rb] = ra
                    else:
                        parent[ra] = rb

    merged = defaultdict(list)
    for k, rows in groups.items():
        merged[find(k)].extend(rows)
    return merged
