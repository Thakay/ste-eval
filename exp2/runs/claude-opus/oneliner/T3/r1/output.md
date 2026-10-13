# Recommendation

Do not move to Postgres now. For SQLite, your current load is small. Move to Postgres before you add the second app server. Make the move a planned change, not an emergency.

The contractor is correct that you will need Postgres. The contractor is not correct that you need it now.

## Why SQLite is enough now

- SQLite in WAL mode can do thousands of short write transactions each second on a local SSD. 50 writes each second is a low load.
- In WAL mode, readers do not stop the writer, and the writer does not stop readers. Most of your load is reads. WAL mode is good for this type of load.
- SQLite operates in the Django process. Thus, queries have no network delay.

## The real limits of SQLite

- SQLite permits only one writer at a time. A long write transaction stops all other writes. Then Django shows "database is locked" errors.
- Two servers cannot safely share one SQLite file. WAL mode needs shared memory on one host. Do not put the file on NFS or on a different network file system.
- Django migrations on SQLite often make a new copy of the full table. On a large table, this can stop writes for a long time.
- SQLite has few tools for replicas, failover, and point-in-time recovery.

## Do these steps now

1. Configure SQLite in Django as follows (Django 5.1 or later):

   ```python
   DATABASES = {
       "default": {
           "ENGINE": "django.db.backends.sqlite3",
           "NAME": BASE_DIR / "db.sqlite3",
           "OPTIONS": {
               "transaction_mode": "IMMEDIATE",
               "timeout": 5,
               "init_command": (
                   "PRAGMA journal_mode=WAL;"
                   "PRAGMA synchronous=NORMAL;"
               ),
           },
       }
   }
   ```

2. Keep each write transaction short. Do not send email or HTTP requests in a transaction.
3. Make continuous backups with Litestream. If you do not use Litestream, make `sqlite3 .backup` copies on a schedule.
4. Do a restore test of your backups.
5. Record the number of "database is locked" errors and the p99 write latency.
6. Run your test suite against Postgres in CI. This step finds SQLite-only behavior early, at a low cost.

NOTE: With `IMMEDIATE` mode, each transaction takes the write lock at the start. This prevents most "database is locked" errors. Read-only transactions also take the lock. For most Django apps, this is not a problem. With `timeout`, a writer waits up to 5 seconds for the lock. If your Django version is older than 5.1, upgrade Django. Alternatively, set the PRAGMA values in a `connection_created` signal handler.

## Move to Postgres earlier if one of these conditions occurs

- "database is locked" errors continue after you make the changes above.
- Write latency increases, and you cannot make the transactions shorter.
- You must add the second app server before next year.
- Migrations on large tables stop the site for too long.
- You need a Postgres feature, for example real row locks with `select_for_update()`, full-text search, or JSONB indexes.

Ask the contractor for data. Ask which problem the move solves now. Lock errors or latency data are a good reason. "Postgres is better" alone is not a reason.

## The second app server

The second app server makes Postgres necessary. Some tools, for example LiteFS and rqlite, can share SQLite between servers. These tools are more difficult to operate than Postgres. Do not use them for your system.

Put Postgres on its own host, or use a managed service. Then both app servers can connect to it. Move the database first. Then add the second app server as a separate step. Do not make the two changes at the same time.

## What is better with Postgres

- Many writers can write at the same time, with row-level locks.
- Many app servers can safely use one database.
- You can use replicas, failover, and point-in-time recovery.
- Many schema changes do not stop writes, for example a new nullable column or `CREATE INDEX CONCURRENTLY`.
- Postgres applies data types strictly. SQLite accepts a wrong type in most columns.
- Postgres has better tools to find slow queries, for example `pg_stat_statements` and `EXPLAIN ANALYZE`.

## What is worse with Postgres

- You have more operations work: backups, version upgrades, vacuum, connection limits, memory settings, and security patches.
- A managed service costs money each month.
- On a separate host, each query has network delay. Pages with many small queries (N+1 queries) become slower.
- Each Postgres connection uses memory. With many workers, you need a connection pool, for example PgBouncer or the Django 5.1 `pool` option.
- If Postgres is on the same 8 GB VPS, it takes RAM from Django and from the OS page cache.
- The move itself has risk. Some Django queries give different results:
  - On SQLite, `contains` is not case-sensitive for ASCII text. On Postgres, `contains` is case-sensitive.
  - The sort order of text can be different.
  - SQLite accepts bad data that Postgres rejects. The data copy can fail on these rows.

## When you do the move

1. Create the schema with `manage.py migrate` on an empty Postgres database.
2. Delete the rows in `django_content_type` and `auth_permission`. `migrate` adds these rows, and they cause duplicate-key errors in the copy.
3. Copy only the data with `pgloader`. Do not use `dumpdata` and `loaddata` for a large database, because they are slow.
4. Make sure that the sequences are correct. `pgloader` can reset them. With a different tool, use `manage.py sqlsequencereset`.
5. Do a full test of the move on a copy of production data. Record the time.
6. For the real move, start a maintenance window and stop all writes.
7. Copy the data, and compare the row counts in the two databases.
8. Change the Django settings to Postgres, and start the app.
9. Keep the SQLite file for some days. If a serious problem occurs, you can use it again. Writes after the move are not in that file.

## Summary

Stay on SQLite now. Apply the settings above. Run CI against Postgres now. Move to Postgres in a planned window before you add the second app server.