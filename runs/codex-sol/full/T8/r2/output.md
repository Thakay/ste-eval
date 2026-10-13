I change my answer: do not add the proposed Redis cache now.

I chose the 10-minute TTL without evidence. I also had no basis for predicting p95 below 200 ms.

A 900 ms p95 does not identify the bottleneck. I do not know your cache hit rate, required price freshness, or why the previous cache served stale prices for two hours.

A TTL limits an entry’s lifetime. It does not guarantee that the price is current. The refund incident shows a real cost from stale prices.

My recommendation is:

1. Measure time spent in database queries, external calls, and application work.
2. Use those measurements to choose a fix. Slow queries might need indexes or fewer database calls.
3. Before caching prices, define the acceptable delay after a price change. Test whether the design meets that limit when updates fail.

Caching stable product fields might help. We lack evidence that caching will solve your latency problem while meeting your price requirements.

Stand firm, Spartan.