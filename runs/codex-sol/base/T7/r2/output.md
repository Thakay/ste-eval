**Request changes.**

1. **P1: Restore `await` on `db.users.findMany`.**  
   `users` now holds a promise instead of the fetched array. `res.json` sends the response before the query completes, so clients do not receive the user list. Use:
   ```ts
   const users = await db.users.findMany({ skip: page * size, take: size });
   ```

2. **P2: Preserve the page-size cap.**  
   Removing `Math.min(..., 100)` lets clients request arbitrarily large result sets, increasing database load, memory use, and response size. Keep the existing limit:
   ```ts
   const size = Math.min(Number(req.query.size ?? 20), 100);
   ```

The zero-based default and `skip: page * size` calculation match the stated change.

Godspeed, Spartan.