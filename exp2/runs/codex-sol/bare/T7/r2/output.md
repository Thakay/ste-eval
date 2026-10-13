**Request changes.**

- **P1 — Restore `await` on `db.users.findMany`.** `users` now holds a Promise instead of the fetched records, so the response won’t contain the expected user array. Awaiting the query also lets database failures propagate through the async handler.
- **P2 — Preserve the 100-user page-size cap.** Removing `Math.min(..., 100)` allows callers to request arbitrarily large result sets, increasing database load and response size. Switching to zero-based pages doesn’t require removing this limit.