# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`:
- Tổng số traces:
- Số PII leak còn lại:
- Link/đường dẫn dashboard:
  - Runtime (local): `http://localhost:8501` — chạy bằng `streamlit run scripts/dashboard_app.py`
  - Spec: [`docs/dashboard-spec.md`](../docs/dashboard-spec.md)
  - Contract: [`config/dashboard.yaml`](../config/dashboard.yaml)
  - Live metrics API: `http://localhost:8000/metrics`
  - Evidence ảnh: [`submission/evidence/dashboard-1.png`](evidence/dashboard-1.png), [`dashboard-2.png`](evidence/dashboard-2.png), [`dashboard-3.png`](evidence/dashboard-3.png)

## 3. Logging và tracing

- Evidence correlation ID:
- Evidence PII redaction:
- Evidence trace waterfall:
- Giải thích một span đáng chú ý:

## 4. Prompt versioning

- Prompt name:
- Version/label baseline:
- Version/label candidate:
- Trace ID của mỗi version:
- Bằng chứng đổi label hoặc rollback:

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: `HỢP LỆ: 6/6 panel` — evidence [`submission/evidence/validate-dashboard.png`](evidence/validate-dashboard.png)
- Evidence dashboard:
  - 6 panel: Latency, Traffic, Errors, Cost, Tokens, Quality
  - Công cụ: Streamlit (`scripts/dashboard_app.py`), nguồn live `/metrics`, charts từ `data/logs.jsonl`
  - Time range mặc định 60 phút, refresh 30 giây, có threshold/SLO line trên từng panel
  - Ảnh: `submission/evidence/dashboard-1.png`, `dashboard-2.png`, `dashboard-3.png`
- SLO đã chọn và lý do (`config/slo.yaml`, cửa sổ 28d):
  - `latency_p95_ms`: objective **3000** ms, target **99.5%** — P95 dưới 3 giây để UX chat/QA vẫn chấp nhận được; khớp threshold panel Latency.
  - `error_rate_pct`: objective **2%**, target **99.0%** — tỷ lệ fail thấp; panel Errors dùng cùng ngưỡng SLO.
  - `daily_cost_usd`: objective **2.5** USD, target **100%** — ngân sách lab/ngày; khớp threshold panel Cost.
  - `quality_score_avg`: objective **0.75**, target **95.0%** — chất lượng trả lời tối thiểu; khớp threshold panel Quality.
- Alert rules và runbook (`config/alert_rules.yaml` + `docs/alerts.md`):
  1. **`high_latency_p95`** (warning, owner: on-call-engineer)  
     Điều kiện: `latency_p95 > 3000ms for 5 minutes`  
     Runbook: [docs/alerts.md#alert-1](../docs/alerts.md#alert-1) — kiểm tra `/metrics` → panel Latency → trace/log theo correlation ID; mitigation: tắt incident, giảm concurrency.
  2. **`elevated_error_rate`** (critical, owner: on-call-engineer)  
     Điều kiện: `error_rate_pct > 5 for 3 minutes` (SLO vẫn ≤ 2%; alert critical cao hơn để tránh noise)  
     Runbook: [docs/alerts.md#alert-2](../docs/alerts.md#alert-2) — `/metrics` + `error_breakdown` → `/health` + `request_failed` → trace/log; mitigation: disable incident, rollback config.
  3. **`cost_budget_exceeded`** (warning, owner: team-lead)  
     Điều kiện: `daily_cost_usd > 2.5`  
     Runbook: [docs/alerts.md#alert-3](../docs/alerts.md#alert-3) — đối chiếu cost/tokens trên `/metrics` và panel Cost → kiểm tra prompt/incident `cost_spike`; mitigation: rollback prompt, giảm concurrency.

## 6. Điều tra challenge

- Challenge ID:
- Triệu chứng từ metrics:
- Trace ID liên quan:
- Log line/correlation ID liên quan:
- Root cause:
- Fix action:
- Preventive measure:

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| | | | |
