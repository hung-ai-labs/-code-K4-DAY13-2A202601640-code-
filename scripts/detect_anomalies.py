"""Phát hiện anomaly từ data/logs.jsonl: PII leak và latency vượt SLO."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.cli import configure_utf8_stdio

LOG_PATH = Path("data/logs.jsonl")
SLO_PATH = Path("config/slo.yaml")
DASHBOARD_PATH = Path("config/dashboard.yaml")

PII_DETECTORS = {
    "email": re.compile(r"[\w.-]+@[\w.-]+\.\w+"),
    "phone_vn": re.compile(r"(?<!\d)(?:\+84|0)(?:[ .-]?\d){9}(?!\d)"),
    "cccd": re.compile(r"\b\d{12}\b"),
    "credit_card": re.compile(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b"),
}


def load_records(path: Path) -> list[dict]:
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def latency_slo_ms() -> float:
    if DASHBOARD_PATH.exists():
        dashboard = yaml.safe_load(DASHBOARD_PATH.read_text(encoding="utf-8"))
        for panel in dashboard.get("dashboard", {}).get("panels", []):
            if panel.get("id") == "latency":
                threshold = panel.get("threshold", {})
                if threshold.get("aggregation") == "p95":
                    return float(threshold.get("value", 3000))
    if SLO_PATH.exists():
        slo = yaml.safe_load(SLO_PATH.read_text(encoding="utf-8"))
        return float(slo.get("slis", {}).get("latency_p95_ms", {}).get("objective", 3000))
    return 3000.0


def detect_pii_leaks(records: list[dict]) -> list[dict]:
    hits = []
    for rec in records:
        raw = json.dumps(rec, ensure_ascii=False)
        types = sorted(name for name, detector in PII_DETECTORS.items() if detector.search(raw))
        if types:
            hits.append(
                {
                    "event": rec.get("event"),
                    "correlation_id": rec.get("correlation_id"),
                    "ts": rec.get("ts"),
                    "pii_types": types,
                }
            )
    return hits


def detect_latency_breaches(records: list[dict], slo_ms: float) -> list[dict]:
    breaches = []
    for rec in records:
        if rec.get("event") != "response_sent":
            continue
        latency = rec.get("latency_ms")
        if latency is None:
            continue
        if float(latency) > slo_ms:
            breaches.append(
                {
                    "correlation_id": rec.get("correlation_id"),
                    "ts": rec.get("ts"),
                    "latency_ms": latency,
                    "slo_ms": slo_ms,
                }
            )
    return breaches


def main() -> None:
    configure_utf8_stdio()
    parser = argparse.ArgumentParser(description="Detect anomalies in data/logs.jsonl")
    parser.add_argument("--log-path", type=Path, default=LOG_PATH)
    args = parser.parse_args()

    records = load_records(args.log_path)
    if not records:
        print(f"No records found in {args.log_path}")
        sys.exit(1)

    slo_ms = latency_slo_ms()
    pii_hits = detect_pii_leaks(records)
    latency_hits = detect_latency_breaches(records, slo_ms)

    print("--- Anomaly Detection Report ---")
    print(f"Log file: {args.log_path}")
    print(f"Records scanned: {len(records)}")
    print(f"Latency SLO (p95 threshold): {slo_ms} ms")
    print()

    print(f"PII leaks: {len(pii_hits)}")
    for hit in pii_hits[:10]:
        print(f"  - {hit['ts']} | {hit.get('correlation_id')} | {hit['pii_types']}")
    if len(pii_hits) > 10:
        print(f"  ... and {len(pii_hits) - 10} more")

    print()
    print(f"Latency SLO breaches: {len(latency_hits)}")
    for hit in latency_hits[:10]:
        print(
            f"  - {hit['ts']} | {hit.get('correlation_id')} | "
            f"{hit['latency_ms']}ms > {hit['slo_ms']}ms"
        )
    if len(latency_hits) > 10:
        print(f"  ... and {len(latency_hits) - 10} more")

    print()
    if pii_hits or latency_hits:
        print("ALERT: anomalies detected")
        sys.exit(2)

    print("OK: no anomalies detected")
    sys.exit(0)


if __name__ == "__main__":
    main()
