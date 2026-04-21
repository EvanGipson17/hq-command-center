# ------------------------------------------------------------------
# flip_analyzer.py  —  turn raw candidate listings into flip alerts.
# ------------------------------------------------------------------
# A "candidate" is a normalized listing dict from any source module:
#   {
#     "source":     "eBay" | "Craigslist" | ...
#     "title":      str,
#     "price":      float | None,       # None = "contact for price"
#     "url":        str,
#     "location":   str | None,         # free-text location if known
#     "is_local":   bool,               # true if clearly Austin pickup
#     "shippable":  bool,               # true if clearly ships
#   }
#
# Flip rules:
#   - Match the candidate against the catalog (catalog.py).
#   - If catalog median is ≥ 30% higher than candidate price → flip.
#   - Need at least 3 sold comps for the matched item.
#   - Confidence: 3-5 comps LOW, 6-14 MEDIUM, 15+ HIGH.
#   - For bundles: estimated_total = item_count * per-item median;
#     flag when bundle_price * 1.4 < estimated_total.
# ------------------------------------------------------------------

import re

from catalog import _tokenize
from bundle_detector import analyze as analyze_bundle

# Tunables
MIN_MARGIN        = 0.30
BUNDLE_MULTIPLIER = 1.4     # bundle must pay back 140% of its price
MIN_COMPS         = 3
SHIP_EST          = 12.00   # flat shipping deduction for shipped flips


def _confidence(samples):
    if samples >= 15:
        return "HIGH"
    if samples >= 6:
        return "MEDIUM"
    return "LOW"


def _best_catalog_match(cand_tokens, catalog):
    """Return (entry, overlap_score) or (None, 0) — Jaccard on tokens."""
    best = None
    best_score = 0.0
    for entry in catalog:
        union = cand_tokens | entry["tokens"]
        if not union:
            continue
        score = len(cand_tokens & entry["tokens"]) / len(union)
        if score > best_score:
            best = entry
            best_score = score
    return best, best_score


def _recommend_venues(source, is_local):
    """Where to resell, based on source + pickup status."""
    if is_local:
        base = ["Facebook Marketplace (Austin)", "Craigslist Austin", "OfferUp Austin"]
    else:
        base = ["eBay", "Mercari"]
    # Add marketplace-specific hints
    if source in ("Depop", "Poshmark"):
        base = ["Poshmark", "Depop", "eBay"]
    return base


def analyze(candidates, catalog, log=print):
    """Run the full analysis. Returns a list of flip dicts."""
    flips = []
    for c in candidates:
        if not c.get("price"):
            continue

        bundle = analyze_bundle(c["title"])
        cand_tokens = _tokenize(c["title"])
        if len(cand_tokens) < 2:
            continue

        match, score = _best_catalog_match(cand_tokens, catalog)
        if not match or score < 0.25 or match["samples"] < MIN_COMPS:
            continue

        # ---- bundle case -------------------------------------------
        if bundle["is_bundle"] and bundle["item_count"]:
            est_total = bundle["item_count"] * match["median_price"]
            if c["price"] * BUNDLE_MULTIPLIER >= est_total:
                continue
            profit = est_total - c["price"] - (0 if c["is_local"] else SHIP_EST)
            if profit <= 0:
                continue
            margin = profit / est_total
            flips.append(_build_flip(
                c, match, score,
                buy_price=c["price"],
                sell_price=round(est_total, 2),
                profit=round(profit, 2),
                margin_pct=round(margin * 100, 1),
                kind="bundle",
                note=f"Estimated {bundle['item_count']} items × "
                     f"${match['median_price']:.2f} each",
            ))
            continue

        # ---- single-item case --------------------------------------
        median = match["median_price"]
        ship = 0 if c["is_local"] else SHIP_EST
        net_buy = c["price"] + ship
        if net_buy >= median * (1 - MIN_MARGIN):
            continue
        profit = median - net_buy
        if profit <= 0:
            continue
        margin = profit / median
        flips.append(_build_flip(
            c, match, score,
            buy_price=c["price"],
            sell_price=round(median, 2),
            profit=round(profit, 2),
            margin_pct=round(margin * 100, 1),
            kind="single",
            note=None,
        ))

    # Only HIGH + MEDIUM go in the email (LOW is noisy).
    flips = [f for f in flips if f["confidence"] in ("HIGH", "MEDIUM")]
    flips.sort(key=lambda f: (f["confidence"] == "HIGH", f["margin_pct"]),
               reverse=True)
    log(f"Analyzer produced {len(flips)} HIGH/MEDIUM flips.")
    return flips


def _build_flip(cand, match, score, *, buy_price, sell_price,
                profit, margin_pct, kind, note):
    return {
        "kind":         kind,           # "single" | "bundle"
        "title":        cand["title"],
        "source":       cand["source"],
        "buy_price":    round(buy_price, 2),
        "sell_price":   sell_price,
        "profit":       profit,
        "margin_pct":   margin_pct,
        "confidence":   _confidence(match["samples"]),
        "sold_samples": match["samples"],
        "comp_label":   match["label"],
        "match_score":  round(score, 2),
        "buy_url":      cand["url"],
        "location":     cand.get("location") or ("Austin, TX" if cand["is_local"] else "Ships"),
        "is_local":     cand["is_local"],
        "shippable":    cand["shippable"],
        "sell_on":      _recommend_venues(cand["source"], cand["is_local"]),
        "note":         note,
    }
