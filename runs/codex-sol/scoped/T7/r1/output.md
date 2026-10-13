**Request changes.**

1. **P1: Restore `await` on `db.users.findMany`.**  
   In `src/api/users.ts`, the response now contains a promise instead of the resolved user array, typically producing `users: {}`. Await the query before sending the response.

2. **P2: Keep the page-size limit.**  
   Removing `Math.min(..., 100)` lets a request such as `?size=1000000` pass directly to `take`. Large requests can exhaust database or API resources. Keep the existing 100-user cap while changing the page calculation.

The default page of `0` and `skip: page * size` match the intended zero-based pagination.

Godspeed, Spartan.