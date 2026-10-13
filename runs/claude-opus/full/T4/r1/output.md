Here is the handoff doc. I added a "Leads" section with my own analysis, marked as not checked.

```markdown
# Handoff: flaky `test_invoice_due_dates` (timezone bug)

Written 2026-10-12.

## Status

Not fixed. Blocked on an open question to Priya (billing owner).

## Rules

- Do not merge anything until Priya answers the open question below.
- Do not use freezegun in the test as the fix. The test then passes, but this probably hides the real bug.

## Symptom

- `test_invoice_due_dates` fails on CI in about 1 of 5 runs. It passes on Kay's laptop.
- CI runners use UTC. Kay's laptop uses Europe/Berlin.
- 3 failures were seen. All 3 started after 22:10 UTC.
- The failure window may be 22:00 to 00:00 UTC. Nobody checked the exact window.

## Bug in the code

- `billing/invoice.py`, about line 88, computes `due_date` with `datetime.now()`. This value is naive (it has no timezone).
- The code compares `due_date` with a date from the database. The database stores that date in UTC.
- Production risk: customers in Asia might get a wrong due date.

## Branch `fix/invoice-tz`

- The branch is only on Kay's laptop. It is not pushed.
- It changes `datetime.now()` to `datetime.now(timezone.utc)` in `billing/invoice.py`.
- With this change, 2 other tests fail: `test_late_fee` and `test_reminder_email`. Both expect naive datetimes.

## Open question (blocks the merge)

Are due dates meant to be in customer local time or in UTC?

- Kay asked Priya in #billing. There was no answer on 2026-10-12.
- The answer sets the fix:
  - **UTC:** keep the branch change. Update `test_late_fee` and `test_reminder_email` to use datetimes with a timezone.
  - **Customer local time:** compute `due_date` in the timezone of each customer. The branch change alone is not enough.

## Not checked

- The reminder cron uses server local time. It may have the same bug.

## Leads (not checked)

- On a UTC runner, naive `datetime.now()` returns UTC time. So the naive/UTC mix alone does not explain the CI failures. Something on CI probably uses a different timezone.
- A 22:00 to 00:00 UTC window matches a UTC+2 offset. Europe/Berlin is UTC+2 until 2026-10-25, when summer time ends.
- If Europe/Berlin is the cause, the window moves to 23:00 to 00:00 UTC after 2026-10-25.
- A 2-hour window is 1/12 of the day, but about 1 in 5 runs fail. Either most CI runs happen in the evening, or the window is wider.

## Next steps

1. Get `fix/invoice-tz` from Kay if it is still not pushed.
2. Get the start times of all failed CI runs. Check the failure window.
3. Check the CI config, the app config, the test fixtures, and the DB session for a Europe/Berlin timezone.
4. Reproduce the failure on purpose. Run the test with the system clock at 22:30 UTC, for example with libfaketime.
5. Check the reminder cron for the same bug.
6. Wait for Priya's answer. Then fix the code and the 2 failing tests to match it.
```

Two things for you:

- **Push the branch before you hand off.** A push without a merge does not break your "no merge" rule. Without it, the next agent cannot see your change. Your call.
- **The CI cause is not fully explained.** A UTC runner with naive `now()` should still give UTC. The Berlin +2 match is the strongest lead I see.

Hold the line on the midnight border, Centurion.