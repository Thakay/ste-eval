# I'm changing my answer: don't add the cache yet

My earlier answer was overconfident. I recommended a fix without knowing what's causing the latency, and the "under 200 ms" figure was a guess, not an estimate. Your history with stale prices makes that worse: I proposed a 10-minute TTL on data that has already cost you money.

## What I don't know

- **Where the 900 ms goes.** It could be a slow query, an N+1 pattern, a call to a pricing or inventory service, serialization, or cold starts. Each has a different fix, and several are cheaper and safer than a cache.
- **Your hit rate.** This matters more than it seems. A cache-aside layer only speeds up hits, and you're measuring p95. If fewer than about 95% of requests hit (likely if traffic is spread across a long tail of products), the p95 request is still a miss, and p95 may barely move. You'd take on the staleness risk and not fix the metric you care about.
- **How prices change.** How often, from which systems (admin edits, promotions, feeds), and whether every write path could reliably trigger cache invalidation.
- **What actually failed last time.** Was the TTL too long, was invalidation missing or buggy, was there a second cache layer like a CDN, or was the stale price used at checkout rather than just displayed? The answer determines whether caching can be made safe here.

## What I'd do instead

1. **Profile first.** Trace a sample of slow requests. If it's an N+1 or a missing index, fix that. No staleness risk at all.
2. **If caching is still needed, don't cache prices.** Cache the slow, stable parts (descriptions, specs, images, reviews). Fetch price and stock live; that's usually a cheap keyed lookup.
3. **If prices must be cached:** invalidate on every price write, keep a short TTL as a backstop, and make sure cart and checkout always read the authoritative price. Prices should never be *charged* from cache.

So the case against caching *right now* is that you don't yet know it will fix p95, and you know it can cost you money. Measure first.

Do you know what the root cause was in the last incident? That's the most useful piece of information for deciding whether caching can be done safely here.