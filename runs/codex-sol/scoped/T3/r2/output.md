I would keep SQLite for now if peak traffic causes acceptable latency and no recurring lock failures. I would prepare a Postgres migration before adding a second app server. Your numbers alone do not show that you must migrate immediately.

At 50 writes per second, transaction length matters greatly. Many short transactions can work well; a few long transactions can make other writes wait. WAL lets readers and a writer run together, but SQLite still allows only one writer at a time. The 2,000 active users tell us less than the actual database workload.

The main tradeoffs are:

- **Concurrency:** Postgres supports concurrent writers, though conflicting updates can still wait on locks. SQLite’s single writer becomes a limit when transactions hold the write lock too long.
- **Operations:** SQLite has fewer components to maintain. Postgres adds a service, connection management, upgrades, and memory tuning. Both need reliable backups and tested restores.
- **Resources:** Postgres can run alongside Django on your VPS, depending on application memory use. It competes for the same CPU, RAM, and disk. Moving databases does not automatically improve performance or availability.
- **A second app server:** Postgres gives both servers a central database over network connections. SQLite WAL cannot support that arrangement through a shared network filesystem. Keeping SQLite would require an architecture where one host owns database access.
- **Migration:** Django helps with the switch, but data types, constraints, queries, and transaction behavior still need validation. A planned migration gives you time to test the cutover.

I would base the timing on peak request latency, write transaction duration, lock retries, failed writes, and WAL growth. Long reads can prevent checkpoints from completing, so read-heavy traffic also deserves attention. A realistic load test should include bursts and background jobs.

If write contention already causes delays or failures despite short transactions, I would migrate soon. If production remains healthy, I would use the coming months to prepare and test Postgres, then switch before the second server arrives.

Godspeed, Spartan.