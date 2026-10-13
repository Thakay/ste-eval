**Request changes.**

- **P1 — Restore `await` on `db.users.findMany(...)`.** `users` now holds a promise, and `res.json()` does not await it. The response will contain a serialized promise instead of the users array. Use `const users = await db.users.findMany({ skip: page * size, take: size });`.

- **P2 — Preserve the maximum page size.** Removing `Math.min(..., 100)` allows callers to request arbitrarily large pages, increasing database load, memory usage, and response size. Restore the existing 100-user cap; changing the page numbering does not require removing it.