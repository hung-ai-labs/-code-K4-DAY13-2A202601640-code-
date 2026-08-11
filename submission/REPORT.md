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

## 3. Logging và tracing

- Evidence correlation ID:
- Evidence PII redaction:
- Evidence trace waterfall:
- Giải thích một span đáng chú ý:

## 4. Prompt versioning

- Prompt name: `day13-chat`
- Version/label baseline: Version `1` — label `baseline`
- Version/label candidate: Version `2` — label `candidate`
- Trace ID của mỗi version:
  - Baseline v1: `152fe9c166a8ea66c038530cd875cd1a`
  - Candidate v2: `[03beec31e293b7799f60f11266756101]`
- Bằng chứng đổi label hoặc rollback:
  - Đã tạo và kiểm tra hai phiên bản của prompt `day13-chat` trên Langfuse.
  - Trace baseline hiển thị đầy đủ metadata: `prompt_name=day13-chat`, `prompt_label=baseline`, `prompt_version=1`, `prompt_source=langfuse`.
  - Trace candidate hiển thị đầy đủ metadata: `prompt_name=day13-chat`, `prompt_label=candidate`, `prompt_version=2`, `prompt_source=langfuse`.
  - Đã chuyển label `production` từ Version 1 sang Version 2 và xác nhận trace sử dụng `prompt_version=2`.
  - Đã thực hiện rollback bằng cách chuyển label `production` từ Version 2 trở lại Version 1.
  - Sau rollback, trace mới xác nhận `prompt_label=production`, `prompt_version=1`, `prompt_source=langfuse`.
  - Evidence của hai prompt version và thao tác rollback được lưu trong `submission/evidence/`.

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`:
- Evidence dashboard:
- SLO đã chọn và lý do:
- Alert rules và runbook:

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
|| Thắng | Phụ trách Tracing & Prompt Versioning. Tạo và kiểm tra ít nhất 10 traces trên Langfuse; kiểm tra các metadata `prompt_name`, `prompt_label`, `prompt_version`, `prompt_source`; quản lý prompt `day13-chat` với baseline v1 và candidate v2; chuyển label `production` sang v2 và thực hiện rollback về v1; xác minh kết quả bằng trace. Trong CP3, sử dụng Langfuse trace để khoanh vùng request chậm của feature `monitoring` trong incident `rag_slow`. . | Hiểu cách sử dụng Langfuse để theo dõi traces của ứng dụng AI, quản lý managed prompt theo version/label, liên kết prompt version với trace, rollback prompt bằng cách thay đổi label mà không cần sửa code application, và sử dụng trace kết hợp với metrics/logs để điều tra incident. |
