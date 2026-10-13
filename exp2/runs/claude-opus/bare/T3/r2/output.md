# Recommendation: plan the Postgres migration, but don't treat it as an emergency

The contractor has the destination right and the urgency probably wrong. At about 50 writes/sec, SQLite in WAL mode is not your bottleneck. A tuned SQLite database on local SSD handles thousands of small write transactions per second. The thing that actually forces a migration is the **second app server**. SQLite can't be safely shared across hosts: WAL needs shared memory on one machine, and network filesystems corrupt it.

So:

1. **Now (a few days of work):** harden SQLite and make the codebase Postgres-ready.
2. **Next 3–6 months, on your schedule:** migrate to Postgres as a planned project, well before the second server goes in.

Move "now" up to "this month" if any of these are true:
- You see persistent `database is locked` errors after the fixes below.
- You don't have tested backups.
- The second server is needed within about 3 months.

## Why not rush it

- **Capacity isn't the problem.** Reads in SQLite are in-process and very fast. Writes serialize, but at 50/sec each one holds the lock for only a millisecond or two.
- **Migration has its own risk.** SQLite's loose typing lets bad data in that Postgres will reject. The classic case is strings longer than `max_length`, which SQLite never enforced.
- **Postgres is another service to run.** Someone has to handle tuning, upgrades, backups, and connection management.

## Why not wait indefinitely

- **The second server requires it.** Postgres is the realistic path for multi-host Django. Distributed-SQLite tools exist (LiteFS, rqlite, libSQL), but none is a clean drop-in for Django.
- **Migration gets harder over time.** It's harder with more data and more SQLite-specific behavior baked into the code.
- **Schema changes get painful.** SQLite emulates most `ALTER TABLE` operations by rebuilding the table, which blocks writes. That gets worse as tables grow. Postgres has transactional DDL, and many alters are instant.
- **Some features silently differ.** `select_for_update()` is a no-op on SQLite. Postgres also gives you better concurrency semantics, full-text search, and point-in-time recovery.

## Step 1: harden SQLite now

- **Use `"transaction_mode": "IMMEDIATE"`** in `DATABASES["default"]["OPTIONS"]` (Django ≥ 5.1). This is the single biggest fix. Django's default deferred transactions can fail instantly with "database is locked" when a read transaction tries to upgrade to a write, and `busy_timeout` doesn't help in that case.
- **Set `"timeout": 10`** or similar so writers wait instead of erroring.
- **Set pragmas via `init_command`:** `journal_mode=WAL` and `synchronous=NORMAL`. With `NORMAL`, an app crash is safe and the database won't corrupt, but a power or OS failure can lose the last few committed transactions. Use `FULL` if that's unacceptable.
- **Keep write transactions short.** Never make HTTP calls or do slow work while holding one. Run bulk jobs in small batches.
- **Watch for WAL growth.** Long-running read transactions block checkpoints.
- **Set up real backups:** Litestream to object storage, plus a restore test. Copying the live file with `cp` is not a backup.

## Step 2: make the code Postgres-ready

- Run your test suite against Postgres in CI now. This surfaces the usual SQLite-isms:
  - `max_length` violations
  - `contains` being case-insensitive on SQLite but case-sensitive on Postgres
  - type affinity surprises
  - raw SQL
- Audit existing data for values Postgres will reject.

## Step 3: migrate

- **Load the data** with pgloader or a scripted export/import. `dumpdata`/`loaddata` is slow for large databases. Then reset sequences with `sqlsequencereset`.
- **Schedule a short maintenance window.** At 2,000 users, a planned window is far simpler than a zero-downtime migration.
- **Pool connections.** Use Django's native psycopg 3 pool (`"pool": True`, Django ≥ 5.1). Add PgBouncer when you go to multiple servers.

## Before adding the second server, ask what it's for

- **Capacity:** a bigger VPS is simpler and cheaper than going multi-host. 4 vCPU / 8 GB is modest.
- **Availability:** two app servers sharing one self-hosted Postgres still has a single point of failure. At that point, **managed Postgres** ($15–60/mo) is usually worth it for a small team, because it gives you backups, PITR, failover, and upgrades without anyone on call for them.

## Tradeoffs at a glance

| | SQLite (tuned) | Postgres |
|---|---|---|
| Your current load | Plenty of headroom | Plenty of headroom |
| Multiple app servers | No | Yes |
| Ops burden | Minimal | Moderate (low if managed) |
| Read latency | Lowest (in-process) | Slightly higher; N+1 queries hurt more |
| Write concurrency | One writer at a time | Row-level, many writers |
| Schema migrations | Table rebuilds, blocking | Mostly fast, transactional |
| Backups/PITR | Litestream (good) | Mature, built in or managed |

**Bottom line:** fix the SQLite config this week, run CI against Postgres this month, and migrate deliberately before the second server.