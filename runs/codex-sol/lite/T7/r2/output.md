**Request changes.**

1. **P1: Missing `await` on `findMany`.** `users` contains a Promise, so `res.json` does not return the user records. Restore `await` before sending the response.

2. **P2: Removed size limit.** Clients can now request arbitrarily large result sets, which can overload the database and server. Restore the 100-user cap.

Godspeed Spartan.