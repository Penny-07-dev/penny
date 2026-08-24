"""
The poller: every POLL_INTERVAL_SECONDS, ask the warehouse "what's
everything's stock level right now?" and refresh the cache.

THIS FILE IS THE ONE THAT GETS DELETED/DEPRECATED IN THE PIVOT.
Keep that in mind while building v2 - poller.py has no equivalent
there, because webhooks push to you instead of you asking.
"""

import asyncio
import logging

from warehouse_mock import fetch_stock_snapshot, simulate_warehouse_activity
from shared.cache import StockCache

logger = logging.getLogger("poller")

# Original spec says "every 5 minutes". Set low here so you can actually
# watch it work during development/demo - document this in your README,
# don't silently change the spec.
POLL_INTERVAL_SECONDS = 10


async def poll_loop(cache: StockCache):
    while True:
        simulate_warehouse_activity()  # pretend real warehouse activity happened
        snapshot = fetch_stock_snapshot()

        for sku, qty in snapshot.items():
            cache.set(sku, qty, source="poll")

        logger.info(f"[poll] refreshed {len(snapshot)} SKUs")
        await asyncio.sleep(POLL_INTERVAL_SECONDS)
