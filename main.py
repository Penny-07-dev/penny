"""
v1 - ORIGINAL SPEC (Day 3)
Poll a warehouse API every N seconds -> cache stock -> expose a query endpoint.

Run:
    cd v1_polling
    uvicorn main:app --reload --port 8001
"""

import sys
import os
import asyncio
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared.cache import StockCache
from shared.schemas import StockResponse
from poller import poll_loop, POLL_INTERVAL_SECONDS

app = FastAPI(title="Northstar Inventory Sync - v1 (Polling)")
cache = StockCache()


@app.on_event("startup")
async def start_background_poller():
    # Fire-and-forget background task. This line is the architectural
    # heart of v1 - the app pulls data on its own schedule, independent
    # of any client request.
    asyncio.create_task(poll_loop(cache))


@app.get("/health")
def health():
    return {"status": "ok", "mode": "polling", "poll_interval_seconds": POLL_INTERVAL_SECONDS}


@app.get("/stock/{sku}", response_model=StockResponse)
def get_stock(sku: str):
    entry = cache.get(sku)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"No cached data for {sku}")

    age = (datetime.now(timezone.utc) - entry["last_updated"]).total_seconds()
    return StockResponse(
        sku=sku,
        quantity=entry["quantity"],
        last_updated=entry["last_updated"].isoformat(),
        source=entry["source"],
        stale_seconds=round(age, 1),
    )
