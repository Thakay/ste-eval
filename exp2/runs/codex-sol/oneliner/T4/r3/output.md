Do not merge the changes until Priya answers the time zone question.

- `test_invoice_due_dates` fails in about 1 of 5 CI runs. It passes on the local computer.
- CI runners use UTC. The local computer uses Europe/Berlin.
- In `billing/invoice.py`, near line 88, `datetime.now()` calculates `due_date` without a time zone. The code compares this value with a database date stored in UTC.
- All 3 observed failures occurred after 22:10 UTC. The possible failure window is 22:00–00:00 UTC. The exact window is not known.
- A trial with `freezegun` made the test pass. This can hide the cause of the failure. Production users in Asia can possibly receive incorrect due dates. This effect is not confirmed.
- Branch `fix/invoice-tz` changes the call to `datetime.now(timezone.utc)`. The branch has not been pushed.
- After this change, `test_late_fee` and `test_reminder_email` fail. Both tests expect datetime values without a time zone.
- Priya is responsible for billing. The question in `#billing` asks whether due dates must use customer local time or UTC. Priya has not answered.
- The reminder cron uses server local time. It can have the same fault. This has not been checked.

The next agent must:

1. Get Priya’s answer before a merge.
2. Use that answer to correct the invoice code and test expectations.
3. Run all three tests on CI.
4. Check the reminder cron for the same time zone fault.