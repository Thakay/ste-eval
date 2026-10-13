**Request changes.** Two bugs block the merge, and the change to what `page` means needs a rollout plan.

### Blocking

1. **Missing `await` on `findMany`.** `users` is now a Promise. `res.json` turns a Promise into `{}`, so every response returns `"users": {}`. A database error also becomes an unhandled rejection instead of a 500. Put `await` back.

2. **The page size cap is gone.** The old code limited `size` to 100. Now a client can send `?size=1000000` and pull the whole table in one request. That is a memory and denial-of-service risk. The PR description does not mention this change, so it looks accidental. Put the cap back.

3. **Silent breaking change for current clients.** A client that still sends `page=1` for the first page now gets the second page. It gets no error, so it skips the first 20 users without any sign. Before merge, confirm:
   - Which clients call this endpoint? Check the web app, admin tools, and old mobile builds still on users' phones.
   - Do all of them switch in the same release?

   If they cannot all switch at once, do not change what `page` means. Add a new parameter or a versioned route instead. The simplest option may be to change only the mobile app so it sends `page + 1`. That fix carries no risk to other clients.

### Should fix

4. **No input validation.** This problem existed before, but this PR is a good time to fix it. `?page=abc` gives `NaN`, and `?page=-1` gives a negative `skip`. Most ORMs, Prisma included, throw on both, so the client gets a 500 instead of a 400. Non-integer, zero, and negative `size` values also get through.

5. **Tests and docs.** Add tests for page 0, the size cap, and bad input. Update the API docs to describe the new zero-based pages.

### Suggested code

```ts
const MAX_SIZE = 100;

export async function listUsers(req, res) {
  const page = Number(req.query.page ?? 0);
  const size = Math.min(Number(req.query.size ?? 20), MAX_SIZE);
  if (!Number.isInteger(page) || page < 0 || !Number.isInteger(size) || size < 1) {
    return res.status(400).json({ error: `page must be an integer >= 0; size must be an integer from 1 to ${MAX_SIZE}` });
  }
  const users = await db.users.findMany({ skip: page * size, take: size });
  res.json({ page, size, users });
}
```

`Math.min(NaN, 100)` returns `NaN`, so the `Number.isInteger` check also catches a bad `size`.

Stand fast at the gate, sentinel. Nothing broken gets past the wall.