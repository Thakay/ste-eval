Here is the handoff doc. I did not save it to a file.

```markdown
# Handoff: flaky test `test_invoice_due_dates`

## Status

`test_invoice_due_dates` fails on CI in about 1 of 5 runs. It passes on Kay's laptop.
The probable cause is a timezone mismatch in `billing/invoice.py`.
The fix waits for a decision from Priya, the billing owner.

## Rules

1. Do not merge a fix until Priya answers the timezone question in #billing.
2. Do not use `freezegun` as the fix. It hides the real bug in production.
   You may use it to run the test at specific times.

## Facts

- CI runners use UTC. Kay's laptop uses Europe/Berlin.
- `billing/invoice.py` computes `due_date` with `datetime.now()` near line 88.
  This value is naive (it has no timezone).
- The code compares this value with a date from the database. The database stores that date in UTC.
- In production, users in Asia possibly get a wrong due date.
- All 3 recorded CI failures started after 22:10 UTC.

## Branch `fix/invoice-tz`

- The branch is only on Kay's laptop. Nobody pushed it.
- The branch changes `datetime.now()` to `datetime.now(timezone.utc)` in `billing/invoice.py`.
- With this change, 2 other tests fail: `test_late_fee` and `test_reminder_email`.
- Both tests expect naive datetimes.

## Open items

1. **Due date timezone.** Priya must decide if due dates use UTC or the customer's local time.
   Kay asked in #billing. Priya has not answered.
2. **Failure window.** The suspected window is 22:00 to 00:00 UTC.
   Only 3 failures support this. Nobody confirmed it.
3. **CI cause.** CI runs in UTC, so naive `datetime.now()` alone does not explain the CI failures.
   22:00 UTC is 00:00 in Berlin during summer time (UTC+2).
   Possibly a part of CI (database, app config, or test fixture) uses Europe/Berlin. Nobody checked this.
   Summer time ends on 2026-10-25. After that date, the window possibly moves to 23:00 to 00:00 UTC.
4. **Reminder cron.** The reminder cron uses server local time. It possibly has the same bug. Nobody checked it.

## Next steps

1. Read #billing for an answer from Priya.
2. If `fix/invoice-tz` is not on the remote, make the one-line change again.
3. Run `test_invoice_due_dates` with the clock fixed at 21:30, 22:30, and 23:30 UTC.
4. Record which times fail. Update the failure window in this doc.
5. Search CI config, database settings, and test fixtures for Europe/Berlin or other non-UTC timezones.
6. Check if the reminder cron has the same timezone bug.
7. If due dates use UTC, keep the `fix/invoice-tz` change.
8. If due dates use customer local time, compute `due_date` in the customer's timezone.
9. Update `test_late_fee` and `test_reminder_email` to expect timezone-aware datetimes.
10. Add a regression test with the clock fixed at 23:30 UTC.
11. If Priya has answered and all tests pass, open a pull request.
```

**What I added beyond your notes:**

- **A gap in the cause (open item 3).** CI runs in UTC, so a naive `datetime.now()` there should match a UTC date from the DB. The failure window starting at exactly Berlin midnight suggests something on CI runs in Berlin time. I have not seen the code, so this is a lead, not a finding.
- **The branch is invisible to the next agent.** It lives only on your laptop. I suggest you push it now without a PR. Your notes only block merging, but it is your call since the remote is shared. Step 2 covers the case where you don't.
- **freezegun as a probe, not a fix.** Steps 3 and 4 pin the clock at three times to confirm the window in minutes, instead of waiting for random CI failures.

Want me to save it to a file? I can also drop the DST line if you expect this bug to close before 2026-10-25.

Hold the line, clockwarden. Midnight does not get past you.