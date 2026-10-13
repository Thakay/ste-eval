**I change my answer. Do not add the cache now.**

My first answer was too confident. I said "well under 200 ms," but I had no data for that number. I do not know the cause of your latency.

**Why the cache can fail**

- A cache does not repair a slow query. It only hides the slow query when the data is in the cache.
- Requests can go to many different products. If so, many requests do not find the data in the cache. Then p95 does not decrease much.
- With a 10 minute TTL, a price can stay incorrect for 10 minutes. If the removal of old entries fails, the time can be longer. You had 2 hours.

**What I do not know**

- The cause of the 900 ms. It can be a slow database query, many small queries, or calls to other services.
- How frequently your prices change.
- The ratio of reads to writes.
- Why the last cache kept old prices for 2 hours. Was the TTL too long? Did the removal of old entries fail? Did a CDN or a second cache also keep the data?

**Procedure**

1. Find the cause of the latency first. Use a trace tool or the query logs for the slow requests.
2. Repair the cause if possible. For example, add an index or change the query. This does not cause old prices.
3. If the latency stays too high, cache only data that changes slowly, for example descriptions and images. Read the price from the database for each request.
4. If you must cache the price, remove the cache entry when the price changes. Also set a short TTL, for example 30 seconds, as a second safety limit.

**WARNING:** Always read the price from the database at checkout. Do not use a cached price to calculate the payment. This prevents refunds from an incorrect cache.

Tell me what the trace shows. Then I can give a better recommendation.