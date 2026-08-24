"""
Stand-in for Northstar's real warehouse API.

In real life, Day 1-3 you'd be polling an actual HTTP endpoint Northstar
gave you. Since we don't have that, this module simulates one: stock
levels drift randomly over time, as if real warehouse activity were
happening. Your poller (poller.py) calls fetch_stock_snapshot() exactly
the way it would call `requests.get("https://northstar.example/api/stock")`
in real life — swap this out for a real HTTP call and nothing else
needs to change.
"""

import random

# Pretend ground-truth warehouse state
_WAREHOUSE_DB = {
    "SKU-1001": 42,
    "SKU-1002": 7,
    "SKU-1003": 0,
    "SKU-1004": 150,
    "SKU-1005": 3,
}


def simulate_warehouse_activity():
    """Randomly nudges stock levels, as if orders/restocks were happening.
    Call this occasionally (e.g. from a background loop) so polling has
    something new to discover."""
    sku = random.choice(list(_WAREHOUSE_DB.keys()))
    delta = random.choice([-3, -1, -1, 1, 1, 5])
    _WAREHOUSE_DB[sku] = max(0, _WAREHOUSE_DB[sku] + delta)


def fetch_stock_snapshot():
    """This is the function that stands in for 'call the warehouse API'.
    Returns a full snapshot of every SKU's current quantity, exactly
    like a GET /stock endpoint would."""
    return dict(_WAREHOUSE_DB)
