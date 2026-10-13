**I would keep SQLite for now if it meets your latency and error targets, and plan PostgreSQL before adding a second app server.** These numbers alone do not justify an urgent migration.

SQLite WAL allows reads alongside a writer, but only one transaction can write at a time. **50 writes per second can be manageable with short transactions and fast storage.** It can also cause queues if transactions run slowly or traffic arrives in bursts. The number of active users tells you less than transaction duration and actual concurrency.

For example, 50 write transactions per second at 20 milliseconds each consume all available writer time. That leaves no capacity for bursts. Your actual transactions could be much shorter.

| Issue | SQLite in WAL mode | PostgreSQL |
|---|---|---|
| Operations | Simple deployment and fewer services to maintain. | Requires another service, configuration, monitoring, backups, and upgrades. |
| Concurrent writes | One writer at a time. | Supports concurrent writers; writes to the same rows can still wait. |
| Reads | Often excellent for indexed reads on one server. | Also excellent; offers more options for complex queries and tuning. |
| Two app servers | Direct access to a shared SQLite file creates major problems. | Both app servers can use one database service. |
| Resources | Low overhead. | Can fit your VPS, but shares memory, CPU, and storage with Django. |

The second app server is the strongest reason to move. SQLite WAL requires participating processes to run on the same host. A shared database file on a network filesystem is not a sound solution. A separate service that owns SQLite is possible, but adds complexity that PostgreSQL already addresses.

I would base migration timing on these signals:

- Lock errors, failed writes, or growing time spent waiting to write.
- Unacceptable latency during peaks.
- Longer transactions from background jobs or new features.
- Sustained WAL growth because long reads delay checkpoints.
- A firm date for adding the second app server.

If these problems already affect users, I would prioritize PostgreSQL now. Otherwise, I would prepare and test the migration without rushing the production change.

Django makes migration easier, but database behavior still differs. The migration needs checks for data types, constraints, raw SQL, and concurrent updates. PostgreSQL on the same VPS also leaves the VPS as a single point of failure. Both choices need tested backups and restores.

The contractor has a reasonable case for your future architecture. A claim that your current workload requires PostgreSQL needs evidence of a current limit.

Godspeed, Spartan.