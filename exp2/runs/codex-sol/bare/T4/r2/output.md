**Invoice due-date flake: handoff**

- **Symptom:** `test_invoice_due_dates` fails on CI roughly one in five runs but passes locally. CI runners use UTC; the reporting developer’s laptop uses Europe/Berlin.
- **Finding:** In `billing/invoice.py` around line 88, the due date is computed using naive `datetime.now()` and compared against a date from the database stored as UTC. A timezone mismatch is suspected; the intended due-date timezone is still unknown.
- **Timing evidence:** Three observed failures occurred after 22:10 UTC. The suspected failure window is 22:00–00:00 UTC, but this is unconfirmed.
- **Work attempted:** Using `freezegun` makes the test pass, but may mask the underlying bug. There is a concern that production users in Asia could receive incorrect due dates; this has not been verified.
- **Current change:** Branch `fix/invoice-tz` changes the call to `datetime.now(timezone.utc)`. The branch has **not been pushed**. Two other tests now fail: `test_late_fee` and `test_reminder_email`, both expecting naive datetimes.
- **Pending decision:** Priya owns billing. She was asked in `#billing` whether due dates should follow customer local time or UTC; no response yet. **Do not merge anything until Priya answers.**
- **Related lead:** The reminder cron uses server local time and may have the same issue. It has not been investigated.

Suggested next steps:

1. Confirm the due-date timezone policy with Priya before finalizing the fix.
2. Reproduce the failure around the observed UTC times and relevant timezone day boundaries; establish the actual failure window.
3. Align the implementation and affected tests with the confirmed policy.
4. Investigate the reminder cron’s timezone handling.