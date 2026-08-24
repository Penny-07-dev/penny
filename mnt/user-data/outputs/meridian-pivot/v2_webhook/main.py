"""
v2 - PIVOTED SPEC (Day 4/5)
Warehouse pushes stock changes to us via webhook -> cache stock -> expose
the SAME query endpoint as v1.

Run:
    cd v2_webhook
    uvicorn main:app --reload --port 8002

Notice what's GONE compared to v1:
    - no poller.py equivalent
    - no background task on startup
    - no POLL_INTERVAL_SECONDS
    - no warehouse_mock "pull" function
Notice what's the SAME:
    - shared/cache.py
    - shared/schemas.py
    - GET /stock/{sku} response shape
That symmetry/asymmetry IS your Scope Delta Analysis - write it from
this diff, not from memory.
"""

import sys
import os
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Request, Header

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.cache import StockCache
from shared.schemas import StockResponse
from webhook_security import verify_signature

app = FastAPI(title="Northstar Inventory Sync - v2 (Webhook)")
cache = StockCache()


@app.get("/health")
def health():
    return {"status": "ok", "mode": "webhook"}


@app.post("/webhooks/stock-update")
async def receive_stock_update(
    request: Request,
    x_signature: str = Header(None, alias="X-Signature"),
):
    raw_body = await request.body()

    if x_signature is None or not verify_signature(raw_body, x_signature):
        # Reject anything we can't verify came from Northstar.
        raise HTTPException(status_code=401, detail="Invalid or missing signature")

    payload = await request.json()

    # Expected payload shape from Northstar's webhook:
    # { "sku": "SKU-1001", "quantity": 42, "event_id": "evt_123" }
    sku = payload.get("sku")
    quantity = payload.get("quantity")

    if sku is None or quantity is None:
        raise HTTPException(status_code=400, detail="Payload must include sku and quantity")

    cache.set(sku, quantity, source="webhook")
    return {"status": "accepted", "sku": sku}


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
