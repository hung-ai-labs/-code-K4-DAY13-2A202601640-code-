# Kịch bản demo (Hùng — điều phối, ~5-7 phút)

Luồng bắt buộc: **Metrics → Traces → Logs → Root cause → Fix**

## Chuẩn bị trước demo

- [ ] API đang chạy, `/health` trả `ok: true`.
- [ ] `data/logs.jsonl` có dữ liệu từ load test + challenge run.
- [ ] `python scripts/validate_logs.py` ≥ 80/100.
- [ ] `python scripts/validate_dashboard.py` báo 6/6 panel.
- [ ] Dashboard, Langfuse trace list, và evidence đã có trong `submission/evidence/`.
- [ ] Challenge đã chạy: `python scripts/inject_incident.py` (enable) rồi `python scripts/load_test.py --challenge`.

## 1. Mở đầu (30s)

- Giới thiệu nhóm, hệ thống: API AI có RAG + LLM giả lập, mục tiêu là quan sát và điều tra sự cố bằng evidence.

## 2. Metrics (1.5 phút) — Quân trình bày

- Mở dashboard, chỉ ra 6 nhóm chỉ số: latency P50/P95/P99, traffic, error rate, cost, token, quality.
- Chỉ vào panel latency: **P95/P99 = 2661ms** trong khi **P50 = 156ms** (evidence: `submission/evidence/cp3-metrics-during-incident.json`), vượt SLO/threshold `latency_p95 > 3000ms`... thực tế đã sát ngưỡng cảnh báo và vượt hẳn `latency_threshold_ms=2000` của challenge. `error_rate_pct = 0%` — loại trừ nguyên nhân lỗi request.
- Nêu triệu chứng: đây là vấn đề latency cục bộ ở feature `monitoring`, không phải lỗi hệ thống diện rộng.

## 3. Traces (1.5 phút) — Thắng trình bày

- Mở Langfuse, lọc trace theo khoảng thời gian challenge chạy (~08:34:54–08:35:xx UTC).
- Mở trace ứng với `correlation_id=req-790adaed`, chỉ ra span retrieval/RAG chiếm phần lớn thời gian (~2.5s) so với span LLM.
- Chỉ rõ `prompt_name`, `prompt_label`, `prompt_version` trên trace để xác nhận đúng phiên bản đang chạy.
- <!-- TODO (Thắng): điền trace ID thật vào đây và vào submission/REPORT.md mục 6 -->

## 4. Logs (1.5 phút) — Tín trình bày

- Lấy correlation ID `req-790adaed` từ span nghi vấn ở bước 3.
- Mở `submission/evidence/cp3-logs-req-790adaed.jsonl`: `request_received` lúc `08:34:54.651Z` → `response_sent` lúc `08:34:57.322Z`, `latency_ms=2661`, không có PII nguyên văn (chỉ `user_id_hash`).
- Đối chiếu log với trace để khớp thời gian và nguyên nhân.

## 5. Root cause & Fix (1.5 phút) — Hùng trình bày

- Root cause: `app/mock_rag.py::retrieve()` gọi `time.sleep(2.5)` khi cờ incident `rag_slow` được bật (`scripts/inject_incident.py`, theo `config/challenge.json`) — span retrieval trong `app/agent.py::LabAgent.run()` chạy trước LLM nên toàn bộ 2.5s cộng dồn vào latency tổng, khớp với 2661ms đo được (metrics → trace → log đều thống nhất).
- Fix action: đã tắt incident (`inject_incident.py --disable`, evidence `submission/evidence/cp3-incident-toggle.txt`); trong hệ thống thật cần đặt timeout ~800ms-1s cho bước retrieval kèm fallback trả lời không kèm tài liệu khi vector store chậm.
- Preventive measure: alert riêng cho latency của span retrieval (không chỉ latency tổng), SLO P95 theo từng bước pipeline để cô lập nhanh nguồn gây chậm.
- Tham chiếu đúng mục 6 trong `submission/REPORT.md`.

## 6. Q&A / cá nhân giải thích phần mình (còn lại)

- Mỗi thành viên sẵn sàng trả lời câu hỏi về phần mình đã làm (tham khảo `docs/mock-debug-qa.md`).

## Rủi ro cần kiểm tra trước giờ chấm

- Không commit `.env`, secret, hoặc PII chưa che (`git status`, kiểm tra `.gitignore`).
- Screenshot trong `submission/evidence/` phải thấy rõ tên panel, time range, đơn vị, threshold.
- Xác nhận `submission/REPORT.md` khớp với commit/PR thực tế của từng người (mục 7).
