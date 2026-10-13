I’d change my answer: **don’t add the proposed Redis cache yet.** My 10-minute TTL recommendation and prediction of p95 below 200 ms were unjustified.

A 10-minute TTL permits stale prices during that window. We haven’t established that any price staleness is acceptable, and your refund incident gives us a concrete cost when it goes wrong. Redis alone doesn’t solve freshness.

I don’t know where the 900 ms is spent, what caused the previous two-hour staleness, or what cache hit rate you’d achieve. If slow requests are mostly cache misses, p95 could remain high anyway.

My recommendation is:

- Trace slow requests to identify the expensive database queries, downstream calls, or other bottlenecks.
- Investigate the previous stale-price failure before introducing another cache.
- Keep prices on an authoritative read path while optimizing the measured bottleneck. If caching later proves worthwhile, consider stable product metadata separately.

Caching could eventually be justified. **Right now, we have a known correctness cost and an unmeasured performance benefit.** That’s enough reason to reject my original proposal.