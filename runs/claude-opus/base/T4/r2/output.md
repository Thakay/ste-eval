# Handoff: flaky `test_invoice_due_dates`

**As of:** 2026-10-12
**Status:** Likely cause found. A fix is drafted locally but is blocked on a product decision from Priya (billing owner).

## Rule

- **Do not merge anything until Priya answers.**

## The bug

- `test_invoice_due_dates` fails on CI about 1 in 5 runs. It passes locally.
- `billing/invoice.py:88` (approx.) computes `due_date` with naive `datetime.now()`. It then compares that against a date from the DB that is stored in UTC.
- CI runners use UTC. The original dev laptop uses Europe/Berlin.
- 3 failures were observed, all after 22:10 UTC. The suspected failure window is 22:00 to 00:00 UTC, but this is not confirmed.
- This is a real bug, not just a test problem. Prod users far from UTC (for example in Asia) may get a due date that is off by one day.

## Unexplained

- On a UTC runner, naive `datetime.now()` already equals UTC time. So the naive-vs-UTC mismatch alone should not fail on CI. Something else in the CI path is probably using a non-UTC zone. Candidates: the DB session timezone, a `TZ` setting in the test config, or a `date.today()` call somewhere else.
- A window starting at 22:00 UTC matches a UTC+2 date boundary, which is Berlin summer time. If that is the cause, the window should move to 23:00 to 00:00 UTC after DST ends on 2026-10-25.
- Confirm this before trusting the fix. The `timezone.utc` change might not fix CI at all.

## Current state of work

- **Branch `fix/invoice-tz`:** local only, NOT pushed. It changes `invoice.py` to use `datetime.now(timezone.utc)`.
- With that change, `test_late_fee` and `test_reminder_email` fail because they expect naive datetimes.
- **freezegun:** pinning time in the test makes it pass, but that hides the real bug. It is not accepted as the fix. It is still the right tool for deterministic tests once the real fix is in.

## Blocker

Question asked in #billing, with no answer yet: should due dates be in the customer's local time, or in UTC?

| Answer | Fix |
|---|---|
| UTC | Keep the `timezone.utc` change. Update `test_late_fee` and `test_reminder_email` to use aware datetimes. |
| Customer local time | Due date calculation needs the customer's timezone. This is a bigger change, so scope it before starting. |

## Open items

- Confirm the exact failure window.
- The reminder cron uses server local time and may have the same bug. Not checked yet.

## Next steps

1. Check #billing for Priya's answer.
2. Get the `fix/invoice-tz` changes. Either ask Kay to push the branch, or recreate it, since it is a one-line change.
3. Reproduce deterministically. Pin time with freezegun to 21:59 and 22:01 UTC (and 23:59 / 00:01) and see which side fails. This beats waiting for a late CI run.
4. Find the non-UTC source described under "Unexplained".
5. Apply the fix that matches Priya's answer, and update the two dependent tests.
6. Add date-boundary test cases so this cannot regress.
7. Check the reminder cron for the same issue.

---

**What I added beyond your notes:**
- **The UTC-runner puzzle.** Your notes put the cause on naive `now()`, but on a UTC box that is already UTC. Something else is probably running in Berlin time. Worth knowing before anyone ships the fix.
- **Branch reachability.** `fix/invoice-tz` exists only on your machine, so the next agent can't see it. Pushing it as a WIP branch (not merging) keeps the "don't merge" rule intact. That's your call since it's outward-facing.
- **Deterministic repro.** Use freezegun at the boundary to find the window instead of waiting for CI.

Want me to save this as a file somewhere?

Hold the line until Priya speaks, timekeeper. 🛡️