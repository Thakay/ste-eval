**Request changes.**

- **[P1] `db.users.findMany`:** Add `await`. Without it, `users` is a promise. The response does not contain the user records.
- **[P2] `size`:** Restore the limit of 100 records. Without this limit, large requests can increase memory use and response time.