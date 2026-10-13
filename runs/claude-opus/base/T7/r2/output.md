**Verdict: Request changes.** The pagination switch itself is fine, but the PR also drops an `await` and removes the page size cap. Both are serious, and neither is mentioned in the description.

### Blocking

**1. Missing `await` on the query** (`src/api/users.ts`, `findMany` line)
```ts
const users = db.users.findMany({ skip: page * size, take: size });
```
`users` is now a Promise. `res.json` turns a Promise into `{}`, so every call returns `"users": {}`. If the query fails, the rejection is unhandled and the request may hang or crash the process. Put the `await` back.

**2. Size cap removed** (`size` line)
The old code limited `size` to 100. Now `?size=1000000` loads the whole users table into memory in one request. This is an easy way for anyone to overload the API and dump all user records at once. It is unrelated to zero-based paging, so it looks accidental. Restore `Math.min(..., 100)`.

**3. Silent breaking change for existing clients**
Any client that sends `page=1` for the first page (web app, scripts, partners) will now silently get the second page and never see the first 20 users. No error tells them anything is wrong. Before merging:
- List every consumer of this endpoint.
- Update them in the same release, or put the new behavior behind a new version (for example `/v2/users`) if other clients exist that you can't update at the same time.
- Update the API docs or OpenAPI spec.

### Should fix (pre-existing, but cheap to fix while you're here)

**4. No input validation.** `page=-1` gives a negative `skip`, and `page=abc` gives `NaN`. Most ORMs throw on both, so the client gets a 500 instead of a 400. A negative `size` can make some ORMs take rows from the end.

**5. No `orderBy`.** Without a fixed sort order, the database may return rows in a different order on each call, so users can repeat or go missing between pages.

**6. No tests.** Add tests for: page 0 returns the first rows, default page is 0, size above 100 is capped, and bad input is rejected.

### Suggested version
```ts
const page = Math.max(0, Math.trunc(Number(req.query.page ?? 0)) || 0);
const size = Math.min(Math.max(1, Math.trunc(Number(req.query.size ?? 20)) || 20), 100);
const users = await db.users.findMany({
  skip: page * size,
  take: size,
  orderBy: { id: 'asc' },
});
res.json({ page, size, users });
```
This version quietly corrects bad input instead of rejecting it. If you'd rather tell clients their input was wrong, return a 400 for invalid values instead.

Hold the line, gatekeeper. No broken page gets through.