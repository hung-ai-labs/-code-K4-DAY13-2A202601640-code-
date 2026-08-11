# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: K4 — A2-1
- Repository URL: https://github.com/hung-ai-labs/-code-K4-DAY13-2A202601640-code-
- Commit SHA cuối: `5247def1b7147804dd0fd948e2f58f730f1fbd47` (cập nhật lại nếu có commit mới sau khi push bản này)
- Thành viên và vai trò:

| Họ tên | Mã học viên | Vai trò |
|---|---|---|
| Hồ Trung Tín | 2A202601688 | Logging & PII (correlation ID, log metadata, PII redaction) |
| Nguyễn Mạnh Thắng | 2A202601944 | Tracing & Prompt Version (traces Langfuse, prompt v1/v2, rollback) |
| Hoàng Minh Quân | 2A202601574 | Dashboard, SLO & Alert (6 panel dashboard, SLO threshold, alert rules & runbook) |
| Nguyễn Xuân Hùng | 2A202601640 | Incident, Report & Demo (load test, điều tra challenge CP3, báo cáo, demo) |

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: **100/100** (sau khi làm mới `data/logs.jsonl` bằng load test, log cũ trước fix được backup tại `data/logs.jsonl.bak-preTin`)
- Tổng số traces: ≥ 2 xác nhận qua trace ID trong REPORT.md mục 4 (`152fe9c166a8ea66c038530cd875cd1a`, `03beec31e293b7799f60f11266756101`); Thắng xác nhận đã tạo/kiểm tra tối thiểu 10 traces trên Langfuse (mục 7)
- Số PII leak còn lại: 0 (theo `validate_logs.py`)
- Link/đường dẫn dashboard:
  - Runtime (local): `http://localhost:8501` — chạy bằng `streamlit run scripts/dashboard_app.py`
  - Spec: [`docs/dashboard-spec.md`](../docs/dashboard-spec.md)
  - Contract: [`config/dashboard.yaml`](../config/dashboard.yaml)
  - Live metrics API: `http://localhost:8000/metrics`
  - Evidence ảnh: [`submission/evidence/dashboard-1.png`](evidence/dashboard-1.png), [`dashboard-2.png`](evidence/dashboard-2.png), [`dashboard-3.png`](evidence/dashboard-3.png)

## 3. Logging và tracing

- Evidence correlation ID: `python scripts/validate_logs.py` → **37 unique correlation IDs**, mỗi request có `correlation_id` dạng `req-<8-hex>` xuyên suốt `request_received` → `response_sent` (middleware `app/middleware.py`, bind qua `structlog.contextvars`).
- Evidence PII redaction: `submission/evidence/REDACT_EMAIL.png` (email bị che trong log), `submission/evidence/log_score.png` (điểm `validate_logs.py`); regex PII gồm email, `phone_vn`, `cccd`, `credit_card`, `passport`, `address_vn` (`app/pii.py`).
- Evidence trace waterfall: xem trace baseline/candidate ở mục 4 (Thắng phụ trách, evidence lưu trong `submission/evidence/`).
- Giải thích một span đáng chú ý: span retrieval (`app/mock_rag.py::retrieve()`) của request `req-790adaed` — bình thường 320–330ms, khi incident `rag_slow` bật thì tăng lên ~2.5s do `time.sleep(2.5)` giả lập vector store chậm, kéo latency tổng của request lên 2661ms (chi tiết ở mục 6).

## 4. Prompt versioning

- Prompt name: `day13-chat`
- Version/label baseline: Version `1` — label `baseline`
- Version/label candidate: Version `2` — label `candidate`
- Trace ID của mỗi version:
  - Baseline v1: `152fe9c166a8ea66c038530cd875cd1a`
  - Candidate v2: `03beec31e293b7799f60f11266756101`
