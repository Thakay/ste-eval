**I change my answer. Do not add the cache yet.** My earlier answer was too confident. I do not know where the 900 ms goes, so "well under 200 ms" was a guess.

**Why I change it**
- A cache hides a slow path. It does not fix it. If the cause is a missing index or an N+1 query, a fix at the source is simpler and has no stale-data risk.
- Cache-aside with a 10 minute TTL can serve an old price for up to 10 minutes after a change. That is your last incident again, only shorter.
- Your team already had one stale-cache incident. That tells me the invalidation path in this system is a weak point, or was.

**What I do not know**
- Where the 900 ms goes: database, downstream calls, serialization, or network.
- How often prices change, and which systems write them.
- Why the last cache stayed stale for 2 hours. Maybe the TTL was long, or a write path skipped invalidation.
- Whether the p95 is high for all products or only for some requests.
- The read-to-write ratio. A cache helps only if the same products get read again and again.
- If the price lookup is itself the slow part, then a cache on the other fields does not help much.

**What I recommend**
1. Profile the endpoint. Find the slowest span in the p95 requests.
2. Fix that cause at the source (query, index, N+1, slow downstream call).
3. If the endpoint is still too slow, cache only fields that change rarely (description, images, specs).
4. Read price and stock from the source of truth on every request.
5. Make checkout re-read the price from the database, with or without a cache. Then a stale cache cannot change what customers pay.

**Warning:** If you cache price later, delete the cache key on every price write. If you do not, the cache serves old prices until the TTL ends.

Hold the line, shield-bearer. Measure before you strike.