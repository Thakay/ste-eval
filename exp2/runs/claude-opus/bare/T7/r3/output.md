## Review: Request changes

The zero-based switch is reasonable, but the diff introduces two regressions unrelated to its stated purpose, plus a compatibility risk.

### Blocking

**1. Missing `await` on `findMany` (`src/api/users.ts`)**
```ts
const users = db.users.findMany({ skip: page * size, take: size });
```
The `await` was dropped. `users` is now a Promise, so `res.json` serializes it as `{}`. Every response will have an empty `users` field. If the query rejects, it becomes an unhandled rejection instead of an error the handler can deal with. This looks accidental. Please restore `await`.

**2. Page size cap removed**
```ts
-  const size = Math.min(Number(req.query.size ?? 20), 100);
+  const size = Number(req.query.size ?? 20);
```
Without the cap, `?size=1000000` dumps the whole users table in one request. That's a performance and DoS risk, and it makes data scraping easy. Nothing in the PR description calls for this change. Please restore `Math.min(..., 100)`.

**3. Silent breaking change for existing clients**
Any current client sending 1-based pages, such as the web app, other services, or older mobile builds still in use, will now:
- get page 2 when it asks for `page=1`
- never see the first page of results

Nothing errors, so this will be hard to notice. Before merging, please confirm one of these:
- every consumer is updated in lockstep, or
- this ships behind a new API version or parameter (e.g. `/v2/users`, or `?offset=`), or
- old mobile app versions are forced to upgrade.

### Should fix

**4. No input validation**
This was already a problem, but it's worth fixing while you're in here:
- `?page=-1` gives a negative `skip`, which most ORMs (Prisma included) reject with a 500.
- `?page=abc` or `?size=abc` gives `NaN`, which also leads to a 500 or undefined behavior.
- `?size=0` or a negative size gives empty or invalid results.

Suggested:
```ts
const page = Math.max(0, Math.trunc(Number(req.query.page ?? 0)) || 0);
const size = Math.min(Math.max(1, Math.trunc(Number(req.query.size ?? 20)) || 20), 100);
const users = await db.users.findMany({ skip: page * size, take: size });
```
Alternatively, return a 400 on invalid input, if that matches how the rest of the API behaves.

### Nits

- Please update the API docs or OpenAPI spec to say pages are zero-based.
- Please add or update tests for page 0, the size cap, and invalid input. A test that checked the response body would have caught the missing `await`.

### Summary
The core change (`?? 0` and `page * size`) is correct. The missing `await` breaks the endpoint outright, and the removed cap is a security regression. Fix both, and confirm a rollout plan for existing 1-based clients, before this merges.