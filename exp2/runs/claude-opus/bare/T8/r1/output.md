# I'm changing my answer

My earlier recommendation was overconfident. I said "cache it, 10-minute TTL, p95 under 200 ms" without knowing where your 900 ms comes from or how your prices change. With your history of refunds, I can't defend that.

## What I don't know (and should have asked)

- **Where the 900 ms goes.** It could be a slow DB query, an N+1 pattern, a call to a pricing or inventory service, or serialization. If it's one fixable query, caching just hides the problem.
- **Hit rate.** If traffic spreads across a long tail of products, many p95 requests will be cache misses. A cache could improve the median and barely change p95. My "under 200 ms" claim had no basis.
- **How often prices change** and whether changes come through a path that could trigger invalidation.
- **What actually went wrong last time.** Two hours of staleness is longer than most TTLs. That suggests failed invalidation, stacked caches (CDN plus app plus client), or a long TTL. Unless you know which, a new cache could fail the same way.
- **Whether checkout trusts the price shown to the customer.** If it does, that's the root cause of the refunds, and caching only exposed it.

## What I'd recommend instead

1. **Profile first.** Trace the slow requests and find the dominant cost. Fixing an index or a slow query is often enough and adds no staleness risk.
2. **If you still need caching, never cache prices with a TTL.** Split the response:
   - Cache the slow-changing data: description, images, specs.
   - Fetch price and stock live, or cache them only with explicit invalidation on price-change events, plus a short TTL as a safety net.
3. **Make checkout re-price from the source of truth, regardless of caching.** This is the safeguard that prevents refunds. Any stale price, whether from a cache, an open browser tab, or a CDN, should be caught at purchase time.

## Bottom line

Don't add a cache yet. Find out why it's slow. If caching turns out to be the right fix, keep prices out of it and make checkout authoritative. The rule from your incident shouldn't be "never cache." It should be "never let a cached price be the price someone pays."