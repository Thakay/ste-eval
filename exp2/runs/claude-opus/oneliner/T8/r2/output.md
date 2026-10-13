**I change my answer.** My first answer was too confident. I did not know the cause of the 900 ms, and I did not know about the old incident. Do not add the cache yet.

**What I do not know**

- I do not know where the 900 ms goes. The cause can be a slow query, a missing index, many small queries (N+1), or a slow call to a different service.
- I do not know how frequently your prices change.
- I do not know if checkout gets the price again from the database.
- I do not know why the old values stayed for 2 hours. If the cause was bad invalidation logic, a 10-minute TTL does not prevent the same problem.

**Why my first claim was not correct**

I said "well under 200 ms," but I had no data for that claim. A cache makes only cache hits faster. Misses still take 900 ms. If fewer than 95% of requests are hits, the p95 can stay near 900 ms. Also, a 10-minute TTL lets each price be up to 10 minutes old. For prices, that can be too long.

**What to do**

1. Find the cause of the latency first. Use traces or a profiler on the slow requests.
2. If the cause is a query or an index, fix it. Then you possibly do not need a cache.
3. If you need a cache, do not put the price in it. Cache only data that changes slowly, such as the name, description, and images.
4. Get the price and stock from the source of truth on each request.
5. Make sure that checkout always gets the price from the source of truth. Then an old value on the page cannot cause an incorrect charge.
6. If you must cache the price, delete the cache key when the price changes. Use a short TTL only as a safety limit.
7. Monitor the age of the cached values. Set an alarm for old values.
8. Find the root cause of the old incident before you add a new cache.

**Summary**

The 900 ms is a real problem. A cache can be part of the solution, but it is not the first step. Never use a cached price as the price that you charge.