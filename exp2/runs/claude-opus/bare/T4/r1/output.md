# Handoff: flaky `test_invoice_due_dates`

## TL;DR
`test_invoice_due_dates` fails on CI about 1 in 5 runs and passes locally. The suspected cause is a naive `datetime.now()` in `billing/invoice.py` (around line 88) being compared against UTC dates from the DB. A candidate fix exists on a **local, unpushed** branch, but it breaks two other tests. **Do not merge anything until Priya (billing owner) confirms whether due dates should be in customer-local time or UTC.**

## ⛔ Blocker
- Question posted in **#billing** to Priya: *Are due dates meant to be in customer local time or UTC?* No answer yet.
- The right fix depends on that answer. Don't merge, and don't force a direction, until it's resolved.

## Symptoms
- Flaky on CI (~1 in 5 runs). Passes on the original dev's laptop.
- CI runners are UTC. The laptop is Europe/Berlin.
- Three observed failures, all after **22:10 UTC**. The suspected failure window is **22:00–00:00 UTC**, but that's **not confirmed** (small sample).

## Suspected root cause
- `billing/invoice.py` (~line 88) computes `due_date` using `datetime.now()`, which is naive and uses the server's local time.
- That value is compared against a date from the DB, which is stored as UTC.
- **Real-world impact, not just a test problem:** users in non-UTC timezones (e.g., Asia) may be getting incorrect due dates in prod.

## What's been tried
| Attempt | Result | Notes |
|---|---|---|
| `freezegun` in the test | Test passes | **Rejected.** It hides the bug instead of fixing it. Don't ship this as the fix. |
| Change to `datetime.now(timezone.utc)` in `invoice.py` | Target test fixed, **2 other tests now fail** | `test_late_fee` and `test_reminder_email` expect naive datetimes |

## Current state of the code
- Branch: `fix/invoice-tz`, **NOT pushed**. It only exists on the original dev's machine. Ask them to push it, or recreate the one-line change.
- The branch has the `timezone.utc` change only. `test_late_fee` and `test_reminder_email` haven't been updated.

## Open questions
1. **UTC or customer-local due dates?** Waiting on Priya. This decides the fix.
2. **Exact failure window.** It's unverified. The mechanism also doesn't fully add up yet: on a UTC runner, naive `now()` already equals UTC wall time. Something else in the test path may be using a non-UTC zone (fixture, DB session timezone, `date.today()` somewhere). Worth confirming before declaring root cause found.
3. **Should `test_late_fee` and `test_reminder_email` be updated to aware datetimes,** or does the code they cover also need changes? Likely the same bug class.

## Possibly related (unchecked)
- The **reminder cron uses server local time**. It may have the same bug. Nobody has looked at it yet.

## Suggested next steps
1. Check #billing for Priya's answer, and follow up if it's still silent.
2. Get `fix/invoice-tz` pushed, or recreate it.
3. Pin down the failure window. For example, run the test with the clock frozen at times around 22:00 and 00:00 UTC, purely as a diagnostic.
4. Once the UTC/local decision is made:
   - Fix `invoice.py` accordingly.
   - Update `test_late_fee` and `test_reminder_email` to match. Check whether their code paths also need fixing.
   - Audit the reminder cron for the same issue.
5. Grep `billing/` for other naive `datetime.now()` and `date.today()` calls.
6. Merge only after Priya signs off.

---

Two things to sort out before handing off:
- **The branch is only on your machine.** Push it, or the next agent can't pick it up.
- **Add the date you asked Priya** in #billing so the next agent knows how long it's been waiting.