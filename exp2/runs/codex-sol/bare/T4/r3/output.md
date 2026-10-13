- **Bug:** `test_invoice_due_dates` is flaky on CI, failing roughly 1 in 5 runs, but passes locally. CI runners use UTC; the local laptop uses Europe/Berlin.

- **Suspected cause:** `billing/invoice.py`, around line 88, computes `due_date` using naive `datetime.now()` and compares it against a date from the database stored as UTC. The intended timezone for due dates is still unresolved.

- **Timing evidence:** Three observed failures occurred after 22:10 UTC. A possible 22:00–00:00 UTC failure window is **unconfirmed**.

- **Current work:** Branch `fix/invoice-tz` contains an **unpushed** change to `datetime.now(timezone.utc)`. Two other tests now fail: `test_late_fee` and `test_reminder_email`, which expect naive datetimes. This change is provisional pending clarification of the intended behavior.

- **Previous attempt:** Using `freezegun` makes the invoice test pass, but may mask the underlying timezone issue. Incorrect production due dates for users in Asia are a concern, not a verified impact.

- **Decision blocker:** Priya owns billing and was asked in `#billing` whether due dates should follow customer local time or UTC. No reply yet. **Do not merge anything until Priya answers.**

- **Related lead:** The reminder cron uses server local time and may have a similar issue. It has not been investigated.

- **Next steps:** Reproduce the failure around the suspected time boundary. Once Priya clarifies the timezone contract, align the implementation and affected tests with it, verify behavior across relevant timezones and date boundaries, and investigate the reminder cron.