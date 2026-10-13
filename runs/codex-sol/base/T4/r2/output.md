The billing due-date bug is still open. **Do not merge anything until Priya confirms whether due dates should use customer local time or UTC.**

Current findings:

- `test_invoice_due_dates` fails on CI roughly 1 in 5 runs but passes locally. CI runners use UTC; the local laptop uses Europe/Berlin.
- Around line 88 in `billing/invoice.py`, due dates are computed using naive `datetime.now()` and compared against a date from the database stored as UTC. This is the suspected cause, not yet confirmed.
- Three observed CI failures occurred after 22:10 UTC. The suspected failure window is 22:00 to 00:00 UTC, but that window is unverified.
- Trying `freezegun` made the test pass. That does not confirm the production behavior is correct. Incorrect due dates for users in Asia are a concern, not an observed production issue.

Work in progress:

- Branch: `fix/invoice-tz`, **not pushed**.
- Changed `invoice.py` to use `datetime.now(timezone.utc)`.
- Two other tests now fail: `test_late_fee` and `test_reminder_email`. Both expect naive datetimes.
- Treat this change as a candidate fix until the intended timezone behavior is confirmed.

Priya owns billing. She was asked in `#billing` whether due dates should follow customer local time or UTC; no answer yet.

Next steps:

1. Get Priya’s answer before deciding on the final fix or merging.
2. Make the calculation, database comparison, and test expectations consistent with that decision.
3. Verify behavior around date boundaries, including the suspected CI failure window.
4. Investigate the reminder cron, which uses server local time. It may have a related bug, but it has not been checked.

Stand ready, Spartan.