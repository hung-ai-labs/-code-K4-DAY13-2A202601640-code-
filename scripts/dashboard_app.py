"""Day 13 dashboard — primary live source: GET /metrics; charts from data/logs.jsonl."""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import pandas as pd
import streamlit as st
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = REPO_ROOT / "data" / "logs.jsonl"
DASHBOARD_CONFIG = REPO_ROOT / "config" / "dashboard.yaml"
SLO_CONFIG = REPO_ROOT / "config" / "slo.yaml"
METRICS_URL = "http://127.0.0.1:8000/metrics"


def load_logs(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    if "ts" in df.columns:
        df["ts"] = pd.to_datetime(df["ts"], utc=True, errors="coerce")
    return df


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def fetch_metrics() -> dict | None:
    try:
        resp = httpx.get(METRICS_URL, timeout=3.0)
        resp.raise_for_status()
        payload = resp.json()
        return payload if isinstance(payload, dict) else None
    except Exception:
        return None


def filter_window(df: pd.DataFrame, minutes: int) -> pd.DataFrame:
    if df.empty or "ts" not in df.columns:
        return df
    latest = df["ts"].max()
    if pd.isna(latest):
        return df
    cutoff = latest - pd.Timedelta(minutes=minutes)
    return df[df["ts"] >= cutoff].copy()


def main() -> None:
    st.set_page_config(page_title="Day 13 AI Observability", layout="wide")
    dashboard_cfg = load_yaml(DASHBOARD_CONFIG)
    slo_cfg = load_yaml(SLO_CONFIG)
    dash = dashboard_cfg.get("dashboard", {})
    minutes = int(dash.get("time_range_minutes", 60))
    refresh = int(dash.get("refresh_seconds", 30))

    st.title(dash.get("title", "Day 13 AI Observability"))
    st.caption(
        f"Live source: `GET /metrics` · History charts: `data/logs.jsonl` · "
        f"Time range: {minutes} min · Refresh target: {refresh}s"
    )
    st.caption("Tool: Streamlit · Spec: docs/dashboard-spec.md")

    if st.button("Reload"):
        st.rerun()

    metrics = fetch_metrics()
    if metrics is None:
        st.error("Không gọi được `/metrics`. Hãy chạy: `uvicorn app.main:app --reload --env-file .env`")
        st.stop()

    df = filter_window(load_logs(LOG_PATH), minutes)
    sent = df[df["event"] == "response_sent"] if not df.empty else pd.DataFrame()
    failed = df[df["event"] == "request_failed"] if not df.empty else pd.DataFrame()

    # 1. Latency
    st.subheader("1. Latency percentiles")
    c1, c2, c3 = st.columns(3)
    c1.metric("latency_p50 (ms)", f"{metrics.get('latency_p50', 0):.0f}")
    c2.metric("latency_p95 (ms)", f"{metrics.get('latency_p95', 0):.0f}", delta="SLO ≤ 3000", delta_color="off")
    c3.metric("latency_p99 (ms)", f"{metrics.get('latency_p99', 0):.0f}")
    if not sent.empty and "latency_ms" in sent.columns and "ts" in sent.columns:
        st.line_chart(sent.set_index("ts")[["latency_ms"]].sort_index())
    st.caption("SLO line: P95 ≤ 3000 ms")

    st.divider()
    left, right = st.columns(2)

    # 2. Traffic
    with left:
        st.subheader("2. Request traffic")
        traffic = int(metrics.get("traffic", 0))
        st.metric("traffic (counter)", traffic)
        st.metric("approx req/min (window)", f"{traffic / max(minutes, 1):.2f}", delta="threshold ≥ 1", delta_color="off")

    # 3. Errors
    with right:
        st.subheader("3. Error rate & breakdown")
        err = float(metrics.get("error_rate_pct", 0.0))
        st.metric("error_rate_pct", f"{err:.2f}%", delta="SLO ≤ 2% · alert > 5%", delta_color="off")
        breakdown = metrics.get("error_breakdown") or {}
        if breakdown:
            st.bar_chart(pd.Series(breakdown, dtype=float))
        elif not failed.empty and "error_type" in failed.columns:
            st.bar_chart(failed["error_type"].fillna("unknown").value_counts())
        else:
            st.caption("Chưa có lỗi trong cửa sổ hiện tại.")

    st.divider()
    a, b, c = st.columns(3)

    # 4. Cost
    with a:
        st.subheader("4. Cost")
        total = float(metrics.get("total_cost_usd", 0.0))
        avg = float(metrics.get("avg_cost_usd", 0.0))
        st.metric("total_cost_usd", f"${total:.4f}", delta="budget ≤ $2.5", delta_color="off")
        st.metric("avg_cost_usd", f"${avg:.4f}")

    # 5. Tokens
    with b:
        st.subheader("5. Tokens")
        tin = int(metrics.get("tokens_in_total", 0))
        tout = int(metrics.get("tokens_out_total", 0))
        st.metric("tokens_in_total", f"{tin}")
        st.metric("tokens_out_total", f"{tout}")
        st.metric("total tokens", f"{tin + tout}", delta="threshold ≤ 50000", delta_color="off")

    # 6. Quality
    with c:
        st.subheader("6. Quality")
        q = float(metrics.get("quality_avg", 0.0))
        st.metric("quality_avg", f"{q:.3f}", delta="SLO ≥ 0.75", delta_color="off")

    st.divider()
    st.subheader("SLO summary (`config/slo.yaml`)")
    rows = [
        {"SLI": name, "objective": spec.get("objective"), "target_%": spec.get("target"), "note": spec.get("note", "")}
        for name, spec in (slo_cfg.get("slis") or {}).items()
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True)
    st.caption("Alerts: `config/alert_rules.yaml` · Runbook: `docs/alerts.md`")

    with st.expander("Raw /metrics JSON"):
        st.json(metrics)


if __name__ == "__main__":
    main()
