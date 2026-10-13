**Request changes.**

1. **P1, `const users = ...`:** Restore `await` before `db.users.findMany`. Without it, `users` is a promise, so the response contains `{}` instead of the user array. Query failures can also become unhandled rejections.

2. **P2, `const size = ...`:** Restore the 100-user cap. Removing it lets clients request very large result sets, increasing database load, memory use, and response size.

Godspeed, Spartan.