- Bằng chứng đổi label hoặc rollback:
  - Đã tạo và kiểm tra hai phiên bản của prompt `day13-chat` trên Langfuse.
  - Trace baseline hiển thị đầy đủ metadata: `prompt_name=day13-chat`, `prompt_label=baseline`, `prompt_version=1`, `prompt_source=langfuse`.
  - Trace candidate hiển thị đầy đủ metadata: `prompt_name=day13-chat`, `prompt_label=candidate`, `prompt_version=2`, `prompt_source=langfuse`.
  - Đã chuyển label `production` từ Version 1 sang Version 2 và xác nhận trace sử dụng `prompt_version=2`.
  - Đã thực hiện rollback bằng cách chuyển label `production` từ Version 2 trở lại Version 1.
  - Sau rollback, trace mới xác nhận `prompt_label=production`, `prompt_version=1`, `prompt_source=langfuse`.
  - Evidence của hai prompt version và thao tác rollback được lưu trong `submission/evidence/`.

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
- Trace ID liên quan: `7cad28af73c4ce87f52ef286a4f2b48b` (tra qua Langfuse API `GET /api/public/traces`, lọc theo `sessionId=k4-challenge-s02`, xác nhận `metadata.correlation_id=req-790adaed`, `latency=2.664s`, `prompt_version=1/production` — khớp với `latency_ms=2661` trong log và `latency_p95=2661` trong metrics). Evidence: `submission/evidence/cp3-trace-req-790adaed.json`.
- Log line/correlation ID liên quan: `correlation_id=req-790adaed`, feature `monitoring`, `request_received` lúc `08:34:54.651Z` → `response_sent` lúc `08:34:57.322Z` (`latency_ms=2661`). Toàn bộ 5 request challenge đều có latency 2665–2685ms, gấp hơn 15 lần P50 baseline bình thường (~156–330ms từ load test thường). Evidence: `submission/evidence/cp3-logs-req-790adaed.jsonl`.
- Root cause: `app/mock_rag.py` hàm `retrieve()` gọi `time.sleep(2.5)` khi cờ `STATE["rag_slow"]` được bật (qua `app/incidents.py`, kích hoạt bởi `scripts/inject_incident.py` theo `config/challenge.json`). Bước retrieval (RAG) trong `app/agent.py::LabAgent.run()` là span chạy trước khi gọi LLM, nên toàn bộ 2.5s delay cộng dồn vào latency tổng của request — khớp với latency đo được (~2.5s sleep + ~150-180ms xử lý còn lại).
- Fix action: Trong tình huống thật, cần đặt timeout cho bước retrieval (ví dụ giới hạn 800ms-1s) kèm circuit breaker/fallback trả lời không kèm tài liệu khi vector store chậm, thay vì chờ vô thời hạn. Ở đây là incident giả lập nên fix là tắt lại cờ: `python scripts/inject_incident.py --disable` (đã thực hiện, xác nhận `rag_slow: false`).
- Preventive measure: Thêm alert riêng cho latency của span retrieval (không chỉ latency tổng), đặt SLO P95 cho từng bước pipeline (retrieval vs LLM) để cô lập nhanh nguồn gây chậm; bổ sung timeout + retry có giới hạn cho lời gọi vector store trong `mock_rag.retrieve()`/vector store thật.

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Tín | Correlation ID middleware, log enrichment, PII redaction (bao gồm regex phone/passport/address) | | |
| Thắng | Phụ trách Tracing & Prompt Versioning. Tạo và kiểm tra ít nhất 10 traces trên Langfuse; kiểm tra các metadata `prompt_name`, `prompt_label`, `prompt_version`, `prompt_source`; quản lý prompt `day13-chat` với baseline v1 và candidate v2; chuyển label `production` sang v2 và thực hiện rollback về v1; xác minh kết quả bằng trace. Trong CP3, sử dụng Langfuse trace để khoanh vùng request chậm của feature `monitoring` trong incident `rag_slow`. | Hiểu cách sử dụng Langfuse để theo dõi traces của ứng dụng AI, quản lý managed prompt theo version/label, liên kết prompt version với trace, rollback prompt bằng cách thay đổi label mà không cần sửa code application, và sử dụng trace kết hợp với metrics/logs để điều tra incident. |
| Quân | Dashboard 6 panel (Streamlit), SLO threshold (`config/slo.yaml`), alert rules & runbook (`config/alert_rules.yaml`, `docs/alerts.md`) | | |
| Hùng | Load test, điều tra incident CP3 (root cause `rag_slow` trong `mock_rag.py`), viết REPORT.md, chuẩn bị demo | | |
