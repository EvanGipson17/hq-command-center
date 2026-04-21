# HEARTBEAT

This file defines the rules OpenClaw executes every 30 minutes during its scheduled heartbeat check.

---

## Rule 1 — Urgent Email Check

Scan `evangipson90@gmail.com` for unread messages that meet any of the following criteria:

- Marked as important or starred
- Subject line or body contains any of these keywords: `urgent`, `ASAP`, `emergency`, `today`, `deadline`, `call me`, `need you now`

If one or more urgent emails are found, send a Telegram notification to `@EvanGipsonAI_bot` with a brief summary: sender name, subject line, and a one-sentence preview of the message body.

---

## Rule 2 — Calendar Check

Check Evan's Google Calendar for any events starting within the next **60 minutes**.

If an upcoming event is found, send a Telegram reminder to `@EvanGipsonAI_bot` with the event title, start time, and any location or meeting link attached to the event.

---

## Rule 3 — Silent OK

If no urgent emails are found and no events are starting within 60 minutes:

- Do **not** send any Telegram message.
- Log `HEARTBEAT_OK` to the OpenClaw log file only (`C:\Users\wwgip\.openclaw\logs\openclaw.log`).
- Do not interrupt Evan unless there is something actionable.
