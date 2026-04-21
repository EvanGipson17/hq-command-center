# ------------------------------------------------------------------
# emailer.py  —  formats the scan payload into a clean HTML email
# and sends it through Gmail SMTP.
# ------------------------------------------------------------------

import os
import smtplib
import ssl
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_APP_PASSWORD")
TO_ADDRESS = os.getenv("ALERT_TO", GMAIL_USER)

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465


STYLE = """
<style>
  body  { font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;
          background:#0a0a0a; color:#f5f5f7; margin:0; padding:24px; }
  .wrap { max-width:680px; margin:0 auto; }
  h1    { font-size:20px; margin:0 0 4px; color:#10b981; letter-spacing:-0.01em; }
  .sub  { font-size:12px; color:#a1a1aa; text-transform:uppercase;
          letter-spacing:0.1em; margin-bottom:20px; }
  .section-h { font-size:11px; color:#6b6b73; text-transform:uppercase;
               letter-spacing:0.12em; margin:20px 0 8px; }
  .deal { background:#111113; border:1px solid #1f1f22; border-radius:10px;
          padding:16px; margin-bottom:10px; }
  .top  { display:flex; justify-content:space-between; margin-bottom:8px;
          font-size:11px; text-transform:uppercase; letter-spacing:0.08em; }
  .src  { color:#10b981; font-weight:600; }
  .loc  { color:#eab308; }
  .ship { color:#a1a1aa; }
  .conf-HIGH   { color:#10b981; }
  .conf-MEDIUM { color:#eab308; }
  .title{ font-weight:600; font-size:15px; margin:2px 0 10px; }
  .row  { font-size:13px; color:#d4d4d8; margin:3px 0;
          display:flex; justify-content:space-between; }
  .muted{ color:#a1a1aa; }
  .green{ color:#10b981; font-weight:600; }
  .note { font-size:12px; color:#a1a1aa; font-style:italic; margin-top:6px; }
  a.btn { display:inline-block; margin-top:10px; padding:8px 14px;
          background:#10b981; color:#0a0a0a !important; border-radius:6px;
          font-weight:600; font-size:12px; text-decoration:none;
          text-transform:uppercase; letter-spacing:0.08em; }
  .venues { font-size:11px; color:#a1a1aa; margin-top:8px; }
  .empty  { padding:24px; text-align:center; color:#a1a1aa;
            border:1px dashed #1f1f22; border-radius:10px; }
  .foot   { margin-top:24px; font-size:11px; color:#6b6b73; text-align:center; }
  table.status { width:100%; border-collapse:collapse; font-size:11px;
                 color:#a1a1aa; margin-top:8px; }
  table.status td { padding:4px 8px; border-bottom:1px solid #1f1f22; }
</style>
"""


def _confidence_chip(conf):
    return f"<span class='conf-{conf}'>{conf}</span>"


def _render_deal(d):
    loc_chip = f"<span class='loc'>📍 LOCAL PICKUP — AUSTIN TX</span>" if d["is_local"] \
               else f"<span class='ship'>✈ Ships nationally</span>"
    note = f"<div class='note'>{d['note']}</div>" if d.get("note") else ""
    profit_line = (
        f"${d['profit']:.2f} ({d['margin_pct']:.0f}%)"
        if d["is_local"]
        else f"${d['profit']:.2f} ({d['margin_pct']:.0f}%) — after est. shipping"
    )
    return f"""
    <div class="deal">
      <div class="top">
        <span class="src">{d['source']} · {d['kind'].upper()}</span>
        <span>{loc_chip} · {_confidence_chip(d['confidence'])}</span>
      </div>
      <div class="title">{d['title']}</div>
      <div class="row"><span class="muted">Buy for</span><span>${d['buy_price']:.2f}</span></div>
      <div class="row"><span class="muted">Est. resale</span><span>${d['sell_price']:.2f}</span></div>
      <div class="row"><span class="muted">Profit</span><span class="green">{profit_line}</span></div>
      <div class="row"><span class="muted">Comps</span>
        <span>{d['sold_samples']} sold · match {int(d['match_score']*100)}%</span></div>
      {note}
      <a class="btn" href="{d['buy_url']}">View listing →</a>
      <div class="venues">Resell on: {", ".join(d['sell_on'])}</div>
    </div>
    """


def _render_site_status(site_status):
    if not site_status:
        return ""
    rows = "".join(
        f"<tr><td>{name}</td>"
        f"<td>{info['status']}</td>"
        f"<td style='text-align:right'>{info['candidates']} listings</td></tr>"
        for name, info in site_status.items()
    )
    return f"""
      <div class="section-h">Source status</div>
      <table class="status">{rows}</table>
    """


def build_subject(payload):
    n = payload["deal_count"]
    today = datetime.now().strftime("%b %d")
    if n == 0:
        return f"😴 No Confident Flips Today - {today}"
    return f"🔥 {n} Flip Opportunit{'y' if n == 1 else 'ies'} Found - {today}"


def build_html(payload):
    when = datetime.now().strftime("%A, %b %d · %I:%M %p")

    # Group by local vs. shipped for the email body
    local = [d for d in payload["deals"] if d["is_local"]]
    shipped = [d for d in payload["deals"] if not d["is_local"]]

    if not payload["deals"]:
        body = f"""
        <div class="empty">
          No confident flips found this scan.<br>
          Thresholds: 30%+ margin, 3+ sold comps, HIGH/MEDIUM confidence only.
        </div>
        """
    else:
        sections = ""
        if local:
            sections += "<div class='section-h'>Austin Local Pickup</div>"
            sections += "".join(_render_deal(d) for d in local)
        if shipped:
            sections += "<div class='section-h'>Shipped Nationwide</div>"
            sections += "".join(_render_deal(d) for d in shipped)
        body = sections

    status_table = _render_site_status(payload.get("site_status", {}))

    return f"""
    <!doctype html>
    <html><head><meta charset="utf-8">{STYLE}</head>
    <body><div class="wrap">
      <h1>HQ · Deal Flipper</h1>
      <div class="sub">{when} · {payload['deal_count']} flips ·
        catalog {payload.get('catalog_size', 0)} items ·
        {payload.get('elapsed_sec', 0)}s</div>
      {body}
      {status_table}
      <div class="foot">Automated scan · HQ Command Center</div>
    </div></body></html>
    """


def send_report(payload):
    if not (GMAIL_USER and GMAIL_PASS):
        raise RuntimeError("Missing GMAIL_USER / GMAIL_APP_PASSWORD — check .env")

    msg = MIMEMultipart("alternative")
    msg["From"] = GMAIL_USER
    msg["To"]   = TO_ADDRESS
    msg["Subject"] = build_subject(payload)

    # Plain-text fallback
    if payload["deals"]:
        lines = []
        for d in payload["deals"]:
            loc = "[LOCAL AUSTIN]" if d["is_local"] else "[SHIPS]"
            lines.append(
                f"{loc} {d['source']} - {d['title']}\n"
                f"  Buy ${d['buy_price']:.2f} → Sell ~${d['sell_price']:.2f} "
                f"({d['margin_pct']:.0f}% margin, {d['confidence']})\n"
                f"  {d['buy_url']}\n"
            )
        text = "\n".join(lines)
    else:
        text = "No confident flips found this scan."
    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(build_html(payload), "html"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
        server.login(GMAIL_USER, GMAIL_PASS)
        server.sendmail(GMAIL_USER, [TO_ADDRESS], msg.as_string())
    print(f"Email sent → {TO_ADDRESS}", flush=True)
