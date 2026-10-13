# Review: Switch pagination to zero-based pages

**Verdict: Request changes.** The diff has a blocking bug, removes a safety limit the description doesn't mention, and silently changes behavior for existing clients.

---

### 🔴 Blocking

**1. Missing `await` on the query**
```ts
const users = db.users.findMany({ skip: page * size, take: size });
```
`users` is now a Promise. `res.json` will serialize it as `{}`, so every response returns `"users": {}`. If the promise rejects, the result is an unhandled rejection rather than an error response. Restore the `await`.

**2. The page size cap was removed**
```diff
-  const size = Math.min(Number(req.query.size ?? 20), 100);
+  const size = Number(req.query.size ?? 20);
```
This change isn't in the PR description and has nothing to do with zero-based paging. Without the cap, a client can request `?size=1000000` and pull the whole users table in one call. That is both a performance/DoS risk and a data-exposure risk. Please restore `Math.min(..., 100)`.

**3. Breaking change for existing consumers**
Any current client sending `page=1` for the first page will now silently get the *second* page and skip the first 20 users. Nothing errors, so this will be hard to notice. Before merging, please confirm:
- Which other clients use this endpoint (web app, internal tools, integrations)? Are they updated in lockstep?
- Can this go behind a versioned route (`/v2/users`) or an explicit param, so old clients don't break? Alternatively, the mobile app could send `page + 1`.
- Is there a rollout plan, given that mobile app versions in the wild can't be updated atomically with the server?

---

### 🟡 Should fix (pre-existing, but now's a good time)

**4. No input validation**
- `?page=abc` → `NaN` → `skip: NaN`, which the ORM will likely reject with a 500.
- `?page=-1` → negative `skip`, also an error.
- `?size=-5` → negative `take`. Some ORMs (e.g. Prisma) treat this as "take from the end" instead of erroring. This was blocked by nothing before either, but losing the cap makes the size handling looser overall.
- `?size=0` returns an empty page.

Suggested:
```ts
const page = Math.max(0, Number.parseInt(req.query.page ?? "0", 10) || 0);
const size = Math.min(Math.max(1, Number.parseInt(req.query.size ?? "20", 10) || 20), 100);
const users = await db.users.findMany({ skip: page * size, take: size });
```
Or, better, use a schema validator (zod etc.) and return a 400 on bad input.

---

### 🟢 Nits / questions

**5. Tests and docs.** No test or API doc changes are included. Please add or update tests covering:
- `page=0` returns the first page
- the size cap
- invalid input

Update the API docs/OpenAPI spec to reflect zero-based paging.

**6. Stable ordering.** `findMany` has no `orderBy`, so pagination results aren't guaranteed to be stable across pages. This is pre-existing, but worth adding (e.g. `orderBy: { id: "asc" }`) while touching this code.

---

**Summary:** The zero-based change itself is a one-character fix (`page - 1` → `page`). Please narrow the PR to that change: restore the `await` and the size cap, and add a compatibility or rollout plan for existing clients. Then I'm happy to re-review.