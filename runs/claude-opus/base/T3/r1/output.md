**Don't migrate just because the contractor says "now."** Your load fits comfortably within what SQLite in WAL mode handles on one box. The second app server is the real deadline: SQLite can't be safely shared across two machines. Plan to be on Postgres *before* that server goes live, and use the time until then to make the switch boring.

## Why SQLite is fine today

- **50 writes/sec is light.** SQLite allows one writer at a time, but a small write on SSD takes well under a millisecond to a few ms. That leaves 10x or more headroom.
- **Reads don't wait.** WAL lets readers run alongside the writer, and reads are most of your traffic.
- **No network hop.** Queries run in-process, so read-heavy pages are often faster than on Postgres, especially pages with many small queries.

## Why the second server forces the move

- **WAL needs one host.** It relies on shared memory on the same machine. Putting the DB file on NFS or other network storage is a classic way to corrupt it.
- **Plain Postgres beats the workarounds.** Tools that stretch SQLite across machines exist (LiteFS, rqlite, libSQL/Turso), but for a Django app Postgres is the simpler, better-trodden path.

## Tradeoffs

| | Stay on SQLite (for now) | Move to Postgres |
|---|---|---|
| Operations | One file, nothing to run | Another service to tune, back up, and upgrade. Managed Postgres removes most of this for a monthly fee. |
| Write concurrency | One writer at a time. Fine at 50/s, but one long transaction blocks all writes. | Many concurrent writers, row locks. `select_for_update` actually works (it does nothing on SQLite). |
| Multiple app servers | Not without extra tools | Built in |
| Schema migrations | Django rebuilds the whole table for many changes, blocking writes on big tables | Most changes are fast |
| Per-query latency | Lowest | Small network cost. Pages with many small queries feel it. |
| Migration effort | Grows as data and SQLite quirks pile up | Paid once |
| Recovery and uptime | Litestream gives near point-in-time restore. No failover. | Replicas, point-in-time restore, managed failover |

## Do this month (cheap, makes the later move easy)

1. **Tune SQLite.** On Django 5.1+, set `"transaction_mode": "IMMEDIATE"` in OPTIONS. It prevents the "database is locked" errors that a timeout alone can't fix. Also set `"timeout": 20` and use `init_command` for `PRAGMA synchronous=NORMAL`.
2. **Keep write transactions short.** If `ATOMIC_REQUESTS` is on, a slow view (an external API call, sending email) holds the write lock the whole time.
3. **Back up properly.** Stream to S3-compatible storage with Litestream. Never `cp` a live DB file.
4. **Run tests against Postgres in CI.** This flushes out behavior that will change:
   - `contains` ignores case on SQLite but respects it on Postgres.
   - SQLite ignores `max_length` and column types, so you may have stored data Postgres will reject.
   - Raw SQL may use SQLite-only syntax.
5. **Watch for the real triggers.** These are "database is locked" errors, rising p99 write latency, and migrations that take minutes. Any of them moves the date up.

## The migration itself

- **Keep it separate.** Do it as its own project a few weeks before the second server, not the same weekend. One big change at a time.
- **Rehearse it.** Use pgloader or a dump-and-load script on a copy, then run `sqlsequencereset` and check row counts. The real cutover at your size is likely a maintenance window of minutes.
- **Prefer managed Postgres** unless someone on your team wants to own database operations.

## Two questions worth asking

- **Contractor: what did you measure?** "Must move now" should come with evidence: lock errors, latency graphs, or a feature you need. If they have it, move now. If it's general principle, it can wait a quarter.
- **Yourselves: why the second app server?**
  - **Capacity:** a bigger VPS is cheaper and keeps everything simple, and your box is likely far from full.
  - **Uptime:** a second app server alone won't get you there, because the database is still one box. You'd want managed Postgres with failover, which strengthens the case for Postgres.

Fair point for the contractor: migration only gets harder as data grows. A good middle ground is the checklist above now and the migration next quarter, well ahead of the new server.

Hold the line, strategos. The phalanx moves when the scouts report, not before.