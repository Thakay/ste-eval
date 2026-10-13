Here is the handoff doc. Beyond your notes, I added a likely root cause, a way to reproduce the failure, and a concrete plan for each of Priya's possible answers.

```markdown
# Handoff: flaky test_invoice_due_dates (time zone bug)

Updated: 2026-10-12
Status: Blocked. Wait for Priya (billing owner) to answer before you merge anything.

## Summary

`test_invoice_due_dates` fails on CI in about 1 of 5 runs. It passes on Kay's laptop.
The cause is a time zone mismatch in the due date calculation.
The correct fix depends on an open product decision.

## Rules

- Do not merge any fix until Priya answers. The correct fix depends on that decision.
- Do not use freezegun as the fix. It hides the bug. Customers in Asia can then get a wrong due date.

## Open question

Which time zone do due dates use: customer local time or UTC?
Kay asked Priya in #billing. There is no answer yet.

## Facts

- CI runners use UTC. Kay's laptop uses Europe/Berlin.
- `billing/invoice.py` (near line 88) computes `due_date` with `datetime.now()`.
- This value is naive: it has no time zone.
- The code compares this value with a date from the database. The database stores dates in UTC.
- 3 CI failures are on record. All 3 started after 22:10 UTC.
- The failure window is not confirmed. The likely window is 22:00 to 00:00 UTC.
- The reminder cron job uses server local time. Nobody has checked it for the same bug.

## Current state of the code

- Branch `fix/invoice-tz` changes `invoice.py` to `datetime.now(timezone.utc)`.
- This branch is only on Kay's laptop. It is not pushed. If you need it, ask Kay.
- On this branch, `test_late_fee` and `test_reminder_email` fail. Both tests expect naive datetimes.
- A freezegun patch in the test makes the test pass. Do not keep it as the fix.

## Hypothesis (not verified)

On a UTC runner, a naive `datetime.now()` already returns UTC time.
So the naive call alone does not explain the CI failures.
The window 22:00 to 00:00 UTC is 00:00 to 02:00 in Berlin summer time (UTC+2).
In that window, the Berlin date is one day after the UTC date.
So some part of the CI setup probably uses Europe/Berlin time.

Places to check:
- The time zone setting of the app. For example, Django sets the process time zone from `TIME_ZONE`.
- The `TZ` variable in the CI config.
- The time zone of the database connection.
- Test fixtures that create dates.

Berlin summer time ends on 2026-10-25.
If this hypothesis is correct, the window then changes to 23:00 to 00:00 UTC.

freezegun makes a naive `datetime.now()` ignore the process time zone.
This can explain why the freezegun patch makes the test pass.

## Next steps

1. Run `test_invoice_due_dates` with the system clock at 23:30 UTC. Use libfaketime, not plain freezegun.
2. Make sure the test fails. This confirms the failure window.
3. Find where Europe/Berlin time enters on CI. Use the list in "Places to check".
4. Check the reminder cron job for the same bug.
5. If Priya answers "UTC", do these steps:
   1. Apply the change from `fix/invoice-tz`.
   2. Find why `test_late_fee` and `test_reminder_email` expect naive datetimes.
   3. Fix that code to use aware (time zone) datetimes. Do not change only the tests.
   4. Add the 23:30 UTC run as a regression test.
6. If Priya answers "customer local time", do these steps:
   1. Find where the app stores the time zone of each customer. Nobody knows this yet.
   2. Compute `due_date` in the time zone of the customer. Naive time and UTC are both wrong here.
   3. Add a regression test with a customer in Asia.
7. If the reminder cron job has the same bug, fix it with the same time zone decision.
```

What I added, so you can check it:

- **Root cause guess.** Your 22:00 to 00:00 UTC window matches the 2-hour Berlin summer offset exactly. On a UTC runner, naive `now()` is already UTC, so something on CI probably runs in Berlin time. Django's `TIME_ZONE` is a classic cause because it resets the process time zone. This is my inference and nobody has verified it.
- **Free test.** If the theory holds, failures after 2026-10-25 should only happen from 23:00 UTC onward.
- **freezegun.** Plain freezegun ignores the process time zone for naive `now()`. That is probably why it "fixed" the test, and it also means plain freezegun cannot reproduce the bug. libfaketime can.
- **Fix the code, not only the tests.** `test_late_fee` and `test_reminder_email` probably expect naive datetimes because the code they cover passes naive values around.
- **Branch access.** `fix/invoice-tz` exists only on your laptop, so the next agent cannot see it. You could push it without opening a PR. That does not break your "don't merge" rule. Your call.

Tell me a path if you want this saved as a file.

Hold the line until Priya speaks, shield-bearer.