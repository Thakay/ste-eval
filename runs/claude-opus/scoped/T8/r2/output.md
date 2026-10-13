**I change my answer: do not add a cache yet.** My first answer was too confident. I said "well under 200 ms" with no data about where your 900 ms goes.

**Why I changed it**

- A cache hides a slow path but does not fix it. If the cause is a missing index, an N+1 query, or a slow pricing call, a fix there gives you the speed with no risk of stale data.
- Cache-aside helps only on a cache hit. If your p95 comes from a long tail of rarely viewed products, most of those requests miss the cache, and p95 may barely move.
- Price is the one field where stale data costs real money. You already paid that cost once.

**What I don't know**

- Where the 900 ms goes: the database, an upstream service, serialization, or cold starts.
- How often prices change, and whether every price change goes through one write path that you control.
- Your read pattern: a few hot products, or a long tail.
- Why the last cache served prices that were 2 hours old. A 10 minute TTL alone cannot do that. So something else failed, for example a key with no TTL, a missed invalidation, or a CDN layer on top. Find that cause before you build any new cache, because the same failure can happen again with Redis.

**What I recommend**

1. Trace 20 slow requests in production.
2. Find the step that uses most of the 900 ms.
3. Fix that step.
4. Measure p95 again.
5. If p95 is still above your target, cache only the static fields: name, description, images, and specs.
6. Read price and stock from the source of truth on every request.
7. Make checkout charge the live price, never a cached price.

Step 7 is your real guard against refunds. With it, a cache bug can show a wrong price, but a customer never pays one. A wrong displayed price is still a problem for trust, and in some regions it can be a legal problem, so do not treat step 7 as a reason to cache price.

If you later must cache price, invalidate the key on every price write. Keep a short TTL only as a backstop. Add an alert for when the cache and the database disagree.

Hold the shield wall, quartermaster. No stale coin passes the gate.