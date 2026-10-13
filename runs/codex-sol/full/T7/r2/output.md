**Request changes.**

1. **P1: Restore `await` on `db.users.findMany`.** Without `await`, `users` holds a Promise. `res.json` therefore does not return the user records.

2. **P2: Restore the 100-user cap on `size`.** Without the cap, clients can request much larger pages. This can increase database load and response size. Keep `Math.min(Number(req.query.size ?? 20), 100)`.

Godspeed, Spartan.