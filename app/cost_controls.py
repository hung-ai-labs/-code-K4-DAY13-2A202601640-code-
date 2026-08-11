from __future__ import annotations

import hashlib
import os

MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "180"))
RESPONSE_CACHE_ENABLED = os.getenv("RESPONSE_CACHE_ENABLED", "true").lower() in {
    "1",
    "true",
    "yes",
}


def cap_output_tokens(output_tokens: int) -> int:
    return min(output_tokens, MAX_OUTPUT_TOKENS)


def make_cache_key(feature: str, message: str) -> str:
    payload = f"{feature}:{message.strip().lower()}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]
