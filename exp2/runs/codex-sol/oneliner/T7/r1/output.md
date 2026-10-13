**Request changes.**

1. **`const users = db.users.findMany(...)`**  
   Add `await` before `db.users.findMany(...)`. The function returns a promise. Without `await`, `res.json` receives the promise instead of the user list.

2. **`const size = Number(req.query.size ?? 20)`**  
   Keep the maximum page size of 100. A client can now request a very large page. This can use too much memory and increase response time. The change to zero-based pages does not require removal of this limit.