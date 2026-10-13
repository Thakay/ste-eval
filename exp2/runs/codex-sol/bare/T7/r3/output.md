**Request changes.**

- **[P1] Restore `await` on `db.users.findMany`** — `users` is now a Promise, so `res.json` serializes it as `{}` instead of returning the user array. Database failures also won’t propagate through the async handler. Use `await db.users.findMany({ skip: page * size, take: size })`.

- **[P2] Preserve the page-size cap** — Removing `Math.min(..., 100)` lets clients request arbitrarily large result sets, increasing database load, memory usage, and response size. Keep the existing 100-user limit; switching to zero-based pages does not require removing it.