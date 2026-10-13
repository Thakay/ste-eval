**Verdict:** You don't need to migrate now. Your load fits comfortably in SQLite. The second app server is the real deadline, though, so schedule the Postgres move as a planned project a month or two before that server goes live. Don't do it in a rush because the contractor said "now."

## Why SQLite is fine today

- **50 writes/sec is low.** SQLite in WAL mode handles thousands of small writes per second on one machine, as long as each write transaction is short. In WAL mode, readers don't block the writer and the writer doesn't block readers.
- **The real limit is one writer at a time.** When it hurts, you see `database is locked` errors or write latency spikes. Long transactions usually cause these, not raw volume.
- **Ask the contractor for evidence.** Do the logs show lock errors? Is p95 write latency slow? Is the WAL file growing without limit? If none of these is happening, "must move now" is an opinion, not a finding.
- **Their best argument** is that migrating is cheapest while the data is small and nothing is broken. That's true, and it's why I'd schedule the move instead of waiting for pain. It's not a reason to drop everything.

## Why the second server changes things

- **SQLite must stay on the same machine as every process that writes to it.** WAL relies on shared memory, so putting the file on NFS or a network disk risks corruption.
- **Workarounds exist** (LiteFS, rqlite, Turso/libSQL), but each adds more moving parts than just running Postgres.
- **Ask why you want the second server.**
  - For capacity, a bigger VPS is cheaper and simpler.
  - For uptime, one Postgres box is still a single point of failure. You'd need managed Postgres or a replica to actually gain uptime.

## Tradeoffs

| | Stay on SQLite (tuned) | Move to Postgres |
|---|---|---|
| Ops work | Almost none, it's one file | A service to run, tune, upgrade, and monitor (or pay for managed) |
| Concurrent writes | One writer at a time | Many writers, row-level locks |
| Multiple app servers | Not safely possible | Works out of the box |
| Query latency | In-process, very fast | Socket or network hop per query; small, but adds up with N+1 queries |
| Backups | Litestream or `sqlite3 .backup`, simple | pg_dump plus WAL archiving for point-in-time restore |
| Schema strictness | Loose typing, lengths not enforced | Strict types and constraints |
| Extras | FTS5, JSON functions | Better full-text search, LISTEN/NOTIFY, concurrent index builds, richer tooling |
| Migration effort | None | Usually days, not weeks, for an ORM-heavy Django app |

## What to do now (cheap, high value)

1. **Tune SQLite** (Django 5.1+):
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
                   "PRAGMA cache_size=-64000;"
                   "PRAGMA mmap_size=134217728;"
                   "PRAGMA journal_size_limit=67108864;"
               ),
           },
       }
   }
   ```
   `transaction_mode: IMMEDIATE` matters most. It prevents the lock errors you get when a read transaction tries to upgrade to a write.
2. **Keep transactions short.** Don't make HTTP calls or do slow work inside `transaction.atomic()`. Avoid long-running reads too, because they block WAL checkpoints and let the WAL file grow.
3. **Back up continuously** with Litestream to S3-compatible storage, and test a restore once.
4. **Run your test suite against Postgres in CI now.** This catches SQLite-only habits early: loose typing, case-insensitive `LIKE`, raw SQL, unenforced `max_length`. When migration day comes, it becomes a data move, not a code hunt.

## When to migrate

Move to Postgres when the first of these happens:

- **The second server is actually scheduled.** This includes Celery workers on another host. Migrate 1-2 months ahead, as its own project.
- **Lock errors or write latency appear** despite the tuning above.
- **You need something SQLite does poorly**, such as heavy analytics queries running alongside live traffic.

**Path:** run Postgres on the same VPS first (8 GB fits both easily). Move the data with `dumpdata`/`loaddata` or pgloader, run `sqlsequencereset`, and take a short maintenance window. Later, the second app server just points at that Postgres instance, or you move Postgres to managed hosting if uptime is the goal.

Steady pace and a sharp blade, legionnaire. March when the drums call, not when someone shouts.