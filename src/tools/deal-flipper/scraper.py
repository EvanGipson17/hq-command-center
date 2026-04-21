# ------------------------------------------------------------------
# scraper.py  —  orchestrator.
# ------------------------------------------------------------------
# Run order:
#   1) Build a sold-price catalog from eBay (catalog.py).
#   2) Ask every source module for candidate listings (sources/*).
#   3) Feed candidates + catalog into flip_analyzer → flips.
#   4) Write the public JSON the dashboard reads.
#
# run_scan() returns the full payload; scheduler.py wraps it with
# the emailer.
# ------------------------------------------------------------------

import json
import sys
import time
from pathlib import Path

from catalog import build_catalog
from flip_analyzer import analyze
from sources import ALL_SOURCES

RESULTS_FILE = Path(__file__).resolve().parents[2].parent / "public" / "deal-flipper-results.json"


def _log(*args, **kwargs):
    kwargs.setdefault("flush", True)
    print(*args, **kwargs)


def run_scan():
    _log("=" * 60)
    _log("Deal Flipper scan starting…")
    _log("=" * 60)

    t0 = time.time()

    # --- phase 1: catalog ------------------------------------------
    catalog = build_catalog(log=_log)
    if not catalog:
        _log("!! No catalog built — eBay may be blocking us. Aborting scan.")
        return _write_payload(deals=[], catalog_size=0, site_status={}, elapsed=0)

    # --- phase 2: gather from every source -------------------------
    _log("\nGathering candidate listings from all sources…")
    all_candidates = []
    site_status = {}

    for mod in ALL_SOURCES:
        name = getattr(mod, "NAME", mod.__name__)
        _log(f"\n  › Scanning {name}…")
        try:
            candidates, status = mod.gather(log=_log)
        except Exception as e:
            candidates, status = [], f"error: {e}"
            _log(f"    !! {name} errored: {e}")
        site_status[name] = {
            "status": status,
            "candidates": len(candidates),
        }
        all_candidates.extend(candidates)
        _log(f"     Found {len(candidates)} potential flips on {name}")

    _log(f"\nTotal candidates: {len(all_candidates)}")

    # --- phase 3: analyze ------------------------------------------
    _log("\nAnalyzing against sold-price catalog…")
    flips = analyze(all_candidates, catalog, log=_log)

    elapsed = round(time.time() - t0, 1)
    _log(f"\nScan complete in {elapsed}s — {len(flips)} high-quality flips.")
    _log("=" * 60)
    return _write_payload(flips, len(catalog), site_status, elapsed)


def _write_payload(deals, catalog_size, site_status, elapsed):
    payload = {
        "scanned_at":    int(time.time()),
        "deal_count":    len(deals),
        "deals":         deals,
        "catalog_size":  catalog_size,
        "site_status":   site_status,
        "elapsed_sec":   elapsed,
        "config": {
            "min_margin_pct":   30,
            "min_sold_samples": 3,
            "bundle_multiplier": 1.4,
        },
    }
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_FILE.write_text(json.dumps(payload, indent=2))
    print(f"Wrote results → {RESULTS_FILE}", flush=True)
    return payload


if __name__ == "__main__":
    run_scan()
