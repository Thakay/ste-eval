Here is the handoff document.

---

# Handoff: `test_invoice_due_dates` fails on CI

## Status
- The bug is not corrected.
- Work is stopped. We wait for an answer from Priya.
- **Do not merge changes until Priya answers.**

## Symptom
- `test_invoice_due_dates` fails on CI in approximately 1 of 5 runs.
- The test passes on a local computer.
- CI runners use UTC. The local computer of the previous engineer uses Europe/Berlin.

## Cause found
- File: `billing/invoice.py`, approximately line 88.
- The code calculates `due_date` with `datetime.now()`. This gives a naive datetime (no time zone).
- The code compares this value with a date from the database. The database keeps this date in UTC.

## Time window of the failures (not confirmed)
- 3 failures occurred. All 3 occurred after 22:10 UTC.
- Possible window: 22:00 to 00:00 UTC. The exact window is not known.

## Open question (not verified)
- On a UTC runner, `datetime.now()` gives UTC time.
- Thus, it is possible that the naive/UTC difference alone does not cause the CI failures.
- A 2-hour window agrees with a UTC+2 offset. Europe/Berlin is UTC+2 at this time (summer time).
- Find the component that uses a different time zone on CI. Possible components are the database, a test fixture, or the test data.

## Things tried
1. **freezegun in the test**
   - The test passes.
   - This is not a satisfactory correction. It does not correct the bug in the code.
   - Risk: users in Asia can possibly receive an incorrect due date in production.
2. **Code change on branch `fix/invoice-tz`**
   - Change in `billing/invoice.py`: `datetime.now()` → `datetime.now(timezone.utc)`.
   - **The branch is not pushed.** It is only on the local computer of the previous engineer.
   - Result: 2 other tests now fail: `test_late_fee` and `test_reminder_email`.
   - These 2 tests compare results with naive datetimes.

## Blocker
- Billing owner: Priya.
- Question in #billing: "Are due dates in customer local time or in UTC?"
- There is no answer at this time.
- You must know the answer before you select a correction.

## Possible related bug (not examined)
- The reminder cron uses server local time.
- It is possible that the cron has the same bug. Nobody examined it.

## Next steps
1. If there is no answer, ask Priya again in #billing.
2. Ask the previous engineer to push `fix/invoice-tz`. Or, do the one-line change again.
3. Find the exact failure window. In the test, set the clock to different UTC times (for example, 21:59, 22:00, 23:59, 00:00). Use freezegun only for this diagnosis.
4. Find the cause of the failure on UTC runners. Refer to "Open question".
5. When Priya answers, select the correction. Then change `test_late_fee` and `test_reminder_email` to agree with the correction.
6. Examine the reminder cron for the same bug.
7. Do not merge until Priya answers.

---

Note: The "Open question" section is my analysis. It is not in your notes. Remove it if you do not agree.

If you want this text in a file, tell me the file name.