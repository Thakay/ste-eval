# Handoff: `test_invoice_due_dates` flaky on CI

**Status:** Root cause suspected, fix drafted locally, **blocked on billing-owner decision**
**Owner of billing domain:** Priya (asked in #billing, no reply yet)

---

## ⚠️ Before you do anything

- **Do not merge anything until Priya answers** the UTC-vs-local-time question below.
- The fix branch `fix/invoice-tz` is **local only, not pushed**. If you're not on the original laptop, you won't have it. The change is small (see below) and easy to recreate.

## Symptom

- `test_invoice_due_dates` fails on CI about 1 in 5 runs and always passes locally.
- CI runners are UTC. The original dev's laptop is Europe/Berlin.
- All 3 observed failures were in CI runs after 22:10 UTC. The suspected failure window is 22:00–00:00 UTC, but that is **not confirmed** because there are only 3 data points.

## Suspected root cause

`billing/invoice.py` around line 88 computes `due_date` using `datetime.now()`. That is a naive datetime in server-local time. It is then compared against a date from the DB that is stored as UTC. Mixing naive local time with UTC means the computed due date can land on the wrong calendar day near midnight.

**Open gap in the explanation:** on a UTC runner, naive `datetime.now()` should equal UTC wall-clock time, so this alone doesn't fully explain a 22:00–00:00 UTC failure window. Something else in the path probably applies an offset, such as test fixtures, the DB session timezone, or another `now()` call. Confirm the exact mechanism before trusting the fix.

## What's been tried

| Attempt | Result | Notes |
|---|---|---|
| `freezegun` in the test | Test passes | **Rejected.** It hides the bug instead of fixing it. Prod users in far-from-UTC zones (e.g. Asia) could still get wrong due dates. |
| `datetime.now()` → `datetime.now(timezone.utc)` in `invoice.py` (branch `fix/invoice-tz`, unpushed) | Target test fixed, but `test_late_fee` and `test_reminder_email` now fail | Both tests expect naive datetimes. Whether to update them depends on Priya's answer. |

## Blocking question (asked Priya in #billing)

> Are invoice due dates meant to be in **customer local time** or **UTC**?

- **If UTC:** the `timezone.utc` fix is roughly right. Update `test_late_fee` and `test_reminder_email` to expect aware UTC datetimes, and audit other callers for naive/aware comparisons.
- **If customer local time:** the fix is bigger. Due dates need the customer's timezone, and a plain UTC switch would be wrong.

## Possibly related, not yet checked

- The **reminder cron uses server local time**. It may have the same class of bug. Nobody has looked at it yet.

## Suggested next steps

1. Follow up with Priya if there's still no answer. Don't proceed on the fix direction without it.
2. Meanwhile, pin down the failure mechanism: reproduce by running the test with the clock set to around 22:30 UTC (e.g. `TZ=UTC` plus a frozen time, *for diagnosis only*) and trace where the date shifts.
3. Collect more CI failure timestamps to confirm or refine the 22:00–00:00 UTC window.
4. Check the reminder cron for naive/local-time usage.
5. Once Priya answers, finish the fix, update the two dependent tests accordingly, push, and open a PR for Priya to review.