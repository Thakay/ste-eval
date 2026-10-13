**Request changes.**

1. **P1: Restore `await` on `db.users.findMany()`.**  
   `users` now contains a promise instead of the user array. `res.json()` does not wait for that promise. Await the query before sending the response.

2. **P2: Restore the 100-user page limit.**  
   Removing the cap allows requests such as `?size=1000000`. Large requests can overload the database and exhaust server memory. Keep the cap while changing the page numbering.

Godspeed, Spartan.