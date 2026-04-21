# HEARTBEAT

This file defines the rules OpenClaw follows every 30 minutes during its heartbeat check.

## Rules

1. **Check for urgent emails**
   - Scan `evangipson90@gmail.com` for unread messages marked urgent, flagged, or containing keywords: "urgent", "ASAP", "emergency", "today", "deadline".
   - If any urgent emails are found, send a Telegram notification to @EvanGipsonAI_bot with a summary.

2. **Check calendar for upcoming events**
   - Check Google Calendar for any events starting within the next 60 minutes.
   - If an upcoming event is found, send a Telegram reminder to @EvanGipsonAI_bot with the event title and start time.

3. **If nothing urgent, reply silently**
   - If no urgent emails and no upcoming events are found, do not send any Telegram message.
   - Log `HEARTBEAT_OK` to the OpenClaw log file only.
   - Do not interrupt Evan unless there is something actionable.
