"""
Shared response contract for the /stock/{sku} query endpoint.

IMPORTANT (for your Scope Delta Analysis):
This file is identical in v1 and v2 on purpose. Northstar's support tool
calls /stock/{sku} and expects this shape back — it does NOT know or care
whether the data underneath was filled by polling or by a webhook. Keeping
this contract stable across the pivot is exactly what "architectural
integrity" is graded on: the pivot should be invisible to consumers of
your API.
"""

from pydantic import BaseModel
from typing import Optional


class StockResponse(BaseModel):
    sku: str
    quantity: int
    last_updated: str          # ISO 8601 timestamp of when we last heard this value
    source: str                 # "poll" or "webhook" - included so you can SEE which
                                 # architecture produced the data, useful for your
                                 # own debugging/demo, not something Northstar's tool needs
    stale_seconds: Optional[float] = None  # how old is this cached value right now
