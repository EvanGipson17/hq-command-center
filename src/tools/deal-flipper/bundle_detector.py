# ------------------------------------------------------------------
# bundle_detector.py  —  does a listing look like a bundle/lot?
# ------------------------------------------------------------------
# A bundle = multiple items sold together. If we can estimate the
# individual resale value of each, a cheap bundle is often a flip.
#
# This module is pure text analysis. It returns:
#   { "is_bundle": bool, "item_count": int, "keyword": str | None }
# ------------------------------------------------------------------

import re

BUNDLE_KEYWORDS = (
    "lot", "bundle", "bulk", "collection", "set", "wholesale",
    "joblot", "mixed lot", "huge lot", "estate sale", "moving sale",
    "grab bag", "assorted", "resellers", "reseller lot", "lot of",
    "pallet", "flea market", "liquidation",
)

# Matches "lot of 12", "12 pieces", "x 20", "bundle of 5", etc.
_COUNT_PATTERNS = [
    re.compile(r"lot of\s*(\d{1,3})", re.I),
    re.compile(r"bundle of\s*(\d{1,3})", re.I),
    re.compile(r"set of\s*(\d{1,3})", re.I),
    re.compile(r"\((\d{1,3})\s*(?:pc|pcs|pieces|items|count)\)", re.I),
    re.compile(r"\b(\d{1,3})\s*(?:pc|pcs|pieces|items|count)\b", re.I),
    re.compile(r"\bx\s*(\d{1,3})\b", re.I),
]


def analyze(title):
    """Return bundle info for a listing title."""
    t = (title or "").lower()

    keyword_hit = next((kw for kw in BUNDLE_KEYWORDS if kw in t), None)

    count = None
    for pat in _COUNT_PATTERNS:
        m = pat.search(t)
        if m:
            try:
                n = int(m.group(1))
                if 2 <= n <= 500:
                    count = n
                    break
            except ValueError:
                pass

    is_bundle = keyword_hit is not None or (count and count >= 3)
    return {
        "is_bundle": bool(is_bundle),
        "item_count": count,
        "keyword": keyword_hit,
    }
