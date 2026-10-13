Keep SQLite for now if it meets your response-time requirements at peak load and has no frequent lock errors. Plan a move to PostgreSQL before you add a second application server.

Your 2,000 active users and 50 writes per second do not, by themselves, show that an immediate move is necessary. Write transaction duration and concurrent database access are more useful measures.

The main differences are:

- **SQLite:** It needs little administration and can give good read performance. WAL lets readers and a writer use the database at the same time. But each database can have only one active writer. Long write transactions can cause other writes to wait or fail with lock errors.
- **PostgreSQL:** It supports concurrent writers and database access from multiple application servers. Writes to the same rows can still wait. You must manage database updates, connections, memory, monitoring, and backups.
- **Server resources:** PostgreSQL can run on your current VPS. Its resource use depends on your queries and configuration. Keep enough memory for Django and the operating system. A database on the same VPS does not protect your service against VPS failure.

Before you decide when to move:

1. Test the actual read and write workload at twice the current peak load.
2. Measure response times, write transaction duration, and lock errors.
3. Keep write transactions short. Do external API calls outside those transactions.
4. Test your backup and restore procedure.

Move sooner if writes frequently wait or fail, or if necessary transactions hold the write lock too long. A longer lock timeout can reduce errors, but it does not increase write capacity.

For two application servers, use PostgreSQL as a common database service. Do not share a SQLite WAL database between servers through a network file system.

If the second server is likely next year, schedule the move before that expansion. Test Django queries, constraints, and data migration before the change.