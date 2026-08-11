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
- Chỉ vào panel bất thường (latency tăng ở feature `monitoring` trong lúc chạy challenge) và SLO/threshold line đang bị vi phạm.
- Nêu triệu chứng quan sát được từ metrics (không đoán nguyên nhân ở bước này).

## 3. Traces (1.5 phút) — Thắng trình bày

- Mở Langfuse, lọc trace theo khoảng thời gian triệu chứng xuất hiện.
- Mở một trace waterfall, chỉ ra span nào chiếm phần lớn thời gian (ví dụ span retrieval/RAG chậm).
- Chỉ rõ `prompt_name`, `prompt_label`, `prompt_version` trên trace để xác nhận đúng phiên bản đang chạy.

## 4. Logs (1.5 phút) — Tín trình bày

- Lấy correlation ID / trace ID từ span nghi vấn ở bước 3.
- Grep log theo correlation ID đó trong `data/logs.jsonl`, chỉ ra log chi tiết của span (timing, metadata, không có PII nguyên văn).
- Đối chiếu log với trace để khớp thời gian và nguyên nhân.

## 5. Root cause & Fix (1.5 phút) — Hùng trình bày

- Kết luận root cause dựa trên 3 lớp evidence đã trình bày (metrics chỉ triệu chứng → trace khoanh vùng span → log chứng minh nguyên nhân).
- Đề xuất fix action cụ thể và preventive measure (ví dụ: cache/timeout cho retrieval, alert sớm hơn theo SLO).
- Tham chiếu đúng mục 6 trong `submission/REPORT.md`.

## 6. Q&A / cá nhân giải thích phần mình (còn lại)

- Mỗi thành viên sẵn sàng trả lời câu hỏi về phần mình đã làm (tham khảo `docs/mock-debug-qa.md`).

## Rủi ro cần kiểm tra trước giờ chấm

- Không commit `.env`, secret, hoặc PII chưa che (`git status`, kiểm tra `.gitignore`).
- Screenshot trong `submission/evidence/` phải thấy rõ tên panel, time range, đơn vị, threshold.
- Xác nhận `submission/REPORT.md` khớp với commit/PR thực tế của từng người (mục 7).
