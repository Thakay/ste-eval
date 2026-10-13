**Verdict: Request changes.** The diff drops an `await`, and that breaks the endpoint. It also removes the size limit and changes the meaning of `page` for all clients.

## Review comments

**1. Must fix: missing `await`**
On `const users = db.users.findMany(...)`:
> `users` is now a Promise, not an array. `res.json` serializes a Promise as `{}`. Every response then contains `"users": {}`. If the query fails, no code handles the rejection. In Node 15 and later, an unhandled rejection stops the process by default. Put the `await` back.

**2. Must fix: size limit removed**
On `const size = Number(req.query.size ?? 20);`:
> The old code limited `size` to 100. This diff removes that limit, and the PR description does not mention it. A client can now send `size=1000000` and read the full table in one request. The server must then hold all those rows in memory. Put `Math.min(..., 100)` back.

**3. Must fix or confirm: breaking change for current clients**
On `const page = Number(req.query.page ?? 0);`:
> This change applies to every caller, not only the mobile app. A client that starts at `page=1` now misses the first `size` users. The client gets no error, so the bug is hard to see.
> - Which other clients call this endpoint (web app, admin tools, scripts)?
> - If other clients exist, update them in the same release or add a versioned endpoint.
> - Confirm that all mobile app versions in use send zero-based pages.
> - Update the API docs for the new meaning of `page`.

**4. Should fix: no input validation (old issue)**
> `page=abc` gives `NaN`. `page=-1` gives a negative `skip`. The values `size=0`, `size=-5`, and `size=2.5` also pass through. The database call then throws or returns unexpected rows. Return `400` if a value is not a valid integer in range.

**5. Should fix: no tests**
> The diff changes no tests. Add tests for these cases:
> - A request with no `page` returns the first page.
> - `page=1` skips the first `size` rows.
> - The API caps `size` at 100.
> - An invalid `page` or `size` returns `400`.

## Suggested fix

```ts
export async function listUsers(req, res) {
  const page = Number(req.query.page ?? 0);
  const size = Number(req.query.size ?? 20);
  if (!Number.isInteger(page) || page < 0 || !Number.isInteger(size) || size < 1) {
    return res.status(400).json({ error: "page must be an integer >= 0 and size an integer >= 1" });
  }
  const take = Math.min(size, 100);
  const users = await db.users.findMany({ skip: page * take, take });
  res.json({ page, size: take, users });
}
```

This version keeps the old cap behavior instead of rejecting large sizes. That avoids a second behavior change in the same PR. The response also returns the size that the server actually used.

Raise your shield, Hoplite. This one does not pass the gate until the `await` comes home.