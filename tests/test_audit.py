from __future__ import annotations

import json
from pathlib import Path

from app import audit


def test_write_audit_appends_jsonl(tmp_path: Path, monkeypatch) -> None:
    path = tmp_path / "audit.jsonl"
    monkeypatch.setattr(audit, "AUDIT_LOG_PATH", path)

    audit.write_audit("incident_enabled", name="cost_spike")
    audit.write_audit("incident_disabled", name="cost_spike")

    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    first = json.loads(lines[0])
    assert first["service"] == "audit"
    assert first["event"] == "incident_enabled"
    assert first["payload"]["name"] == "cost_spike"
