I change my answer: **do not add Redis caching yet.** My earlier recommendation was too confident. The 900 ms p95 alone does not justify caching or support my promise of latency below 200 ms.

Your refund incident makes price freshness a critical requirement. A ten-minute TTL can still expose customers to prices that are ten minutes old. I do not know what caused the two-hour delay, so I cannot say a shorter TTL would prevent another incident.

I also do not know whether database queries, external services, or application work cause the latency. We need that information before we choose a fix.

1. Measure where slow requests spend their time.
2. Fix the measured cause, such as slow queries or repeated database calls.
3. Define the maximum acceptable delay for price changes.

Consider caching prices only after you can meet that freshness requirement during updates and failures. If customers require current prices, avoid a price cache that relies only on TTL expiration.

Advance with care, Spartan.