**Verdict: Request changes.** The zero-based switch is fine as an idea. But the diff also drops an `await` and removes the `size` cap. The PR description mentions neither change, and both cause real bugs.

## Review comments

**1. Blocker: missing `await` on `db.users.findMany`**

`users` is now a Promise, not an array. `res.json` serializes a Promise as `{}`, so every response returns `users: {}`. A database error also becomes an unhandled rejection, not a normal request error.

- Restore `await`.

**2. Blocker: `size` cap removed**

The old code capped `size` at 100 with `Math.min`. Now a client can send `size=1000000` and pull the whole users table in one request. This is a load and denial-of-service risk. It also exposes more user data per call. This change is not part of the zero-based switch.

- Restore the cap.

**3. Breaking change for current clients**

A client that sends `page=1` for the first page now gets the second page. It skips the first 20 users with no error, so nobody notices. Requests with no `page` parameter still work.

- List every client of this endpoint (web app, admin tools, integrations).
- If the mobile app is the only client, ship the server and app changes together.
- If other clients exist, do not change what `page` means.

Simpler option to consider: the mobile app can send `page + 1` and the server stays one-based. That fixes the mismatch with no breaking change.

**4. Input validation (old gap, cheap to fix now)**

- `page=abc` gives `NaN`.
- `page=-1` gives a negative `skip`.
- `page=1.5` gives a fractional `skip`.

The ORM will likely throw on these, so the client gets a 500, not a 400. Suggested version:

```ts
const page = Number(req.query.page ?? 0);
const size = Math.min(Number(req.query.size ?? 20), 100);
if (!Number.isInteger(page) || page < 0 || !Number.isInteger(size) || size < 1) {
  return res.status(400).json({ error: "invalid page or size" });
}
const users = await db.users.findMany({ skip: page * size, take: size });
res.json({ page, size, users });
```

`Math.min` returns `NaN` for a bad `size`, and `Number.isInteger(NaN)` is false, so the check catches it.

**5. Tests and docs**

The diff has no test changes.

- Add a test that `page=0` returns the first page.
- Add a test that `size` above 100 returns 100 users at most.
- Add a test that bad input returns 400.
- Update the API docs to say pages start at 0.

Shields locked, Kay. Hold the gate until the `await` comes home.