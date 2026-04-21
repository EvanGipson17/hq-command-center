# ------------------------------------------------------------------
# http_client.py  —  polite, block-tolerant HTTP fetcher.
# ------------------------------------------------------------------
# Every scraper module calls fetch() instead of requests.get():
#   - rotates User-Agents per request
#   - randomizes delay between requests
#   - never raises on block — returns None so the caller skips cleanly
# ------------------------------------------------------------------

import random
import time

import requests

from user_agents import random_ua

# Tunables
DELAY_RANGE_SEC = (3.0, 7.0)
TIMEOUT_SEC = 20

# Signals a page is a block/captcha page instead of real content.
_BLOCK_MARKERS = (
    "captcha",
    "access denied",
    "request was blocked",
    "unusual traffic",
    "please verify",
    "robot check",
)


def polite_sleep():
    """Random pause between requests so we don't look automated."""
    time.sleep(random.uniform(*DELAY_RANGE_SEC))


def fetch(url, *, referer=None):
    """
    Fetch a URL with rotated UA + realistic headers.

    Returns HTML string on success, or None if the site blocked/erred.
    Never raises — scraping is best-effort.
    """
    headers = {
        "User-Agent":      random_ua(),
        "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection":      "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    if referer:
        headers["Referer"] = referer

    try:
        resp = requests.get(url, headers=headers, timeout=TIMEOUT_SEC)
    except requests.RequestException:
        return None

    if resp.status_code in (403, 429, 503):
        return None
    if resp.status_code >= 400:
        return None

    text = resp.text or ""
    lower = text[:4000].lower()
    if any(m in lower for m in _BLOCK_MARKERS):
        return None

    return text
