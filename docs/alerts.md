# Alert và Runbook — Day 13 Observability

Mỗi alert dựa trên triệu chứng người dùng / SLO, không dựa vào tên implementation nội bộ.

## Alert 1

- Tên: `high_latency_p95`
- Severity: warning
- SLI/SLO liên quan: `latency_p95_ms` — objective ≤ 3000 ms, target 99.5%
- Điều kiện kích hoạt: `latency_p95 > 3000ms for 5 minutes`
- Ảnh hưởng tới người dùng: câu trả lời chat/QA chậm rõ; người dùng chờ lâu hoặc bỏ request
- Ba bước kiểm tra đầu tiên:
  1. Gọi `GET /metrics` — xác nhận `latency_p95` (và P50/P99) có vượt 3000 ms không.
  2. Mở panel Latency trên dashboard (time range 60 phút) — xem spike bắt đầu lúc nào.
  3. Lấy 1–2 request chậm trong khoảng đó → giao Tracing mở waterfall / giao Logging tìm cùng correlation ID.
- Mitigation tạm thời: tắt incident practice đang bật (`inject_incident.py --scenario ... --disable`); giảm concurrency; ưu tiên phục hồi latency trước khi tăng traffic.
- Owner: on-call-engineer

## Alert 2

- Tên: `elevated_error_rate`
- Severity: critical
- SLI/SLO liên quan: `error_rate_pct` — SLO objective ≤ 2%; alert critical khi > 5% trong 3 phút
- Điều kiện kích hoạt: `error_rate_pct > 5 for 3 minutes`
- Ảnh hưởng tới người dùng: nhiều request thất bại; không nhận được câu trả lời
- Ba bước kiểm tra đầu tiên:
  1. Gọi `GET /metrics` — đọc `error_rate_pct` và `error_breakdown`.
  2. Kiểm tra `/health` và log `request_failed` gần nhất (error_type).
  3. Khoanh thời gian lỗi → Tracing tìm span fail → Logging chứng minh root cause bằng correlation ID.
- Mitigation tạm thời: disable incident đang inject; rollback thay đổi prompt/config vừa deploy nếu nghi ngờ; giữ API healthy trước khi mở lại traffic.
- Owner: on-call-engineer

## Alert 3

- Tên: `cost_budget_exceeded`
- Severity: warning
- SLI/SLO liên quan: `daily_cost_usd` — objective ≤ 2.5 USD, target 100%
- Điều kiện kích hoạt: `daily_cost_usd > 2.5`
- Ảnh hưởng tới người dùng: chi phí inference tăng bất thường; có thể phải cắt traffic hoặc giới hạn feature
- Ba bước kiểm tra đầu tiên:
  1. Gọi `GET /metrics` — đối chiếu `total_cost_usd`, `avg_cost_usd`, `tokens_in_total`, `tokens_out_total`.
  2. Mở panel Cost/Tokens trên dashboard — xác định khoảng thời gian cost tăng.
  3. Kiểm tra prompt label/version đang dùng và có incident `cost_spike` không; lấy sample `response_sent` cost cao.
- Mitigation tạm thời: tắt `cost_spike` nếu đang practice; rollback prompt `production` về version ổn định; giảm concurrency / tạm khóa feature tốn token.
- Owner: team-lead
