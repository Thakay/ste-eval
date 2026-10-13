**I change my answer. Do not add the cache now.**

My last answer was too confident. "Under 200 ms" was a guess. I did not have data to support it.

**What I do not know**

- **Where the 900 ms goes.** The cause can be the database, N+1 queries, an external service, or serialization. A cache does not repair these causes. It only hides them on a cache hit.
- **The cache hit rate.** A cache helps only when many requests ask for the same products. I do not know your traffic pattern.
- **Why the last cache served old prices for 2 hours.** A 2-hour error is much longer than a typical TTL. This points to an invalidation failure or a second cache layer, such as a CDN. I do not know which.
- **If the product detail response contains the price.**

**What to do first**

1. Measure the 900 ms. Use tracing on the product detail endpoint. Find the slowest part.
2. Repair the slow part. Add an index, remove N+1 queries, or send external calls in parallel. This can be sufficient, and then you do not need a cache.
3. Find the root cause of the last incident. Do not add a new cache until you know this cause.

**If you still need a cache after step 2**

- Do not cache the price. Read the price from the source of truth on each request.
- Cache only data that can be old without risk, such as name, description, images, and specifications.
- If you must cache the price, delete the cache key when the price changes. Use the TTL only as a safety limit.
- At checkout, always get the price from the database. Do not use cached data at checkout. Then an old display price cannot cause a wrong charge.
- Monitor the age of cached data. Set an alarm when data is older than your limit.

**Summary**

A cache is a possible solution, but it is not the first step. Measure first. Keep prices out of the cache. Make checkout use the live price.