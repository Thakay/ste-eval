I change my answer: **I would not add Redis caching to this endpoint yet.**

My earlier advice was too confident. A 900 ms p95 does not identify the bottleneck. I had no basis for choosing a 10 minute TTL or promising latency below 200 ms.

Your refund incident makes price freshness a business requirement. Even a correctly enforced 10 minute TTL could show an outdated price for nearly 10 minutes. That may still be unacceptable.

I do not know:

- Whether database queries, downstream services, or something else cause the delay.
- Whether repeated requests would produce enough cache hits to improve p95.
- How prices change, how the previous cache failed, or whether checkout verifies the current price.

I would first measure where slow requests spend their time. Those measurements may support query improvements or fewer downstream calls, without adding another copy of prices.

Caching could later make sense for descriptions or images, separately from prices. Price caching needs an explicit freshness requirement and evidence that the design meets it during updates and failures.

**The latency measurement supports investigation. It does not yet justify Redis.**

Stand firm, Spartan.