**I am changing my answer: do not add the cache yet. My first answer was too confident.** I did not know where the 900 ms comes from, and I still do not know. The "well under 200 ms" claim had no data behind it.

**Why I changed my answer**

- A cache hides a slow request. It does not fix the cause. The cause can be a missing index, N+1 queries, or a slow pricing service.
- A 10 minute TTL means wrong prices for up to 10 minutes, by design. If invalidation fails, the wrong price can stay longer. Your 2 hour incident shows this.
- The speed gain depends on the cache hit rate. If customers view many different products, most requests miss the cache. Then p95 stays high.

**My honest position:** I will not argue "never cache." The risk is caching **price**. Product data that does not affect money is safe to cache.

| Data | Cache it? | Reason |
|---|---|---|
| Description, images, specs | Yes, if profiling shows you need it | It changes rarely. Stale data costs no money. |
| Price, discounts | No | A stale price causes refunds. |
| Stock (if the endpoint shows it) | No | Stale stock causes overselling. |

**What to do**

1. Profile the endpoint. Find which part uses the 900 ms.
2. If the cause is cheap to fix, fix it first. Then measure p95 again.
3. If p95 is still too high, cache only the data from the "Yes" row.
4. Read price from the source of truth on every request.
5. Make checkout read the price from the source of truth. This step prevents refunds, even if a page shows an old price.

**What I do not know**

- Where the 900 ms goes.
- How often prices change, and which system changes them.
- Why the last incident lasted 2 hours. It can be a long TTL, failed invalidation, or no alert. Please tell me, because the answer changes the design.
- If checkout uses the cached price or the source of truth.

Measure before you march, quartermaster.