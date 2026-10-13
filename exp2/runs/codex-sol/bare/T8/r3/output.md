I’d change my answer: **don’t add the Redis cache I proposed for full product responses.** My ten-minute TTL and “under 200 ms” prediction had no supporting evidence.

Your previous incident is concrete evidence of a costly correctness risk. The 900 ms p95 is evidence of a performance problem, but it doesn’t tell us that caching will solve it. A faster response with the wrong price can be worse than a slow response.

I don’t know where that latency is spent, how often prices change, or why the previous cache stayed stale for two hours. Without those facts, I can’t justify Redis, choose a safe TTL, or predict the improvement. A shorter TTL still permits stale prices; invalidation needs evidence that it works when updates fail or arrive out of order.

My recommendation now is:

- **Measure the slow requests first.** Identify time spent in database queries, downstream services, and application work. Fix the measured bottleneck where possible.
- **Keep prices authoritative while investigating.** Rechecking at checkout helps prevent incorrect charges, but doesn’t make misleading displayed prices harmless.
- **Consider caching stable fields separately**, such as descriptions and images, only if that would materially reduce latency.

Caching could become defensible with an explicit freshness requirement and a tested way to meet it. Until then, another copy of pricing data adds a failure mode you’ve already paid for, without a demonstrated performance benefit.