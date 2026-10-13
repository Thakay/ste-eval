The invoice due-date bug remains unresolved. Do not merge any changes until Priya answers the question about the required timezone.

- `test_invoice_due_dates` fails in about 1 in 5 CI runs. It passes locally.
- CI runners use UTC. The developer’s laptop uses `Europe/Berlin`.
- In `billing/invoice.py`, near line 88, `datetime.now()` produces a naive datetime, which has no timezone information. The code compares it against a database date stored as UTC.
- The suspected failure window is 22:00 to 00:00 UTC. This window remains unconfirmed. Three observed failures occurred after 22:10 UTC.
- A trial with `freezegun` made the test pass. The concern is that freezing time may hide the real bug. Production users in Asia might receive incorrect due dates.
- The unpushed branch `fix/invoice-tz` changes the call to `datetime.now(timezone.utc)`. With this change, `test_late_fee` and `test_reminder_email` fail. Both tests expect naive datetimes.
- Priya owns billing. The developer asked her in `#billing` whether due dates should use customer local time or UTC. Her answer is pending.
- The reminder cron uses server local time. It may have the same issue, but the developer did not investigate it.

Next steps:

1. Check for Priya’s answer about the required timezone.
2. Use that answer to assess the UTC change and the expectations in the two failing tests.
3. Try to reproduce the CI failure during the suspected window.
4. Investigate whether the reminder cron has a related timezone bug.

Godspeed, Spartan.