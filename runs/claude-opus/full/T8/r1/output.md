**I change my answer. Do not add the cache yet.** My first answer was too confident. I said p95 would drop "well under 200 ms," but I had no data about where the 900 ms goes.

**What I do not know**

- **Where the 900 ms goes.** Possible causes include a slow query, N+1 queries (one extra query per related row), or a slow downstream service. A cache hides the cause. It does not fix it.
- **Your hit rate.** A cache helps only on a hit. A miss still costs 900 ms. If many requests ask for products that people rarely view, p95 may not drop much.
- **How often prices change**, and what one minute of a wrong price costs you.
- **Why the last cache stayed stale for 2 hours.** Something did not expire or clear the old data. Possible causes are a long TTL, a missing invalidation, or a second cache layer such as a CDN. If you do not know the cause, a new cache can repeat it.

**What I recommend**

1. Trace the slowest requests. Find the step that uses the time.
2. Fix that step directly if you can. A new index or fewer queries cannot serve a stale price.
3. If you still need a cache after that, do not cache price or stock. Cache only fields that rarely change, such as name, description, and images.
4. If you must cache price, delete the cache entry on each price change. Keep a short TTL as a backup. Always read the price from the database at checkout.
5. Find the root cause of the 2-hour incident before you deploy any new cache.

Hold the line, Centurion. Measure first, then strike.