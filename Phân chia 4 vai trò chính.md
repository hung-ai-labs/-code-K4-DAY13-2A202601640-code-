

### **Phân chia 4 vai trò chính**

* **Tín:** Vai trò Logging & PII.   
* **Thắng:** Vai trò Tracing & Prompt Version.   
* **Quân:** Vai trò Dashboard, SLO & Alert.   
* **Hùng:** Vai trò Incident, Report & Demo. 

### **Chi tiết công việc theo từng Checkpoint**

#### **Checkpoint 0 — 0:00–0:30: Setup và baseline**

* **Cả nhóm:** Làm theo tài liệu SETUP.md để cài đặt và đảm bảo API cùng load test chạy được.   
* MD  
* **Tín:** Chạy lệnh python scripts/validate\_logs.py để lấy kết quả baseline và lưu vào báo cáo. Đảm bảo có file data/logs.jsonl.   
* MD+ 1  
* **Quân:** Chạy lệnh python scripts/validate\_dashboard.py để hiểu contract đầu ra của dashboard.   
* MD

#### **Checkpoint 1 — 0:30–1:30: Logging và PII**

* **Tín (Thực hiện chính):**  
  * Đảm bảo mỗi request đều được cấp một correlation ID hợp lệ.   
  * MD  
  * Bổ sung metadata vào log API để chứa đầy đủ các trường: user\_id\_hash, session\_id, feature, model, env.   
  * MD  
  * Che dấu dữ liệu PII để email, số điện thoại và số thẻ thử nghiệm không xuất hiện nguyên văn bên trong log.   
  * MD  
  * Chạy script validate\_logs.py để đảm bảo hệ thống đạt tối thiểu 80/100 điểm.   
  * MD  
  * **Bàn giao:** File log có chứa correlation ID và bằng cTín PII đã được che (redacted).   
  * MD

#### **Checkpoint 2 — 1:30–2:30: Metrics, traces và dashboard**

* **Thắng (Tracing & Prompt Version):**  
  * Tạo ra tối thiểu 10 traces đi kèm metadata trên Langfuse.   
  * MD+ 1  
  * Tạo prompt v1/v2, đảm bảo trace ghi nhận đủ prompt\_name, prompt\_label và prompt\_version.   
  * MD  
  * Thực hiện Quân công thao tác đổi label hoặc rollback prompt.   
  * MD  
  * **Bàn giao:** Trace gắn Hùng phiên bản prompt, chụp ảnh hai trace prompt và thao tác rollback lưu vào thư mục submission/evidence/.   
  * MD+ 1  
* **Quân (Dashboard, SLO & Alert):**  
  * Xây Hùng dashboard thể hiện 6 nhóm chỉ số từ file config/dashboard.yaml: latency, traffic, error, token/cost và quality.   
  * MD  
  * Thiết lập SLO line hoặc các threshold báo động rõ ràng.   
  * MD  
  * **Bàn giao:** Kết quả chạy hợp lệ từ validate\_dashboard.py và ảnh chụp dashboard có đủ time range, đơn vị cùng threshold.   
  * MD+ 1

#### **Checkpoint 3 — 2:30–3:30: Challenge chính thức**

* **Hùng (Điều phối chính):** Chờ Lab Coach release file config/challenge.json, sau đó chạy incident và bắt đầu bơm input chính thức.   
* MD+ 1  
* **Quân:** Hùng sát và xác định các triệu cTín bất thường trực tiếp từ metrics.   
* MD  
* **Thắng:** Dựa vào thời gian lỗi, Hùng trace để khoanh vùng chính xác span gặp sự cố.   
* MD  
* **Tín:** Đọc log chi tiết của span đó để cTín minh nguyên nhân gốc rễ (root cause).   
* MD  
* **Hùng:** Dựa trên dữ liệu nhóm cung cấp, đề xuất bản fix cùng các biện pháp phòng ngừa tương lai.   
* MD  
  * **Bàn giao:** Tài liệu ghi nhận root cause, hướng sửa lỗi (fix) và preventive measure.   
  * MD

#### **Hoàn tất — 3:30–4:00: Báo cáo và demo**

 MD+ 4

* **Hùng:** Hoàn thiện toàn bộ nội Hùng tài liệu trong file submission/REPORT.md. Thiết kế kịch bản chuẩn bị demo ngắn bám sát luồng: Metrics → Traces → Logs → Root cause.   
* MD+ 1  
* **Cả nhóm:** Kiểm tra repo Git nhằm đảm bảo không commit bất kỳ secret, .env, API key hay PII chưa che. Tiến hành commit toàn bộ source code, test và bằng cTín hợp lệ lên hệ thống. Chuẩn bị giải thích rành mạch phần việc cá nhân mình đã đảm nhận.   
* MD+ 4

Nhóm 4 người :   
Tín  (Logging & Middleware): Phụ trách CP1 (Middleware, Correlation ID, và gán log metadata).   
Thắng  (Security & Compliance): Phụ trách CP1 (Uncomment processor, cấu hình regex patterns che PII và nâng cấp che PII toàn cục).   
Quân (Metrics & Alerting): Phụ trách CP2 (Tích hợp Langfuse, đo đếm error\_rate\_pct, SLO, Alert rules và Runbook).   
Hùng  (QA & Incident Analyst): Chạy load test sinh dữ liệu, thiết kế Dashboard Spec, chủ trì điều tra Challenge (CP3) và Thắng báo cáo REPORT.md. 