# Recommendation: plan the Postgres move, but don't treat it as an emergency

Your contractor is probably right that you'll end up on Postgres. They're wrong that you must move now. Plan the migration over the next few months, and finish it well before the second app server goes in.

## Why "now" isn't justified on performance

- **50 writes/sec is low for SQLite in WAL mode.** On an SSD with `synchronous=NORMAL`, SQLite typically handles hundreds to thousands of short write transactions per second. Writes are serialized, but each one holds the lock for a millisecond or two, so you're using a small fraction of capacity.
- **Read-heavy workloads suit SQLite well.** In WAL mode, readers don't block writers, and in-process reads avoid network round-trips entirely.
- **2,000 active users on one box is a normal SQLite deployment.**

If you aren't seeing `database is locked` errors, write-latency spikes, or WAL files growing without bound, you don't have a database problem today.

## Why Postgres is still the likely destination

- **The second app server is the real deadline.** SQLite needs every process on the same host. WAL relies on shared memory, and running SQLite over NFS or another network filesystem risks corruption. Two app servers can't safely share one SQLite file.
- **The workarounds are niche.** LiteFS, rqlite, and libSQL/Turso exist, but they have little Django ecosystem support. You'd trade a well-understood migration for unusual infrastructure. I wouldn't do it.
- **Migrating is easier when it's calm.** A smaller dataset and no time pressure make a cleaner cutover than a forced move during a scaling crunch.

## Tradeoffs

| | Stay on SQLite | Move to Postgres |
|---|---|---|
| Ops burden | Very low: one file, no service | A service to tune, back up, upgrade, and monitor |
| Read latency | Excellent (in-process) | Slightly higher per query; N+1 patterns hurt more |
| Write concurrency | Single writer; fine at your load | True concurrent writers |
| Multiple app servers | Not viable | Standard |
| Backups / PITR | Litestream works well | Mature tooling (pgBackRest, WAL archiving, managed snapshots) |
| Django features | `select_for_update` is a no-op; table-rebuilding migrations; weaker typing | Full support: `select_for_update`, full-text search, JSON ops, constraints |
| Schema migrations | Large tables get rebuilt and locked | Most `ALTER`s are cheap |
| Cost | $0 | $0 on the same box, or about $15–60/mo managed |

## Migration gotchas to plan for

- **Lax typing in SQLite.** It doesn't enforce `max_length`, and it accepts the wrong type in columns. Expect some data to fail on import into Postgres.
- **Case sensitivity.** On SQLite, `__contains` behaves like `__icontains` for ASCII. On Postgres it's case-sensitive, so search behavior may change.
- **Sequences.** After bulk-loading data, reset them (`manage.py sqlsequencereset`), or new inserts will collide with existing IDs.
- **Raw SQL** and anything that depends on SQLite-specific functions.
- **N+1 queries.** These cost almost nothing in-process but add up over a socket. Profile your hot pages after the switch.

## What I'd do

**Now (low effort, protects you either way):**
1. Harden SQLite. Set `busy_timeout=5000`, `synchronous=NORMAL`, and `foreign_keys=ON`. On Django 5.1+, set `"transaction_mode": "IMMEDIATE"` in `OPTIONS`. This prevents most `database is locked` errors, which come from deferred transactions trying to upgrade to write locks.
2. Keep write transactions short, and never make HTTP or API calls inside them.
3. If you don't already have off-box backups, set up Litestream to replicate to S3-compatible storage.

**Next 1–3 months:**

4. Run your test suite against Postgres in CI. This shows you the incompatibilities cheaply.
5. Rehearse the data migration (pgloader, or a custom script) and validate row counts and constraints.

**Cutover (before the second server):**

6. Take a short maintenance window. At your scale, 10–30 minutes during off-peak is reasonable: switch to read-only, do the final copy, reset sequences, switch over. Keep the SQLite file around as a rollback.

## One more question to settle

What is the second app server for?
- **If it's for capacity:** a bigger VPS is usually cheaper and simpler. A 4 vCPU box has a lot of headroom for 2,000 users.
- **If it's for redundancy:** Postgres on app server #1 just moves the single point of failure. You'd want managed Postgres or a dedicated DB host. That decision affects where you put Postgres during the migration, so make it first.

**Bottom line:** the contractor has the right destination and the wrong urgency. Harden what you have this week, and migrate deliberately over the next quarter.