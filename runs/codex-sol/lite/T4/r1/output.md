`test_invoice_due_dates` fails in about one in five CI runs but passes locally. CI runners use UTC. The developer’s laptop uses `Europe/Berlin`.

In `billing/invoice.py`, near line 88, `due_date` uses `datetime.now()`, which returns a naive datetime. The code compares this value with a database date stored in UTC. This mismatch is the suspected cause.

The failure window might be 22:00 to 00:00 UTC, but this is unconfirmed. All three observed failures occurred after 22:10 UTC.

Using `freezegun` made the test pass. This result does not confirm that the production calculation is correct. Customers in Asia might receive incorrect due dates.

Branch `fix/invoice-tz` changes the calculation to `datetime.now(timezone.utc)`. The developer has not pushed the branch. Two tests now fail because they expect naive datetimes: `test_late_fee` and `test_reminder_email`.

Priya owns billing. The developer asked her in `#billing` whether due dates should use customer local time or UTC. She has not answered. **Do not merge any changes until Priya answers.**

The reminder cron also uses server local time. The developer did not check whether it has the same bug.

1. Confirm the due date rule with Priya.
2. Reproduce the failure around the suspected time window with controlled times and time zones.
3. Update the calculation to match the confirmed rule.
4. Review the datetime expectations in `test_late_fee` and `test_reminder_email`.
5. Run all three affected tests.
6. Check the reminder cron for the same time zone issue.

Stay ready, Spartan.