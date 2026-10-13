## Review: request changes

This PR has one bug that makes the endpoint return no users. The PR also removes a size limit and changes the API for all clients.

### 1. Missing `await`: must fix

Line: `const users = db.users.findMany({ skip: page * size, take: size });`

The code does not wait for `findMany`. Thus, `users` is a Promise, not an array. `res.json` serializes a Promise as `{}`. Each response then contains `"users": {}`. If the query fails, the code does not catch the rejection.

Put `await` back:

```ts
const users = await db.users.findMany({ skip: page * size, take: size });
```

### 2. Size limit removed: must fix

The diff removes `Math.min(..., 100)`. A client can now send `size=1000000`. The database then reads all rows for one request. This can cause high memory use and slow responses. An attacker can use this to stop the service.

The PR description does not mention this change. Keep the limit:

```ts
const size = Math.min(Number(req.query.size ?? 20), 100);
```

If you must remove the limit, write the reason in the PR description.

### 3. Breaking change for current clients: must fix

Current clients send `page=1` for the first page. After this change, `page=1` returns the second page. These clients will not show the first page. The API does not return an error, so this problem is difficult to find.

This change affects all clients, not only the mobile app. Do one of these steps:

- Change the mobile app to add 1 to the page number. This is the smallest change.
- Add a new API version (for example, `/v2/users`) with zero-based pages.
- Add a new parameter (for example, `pageIndex`) and keep `page` one-based.
- Make sure that the team updates all other clients in the same release.

### 4. No input validation: should fix

This problem was in the code before this PR. But the PR makes it more dangerous because the size limit is gone.

- `page=abc` gives `NaN`. The ORM can then throw an error, and the endpoint returns 500.
- `page=-1` gives a negative `skip`. This can also cause a 500 error.
- `size=-5` gives a negative `take`. In Prisma, a negative `take` reads rows in reverse order.

Validate the values and return 400 for incorrect input:

```ts
const page = Number(req.query.page ?? 0);
const size = Number(req.query.size ?? 20);
if (!Number.isInteger(page) || page < 0 || !Number.isInteger(size) || size < 1) {
  return res.status(400).json({ error: "Invalid page or size" });
}
const take = Math.min(size, 100);
const users = await db.users.findMany({ skip: page * take, take });
res.json({ page, size: take, users });
```

### 5. Tests and documentation: should fix

The diff does not change tests or API documentation. Add tests for these conditions:

- The first page (`page=0`).
- The default values.
- A `size` value more than 100.
- Incorrect values (`-1`, `abc`).

Update the API documentation. Show that pages now start at 0.

### Decision

**Request changes.** Fix items 1, 2, and 3 before you merge this PR.