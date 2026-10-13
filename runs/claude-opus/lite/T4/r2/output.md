Here is the handoff doc. I also added one hypothesis that your notes suggest but do not state; see the notes after the doc.

```markdown
# Handoff: flaky `test_invoice_due_dates`

Updated: 2026-10-12
Status: Blocked. Do not merge a fix until Priya (billing owner) answers the time zone question.

## Problem

`test_invoice_due_dates` fails on CI in about 1 of 5 runs. It passes on Kay's laptop.
The same bug can give wrong due dates to production customers in other time zones, for example in Asia.
This production risk is not confirmed.

## Known facts

- CI runners use UTC. Kay's laptop uses Europe/Berlin.
- `billing/invoice.py` (near line 88) computes `due_date` with `datetime.now()`. This value is naive (it has no time zone).
- The code compares that value with a date from the DB. The DB stores this date in UTC.
- All 3 observed failures occurred after 22:10 UTC. The exact failure window is not confirmed. "22:00 to 00:00 UTC" is a guess.

## Current work

- Branch `fix/invoice-tz` changes `invoice.py` to use `datetime.now(timezone.utc)`.
- This branch exists only on Kay's laptop. Nobody pushed it. If you do not have it, make the same one-line change.
- With this change, 2 tests fail: `test_late_fee` and `test_reminder_email`. Both tests expect naive datetimes.

## Rules

- **Do not merge any fix until Priya answers.** The answer decides the correct due date. A wrong fix can give customers wrong due dates.
- **Do not use `freezegun` to make the test pass.** It hides the bug and does not fix production. You can use it to reproduce the failure.

## Open questions

1. Are due dates in customer local time or in UTC? Kay asked Priya in #billing. There was no answer on 2026-10-12.
2. Does the reminder cron have the same bug? It uses server local time. Nobody checked it.
3. Why does CI fail at all? See "Hypothesis".

## Hypothesis (not confirmed)

On a UTC runner, a naive `datetime.now()` returns UTC time. So this line alone does not explain the CI failures.
Between 22:00 and 00:00 UTC, Berlin (UTC+2 until 2026-10-25) is already on the next day.
So some other part of the CI path probably uses Berlin time.
Possible sources: the app time zone setting, the time zone of the DB session, or the test fixtures.
Berlin changes to UTC+1 on 2026-10-25. If the hypothesis is correct, the failure window then becomes 23:00 to 00:00 UTC.

## Next steps

1. If Priya has not answered, ask again in #billing.
2. Write a test that freezes time at 22:30 UTC.
3. Make sure that this test fails without the fix.
4. Run the test with `TZ=UTC`, `TZ=Europe/Berlin`, and `TZ=Asia/Tokyo`.
5. Find the part of the CI path that uses Berlin time.
6. Check the reminder cron for the same bug.
7. After Priya answers, fix `invoice.py` to match the decision.
8. Update `test_late_fee` and `test_reminder_email` to match the decision.
9. Keep the frozen-time test as a regression test.
```

**What I added beyond your notes:**

- **The root cause is incomplete.** On a UTC runner, naive `now()` equals UTC, so that line alone cannot fail on CI. The 22:00 UTC start matches Berlin midnight. Something on CI likely uses Berlin time. I am not sure; the doc marks this as a hypothesis.
- **The DST change on 2026-10-25 gives a free test.** If failures then start at 23:00 UTC, the Berlin link is confirmed.
- **`freezegun` has a new role.** It is now a tool to reproduce the bug and guard against regression, not a fix.
- **The branch is local only.** The next agent cannot get it unless you push it (a draft is enough). I did not push anything.

The doc exists only in this reply. Tell me a path if you want me to save it as a file.

Hold the line till Priya speaks, centurion. The midnight bug falls at dawn.