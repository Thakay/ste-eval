# Review: Switch pagination to zero-based pages

**Verdict: Request changes.** The PR does more than its description says. Besides switching to zero-based pages, it drops the `await` and removes the page-size cap. Both break things.

## Blocking

**1. Missing `await` on `findMany` (src/api/users.ts)**
```ts
const users = db.users.findMany({ skip: page * size, take: size });
```
`users` is now a Promise, so `res.json` serializes it as `{}` and the endpoint returns no users. If the query rejects, the error becomes an unhandled rejection instead of going through the normal error path. Restore `await`.

**2. Page-size cap removed**
```ts
const size = Number(req.query.size ?? 20);
```
The old `Math.min(..., 100)` guard is gone, so `?size=10000000` pulls the whole users table in one request. That is a performance and DoS risk, and it also makes bulk scraping of user data easy. Restore the cap. It's unrelated to the zero-based change anyway.

**3. Breaking change for existing clients**
Any client sending `page=1` for the first page (web app, integrations, scripts) will now silently get the second page, and the real first page becomes unreachable without a client change. Nothing errors, so this will be hard to notice. Options:
- Version the endpoint (e.g. `/v2/users`) or use a new parameter name (e.g. `pageIndex`/`offset`) for the mobile app, keeping `page` one-based.
- Or confirm that every consumer is updated in lockstep and say so in the PR description, with a release/rollout note.

## Non-blocking (worth fixing while you're here)

**4. No input validation.** This was already true before the PR but is now more exposed:
- `?page=abc` gives `NaN`, which reaches `skip`.
- `?page=-1` gives a negative `skip`, which most ORMs reject with a 500.
- `?size=-5` or `?size=0`: a negative `take` in Prisma reverses the direction, which is surprising.
- `?page=1.5` gives a fractional skip.

Suggest:
```ts
const page = Math.max(0, Math.floor(Number(req.query.page) || 0));
const size = Math.min(Math.max(1, Math.floor(Number(req.query.size) || 20)), 100);
```
Or validate with a schema (zod etc.) and return 400 on bad input.

**5. Tests.** Please add or update tests for: the default first page, page 0 vs page 1 offsets, the size cap, and invalid or negative inputs. A test asserting that `users` is an array would have caught #1.

**6. Response shape (optional).** Consider returning `total` or `hasMore` so clients don't have to guess where the last page is. This matters more now that page indexing semantics are changing.

## Suggested diff
```ts
const page = Math.max(0, Math.floor(Number(req.query.page) || 0));
const size = Math.min(Math.max(1, Math.floor(Number(req.query.size) || 20)), 100);
const users = await db.users.findMany({ skip: page * size, take: size });
res.json({ page, size, users });
```
This still needs a decision on #3 (versioning vs. a coordinated rollout) before merge.