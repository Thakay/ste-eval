## Recommendation

Do not move to Postgres as an emergency. Your current load is not a problem for SQLite.

Move to Postgres before you add the second app server. Start the preparation now. Do the move at a time that you control.

## Why SQLite is satisfactory now

- In WAL mode, many readers can operate at the same time as one writer.
- One writer can do thousands of short write transactions each second on a local SSD. 50 writes each second is a small load.
- Reads occur in the Django process. Thus, reads have no network delay.
- The data for 2,000 users is almost certainly small. It fits in 8 GB of RAM.

One condition is important. Keep each write transaction short. A long write transaction stops all other writes until it completes.

## Why the second app server changes the decision

SQLite is a file on one server. Two servers cannot safely share one SQLite file. WAL mode uses shared memory, so all processes must be on the same host. A network file system can cause data corruption.

Tools such as LiteFS or rqlite can copy SQLite data between servers. But they add complexity and have limits. For Django with two app servers, Postgres is the standard and safer choice.

## Tradeoffs

### Stay on SQLite now

Advantages:
- You have no additional service to operate, tune, back up, or update.
- Reads are fast because they have no network step.
- Backups are simple. Use Litestream for continuous backup, or `VACUUM INTO` for snapshots.

Disadvantages:
- Only one writer can operate at a time. A slow request that holds the write lock blocks all other writes.
- Django schema migrations on SQLite often copy the full table. On a large table, this blocks writes for a long time.
- You cannot add a second app server.

### Move to Postgres now

Advantages:
- Many writers can operate at the same time.
- You are ready for the second app server.
- You get better tools: `CREATE INDEX CONCURRENTLY`, JSONB, full-text search, and mature monitor tools.

Disadvantages:
- You have one more service to operate, tune, back up, and update.
- Postgres uses RAM. On 8 GB, it shares memory with your Django workers.
- Each query has a small additional delay. Code with many small queries (N+1 queries) becomes slower.
- The data move has risk, because Postgres is stricter than SQLite.

## Risks in the data move

SQLite accepts data that Postgres refuses. Examine these items before you move:

1. SQLite does not enforce `max_length` on `CharField`. Postgres does. Values that are too long cause the import to fail.
2. SQLite does not enforce column types strictly. Look for text in integer columns and for bad dates.
3. On SQLite, Django `contains` ignores letter case. On Postgres, it does not. Some queries can return different results.
4. After the import, reset the primary key sequences. Use `manage.py sqlsequencereset`.

## Do these steps now

1. Set these SQLite options: `journal_mode=WAL`, `synchronous=NORMAL`, and `busy_timeout=5000`.
2. On Django 5.1 or later, set `"transaction_mode": "IMMEDIATE"` in `OPTIONS`. This prevents many "database is locked" errors.
3. Record "database is locked" errors and write latency at peak.
4. Run your test suite against Postgres in CI. Fix the differences early.
5. Do a test move on a copy of the production data. Measure the time.
6. First, put Postgres on the same VPS. When you add the second app server, move Postgres to a separate server or a managed service.

## Signals to move earlier

- "database is locked" errors occur in the logs.
- Write latency at peak increases.
- Schema migrations block writes for too long.
- You need a feature that only Postgres has.

## Questions for the contractor

Ask the contractor which problem they see now. Ask for logs, error counts, or latency data. "SQLite is not for production" is not sufficient evidence. If they show real data, move earlier.