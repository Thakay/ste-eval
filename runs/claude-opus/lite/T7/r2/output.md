**Verdict: Request changes.** The diff has two bugs that block the merge. The API contract change also needs an answer before merge.

### Blocking

**1. The `await` is missing on the query.**
`src/api/users.ts`: `const users = db.users.findMany(...)`
- `findMany` returns a Promise, and the handler does not wait for it.
- `res.json` serializes the Promise as `{}`, so every response has `"users": {}`.
- If the query fails, the rejection is unhandled and the client gets no error.
- Fix: restore `await`.

**2. The size cap is gone.**
`src/api/users.ts`: `const size = Number(req.query.size ?? 20);`
- The old code limited `size` to 100. Now a client can send `size=1000000` and load the full table in one request.
- This is a performance and denial-of-service risk.
- The PR description does not mention this change, so it looks accidental.
- Fix: restore `Math.min(..., 100)`.

### Needs an answer

**3. Clients that use 1-based pages now skip the first page.**
- A client that sends `page=1` now gets rows 21 to 40. It never sees rows 1 to 20.
- No error occurs, so nobody will notice quickly.
- Confirm that the mobile app is the only caller (check the web app, partner integrations, and scripts).
- If other callers exist, ship all client changes together with this PR. Or add a new parameter (for example `pageIndex`) and keep `page` 1-based.
- Update the API docs to say that pages start at 0.

### Suggestions (not blocking)

**4. Validate the input.** The old code had the same gap, so this fix is optional here.
- `page=-1` gives a negative `skip`. If `db` is Prisma, the query throws and the client gets a 500.
- `page=abc` gives `NaN`.
- Return 400 for values that are not non-negative integers. Also reject `size` less than 1.

**5. Add tests.** The PR changes behavior but adds no tests. Cover these cases:
- No `page` returns the first rows.
- `page=1` returns the second page.
- `size=500` returns at most 100 rows.

### Suggested code

```ts
export async function listUsers(req, res) {
  const page = Number(req.query.page ?? 0);
  const size = Number(req.query.size ?? 20);
  if (!Number.isInteger(page) || page < 0 || !Number.isInteger(size) || size < 1) {
    return res.status(400).json({ error: "page must be >= 0 and size must be >= 1" });
  }
  const take = Math.min(size, 100);
  const users = await db.users.findMany({ skip: page * take, take });
  res.json({ page, size: take, users });
}
```

The response returns the capped `size`. This shows the client the page size that the server used.

Hold the line, shield-bearer. 🛡️