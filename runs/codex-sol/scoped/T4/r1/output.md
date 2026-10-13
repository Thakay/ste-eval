`test_invoice_due_dates` fails on CI in about one in five runs. It passes locally. CI runners use UTC. The local laptop uses Europe/Berlin.

In `billing/invoice.py`, near line 88, `due_date` uses naive `datetime.now()`. The calculation compares this value with a database date stored as UTC. This time mismatch is a suspected cause.

Three observed failures occurred after 22:10 UTC. The suspected failure window is 22:00 to 00:00 UTC. The exact window remains unconfirmed. Incorrect production due dates for users in Asia are a concern, but remain unconfirmed.

Current work:

- Freezegun made the test pass, but it may hide the production issue.
- Branch `fix/invoice-tz` changes the calculation to `datetime.now(timezone.utc)`.
- The branch has not been pushed.
- `test_late_fee` and `test_reminder_email` now fail because they expect naive datetimes.

Priya owns billing. She was asked in `#billing` whether due dates should use customer local time or UTC. Her answer is pending.

Do not merge any changes until Priya answers. The intended time basis is still unknown.

Next steps:

1. Check for Priya’s answer in `#billing`.
2. If Priya confirms the time basis, review the calculation against that rule.
3. Resolve the datetime expectations in `test_late_fee` and `test_reminder_email`.
4. Reproduce the failure around the suspected UTC time window.
5. Run the affected tests with UTC and Europe/Berlin settings.
6. Investigate the reminder cron, which uses server local time.

The reminder cron may have a related issue. It has not been investigated.

Godspeed, Spartan.