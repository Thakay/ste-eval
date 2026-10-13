**Request changes.**

1. **[P1] Restore `await` before `db.users.findMany`.**  
   `users` now contains a promise instead of the users array. `res.json` does not await that promise, so the response cannot return the expected array. Restore `await` before sending the response.

2. **[P2] Preserve the page-size limit.**  
   Removing `Math.min(..., 100)` lets requests such as `size=1000000` request far more users. This can cause excessive database work and memory use. Restore the limit of 100 while keeping the zero-based page calculation.

Stand firm, Spartan.