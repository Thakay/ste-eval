Do not merge changes until Priya answers the question about the required time zone for due dates.

- `test_invoice_due_dates` fails in approximately one of five CI runs. It passes on the local computer.
- CI runners use UTC. The local computer uses `Europe/Berlin`.
- In `billing/invoice.py`, near line 88, `datetime.now()` calculates `due_date`. It returns a naive datetime. The code compares this value with a database date stored as UTC.
- Three failures occurred after 22:10 UTC. The possible failure period is 22:00 to 00:00 UTC. This period is not confirmed.
- The test passes with `freezegun`. This result does not confirm that the production problem is corrected. Users in Asia could receive incorrect due dates. This risk is not confirmed.
- Branch `fix/invoice-tz` changes the call to `datetime.now(timezone.utc)`. The branch has not been pushed. With this change, `test_late_fee` and `test_reminder_email` fail. These tests expect naive datetimes.
- Priya is responsible for billing. She was asked in `#billing` if due dates must use customer local time or UTC. No answer has been received.
- The reminder cron uses server local time. It could have the same problem. This code has not been checked.

After Priya answers:

1. Use her answer to select the required time zone.
2. Correct the implementation and tests for that requirement.
3. Check the possible failure period.
4. Check the reminder cron for the same problem.