I change my answer. I do not recommend the proposed Redis cache for responses that include prices.

My earlier recommendation was too confident. I had no evidence for a 10-minute TTL or p95 below 200 ms. A TTL alone does not guarantee current prices. Your refund history shows that stale prices have a real cost.

I do not know the latency bottleneck, likely cache hit rate, or acceptable delay for price updates. Redis could add complexity without fixing the slow requests.

1. Measure where slow requests spend their time.
2. Use those measurements to choose the performance fix.
3. If measurements justify caching, consider caching stable product fields separately from prices.
4. Before caching prices, define the acceptable delay for updates.
5. Verify that the system enforces that limit during updates and failures.

Caching may eventually help. The available evidence does not justify my original recommendation.

Godspeed, Spartan.