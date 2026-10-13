I’m changing my answer: **don’t add Redis based on a 900 ms p95 alone.** My earlier TTL recommendation and promise of “well under 200 ms” were unjustified.

You have evidence that stale prices cause real harm. We have no evidence yet that caching would fix the latency. A TTL permits stale data by design, and invalidation can fail through missed updates or races. Redis would add another correctness problem to manage.

I don’t know where those 900 ms go, how often prices change, how much traffic repeats the same reads, or whether enough requests would hit the cache to improve p95.

My recommendation:

- Trace slow requests to identify the bottleneck.
- Address expensive queries, unnecessary calls, or slow dependencies where the measurements point.
- If caching later proves useful, start with stable product metadata and keep prices on an authoritative read path. Revisit price caching only with an agreed freshness requirement and evidence that failures stay within it.

Caching may eventually help. Your refund incident makes price correctness a requirement, and we haven’t established how a cache would satisfy it.

Hold the line, Spartan.