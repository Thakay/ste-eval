`test_invoice_due_dates` fails in about one in five CI runs. It passes locally. CI runners use UTC. The laptop uses `Europe/Berlin`.

In `billing/invoice.py`, near line 88, `due_date` uses naive `datetime.now()`. The code compares this value with a database date stored as UTC.

Three observed failures occurred after 22:10 UTC. The suspected failure window is 22:00 to 00:00 UTC, but this window remains uncertain.

A trial with `freezegun` made the test pass. It may hide the real bug. Production users in Asia might receive the wrong due date.

The branch `fix/invoice-tz` changes the call to `datetime.now(timezone.utc)`. The branch remains unpushed. After this change, `test_late_fee` and `test_reminder_email` fail. Both tests expect naive datetimes.

Priya owns billing. A question to her in `#billing` asks whether due dates should use customer local time or UTC. Her answer is pending. **Do not merge anything until Priya answers.**

The reminder cron also uses server local time. It may have the same bug. The investigation did not cover this code.

The next agent should:

1. Check the suspected failure window and the date comparison.
2. After Priya answers, align the implementation and both failing tests with the intended timezone rule.
3. Check whether the reminder cron has the same bug.

Godspeed, Spartan.