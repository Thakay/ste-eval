I change my answer. Do not add a Redis cache for prices now.

My earlier answer was too certain. I had no data to support a 10-minute cache life or a p95 below 200 ms.

A p95 of 900 ms does not identify the cause of the delay. A cache can help only if it removes work that causes that delay. Your previous failure shows that old prices can cause financial loss. A 10-minute cache life can still let customers get old prices.

I do not know:

- Which operations cause the delay.
- Why the previous cache returned old prices for two hours.
- How often prices change.
- Whether any delay in price updates is acceptable.

First, measure the time spent in database queries and calls to other services. Use those results to select a change.

You could later cache product descriptions if old descriptions are acceptable. Keep prices separate. Do not cache prices until you understand the previous failure and have tested how to prevent it.