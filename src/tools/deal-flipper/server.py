# ------------------------------------------------------------------
# server.py  —  tiny local API so the React dashboard's
#              "Run Manual Scan" button actually works.
# ------------------------------------------------------------------
# Run it with:   python server.py
# Listens on:    http://localhost:5001
#
# Endpoints:
#   GET  /api/health     — sanity check
#   GET  /api/results    — the most recent scan payload
#   POST /api/scan       — triggers a new scan (and emails) in the background
#
# If this server isn't running, the React page still works — it just
# reads /deal-flipper-results.json directly and the scan button shows
# a helpful error.
# ------------------------------------------------------------------

import json
import threading
from pathlib import Path

from flask import Flask, jsonify
from flask_cors import CORS

from scraper import run_scan, RESULTS_FILE
from emailer import send_report

app = Flask(__name__)
CORS(app)  # allow the React dev server (localhost:5173) to call us

_scan_lock = threading.Lock()
_scan_state = {"running": False}


def _do_scan_and_email():
    try:
        payload = run_scan()
        send_report(payload)
    except Exception as e:
        print(f"!! background scan failed: {e}")
    finally:
        _scan_state["running"] = False


@app.route("/api/health")
def health():
    return jsonify({"ok": True, "scan_running": _scan_state["running"]})


@app.route("/api/results")
def results():
    if not Path(RESULTS_FILE).exists():
        return jsonify({"scanned_at": None, "deal_count": 0, "deals": []})
    return jsonify(json.loads(Path(RESULTS_FILE).read_text()))


@app.route("/api/scan", methods=["POST"])
def scan():
    with _scan_lock:
        if _scan_state["running"]:
            return jsonify({"started": False, "reason": "scan already in progress"}), 409
        _scan_state["running"] = True

    threading.Thread(target=_do_scan_and_email, daemon=True).start()
    return jsonify({"started": True})


if __name__ == "__main__":
    print("Deal Flipper API on http://localhost:5001")
    app.run(host="127.0.0.1", port=5001)
