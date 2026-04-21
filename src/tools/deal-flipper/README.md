# Deal Flipper · v2

Multi-source arbitrage scanner. Builds a catalog of hot sold-prices from eBay, then hunts every other source for the same items listed cheaper right now (or for bundles worth more than their asking price).

## What it scans

| Source | Status |
|---|---|
| eBay Sold (catalog) | ✅ Fully working |
| eBay Active + Austin local pickup | ✅ Fully working |
| Craigslist Austin (for-sale, free, bundle queries) | ✅ Fully working |
| OfferUp / Depop / Mercari / Poshmark / GoodwillFinds | ⚠️ Best-effort. These sites are JS-rendered SPAs — `requests` only sees the empty shell. Parser tries to mine embedded JSON; logs which sites returned data and which were "js-rendered-shell." |
| Facebook Marketplace | ❌ Skipped — requires login + ToS-prohibited. |

Every source is wrapped with graceful failure, User-Agent rotation, and 3–7 s random delays.

## Flip rules

- **30%+ margin** over sold-median.
- **3+ sold comps** required (more = higher confidence).
- Confidence: LOW < 6, MEDIUM 6–14, HIGH 15+.
- **Only HIGH + MEDIUM** get into the email.
- **Bundles** (title contains "lot", "bundle", "estate sale", etc.) are evaluated separately: estimated total resale = item_count × per-item median. Flagged when `bundle_price × 1.4 < estimated_total`.
- **Shipped flips** get a flat $12 shipping deducted from profit. **Local Austin pickup** flips don't.

## File map

```
user_agents.py      UA rotation pool
http_client.py      polite, block-tolerant fetch()
bundle_detector.py  "is this a bundle/lot?" + item-count parser
catalog.py          builds the sold-price catalog from eBay
flip_analyzer.py    compares candidates against the catalog → flips
sources/
  ebay_active.py    current eBay listings (incl. Austin pickup)
  craigslist.py     Austin CL: for-sale + free + bundle queries
  offerup.py        best-effort
  depop.py          best-effort
  mercari.py        best-effort
  poshmark.py       best-effort
  goodwill.py       best-effort
  facebook.py       skipped (auth required)
scraper.py          orchestrator — run_scan() is the entry point
emailer.py          builds + sends the HTML email
scheduler.py        cron-style loop (07:45 + 18:45 local daily)
server.py           local Flask API for the dashboard button
```

## Setup (one-time)

```
cd src/tools/deal-flipper
pip install -r requirements.txt
```

Credentials are already in `.env` (gitignored).

## Run it

| Command | What it does |
|---|---|
| `python scheduler.py --now` | One-shot: scan + email immediately. Best first test. |
| `python scheduler.py --scan` | Scan only, no email. |
| `python scheduler.py` | Starts the daily scheduler (runs 07:45 + 18:45). |
| `python server.py` | Starts the local API on port 5001 so the dashboard scan button works. |

Typical dev flow = two terminals: `scheduler.py` in one, `server.py` in the other.

## Tuning

Edit the constants at the top of the relevant file:

- **`flip_analyzer.py`** → `MIN_MARGIN`, `BUNDLE_MULTIPLIER`, `MIN_COMPS`, `SHIP_EST`
- **`catalog.py`** → `EBAY_CATEGORIES`, `PAGES_PER_CATEGORY`
- **`http_client.py`** → `DELAY_RANGE_SEC`

## If results go to zero

1. Run `python scheduler.py --scan` and read the log — which sources are "blocked" vs "js-rendered-shell"?
2. If eBay shows "blocked" for every category: you're rate-limited. Wait 30 min, widen `DELAY_RANGE_SEC`.
3. If eBay is fine but no flips: margin too aggressive? Lower `MIN_MARGIN` or `MIN_COMPS` in `flip_analyzer.py`.
4. If the SPA sites show "js-rendered-shell" forever and you want them working, swap `http_client.py` for a Playwright-based fetcher — the rest of the pipeline works unchanged.

## Run at Windows login

1. Win + R → `shell:startup` → Enter.
2. Create `deal-flipper.bat`:
   ```
   @echo off
   cd /d "C:\Users\wwgip\hq-command-center\src\tools\deal-flipper"
   python scheduler.py
   ```
