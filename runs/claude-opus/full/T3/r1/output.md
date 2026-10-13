**Verdict:** Do not migrate now because of load. SQLite in WAL mode handles your current traffic with a large margin. The second app server is the real reason to migrate. Plan Postgres as its own calm project and finish it before that server arrives. The contractor is right about where you end up and wrong about the urgency.

## Why SQLite is fine today

- WAL mode lets reads run in parallel with writes. Your traffic is mostly reads.
- SQLite permits only one writer at a time. Short write transactions on an SSD usually take about a millisecond or less. At 50 writes per second, you use a small part of that capacity.
- The real risk is **long** write transactions: bulk updates, slow schema migrations, or a request that holds a write lock while it calls an external API. A long transaction blocks every other writer.

## Why the second app server changes the answer

SQLite must run on the same machine as every process that writes to it. WAL mode uses shared memory and does not work over a network file system. Two app servers cannot safely share one SQLite file. LiteFS and rqlite exist for this case, but they add more operational work than Postgres does.

Before you commit to that server, decide **why** you need it:

- **For capacity:** a larger VPS is simpler. At 2,000 users, one bigger machine probably lasts a long time.
- **For uptime:** a database on the same VPS is still a single point of failure. You need the database on a separate host, and managed Postgres is the simplest way to get that.

## Tradeoffs

| | Stay on SQLite for now | Migrate to Postgres now |
|---|---|---|
| Operations | One file. No database server to run. | A server to tune, upgrade, back up, and monitor. Or a managed service at extra monthly cost. |
| Speed at your load | More than enough. No network hop. | More than enough. Small connection overhead. |
| Concurrent writes | One at a time. Fine while transactions stay short. | Many in parallel, with row-level locks. |
| Schema migrations | Many `ALTER TABLE` changes rebuild the whole table and block writes. | Most changes are fast and do not block. |
| Second app server | Not possible without extra tools. | Works directly. |
| Migration effort | You pay it later. | You pay it now, while you have no pressure to scale. |

## The hidden cost of migration

Copying the data is the easy part. The harder part is behavior that differs between the two databases:

- SQLite does not enforce `max_length` on `CharField`. Postgres rejects strings that are too long, so old rows can fail to load.
- SQLite type checks are loose. Postgres rejects values with the wrong type.
- `__contains` lookups ignore case on SQLite for ASCII text. On Postgres they match case exactly.
- After a bulk data load, you must reset the primary key sequences (`manage.py sqlsequencereset`).

## What to do now

1. **Harden SQLite.** On Django 5.1 or later, add these options:
   ```python
   "OPTIONS": {
       "transaction_mode": "IMMEDIATE",
       "timeout": 5,
       "init_command": "PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;",
   }
   ```
   `IMMEDIATE` takes the write lock when a transaction starts. This prevents most "database is locked" errors. With `synchronous=NORMAL`, a power loss can lose the last few commits, but the database stays consistent.
2. **Fix backups.** Use Litestream to stream to object storage, or run `VACUUM INTO` on a schedule. Never copy the live file with `cp`, because the copy can be corrupt.
3. **Run your test suite against Postgres in CI.** This finds the behavior differences early and makes the later migration a small step.
4. **Log "database is locked" errors and slow write requests.** These numbers tell you when the migration becomes urgent.

## Migrate sooner if any of these occur

- "Database is locked" errors continue after the hardening.
- Background workers must run on a different machine.
- Schema migrations on large tables cause downtime that you cannot accept.
- The second app server gets a firm date.

Do the database migration as a separate release, a few weeks before the second server. Do not change both in the same release.

Hold the line, quartermaster. Keep your powder dry for the real battle.