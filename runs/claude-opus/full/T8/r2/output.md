**I change my answer. Do not add a cache yet.** My first answer was too confident. I did not ask where the 900 ms goes, or how fresh prices must be. "Well under 200 ms" was a guess, not a measurement.

**What I don't know, and why it matters**

| Unknown | Why it matters |
|---|---|
| Where the 900 ms goes | A missing index or a slow downstream call may be a cheaper fix than a cache. |
| Which requests make up the p95 | The slowest requests are often cache misses, like rare products or the first request after a key expires. If so, p95 may barely move even when the median drops. |
| How often prices change, and how fast a change must show | This sets the longest safe TTL. For some prices, the safe TTL may be zero. |
| What caused the 2 hours of stale prices last time | A long TTL, a missed invalidation, and a key with no expiry each need a different guard. |
| Whether checkout charges the price on the page or reads it again | If checkout charges the cached price, every stale minute can cost money. |

**What I recommend instead**

1. Trace the slow requests and find the step that takes the time.
2. If the cause is cheap to fix, fix it directly. Examples: a missing index, N+1 queries (one query per item in a loop), or a slow call to another service.
3. If you still need a cache, cache only the fields that rarely change (name, description, images, specs). Read the price from the source of truth on every request.
4. Make checkout read the price from the source of truth, whatever the product page shows. This guard protects you from any stale-price bug, with or without a cache.

**My honest view:** the lesson from the refunds is "never cache price without a guard", not "never cache". Step 4 is worth doing even if you never add a cache. The non-price fields are probably safe to cache, but I cannot confirm that without your data model and traffic data.

Measure twice, strike once, legionnaire.