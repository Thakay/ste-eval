I’m changing my answer: **don’t add the proposed 10-minute cache to product responses containing prices.** My promise of p95 below 200 ms was unsupported. A 900 ms p95 tells us requests are slow; it doesn’t tell us why or whether Redis would help.

Your previous incident is concrete evidence that stale prices can cost you money and customer trust. A TTL alone doesn’t establish that prices are fresh enough for your business, and choosing another TTL doesn’t address why you served stale prices for two hours.

I don’t know:

- What drives the latency: database queries, downstream services, application work, or contention.
- What caused the previous cache failure.
- How frequently prices change or how much staleness you can tolerate.

My recommendation is to trace slow requests first, then fix the measured bottleneck. Query improvements, fewer repeated database calls, or changes to downstream requests might help, depending on what the traces show.

If measurements later justify caching, consider stable product descriptions separately and keep prices on an authoritative read path. Validate prices again before customers confirm payment, while recognizing that checkout validation doesn’t fix incorrect prices shown earlier.

**We have enough evidence to reject my original proposal, but not enough to reject caching every kind of product data forever.**

Hold the line, Spartan.