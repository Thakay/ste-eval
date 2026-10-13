**Decision: Request changes.**

This PR has one critical error and two high-risk changes. Correct items 1, 2, and 3 before you merge.

---

**1. No `await` on `findMany` (critical)**

The new code removes `await`. Thus, `users` is a `Promise`, not an array. `res.json` serializes a `Promise` as `{}`. All clients get no user data.

Put `await` back:

```ts
const users = await db.users.findMany({ skip: page * size, take: size });
```

---

**2. The size limit is removed (high)**

The old code limited `size` to 100. The new code has no limit. A client can send `size=1000000`. This causes a very large database query. This query can make the server slow or stop it. The PR description does not mention this change. I think that this change is an error.

Put the limit back:

```ts
const size = Math.min(Number(req.query.size ?? 20), 100);
```

---

**3. Breaking change for current clients (high)**

Current clients send `page=1` for the first page. After this change, `page=1` gives the second page. These clients will not show the first 20 users, and they will not show an error. This error is difficult to find.

Do one of these steps before you merge:

- Add a new API version (for example, `/v2/users`) for zero-based pages.
- Make sure that all clients (web, mobile, and third-party) change at the same time as the server.

Tell me which clients use this endpoint now.

---

**4. No input validation (medium)**

This condition was in the old code, but the removal of the size limit makes it worse.

- `Number("abc")` gives `NaN`.
- A negative `page` gives a negative `skip`. This causes a database error.
- A negative `size` gives a negative `take`. If `db` is Prisma, a negative `take` reads records in the opposite direction.

Validate the values. Send HTTP 400 for values that are not correct:

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

This code also sends the size that the server used, not the size that the client requested.

---

**5. Tests and documentation (low)**

The diff has no test changes. Add tests for these conditions:

- `page=0` gives the first records.
- The response has a user array, not `{}`.
- A `size` value above 100 gives 100 records or fewer.
- Values that are not correct give HTTP 400.

Update the API documentation for zero-based pages.