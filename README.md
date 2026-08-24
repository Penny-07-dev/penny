# Northstar Inventory Sync — Meridian Pivot, Assignment 2

Two working versions of the same system, so the pivot is a real diff you can
point to, not something you have to describe from memory.

- `v1_polling/` — Day 3 original spec: poll every N seconds, cache, query endpoint.
- `v2_webhook/` — Day 4/5 pivoted spec: warehouse pushes via webhook, cache, same query endpoint.
- `shared/` — the parts that stayed identical across the pivot (cache logic, API response contract).
- `scripts/simulate_webhook.py` — stands in for Northstar's warehouse sending you real webhook calls.

## What's been verified so far

This sandbox has no network access, so `fastapi`/`uvicorn` couldn't be
installed here to run the servers live. What WAS tested directly, and
passed:
- `shared/cache.py` — set/get behavior
- `v2_webhook/webhook_security.py` — signature computed and verified correctly,
  and a bad signature is correctly rejected
- All files pass `python -m py_compile` (no syntax errors)

**Before you submit, run both servers yourself** (instructions below) and
confirm end-to-end — that's part of your own due diligence, not something
to take on faith from a syntax check.

## Setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Run v1 (polling)

```bash
cd v1_polling
uvicorn main:app --reload --port 8001
```

Then in a browser or curl, after ~10 seconds (POLL_INTERVAL_SECONDS):

```
GET http://127.0.0.1:8001/stock/SKU-1001
```

You should see `"source": "poll"` and a `stale_seconds` value that resets
roughly every 10 seconds as the poller refreshes.

## Run v2 (webhook)

```bash
cd v2_webhook
uvicorn main:app --reload --port 8002
```

In a second terminal, simulate Northstar sending you stock updates:

```bash
cd scripts
python simulate_webhook.py
```

Then query:

```
GET http://127.0.0.1:8002/stock/SKU-1001
```

You should see `"source": "webhook"`, and `stale_seconds` will NOT reset on
its own — it only changes when a new webhook actually arrives. That
difference in behavior (auto-refreshing vs event-driven) is worth noting
directly in your Scope Delta Analysis — it's a real, observable
consequence of the architecture change, not just a code diff.

## What each demonstrates for grading

- **v1** proves Day 3's original spec: 5-min poll → cache → query endpoint.
- **v2** proves Day 4/5's pivoted spec: webhook push → cache → *same* query
  endpoint contract, plus signature verification as a deliberate
  architectural addition the pivot required you to think about (you're now
  trusting inbound data instead of data you fetched yourself).
- The diff between `v1_polling/` and `v2_webhook/`, with `shared/` held
  constant, is your primary evidence for the Scope Delta Analysis.
