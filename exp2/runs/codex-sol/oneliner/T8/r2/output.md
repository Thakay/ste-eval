I change my answer: Do not add Redis yet. I had no measurements to support a TTL of 10 minutes or p95 latency below 200 ms.

The 900 ms p95 latency does not identify the cause of the delay. I do not know which operations are slow, how prices change, or why the previous cache supplied incorrect prices for two hours.

A TTL limits how long a cache entry stays available. It does not make the price correct. Even 10 minutes of incorrect prices can cause more refunds.

First, measure database query time and time used by external services. Correct the cause of the delay, then measure p95 latency again.

Consider a cache only if measurements show a benefit. Start with product data for which delayed updates are acceptable. Before you use a cache for prices, specify the price accuracy requirements. Test price changes, cache failures, and lost update messages against those requirements.