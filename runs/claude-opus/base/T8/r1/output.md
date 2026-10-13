**I'm changing my answer.** My first reply was overconfident. Don't add a cache yet. First find out where the 900 ms goes. If caching still turns out to be the fix, cache the slow-changing product data, never the price on a timer alone.

**What I got wrong**

- **I don't know why the endpoint is slow.** It could be a slow query (missing index, N+1 queries), a slow downstream call (pricing, inventory), or serialization. A cache hides the cause instead of fixing it, and a query fix carries zero stale-price risk.
- **"Under 200 ms" was a guess.** A cache only speeds up hits. For p95 to drop, more than about 95% of requests must be hits. If traffic is spread across a long tail of products, most of the slowest 5% will still be misses at ~900 ms, and p95 barely moves.
- **A 10 minute TTL on prices repeats your last incident.** The shape is the same: any price change is wrong for up to 10 minutes, longer if invalidation breaks.

**What I don't know that would change the answer**

- Where the 900 ms is spent.
- How many products you have and how traffic spreads across them (this sets the possible hit rate).
- How often prices change, and whether they vary by customer, region, or promo.
- What actually caused the 2-hour staleness last time. Two hours suggests failed invalidation or a second cache layer (CDN, browser), not just a long TTL. If you don't know the root cause, a new cache can fail the same way.

**What I'd do**

1. **Profile the endpoint** with tracing or the slow query log. Fix the actual bottleneck first.
2. **If you still need a cache, split the data.** Cache name, description, images, and specs. Read price and stock live, or cache price only with invalidation on every price change plus a short TTL as a backstop.
3. **Make checkout read the price from the source of truth, always.** If it differs from what the page showed, tell the customer before charging. This guardrail is what prevents refunds, whether you cache or not.
4. **Measure the hit rate and p95** after any change, so you know the cache earns its complexity.

Hunt the real bottleneck first, then strike. Hold the line, Centurion.