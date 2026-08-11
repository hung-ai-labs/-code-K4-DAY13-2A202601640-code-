# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: K4 — Nhóm 4 (Tín, Thắng, Quân, Hùng)
- Repository URL: https://github.com/hung-ai-labs/-code-K4-DAY13-2A202601640-code-
- Commit SHA cuối: <!-- TODO: cập nhật SHA của commit nộp bài cuối cùng trước khi nộp -->
- Thành viên và vai trò:
  - Tín — Logging & PII (correlation ID, log metadata, PII redaction)
  - Thắng — Tracing & Prompt Version (traces Langfuse, prompt v1/v2, rollback)
  - Quân — Dashboard, SLO & Alert (6 panel dashboard, SLO threshold, alert rules & runbook)
  - Hùng — Incident, Report & Demo (load test, điều tra challenge CP3, báo cáo, demo)

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: **100/100** (sau khi làm mới `data/logs.jsonl` bằng load test, log cũ trước fix được backup tại `data/logs.jsonl.bak-preTin`)
- Tổng số traces: <!-- TODO (Thắng) — xác nhận số trace thật trên Langfuse UI, yêu cầu tối thiểu 10 traces -->
- Số PII leak còn lại: 0 (theo `validate_logs.py`)
- Link/đường dẫn dashboard:
  - Runtime (local): `http://localhost:8501` — chạy bằng `streamlit run scripts/dashboard_app.py`
  - Spec: [`docs/dashboard-spec.md`](../docs/dashboard-spec.md)
  - Contract: [`config/dashboard.yaml`](../config/dashboard.yaml)
  - Live metrics API: `http://localhost:8000/metrics`
  - Evidence ảnh: [`submission/evidence/dashboard-1.png`](evidence/dashboard-1.png), [`dashboard-2.png`](evidence/dashboard-2.png), [`dashboard-3.png`](evidence/dashboard-3.png)

## 3. Logging và tracing

<!-- TODO (Tín + Thắng) -->
- Evidence correlation ID:
- Evidence PII redaction:
- Evidence trace waterfall:
- Giải thích một span đáng chú ý:

## 4. Prompt versioning

<!-- TODO (Thắng) -->
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

- Challenge ID: `day13-k4-observability-v1` (feature: `monitoring`, incident: `rag_slow`, latency_threshold_ms: 2000)
- Triệu chứng từ metrics: Chạy `scripts/load_test.py --challenge` sau khi bật `rag_slow` (`scripts/inject_incident.py`) làm `latency_p95`/`latency_p99` tăng vọt lên **~2661ms** trong khi `latency_p50` chỉ **156ms** (`GET /metrics`), vượt ngưỡng `latency_threshold_ms=2000` của challenge; `error_rate_pct` vẫn 0% — đây là vấn đề latency, không phải lỗi request. Evidence: `submission/evidence/cp3-metrics-during-incident.json`, `submission/evidence/cp3-challenge-load-test.txt`.
- Trace ID liên quan: <!-- TODO (Thắng) — dán trace ID trên Langfuse ứng với correlation_id req-790adaed (span retrieve chiếm phần lớn latency) -->
- Log line/correlation ID liên quan: `correlation_id=req-790adaed`, feature `monitoring`, `request_received` lúc `08:34:54.651Z` → `response_sent` lúc `08:34:57.322Z` (`latency_ms=2661`). Toàn bộ 5 request challenge đều có latency 2665–2685ms, gấp hơn 15 lần P50 baseline bình thường (~156–330ms từ load test thường). Evidence: `submission/evidence/cp3-logs-req-790adaed.jsonl`.
- Root cause: `app/mock_rag.py` hàm `retrieve()` gọi `time.sleep(2.5)` khi cờ `STATE["rag_slow"]` được bật (qua `app/incidents.py`, kích hoạt bởi `scripts/inject_incident.py` theo `config/challenge.json`). Bước retrieval (RAG) trong `app/agent.py::LabAgent.run()` là span chạy trước khi gọi LLM, nên toàn bộ 2.5s delay cộng dồn vào latency tổng của request — khớp với latency đo được (~2.5s sleep + ~150-180ms xử lý còn lại).
- Fix action: Trong tình huống thật, cần đặt timeout cho bước retrieval (ví dụ giới hạn 800ms-1s) kèm circuit breaker/fallback trả lời không kèm tài liệu khi vector store chậm, thay vì chờ vô thời hạn. Ở đây là incident giả lập nên fix là tắt lại cờ: `python scripts/inject_incident.py --disable` (đã thực hiện, xác nhận `rag_slow: false`).
- Preventive measure: Thêm alert riêng cho latency của span retrieval (không chỉ latency tổng), đặt SLO P95 cho từng bước pipeline (retrieval vs LLM) để cô lập nhanh nguồn gây chậm; bổ sung timeout + retry có giới hạn cho lời gọi vector store trong `mock_rag.retrieve()`/vector store thật.

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Tín | Correlation ID middleware, log enrichment, PII redaction | | |
| Thắng | Langfuse tracing, prompt v1/v2, rollback/label | | |
| Quân | Dashboard 6 panel, SLO threshold, alert rules & runbook | | |
| Hùng | Load test, điều tra incident CP3, viết REPORT.md, chuẩn bị demo | | |
