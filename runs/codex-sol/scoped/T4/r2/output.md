Do not merge changes until Priya confirms whether due dates use customer local time or UTC.

`test_invoice_due_dates` fails on CI in about one of five runs. It passes locally. CI runners use UTC. The laptop uses Europe/Berlin.

In `billing/invoice.py`, near line 88, `due_date` uses naive `datetime.now()`. The code compares this value with a database date stored as UTC. Three observed failures occurred after 22:10 UTC. The suspected failure window is 22:00 to 00:00 UTC, but this window remains unconfirmed.

A `freezegun` trial made the test pass. It might hide the underlying bug. Customers in Asia might receive incorrect due dates.

The branch `fix/invoice-tz` changes the calculation to `datetime.now(timezone.utc)`. The branch is not pushed. Two tests now fail: `test_late_fee` and `test_reminder_email`. Both expect naive datetimes.

Priya owns billing. She received the due date question in `#billing`, but she has not answered. The reminder cron also uses server local time. It might have the same bug, but nobody checked it during this session.

1. Wait for Priya to confirm the intended time zone.
2. If Priya confirms the intended time zone, align the due date calculation with her answer.
3. Update the affected tests to check the confirmed behavior.
4. Verify the fix with UTC and customer time zone cases.
5. Check the suspected failure window.
6. Investigate the reminder cron for the same issue.

Godspeed, Spartan.