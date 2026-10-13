I’m changing my answer: **do not add the proposed Redis cache for product responses that include prices yet.**

My 10-minute TTL recommendation and prediction of p95 below 200 ms had no supporting evidence. That was too confident. A 900 ms p95 tells us requests are slow. It does not tell us caching will fix them.

Your refund incident gives us a concrete reason for caution. A cache creates another place where prices can become outdated. A shorter TTL limits some stale periods, but it does not guarantee correct prices.

I do not know:

- Where those 900 ms are spent.
- Whether enough requests repeat to make caching effective.
- What caused the previous two-hour stale period.
- How much price staleness the business can accept.

I would first measure database queries, application work, and downstream calls. Those measurements may reveal a fix that improves latency without copying prices into a cache.

Caching descriptions or images could still make sense if the product can tolerate outdated versions. Prices need a separate correctness decision, including verification before charging. That verification alone would not prevent customers from seeing stale prices.

**The latency benefit is unproven; your cost from stale prices is established.** That supports postponing this cache until we have evidence and explicit price freshness requirements.

Stand firm, Spartan.