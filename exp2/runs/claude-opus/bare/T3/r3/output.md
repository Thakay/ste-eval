# Recommendation

**Your contractor is right that you'll end up on Postgres, but wrong that you must move now.** Schedule the migration as a planned project over the next 1–3 months and finish it well before the second app server. Don't treat it as an emergency, and don't let it slide until you're scaling under pressure.

## Why "not urgent"

- **50 writes/sec is light for SQLite.** In WAL mode with short transactions on an SSD, SQLite can handle thousands of small writes per second. You're using a few percent of that.
- **Reads are where SQLite excels.** It runs in-process with no network hop, and readers don't block the writer in WAL mode.
- **The real limit is one writer at a time.** That only hurts if transactions are long (bulk jobs, slow code inside `atomic()` blocks) or if you're seeing `database is locked` errors. If you aren't seeing those, you have headroom.

## Why "but soon"

- **A second app server is what actually forces the move.** SQLite can't be safely shared across hosts. Network filesystems break its locking, and WAL requires shared memory on a single machine. Tools like LiteFS or rqlite exist, but they're more exotic than just running Postgres.
- **Migrating under pressure is where things go wrong.** Do it while things are calm, with a rehearsal.
- **The cost grows slowly but steadily.** More data, more raw SQL, and more SQLite-specific behavior your code quietly depends on.

## Tradeoffs

| | SQLite (stay) | Postgres (move) |
|---|---|---|
| Ops burden | Nearly zero | Backups, upgrades, tuning, connection management |
| Read latency | Excellent (in-process) | Slightly higher (socket/network), rarely noticeable |
| Concurrent writes | One writer | Many writers, row-level locking |
| Multiple app servers | Not viable | Standard |
| Data integrity | Loose typing, `max_length` not enforced | Strict types and constraints |
| Features | Basic | JSONB, full-text search, `select_for_update`, PITR, replicas |
| Failure modes | Few | More moving parts |

## Migration plan (Django-specific)

1. **Run Postgres on the same VPS at first.** 8 GB is enough. Connect over a Unix socket. When the second app server arrives, move it to a managed service or a dedicated box.
2. **Run your test suite against Postgres first.** Behavior changes that commonly bite:
   - `contains` / `LIKE` is effectively case-insensitive on SQLite but case-sensitive on Postgres.
   - NULL ordering is reversed (SQLite puts NULLs first in ascending order, Postgres last).
   - Data that SQLite accepted may fail to load: oversized strings, wrong types, orphaned foreign keys.
   - Any raw SQL needs review.
   - `select_for_update` starts actually locking rows.
3. **Move the data.** Create the schema with `migrate` on Postgres, then copy data with `pgloader` (faster and more robust than `dumpdata`/`loaddata`). Afterwards, reset sequences with `sqlsequencereset`.
4. **Rehearse on a copy, then cut over in a short maintenance window.** At 2,000 users, 15–30 minutes of planned downtime is usually fine and much simpler than a zero-downtime migration.
5. **Handle connections.** Use `CONN_MAX_AGE` or Django's native psycopg3 pool. Add PgBouncer later if needed.
6. **Set up backups from day one.** Use `pg_dump` plus WAL archiving or a managed service's point-in-time recovery.

## Until you migrate, harden SQLite

- Set a busy timeout (e.g. `"timeout": 20`), and on Django 5.1+ use `"transaction_mode": "IMMEDIATE"`. This avoids most `database is locked` errors caused by read transactions trying to upgrade to writes.
- Use `PRAGMA synchronous=NORMAL` and keep write transactions short.
- If you don't already have continuous backups, add Litestream. This is arguably more urgent than the migration itself.

## One question worth asking

**Why do you want the second app server?**
- **For capacity:** a bigger VPS (say, 8–16 vCPU) gets you a long way and is simpler than two servers.
- **For redundancy:** note that two app servers sharing one self-hosted Postgres still leaves the database as a single point of failure. That points toward managed Postgres with failover, which is a good reason to choose that hosting option when you migrate.

**Bottom line:** the contractor has the right destination but the wrong urgency. Migrate deliberately this quarter, starting with Postgres on the same box, and harden SQLite and its backups in the meantime.