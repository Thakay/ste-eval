**Invoice due-date bug handoff**

`test_invoice_due_dates` fails on CI roughly 1 in 5 runs but passes locally. CI runners use UTC; the local laptop uses Europe/Berlin.

- **Suspected cause:** In `billing/invoice.py`, around line 88, `due_date` is computed using naive `datetime.now()` and compared against a database date stored as UTC. The intended timezone for due dates is still unknown.
- **Timing evidence:** Three observed failures occurred after 22:10 UTC. A possible failure window of 22:00–00:00 UTC is unconfirmed.
- **Potential impact:** Production users in Asia may receive incorrect due dates. This has not been verified.

**Work already attempted**

- Freezing time with `freezegun` makes the test pass, but may hide the underlying bug.
- On branch `fix/invoice-tz`, changed the calculation to `datetime.now(timezone.utc)`. The branch has **not been pushed**.
- After that change, `test_late_fee` and `test_reminder_email` fail because they expect naive datetimes.

**Decision needed**

Priya owns billing and was asked in `#billing` whether due dates should follow customer local time or UTC. No answer yet. **Do not merge anything until Priya answers.**

**Next steps**

1. Confirm the intended timezone with Priya before finalizing behavior.
2. Reproduce the failure around UTC and customer-local date boundaries, then add regression coverage for the agreed behavior.
3. Resolve the two failing tests according to that timezone decision.
4. Investigate the reminder cron, which uses server local time and may have a related bug. It has not been checked.

Godspeed, Spartan.