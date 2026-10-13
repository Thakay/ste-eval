This is the handoff document.

---

# Handoff: Test `test_invoice_due_dates` fails on CI

## Status

> **WARNING:** Do not merge a change until Priya gives an answer. Priya owns the billing code.

The test `test_invoice_due_dates` fails in approximately 1 of 5 CI runs. The test passes on the local computer. The possible cause is a time zone error in `billing/invoice.py`.

## Environment

- The CI runners use UTC.
- The local computer of the author uses Europe/Berlin.
- The database keeps dates in UTC.

## Findings

1. `billing/invoice.py` calculates `due_date` with `datetime.now()`. This occurs at approximately line 88.
2. The `datetime.now()` value is naive. It has no time zone.
3. The code compares this naive value with a UTC date from the database.
4. Three CI failures occurred. All three started after 22:10 UTC.
5. Thus, the failure window is possibly 22:00 to 00:00 UTC. This window is not confirmed.

**NOTE:** On a UTC runner, `datetime.now()` gives UTC time. Thus, the naive value alone does not explain the 22:00 UTC window. But 22:00 UTC is 00:00 in Europe/Berlin during summer time (UTC+2). A component in the CI path possibly uses Berlin time. This is not examined.

## Tests done

### Test 1: freezegun in the test

- Result: The test passes.
- Problem: The bug stays in the code. Customers in Asia possibly get an incorrect due date in production.
- Do not use freezegun as the fix.

### Test 2: Change to `datetime.now(timezone.utc)`

- The change is on the branch `fix/invoice-tz`.
- The branch is **not pushed**. It is only on the local computer of the author.
- After this change, 2 other tests fail:
  - `test_late_fee`
  - `test_reminder_email`
- These 2 tests compare the result with naive datetimes.

## Open questions

1. Must due dates use the customer local time or UTC? The author sent this question to Priya in `#billing`. There is no answer at this time.
2. What causes the 22:00 UTC window? Refer to the NOTE in "Findings".
3. The reminder cron job uses the server local time. This is possibly the same bug. Nobody examined the cron job.

## Next steps

1. Wait for the answer from Priya in `#billing`.
2. Get the branch `fix/invoice-tz` from the author. Alternatively, make the change at line 88 again.
3. Examine the reminder cron job for the same time zone problem.
4. Find the exact failure window. Compare the start times of the failed CI runs with the start times of the passed CI runs.
5. When Priya gives an answer, do one of these steps:
   - If due dates use UTC: Change `test_late_fee` and `test_reminder_email` to use datetimes with a time zone.
   - If due dates use customer local time: Use the customer time zone in the fix. `datetime.now(timezone.utc)` alone is not a full fix.
6. Do not merge a change before step 1 is complete.