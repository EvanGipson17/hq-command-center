# Source registry. Each module exposes:
#   NAME:      str   — human label
#   gather():  returns (candidates: list[dict], status: str)
#              status is "ok", "blocked", or "skipped (reason)".
from . import ebay_active, craigslist, offerup, depop, mercari, poshmark, goodwill, facebook

ALL_SOURCES = [
    ebay_active,
    craigslist,
    offerup,
    depop,
    mercari,
    poshmark,
    goodwill,
    facebook,
]
