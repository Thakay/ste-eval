I change my answer. Do not add Redis caching now.

I had no evidence for a 10-minute TTL or a p95 below 200 ms. A TTL alone does not prevent old prices.

Your last cache caused refunds. The benefit of a new cache is unknown. I do not know where the delay occurs, how often prices change, or how your system applies price updates.

First, measure the time spent in database queries, external calls, and application code. Use those results to select a change.

Read prices from the system that controls price updates. Consider a separate cache for product descriptions only if old descriptions are acceptable and measurements show a useful speed increase.