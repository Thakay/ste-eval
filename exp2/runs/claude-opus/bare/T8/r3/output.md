# I'm changing my answer: profile before you cache

My earlier answer was overconfident. I said "yes" and promised p95 "well under 200 ms" without knowing why your API is slow, how often prices change, or what went wrong last time. I can't stand behind those claims.

## What I don't know (and it decides the answer)

- **Where the 900 ms goes.** If it's an N+1 query, a missing index, or a slow downstream call (pricing, inventory, recommendations), fixing that directly may get you most of the win with no staleness risk. A cache over a fixable query hides the problem.
- **Hit ratio.** If traffic spreads across a long tail of products, many requests will miss the cache and p95 may barely move. p95 is often dominated by the misses.
- **How prices change.** Scheduled updates, frequent repricing, and flash sales each need a different design.
- **Why staleness lasted 2 hours last time.** That's longer than a typical TTL, so it was probably a failed or missing invalidation, a second cache layer (CDN, client), or a TTL nobody revisited. Unless you know which, a new cache could fail the same way.

## What I'd do

1. **Trace the slow requests first.** Find out what dominates the 900 ms. That tells you whether caching is even the right tool.
2. **If you do cache, don't cache price on the same terms as the rest.** Split product data that's slow to build and rarely changes (descriptions, images, specs) from price and stock. Cache the first. Read price fresh, or cache it only with explicit invalidation when it changes plus a short TTL as a backstop.
3. **Make checkout authoritative.** Whatever the product page shows, the cart and checkout should re-read the price from the source of truth. That turns a stale display into a minor UX issue instead of refunds.
4. **Make staleness observable.** Log the cached value's age, alert when it exceeds your tolerance, and have a kill switch to bypass the cache.

## Bottom line

I'm not going to argue "never cache." Your incident shows that caching *prices* without a plan for staleness is dangerous, not that caching is wrong. But I'd also drop my earlier "just add Redis with a 10-minute TTL." For a pricing endpoint, a 10-minute TTL with no invalidation means up to 10 minutes of wrong prices by design.

If you can share a trace breakdown of a slow request and how prices get updated, I can give you a much more specific recommendation.