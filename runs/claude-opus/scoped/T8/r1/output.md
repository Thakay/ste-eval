**I change my answer: do not add the 10 minute cache yet.** My first answer was too confident. I did not know where the 900 ms comes from, and I had no evidence for "well under 200 ms."

**What I don't know**

- **Where the 900 ms goes.** It could be a slow query, an N+1 pattern (one query per item in a loop), or a slow call to a pricing service. If it is a missing index, a one-day fix may solve it with no cache.
- **How often prices change.** This decides how old a cached price can safely be.
- **Your hit rate.** If traffic spreads across many products, a cache helps less than it seems.
- **What broke last time.** A 2 hour stale window suggests broken invalidation or a wrong TTL, not caching itself. The real cause tells us what to guard against.

**What I recommend**

1. Trace the slow requests to find which call takes the time.
2. If the cause is cheap to fix (an index, a query, batching), fix it and skip the cache.
3. If you still need a cache, cache only data that rarely changes: name, description, images, specs.
4. Read price and stock live from the source of truth on every request.
5. If the price lookup is the slow part, delete the cached price on every price change. Keep a short TTL as backup.
6. Make checkout always read the live price. Then a stale cache can show a wrong price, but it cannot charge one.

**The case against caching:** a cache adds a new failure mode, and your team already paid for one. If tracing shows a cheap fix, that fix is the better answer.

**One caveat:** step 6 still lets a customer see one price and pay another. That can upset customers, and some regions have rules about it. I don't know which rules apply to you.

Measure twice, cut once, legionnaire.