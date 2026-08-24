# Scope Delta Analysis — Northstar Inventory Sync Pivot

**Original spec (Day 3):** Poll warehouse API every 5 min, cache stock, expose query endpoint.
**Pivoted spec (Day 4, 48hr deadline):** Polling killed — switch to webhook push model.

## Dropped

- `poller.py` — the entire background polling loop (`asyncio` task, `POLL_INTERVAL_SECONDS`,
  the fetch-on-a-timer pattern). No equivalent exists in v2; nothing pulls data anymore.
- `warehouse_mock.fetch_stock_snapshot()` — the "ask for everything" pull call. Webhooks
  deliver one SKU's change at a time, not full snapshots, so this pattern doesn't carry over.
- The startup background task registration in `main.py` (`@app.on_event("startup")`) — v2
  has no long-running background process; it's purely request-driven.

*[Your words: was anything else quietly dropped that isn't obvious from the code diff —
e.g. an assumption your team had been relying on?]*

## Modified

- `main.py` — went from a service with a background task to a pure request/response service
  with one extra inbound route (`POST /webhooks/stock-update`).
- Data freshness model: v1 guarantees data is *at most ~5 minutes stale* by design. v2's
  freshness depends entirely on Northstar actually sending the webhook — if their system
  fails to send one, our cache goes stale silently with no self-correcting mechanism.
- Trust model: v1 trusts data because *we* initiated the request to a known URL. v2 has to
  independently verify inbound data is genuinely from Northstar (see `webhook_security.py`) —
  this wasn't a concern the original spec had to address at all.

*[Your words: which of these modifications took the most rework, and why?]*

## Added

- `webhook_security.py` — HMAC signature verification. Not in the original spec, added
  because accepting unauthenticated inbound POSTs would let anyone feed fake stock data
  into the system.
- `POST /webhooks/stock-update` endpoint and its payload validation.
- `source` field in the API response (`"poll"` vs `"webhook"`) — added for
  debugging/demo visibility during the transition, not a Northstar requirement.

*[Your words: is there anything you added that you'd argue should NOT ship to production
as-is — e.g. the hardcoded shared secret — and what would you do instead given more time?]*

## What did NOT change (contract stability)

- `shared/schemas.py` (`StockResponse`) and `shared/cache.py` are byte-for-byte identical
  between v1 and v2. `GET /stock/{sku}` returns the same shape either way.
- **Why this matters:** Northstar's support tool never has to change a single line to
  consume either version. The pivot is invisible from the consumer's side — this is the
  main architectural integrity claim of this deliverable.

## Regression check

- [ ] Confirmed `GET /stock/{sku}` returns 404 correctly for an unknown SKU in both versions
- [ ] Confirmed a webhook with an invalid/missing signature is rejected (401), not silently cached
- [ ] Confirmed v2 has no leftover references to polling (dead imports, unused config)
- [ ] Confirmed the response `source` field correctly reflects `"webhook"` in v2, not a
      leftover `"poll"` default
- *[Add any regression you personally found while testing — this list should reflect what
  you actually checked, not just what I anticipated]*

## Cost of the pivot (honest accounting)

*[Your words — this is the part graders are actually weighing at 30%. Some prompts to
answer honestly, not rhetorically:]*
- Roughly how much of the original Day 3 code survived unchanged vs had to be rewritten?
- What would you have designed differently on Day 3 if you'd known the pivot was coming —
  and is that a realistic thing to expect, or is some rework simply unavoidable when specs
  change externally?
- What's the biggest remaining risk in the webhook architecture as it stands right now
  (e.g. no retry/replay handling if a webhook delivery fails, no idempotency check on
  `event_id`)?
