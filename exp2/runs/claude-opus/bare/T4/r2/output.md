# Handoff: `test_invoice_due_dates` flaky on CI

**Status:** Root cause partly identified, fix drafted locally, **blocked on product decision from Priya (billing owner)**
**Last updated:** 2026-10-12

## TL;DR

`test_invoice_due_dates` fails on roughly 1 in 5 CI runs and passes locally. The likely cause is a naive `datetime.now()` in `billing/invoice.py` (around line 88) being compared against UTC dates from the DB. This is probably a real production bug, not just a test problem. A fix exists on a local branch, but it breaks two other tests, and the correct behavior (UTC or customer-local due dates) hasn't been decided. **Do not merge anything until Priya answers.**

## Symptom

- `test_invoice_due_dates` fails on about 1 in 5 CI runs. It has never been seen failing locally.
- Environments: CI runners use **UTC**. The original investigator's laptop uses **Europe/Berlin**.
- All 3 observed failures were in CI runs **after 22:10 UTC**. The suspected failure window is 22:00–00:00 UTC, but this is **not confirmed**. It's only 3 data points.

## Root cause (what's known vs. suspected)

**Found:**
- `billing/invoice.py`, around line 88 (verify the exact line): `due_date` is computed with `datetime.now()`, which is naive and uses server-local time.
- It's compared against a date read from the DB, which is stored as UTC.

**Unresolved:**
- 22:00 UTC is exactly midnight in Berlin during summer time (CEST, UTC+2). That suggests something in the stack is applying a UTC+2 offset, for example app config, DB session timezone, or a test fixture.
- On a pure-UTC runner, a naive `now()` should match UTC, so the naive-vs-UTC mismatch alone doesn't fully explain why this fails **only on CI**. Something else is likely involved. Find it before trusting the fix.
- **Testable prediction:** if this is Berlin-offset related, the failure window should shift to **23:00–00:00 UTC** after DST ends on **2026-10-25**.

## What's been tried

| Attempt | Result | Notes |
|---|---|---|
| `freezegun` in the test | Test passes | Rejected as the fix because it hides the bug. Users in Asia (and other non-UTC zones) could get wrong due dates in prod. Still useful for **reproducing** the failure (see next steps). |
| `datetime.now()` → `datetime.now(timezone.utc)` in `invoice.py` | Target test passes; **2 other tests now fail** | `test_late_fee` and `test_reminder_email` expect naive datetimes. |

## Current state of code

- Branch `fix/invoice-tz` contains the `timezone.utc` change.
- ⚠️ **It's only on the original investigator's laptop and was never pushed.** Ask them to push it, or recreate it (it's a one-line change).
- Nothing has been merged, and nothing is in review.

## Blocker

A question was posted in **#billing** to **Priya** (billing owner): *are due dates meant to be in the customer's local time or UTC?* No answer yet.

**Constraint: don't merge anything until Priya answers.** The right fix depends on the answer:

- **If UTC:** keep `datetime.now(timezone.utc)`, then update `test_late_fee` and `test_reminder_email` (and whatever code they exercise) to use aware UTC datetimes.
- **If customer-local:** the fix is larger. `due_date` needs to be computed in the customer's timezone, which means finding out where that's stored, if anywhere. The `timezone.utc` change alone is not the fix.

## Suggested next steps

1. Follow up with Priya in #billing if there's still no answer. Don't start a fix that depends on the answer.
2. **Reproduce deterministically:** on unmodified code, freeze time to about 22:30 UTC in the test and confirm it fails. Then try about 21:30 UTC and confirm it passes. This confirms the window and the root cause.
3. Find the source of the UTC+2 offset on CI: app timezone config, DB connection/session TZ, test fixtures, and how the DB value is converted to a date.
4. Check the **reminder cron**. It reportedly uses server-local time and may have the same bug. **Not yet investigated.**
5. Once Priya decides, implement the fix and add regression tests pinned to the day-boundary times (just before and after midnight UTC, and in a non-UTC customer zone if the answer is local time).

## Open questions

- UTC or customer-local due dates? (Priya)
- What introduces the UTC+2 offset on CI?
- Is the failure window really 22:00–00:00 UTC?
- Does the reminder cron have the same issue? What timezone are prod servers in?
- Are there other naive `datetime.now()` calls in `billing/`?

---

One thing I added beyond your notes: the 22:00 UTC = midnight CEST observation, plus the point that a naive `now()` on a UTC runner shouldn't by itself cause CI-only failures. I flagged both as unresolved rather than as findings. Delete them if you've already ruled that out.