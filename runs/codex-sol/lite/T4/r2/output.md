The invoice due date bug remains open. Do not merge any changes until Priya answers the time zone question.

- **Failure:** `test_invoice_due_dates` fails in about one in five CI runs. It passes locally.
- **Environment:** CI runners use UTC. The laptop uses `Europe/Berlin`.
- **Suspected cause:** In `billing/invoice.py`, near line 88, `due_date` uses naive `datetime.now()`. The code compares this value with a database date stored as UTC.
- **Timing:** All three observed failures occurred after 22:10 UTC. The suspected failure window, 22:00 to 00:00 UTC, remains unconfirmed.
- **Test attempt:** Using `freezegun` made the test pass. This may hide the underlying bug. Production users in Asia may receive incorrect due dates.
- **Current change:** Branch `fix/invoice-tz` changes the calculation to `datetime.now(timezone.utc)`. The branch has not been pushed. `test_late_fee` and `test_reminder_email` now fail because they expect naive datetimes.
- **Pending decision:** Priya owns billing. She was asked in `#billing` whether due dates should use customer local time or UTC. No answer has arrived.
- **Related concern:** The reminder cron uses server local time. It may have the same bug, but it has not been investigated.

Continue with these steps:

1. Check for Priya’s answer in `#billing`.
2. After Priya answers, align the calculation and test expectations with her decision.
3. Reproduce the failure around the suspected UTC window.
4. Verify `test_invoice_due_dates`, `test_late_fee`, and `test_reminder_email`.
5. Investigate whether the reminder cron has the same time zone problem.

Godspeed Spartan.