"""
Webhook signature verification.

Why this exists (worth a line in your Scope Delta as a deliberate ADD,
not something the spec explicitly asked for): in a poll model, YOU
initiate every request, so you inherently trust the response - you
called a known URL with your own credentials. In a webhook model, the
world can POST to your endpoint. Without verifying the request really
came from Northstar, anyone who finds your URL could feed you fake
stock numbers. This is exactly the "webhook verification" concept
track in this sprint, applied for real.

Northstar would normally send a signature header computed as:
    HMAC-SHA256(shared_secret, raw_request_body)
and you recompute it yourself and compare.
"""

import hmac
import hashlib

SHARED_SECRET = "demo-shared-secret-change-me"  # in real life: env var / secrets manager


def compute_signature(raw_body: bytes) -> str:
    return hmac.new(
        SHARED_SECRET.encode(), raw_body, hashlib.sha256
    ).hexdigest()


def verify_signature(raw_body: bytes, provided_signature: str) -> bool:
    expected = compute_signature(raw_body)
    # constant-time comparison - prevents timing attacks on the signature check
    return hmac.compare_digest(expected, provided_signature)
