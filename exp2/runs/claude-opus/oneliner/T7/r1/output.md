**Decision: Request changes**

This PR has one critical defect and two high-risk problems. Correct them before you merge.

---

### 1. Critical: There is no `await` on the database query

```ts
const users = db.users.findMany({ skip: page * size, take: size });
```

- `findMany` gives a Promise. Without `await`, `users` is a Promise, not an array.
- `res.json` changes a Promise to `{}`. Thus, the API sends `"users": {}` for all requests.
- If the query fails, the code does not catch the error. This causes an unhandled rejection.

**Fix:**

```ts
const users = await db.users.findMany({ skip: page * size, take: size });
```

---

### 2. High: The PR removes the limit on `size`

- The old code limited `size` to 100. The new code has no limit.
- A user can send `size=1000000`. Then the database reads very many rows into memory.
- This can make the service slow or stop it.
- The PR description does not give a reason for this change. It is not related to zero-based pages.

**Fix:** Keep the limit.

```ts
const size = Math.min(Number(req.query.size ?? 20), 100);
```

---

### 3. High: The change is not compatible with current clients

- Current clients send `page=1` for the first page. After this change, `page=1` gives the second page.
- Thus, these clients do not show the first 20 users.
- No error occurs, so this problem is difficult to find.
- The PR description refers only to the mobile app. Other clients can also use this endpoint (web app, scripts, integrations).

**Fix:** Add a new API version (for example, `/v2/users`) with zero-based pages. Do not change the old endpoint. If a new version is not possible, release this change at the same time as the updates for all clients.

---

### 4. Medium: The code does not validate the input

- `Number("abc")` gives `NaN`.
- A negative `page` gives a negative `skip` value.
- A `size` of 0 or less is also possible.
- The ORM can send an error for these values. Then the client gets a 500 error, not a 400 error.
- The old code also had this problem. But this PR changes these lines, so correct it now.

**Fix:**

```ts
const page = Number(req.query.page ?? 0);
const size = Math.min(Number(req.query.size ?? 20), 100);
if (!Number.isInteger(page) || page < 0 || !Number.isInteger(size) || size < 1) {
  return res.status(400).json({ error: "Invalid page or size" });
}
```

---

### 5. Low: Tests and documentation

- The diff does not show test changes. Add tests for these conditions:
  - `page=0` gives the first page.
  - `size` larger than 100 gives 100 rows.
  - Values that are not valid give a 400 error.
- Change the API documentation. It must say that pages start at 0.