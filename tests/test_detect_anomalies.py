from __future__ import annotations

import json
from pathlib import Path

from scripts.detect_anomalies import detect_latency_breaches, detect_pii_leaks


def test_detect_pii_leaks_finds_email() -> None:
    records = [
        {
            "event": "request_received",
            "correlation_id": "req-1",
            "payload": {"message_preview": "email me at student@vinuni.edu.vn"},
        }
    ]
    hits = detect_pii_leaks(records)
    assert len(hits) == 1
    assert "email" in hits[0]["pii_types"]


def test_detect_latency_breaches() -> None:
    records = [
        {"event": "response_sent", "correlation_id": "req-1", "latency_ms": 5000},
        {"event": "response_sent", "correlation_id": "req-2", "latency_ms": 100},
    ]
    hits = detect_latency_breaches(records, slo_ms=3000)
    assert len(hits) == 1
    assert hits[0]["correlation_id"] == "req-1"
