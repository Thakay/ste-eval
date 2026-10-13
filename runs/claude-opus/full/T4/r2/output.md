Here is the handoff doc.

```markdown
# Handoff: flaky `test_invoice_due_dates`

Status as of 2026-10-12.

**Rule: do not merge anything until Priya (billing owner) answers the open question below.**

## Problem

`test_invoice_due_dates` fails on CI in about 1 of 5 runs. It passes on the local laptop.

- CI runners use UTC.
- The local laptop uses Europe/Berlin.

## Known cause

`billing/invoice.py` (near line 88) computes `due_date` with `datetime.now()`.
This value is naive (it has no time zone).
The code compares it with a date from the database. The database stores that date in UTC.

## Failure window (not confirmed)

All 3 observed failures ran after 22:10 UTC.
The suspected window is 22:00 to 00:00 UTC. This window is a guess from 3 data points.

## Approaches tried

| Approach | Result | Status |
|---|---|---|
| `freezegun` in the test | The test passes. | Rejected. It hides the bug. Production users in Asia may still get a wrong due date. |
| `datetime.now(timezone.utc)` in `invoice.py` | `test_late_fee` and `test_reminder_email` now fail. Both expect naive datetimes. | On branch `fix/invoice-tz`. Local only, not pushed. |

The notes do not record if `test_invoice_due_dates` passes with this change.

## Open question (blocks merge)

The question is in #billing (Slack channel) for Priya: are due dates meant to be in customer local time or in UTC? No answer yet.

The answer decides the fix:

- **UTC:** keep the `timezone.utc` change. Update `test_late_fee` and `test_reminder_email` to expect timezone-aware datetimes.
- **Customer local time:** the UTC change is not enough. The due date calculation must use the customer time zone.

## Not checked

The reminder cron uses server local time. It may have the same bug. Nobody checked it yet.

## Next steps

1. Wait for Priya's answer in #billing. Do not merge before it.
2. Confirm the failure window. Compare the UTC start times of failing and passing CI runs.
3. Check that `test_invoice_due_dates` passes on `fix/invoice-tz` inside the failure window. Use a frozen time in that window to test it.
4. Check the reminder cron for the same naive-time problem.
5. After Priya answers, complete `fix/invoice-tz` to match the answer. Fix the 2 broken tests.
```

Suggestions before you hand it over:

- **Push the branch.** `fix/invoice-tz` exists only on your laptop. Push it without a PR, or the next agent starts from zero. Pushing does not break the "no merge" rule.
- **The cause may be incomplete.** On a UTC runner, a naive `datetime.now()` already returns UTC wall time. So the naive vs UTC mismatch alone may not shift the date on CI. The 2-hour window matches the current Berlin offset (UTC+2). Something in the test path, such as a fixture or a hardcoded zone, may carry Berlin time. Worth one line in "Open question" or "Not checked".
- **The numbers do not fully agree.** A 2-hour window is 1/12 of the day, but the failure rate is 1 in 5. Either CI runs cluster in the evening, or the window is wider. Step 2 will tell.

Shields locked, centurion. March on.