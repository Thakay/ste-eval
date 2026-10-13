# Handoff: flaky test `test_invoice_due_dates`

## 1. Status

- The possible cause of the bug is known.
- A local change is on branch `fix/invoice-tz`. The branch is **not pushed**.
- With this change, 2 other tests fail.
- The work is stopped until Priya gives an answer (refer to section 5).

> **CAUTION:** Do not merge a change until Priya gives an answer. The correct time zone for due dates is not known.

## 2. Test results

- `test_invoice_due_dates` fails on CI in approximately 1 of 5 runs.
- The test passes on the local laptop.
- CI runners use UTC. The local laptop uses Europe/Berlin.
- 3 CI runs failed. All 3 runs started after 22:10 UTC.
- The time window for the failures is possibly 22:00 to 00:00 UTC. This window is not confirmed.

## 3. Cause (found)

In `billing/invoice.py` (approximately line 88), the code calculates `due_date` with `datetime.now()`. This value is a naive datetime (it has no time zone). The code compares this value with a date from the database. The database stores this date in UTC.

## 4. Completed tasks

**4.1 `freezegun` in the test**

- Result: the test passes.
- Note: this change does not repair the bug in `invoice.py`. It only makes the test pass.
- Risk: production users in Asia can possibly get an incorrect due date.

**4.2 Change to `invoice.py`**

- Branch `fix/invoice-tz` changes `datetime.now()` to `datetime.now(timezone.utc)`.
- The branch is only on the local laptop. It is not on the remote.
- With this change, these tests fail:
  - `test_late_fee`
  - `test_reminder_email`
- These 2 tests expect naive datetimes.

## 5. Question to the billing owner

- Owner of the billing code: Priya.
- Question (in `#billing`): Are due dates in customer local time or in UTC?
- Answer: none at this time.

## 6. Items not examined

- The reminder cron job uses server local time. It is possible that the cron job has the same bug. Nobody examined this.

## 7. Next steps

1. Get the answer from Priya in `#billing`. If there is no answer, ask again.
2. Get branch `fix/invoice-tz` from the previous engineer. You cannot get it from the remote.
3. When Priya gives the answer, select the repair:
   - **Due dates in UTC:** Keep the `timezone.utc` change. Change the code or the tests so that `test_late_fee` and `test_reminder_email` pass with aware datetimes.
   - **Due dates in customer local time:** Use the customer time zone in the calculation. The `timezone.utc` change alone is not sufficient.
4. Examine the reminder cron job for the same bug.
5. Find the exact time window for the failures. Compare the start times of more failed CI runs.
6. Do not use `freezegun` as the only repair.

## 8. Note added at handoff (not tested)

The cause in section 3 alone possibly does not cause the CI failures. If CI uses UTC, `datetime.now()` on CI gives UTC time. Then the comparison with a UTC date is correct.

The window of 22:00 to 00:00 UTC is 2 hours. Europe/Berlin is now UTC+2. In this window, the date in Berlin is one day after the date in UTC. It is possible that a different component on CI uses Europe/Berlin time. Examples: the database session, a fixture, or the test data. Examine this before you select the repair.

---

**Notes for you:**

- Section 8 is not from your notes. I added it. Remove it if you do not agree.
- The next agent cannot get branch `fix/invoice-tz`, because the branch is not pushed. Push the branch (do not merge it), or attach the diff to this document.