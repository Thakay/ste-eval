Here's the handoff doc, ready to drop into the repo or ticket.

---

# Handoff: flaky `test_invoice_due_dates` (timezone bug in invoice due dates)

**Date:** 2026-10-12
**Billing owner:** Priya
**Status:** Likely cause found. Fix in progress on a local branch. Blocked on a product decision.

## Hard rule

Do not merge anything until Priya answers the timezone question below.

## Symptom

- `test_invoice_due_dates` fails on CI about 1 in 5 runs. It passes locally.
- CI runners use UTC. Kay's laptop uses Europe/Berlin.
- All 3 observed failures ran after 22:10 UTC. The exact failure window is not confirmed.

## Cause

- `billing/invoice.py` (around line 88) computes `due_date` with `datetime.now()`. This is naive (no timezone) and uses the machine's local time.
- That value is compared against a date from the DB, which is stored in UTC. When the local date and the UTC date differ, the due date is off by a day.
- This is a real product bug, not only a test problem. Customers far from the server's timezone (for example in Asia) may get the wrong due date in production.

**Gap in the explanation (verify):** on a pure UTC runner, naive `now()` and UTC DB values should agree. So something on CI is probably applying Berlin time, for example an app timezone setting, the DB session timezone, or a test fixture. Supporting evidence: 22:00 UTC is midnight in Berlin during summer time (UTC+2), which matches the failures. If this is right:
- Berlin switches to UTC+1 on 2026-10-25, so the failure window will move to 23:00 to 00:00 UTC.
- A 2-hour window alone does not explain a 1 in 5 failure rate unless CI runs cluster in the evening. Compare run times of passing and failing runs in CI history.

## Work in progress

- Branch `fix/invoice-tz` changes `invoice.py` to `datetime.now(timezone.utc)`.
- **The branch is local on Kay's laptop and not pushed.** Nobody else can see it yet.
- With this change, 2 other tests fail because they expect naive datetimes: `test_late_fee` and `test_reminder_email`.

## Rejected approach

Freezing time with freezegun in the test makes it pass but hides the bug. Do not use it as the fix. It is still useful for a reproduction test (see next steps).

## Open questions

1. **(Blocking)** Are due dates meant to be in the customer's local time or in UTC? Asked Priya in #billing. No answer as of 2026-10-12.
2. What timezone do the production servers run in? This decides how bad the bug is in production today.
3. Does the reminder cron have the same bug? It uses server local time. Not checked yet.

## Next steps

1. Reproduce reliably: run `test_invoice_due_dates` with `TZ=UTC` and time frozen at 22:30 UTC. Confirm it fails, and that 21:30 UTC passes.
2. Find where Berlin time enters on CI (see "Gap in the explanation").
3. Check the reminder cron for the same pattern.
4. When Priya answers:
   - **UTC:** keep `datetime.now(timezone.utc)`, update `test_late_fee` and `test_reminder_email` to use timezone-aware datetimes, and make every due date comparison use aware UTC values.
   - **Customer local time:** compute the due date in the customer's timezone. First check whether a customer timezone is stored at all. If not, scope that change with Priya.
5. Keep the step 1 reproduction as a permanent regression test at the day boundary.
6. Merge only after Priya signs off.

---

**What I added beyond your notes:**
- The UTC-only CI failure does not fully fit the naive `now()` story. The 22:00 UTC timing points to Berlin time leaking in somewhere on CI. Worth checking before building the fix around it.
- The DST change on 2026-10-25 will shift the window, which can confuse whoever looks at this next.
- freezegun is reframed as the way to reproduce the bug on demand, not thrown out.

**You need to act on:** push `fix/invoice-tz` (push only, no merge) so the next agent can see it. Otherwise they start from zero.

Want me to save this as a file somewhere?

Hold the line until Priya speaks, timekeeper. The midnight boundary falls before you do.