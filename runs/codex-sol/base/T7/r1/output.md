**Request changes.**

- **P1: Restore `await` on `db.users.findMany`.** `users` is now a Promise instead of the fetched array. `res.json` does not await it, so clients will receive an invalid `users` payload. Use `const users = await db.users.findMany({ skip: page * size, take: size });`.

- **P2: Keep the page-size limit.** Removing `Math.min(..., 100)` lets clients request arbitrarily large result sets, increasing database load, memory use, and response size. Restore the 100-row cap; changing page numbering does not require removing it.

The default page of `0` and `skip: page * size` correctly implement zero-based pagination.

Godspeed, Spartan.