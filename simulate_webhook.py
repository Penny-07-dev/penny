"""
Stands in for Northstar's warehouse system sending you a webhook.
Use this to demo/test v2 without needing a real warehouse.

Run (with v2's server already running on port 8002):
    python simulate_webhook.py
"""

import json
import sys
import os
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "v2_webhook"))
from webhook_security import compute_signature

WEBHOOK_URL = "http://127.0.0.1:8002/webhooks/stock-update"

events = [
    {"sku": "SKU-1001", "quantity": 41, "event_id": "evt_001"},
    {"sku": "SKU-1002", "quantity": 6, "event_id": "evt_002"},
    {"sku": "SKU-1003", "quantity": 12, "event_id": "evt_003"},
]

for event in events:
    body = json.dumps(event).encode()
    signature = compute_signature(body)

    resp = requests.post(
        WEBHOOK_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Signature": signature,
        },
    )
    print(f"Sent {event['sku']} -> {resp.status_code} {resp.json()}")

print("\nNow try sending one WITHOUT a valid signature to see it get rejected:")
bad_body = json.dumps({"sku": "SKU-1004", "quantity": 999}).encode()
resp = requests.post(
    WEBHOOK_URL,
    data=bad_body,
    headers={"Content-Type": "application/json", "X-Signature": "not-a-real-signature"},
)
print(f"Sent SKU-1004 with bad signature -> {resp.status_code} {resp.json()}")
