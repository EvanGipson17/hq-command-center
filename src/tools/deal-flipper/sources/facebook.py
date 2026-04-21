# ------------------------------------------------------------------
# Facebook Marketplace — intentionally stubbed.
# ------------------------------------------------------------------
# Facebook Marketplace requires login and uses aggressive bot
# detection. Scraping it also violates their Terms of Service.
#
# We include this file so the pipeline is consistent, but it never
# fetches anything. If you want FB coverage later, the right approach
# is a logged-in Playwright session — NOT requests-based scraping.
# ------------------------------------------------------------------

NAME = "Facebook Marketplace"


def gather(log=print):
    log("    · skipped (login required; ToS prohibits unauth scraping)")
    return [], "skipped (auth)"
