`test_invoice_due_dates` is flaky in CI (~1 in 5 runs fail) but passes locally. A timezone mismatch is suspected; the root cause is not confirmed. **Do not merge until Priya confirms the intended due-date timezone.**

- **Environment:** CI runners use UTC; the local laptop uses `Europe/Berlin`.
- **Finding:** Around line 88 in `billing/invoice.py`, the due date is computed using naive `datetime.now()` and compared with a DB value stored in UTC.
- **Timing evidence:** Three observed failures occurred after 22:10 UTC. The suspected 22:00–00:00 UTC failure window is unverified.
- **Test experiment:** Using `freezegun` makes the test pass, but there is concern that this masks a production bug. Incorrect due dates for users in Asia are a suspected risk, not confirmed behavior.
- **Current change:** Branch `fix/invoice-tz` changes the call to `datetime.now(timezone.utc)`. The branch has **not been pushed**. Two other tests now fail: `test_late_fee` and `test_reminder_email`, both expecting naive datetimes.
- **Pending decision:** Priya owns billing and was asked in `#billing` whether due dates should use customer local time or UTC. No response yet.
- **Related lead:** The reminder cron uses server local time and may have a similar issue. It has not been investigated.

Next steps:

1. Obtain Priya’s timezone decision before merging.
2. Reproduce the date-boundary failure and verify its timing; the current change is not yet a validated fix.
3. Trace datetime expectations through late fees and reminder emails before changing their tests.
4. Align the implementation and regression coverage with the agreed timezone semantics.
5. Investigate the reminder cron as a related follow-up.