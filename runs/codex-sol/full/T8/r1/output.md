I change my answer. Do not add the proposed Redis cache for product details that include prices.

My earlier recommendation was too confident. I had no evidence for a ten-minute TTL or a p95 below 200 ms. A 900 ms p95 does not identify the cause.

Your refunds show that stale prices have a real cost. A TTL does not guarantee current prices. Even ten minutes of stale prices could be unacceptable.

I do not know:

- What causes the slow requests.
- How many requests a cache would accelerate.
- How much price staleness your business can accept.
- What caused the previous two-hour incident.

Before choosing a fix:

1. Measure where slow requests spend their time.
2. Define the maximum acceptable price staleness.
3. Address the measured bottleneck, such as an expensive database query.

Caching descriptions or images may still be useful. I would reconsider price caching only with clear freshness requirements and evidence that the design meets them during failures.

For now, the known cost of stale prices outweighs a performance benefit we did not establish.

Stand firm, Spartan.