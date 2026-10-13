**Request changes.**

1. At `const users = db.users.findMany(...)`: Add `await`. Without it, `users` contains a Promise instead of the user records. The response does not contain the required list. Database errors also do not reach the function’s caller.

2. At `const size = Number(req.query.size ?? 20)`: Keep the maximum page size of 100. This change removes that limit. A client can request a very large number of users. Such requests can cause high memory use and slow responses. The change to zero-based pages does not require removal of this limit.