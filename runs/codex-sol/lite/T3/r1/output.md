**Keep SQLite for now if it meets your latency and reliability targets. Plan a Postgres migration before adding a second app server.**

The numbers alone do not justify an urgent migration. Fifty writes per second can be workable for SQLite. Transaction length, disk performance, and traffic bursts determine whether it works for your application. User count alone tells you little about database capacity.

| Tradeoff | SQLite in WAL mode | Postgres |
|---|---|---|
| Concurrent writes | Allows one writer at a time. Long transactions delay other writers. | Allows concurrent writers, although conflicting updates can still wait. |
| Reads | Readers can usually continue during writes. Local access has little overhead. | Handles concurrent reads well. A migration does not guarantee faster reads. |
| Operations | Requires less administration. You still need safe backups and checkpoint monitoring. | Adds connection management, upgrades, configuration, and backup administration. |
| Resources | Uses relatively little memory and CPU. | Uses additional memory and CPU. It can run on your existing VPS. |
| Multiple app servers | A local database complicates shared access. | Provides a central database that both app servers can use. |

Reads dominating does not remove SQLite’s write bottleneck. A short burst or long transaction can cause delays despite a modest average write rate. Long read transactions can also delay checkpoints and let the WAL file grow.

For the current deployment:

1. Measure database latency and lock errors during peak traffic.
2. Check transaction duration, disk load, and WAL growth.
3. Test realistic traffic above your current peak.
4. Verify backups through a restore test.

Move sooner if lock errors persist, write delays breach your targets, or forecasts show little spare capacity. Keep write transactions short. A longer timeout can absorb brief contention, but it does not increase write capacity.

For two app servers, use a central Postgres database. Avoid sharing SQLite through a network filesystem. If the second server becomes a firm plan, schedule the migration while traffic remains manageable.

Postgres on the same VPS improves concurrency and supports that expansion. It does not provide high availability: the VPS remains a single point of failure.

My recommendation is a measured, planned migration. I would request peak-load evidence before accepting the contractor’s claim that you must move now.

Godspeed, Spartan.