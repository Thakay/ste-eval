# Handoff: flaky `test_invoice_due_dates`

Updated: 2026-10-12

## Status

- **Problem:** `test_invoice_due_dates` fails in about 1 of 5 CI runs. It passes on a local machine.
- **Likely cause:** `billing/invoice.py` (about line 88) computes `due_date` with naive `datetime.now()`. The code compares that value with a DB date stored in UTC.
- **Draft fix:** The draft fix is on branch `fix/invoice-tz`. Nobody pushed this branch. It exists only on Kay's laptop.
- **Blocker:** Priya (billing owner) must decide if due dates use UTC or customer local time. Kay asked in #billing. There is no answer yet.

## Rules

1. Do not merge anything until Priya answers. Nobody decided the time zone for due dates yet, so a merge can ship the wrong behavior.
2. Do not use freezegun as the fix. It makes the test pass but hides the real bug. Production users in Asia can possibly get the wrong due date.

## Facts

- CI runners use UTC. Kay's laptop uses Europe/Berlin.
- Kay saw 3 failures. All 3 started after 22:10 UTC.
- The suspected failure window is 22:00 to 00:00 UTC. This window is not confirmed.

## What does not fit yet

- On a UTC runner, naive `datetime.now()` already returns UTC time. So this comparison alone does not explain the CI failures.
- Some other part of the CI run possibly uses a different time zone. Possible sources are the DB container, the test fixtures, and the `TZ` variable.
- 22:00 UTC is midnight in Berlin during summer time (UTC+2). This can be a clue, or it can be chance.
- Berlin summer time ends on 2026-10-25. If Berlin time causes the failures, the window will then move to 23:00 to 00:00 UTC.
- A 2-hour window is about 8% of the day, but the failure rate is about 20%. Either more CI runs occur in the evening, or the window is wider.

## Draft fix on `fix/invoice-tz`

- The branch changes `datetime.now()` to `datetime.now(timezone.utc)` in `billing/invoice.py`.
- With this change, 2 other tests fail. Both tests expect naive datetimes:
  - `test_late_fee`
  - `test_reminder_email`

## Possible related bug

The reminder cron uses server local time. It possibly has the same bug. Nobody checked it.

## Next steps

1. Ask Kay for the `fix/invoice-tz` changes, as a pushed branch or as a diff.
2. Check #billing for an answer from Priya. If there is no answer, ask again.
3. Collect the UTC start times of failed and passed CI runs. Use them to confirm the failure window.
4. Find each part of the CI run that uses local time. Check the runner, the DB, the test fixtures, and `TZ`.
5. When Priya answers, finish the fix:
   - If due dates use UTC, keep `datetime.now(timezone.utc)`. Update `test_late_fee` and `test_reminder_email` to use aware datetimes.
   - If due dates use customer local time, compute `due_date` in the customer's time zone. Change the draft fix to match.
6. Add a regression test with freezegun. Freeze the time inside the failure window, for example at 22:30 UTC.
7. If due dates use customer local time, also test a customer in an Asian time zone.
8. Check the reminder cron for the same bug.
9. Merge only after Priya approves the time zone rule.

## Contacts

- Priya: billing owner. Channel: #billing.
- Kay: has the local branch and the original session notes.

---

**What I added to your notes:**

- **The root cause is not proven.** On a UTC runner, naive `datetime.now()` already gives UTC. So something else in CI probably uses another time zone.
- **There is a Berlin clue.** 22:00 UTC is midnight in Berlin in summer time. After 2026-10-25, a 1-hour shift in the window will confirm this theory.
- **The rate does not match the window.** A 2-hour window cannot easily give a 1-in-5 failure rate.
- **The next agent cannot reach the branch.** It exists only on your laptop. Before the handoff, push it or attach the diff.
- **freezegun still has a use.** It can make a fixed-time regression test after the real fix.

If you want, I can save this doc as a file.

Shields up, timewarden. Midnight does not take this keep.