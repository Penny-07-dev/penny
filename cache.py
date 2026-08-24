"""
A trivially simple in-memory stock cache.

Real production system: this would be Redis or similar so it survives
restarts and works across multiple app instances. For a 1-week sprint
prototype, a dict is fine and lets you focus on the poll->webhook
architecture change, which is the actual point of this assignment.
"""

from datetime import datetime, timezone
from threading import Lock


class StockCache:
    def __init__(self):
        self._data = {}   # sku -> {"quantity": int, "last_updated": datetime, "source": str}
        self._lock = Lock()  # protects against race conditions between
                              # concurrent webhook deliveries / poll writes

    def set(self, sku: str, quantity: int, source: str):
        with self._lock:
            self._data[sku] = {
                "quantity": quantity,
                "last_updated": datetime.now(timezone.utc),
                "source": source,
            }

    def get(self, sku: str):
        with self._lock:
            return self._data.get(sku)

    def all_skus(self):
        with self._lock:
            return list(self._data.keys())
