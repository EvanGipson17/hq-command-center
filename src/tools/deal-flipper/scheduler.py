# ------------------------------------------------------------------
# scheduler.py  —  entry point for the Deal Flipper.
# ------------------------------------------------------------------
# Usage:
#   python scheduler.py           # starts the scheduler (runs forever)
#   python scheduler.py --now     # runs one scan + email immediately
#   python scheduler.py --scan    # runs one scan, no email (prints JSON)
#
# The scheduler fires at:
#   07:45 every morning
#   18:45 every evening
# in your LOCAL time (whatever the machine this runs on).
#
# Keep this running in a terminal window (or use pythonw / a service
# manager / Windows Task Scheduler to run at login — see README.md).
# ------------------------------------------------------------------

import sys
import time
import traceback

import schedule

from scraper import run_scan
from emailer import send_report


def scan_and_email():
    try:
        payload = run_scan()
        send_report(payload)
    except Exception:
        print("!! scan_and_email failed:")
        traceback.print_exc()


def _main():
    args = set(sys.argv[1:])

    if "--now" in args:
        scan_and_email()
        return

    if "--scan" in args:
        run_scan()
        return

    # Normal mode — set up the two daily jobs and loop forever.
    schedule.every().day.at("07:45").do(scan_and_email)
    schedule.every().day.at("18:45").do(scan_and_email)

    print("Deal Flipper scheduler started.")
    print("Next runs: 07:45 and 18:45 local time (every day).")
    print("Press Ctrl+C to stop.\n")

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    _main()
