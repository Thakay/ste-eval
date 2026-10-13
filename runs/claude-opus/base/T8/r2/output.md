**I'm changing my answer: don't add the cache yet.** My first reply was overconfident. I suggested a fix and promised "under 200 ms" without knowing where the 900 ms comes from.

**Why I changed**

- **The cause is unknown.** 900 ms could be a missing index, N+1 queries (one database query per related item), a slow call to a pricing or inventory service, or a large payload. A cache hides these problems instead of fixing them. Cache misses still take the slow path, so if you have many products and a low hit rate, p95 may barely move.
- **Prices are the worst thing to cache.** A 10 minute TTL means a changed price can be wrong for up to 10 minutes by design. Your refund incident shows that cost is real.
- **A cache adds a second source of truth.** That is exactly what hurt you last time.

**What I'd do instead**

1. **Measure first.** Add tracing to the endpoint and find which step takes the time. This is cheap, and it tells you whether caching is even the right tool.
2. **Fix the root cause** if it's a query or index problem. That is often the biggest and cheapest win, with no staleness risk.
3. **Cache only if it's still slow, and never the price.** Cache the parts that rarely change (name, description, images, specs) and read the price live. If the price lookup itself is the slow part, cache it only with invalidation on every price write, a short TTL as a backstop, and an alert on cache age.
4. **Hard rule either way:** checkout and order creation always read the price from the source of truth, never from cache.

**What I don't know**

- Where the 900 ms actually goes.
- Why the last cache stayed stale for 2 hours. Was it a long TTL, a missed invalidation path (for example, bulk price imports skipping the invalidation hook), or a key bug? If you don't know, any new cache can repeat it.
- How often prices change, and whether checkout already uses the live price. If it does, stale prices are a display problem rather than a refund problem. Showing one price and charging another still causes trouble, though.
- Your traffic pattern and the hit rate you'd get.
- Whether 900 ms is actually hurting conversion, or is just a number that looks bad.

If tracing shows the time is spent somewhere a cache can't help, you've saved yourself a risky change. If it shows caching is the right tool, you'll know exactly what to cache and what to leave alone.

Measure before you strike, Legionnaire.