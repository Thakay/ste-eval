`test_invoice_due_dates` fails in approximately 1 of 5 CI runs. It passes on the local computer. CI runners use UTC. The local computer uses `Europe/Berlin`.

In `billing/invoice.py`, near line 88, the due date uses `datetime.now()`. This call returns a datetime with no time zone. The value is compared with a database date stored in UTC. This difference is a possible cause of the failure.

Three failures occurred after 22:10 UTC. The suspected failure period is 22:00–00:00 UTC, but this period is not confirmed.

The test passed with `freezegun`. This result does not prove that the production code is correct. Customers in Asia could receive incorrect due dates. This production effect is not confirmed.

Branch `fix/invoice-tz` changes the call to `datetime.now(timezone.utc)`. The change was not pushed. Two other tests now fail: `test_late_fee` and `test_reminder_email`. These tests expect datetimes with no time zone.

Priya is responsible for billing. She was asked in `#billing` whether due dates must use customer local time or UTC. No answer has been received. **Do not merge any changes until Priya answers.**

The reminder cron uses server local time. A related defect is possible, but this code was not examined.

For the next agent:

- Get Priya’s answer to establish the required time zone.
- Reproduce the failure and confirm the failure period.
- Correct the code and test expectations for the required time zone.
- Run all three tests in CI.
- Examine the reminder cron for a related defect.